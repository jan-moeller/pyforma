import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, final, overload

from .defaulted import defaulted


def _can_call_with(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> bool:
    """Checks if the provided callable can be called with the given arguments

    Args:
        func: The function to check
        args: The arguments to pass to the function
        kwargs: The keyword arguments to pass to the function

    Returns:
        True if the function is callable with the provided arguments, otherwise False

    Raises:
        TypeError: If the provided arguments are not callable
    """
    try:
        signature = inspect.signature(func)
        _ = signature.bind(*args, **kwargs)

        return True

    except TypeError:
        return False

    except Exception as e:  # pragma: no cover
        raise TypeError("Failed to check callability") from e


def _get_positional_index(signature: inspect.Signature, param_name: str) -> int:
    """Get the index of the positional parameter in the signature

    Args:
        signature: The signature of the function
        param_name: The name of the parameter

    Returns:
        The index of the positional parameter in the signature

    Raises:
        TypeError: If no positional index can be determined
    """

    index = 0
    for name, param in signature.parameters.items():
        if param.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            if name == param_name:
                return index

            index += 1

        else:  # pragma: no cover
            break

    # statically impossible to reach in usage below
    raise TypeError(  # pragma: no cover
        f"Can't find positional index of {param_name} in {signature}"
    )


@final
class PipeWrapper[R, **ParamSpec]:
    """Function wrapper that allows piping: val | func"""

    def __init__(
        self,
        func: Callable[ParamSpec, R],
        pipe_arg: int = 0,
        kw_pipe_only: bool = False,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ):
        """Construct a new wrapper

        Args:
            func: The function to wrap
            pipe_arg: Index of the argument that can be piped into the function
            kw_pipe_only: If True, only keyword arguments are allowed in pipe syntax (v | f(a=b))
            args: Positional arguments already passed to the function
            kwargs:  Keyword arguments already passed to the function
        """

        self.func = func
        self.pipe_arg = pipe_arg
        self.kw_pipe_only = kw_pipe_only
        self.args = defaulted(args, ())
        self.kwargs = defaulted(kwargs, dict[str, Any]())

    @overload
    def __call__(self, *args: ParamSpec.args, **kwargs: ParamSpec.kwargs) -> R:
        """Call the function with regular call syntax"""

    @overload
    def __call__(self, *args: Any, **kwargs: Any) -> "PipeWrapper[R, ParamSpec]":
        """Partially call the function with pipe syntax"""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if (self.kw_pipe_only and len(args) != 0) or _can_call_with(
            self.func, args, kwargs
        ):
            return self.func(*args, **kwargs)  # pyright: ignore[reportCallIssue]

        signature = inspect.signature(self.func)

        i = self.pipe_arg
        if len(args) < i:
            _args = args
            _kwargs = kwargs
            _params = tuple(signature.parameters.values())
            for j in range(len(args), i):
                _args = (*_args, kwargs[_params[j].name])
                del _kwargs[_params[j].name]
            _args = (*_args, None)
        else:
            _args = (*args[:i], None, *args[i:])
            _kwargs = kwargs
        bound_args = signature.bind(*_args, **_kwargs)
        return PipeWrapper(
            self.func,
            self.pipe_arg,
            self.kw_pipe_only,
            bound_args.args,
            bound_args.kwargs,
        )

    def __ror__(self, value: Any):
        """Called when 'value | self' is executed."""
        i = self.pipe_arg
        args = (*self.args[:i], value, *self.args[i + 1 :])
        return self.func(*args, **self.kwargs)


def pipeable[R, **Args](
    func: Callable[Args, R],
    /,
    *,
    pipe_arg: int | str = 0,
) -> PipeWrapper[R, Args]:
    """Makes the provided function wrappable

    Args:
        func: The function to wrap
        pipe_arg: Index of the argument that can be piped into the function, or its name

    Returns:
        The wrapped function

    Raises:
        TypeError: Either:
            - The pipe_arg has a default value
            - The pipe_arg is keyword-only
            - The pipe_arg is variadic
            - The pipe_arg name does not exist in the signature
            - The pipe_arg name designates a positional-only argument
            - The pipe_arg index is out of range
    """
    signature = inspect.signature(func)

    match pipe_arg:
        case int() as i:
            if len(signature.parameters) <= i:
                raise TypeError(f"Function must have at least {i + 1} arguments")
            param = list(signature.parameters.values())[i]
        case str() as k:  # pragma: no branch
            if k not in signature.parameters:
                raise TypeError(f"Function must have argument named {k}")
            param = signature.parameters[k]

    match param.kind:
        case inspect.Parameter.POSITIONAL_ONLY if isinstance(pipe_arg, str):
            raise TypeError(
                "POSITIONAL_ONLY arguments must be designated by index, not name"
            )
        case inspect.Parameter.KEYWORD_ONLY:
            raise TypeError("Pipe argument must not be keyword-only")
        case inspect.Parameter.VAR_POSITIONAL | inspect.Parameter.VAR_KEYWORD:
            raise TypeError("Pipe argument must not be variadic")
        case _:
            pass

    # the pipe arg must not be defaulted
    if param.default != inspect.Parameter.empty:
        raise TypeError("Pipe argument can't be defaulted")

    # if any potentially positional arguments are defaulted, or if *args exists -> pipe form only supports keyword arguments
    kw_pipe_only = False
    for p in signature.parameters.values():
        match p.kind:
            case (
                inspect.Parameter.POSITIONAL_ONLY
                | inspect.Parameter.POSITIONAL_OR_KEYWORD
            ):
                kw_pipe_only |= p.default != inspect.Parameter.empty
            case inspect.Parameter.VAR_POSITIONAL:
                kw_pipe_only = True
                break
            case _:
                break

    # translate string form to index form if POSITIONAL_OR_KEYWORD
    if isinstance(pipe_arg, str):
        pipe_arg = _get_positional_index(signature, pipe_arg)

    return wraps(func)(PipeWrapper(func, pipe_arg=pipe_arg, kw_pipe_only=kw_pipe_only))  # pyright: ignore[reportReturnType]
