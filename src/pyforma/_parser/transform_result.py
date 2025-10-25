import inspect
from collections.abc import Callable
from functools import cache
from typing import Any, overload

from .parse_result import ParseResult
from .parse_context import ParseContext
from .parser import Parser, parser
from pyforma._util import defaulted


@overload
def _wrap_transform[T, R](f: Callable[[T], R]) -> Callable[[T, ParseContext], R]: ...


@overload
def _wrap_transform[T, R](
    f: Callable[[T, ParseContext], R],
) -> Callable[[T, ParseContext], R]: ...


def _wrap_transform(f: Callable[..., Any]) -> Callable[..., Any]:
    try:
        sig = inspect.signature(f)
        amount = len(sig.parameters)
    except ValueError:  # Workaround for built-in functions
        amount = 1

    if amount == 2:
        return f
    return lambda p, _: f(p)  # pyright: ignore[reportUnknownLambdaType, reportUnknownVariableType]


@cache
def _transform_result[T, U](
    in_parser: Parser[T],
    /,
    *,
    transform: Callable[[ParseResult[T]], ParseResult[U]]
    | Callable[[ParseResult[T], ParseContext], ParseResult[U]],
    name: str,
) -> Parser[U]:
    transform = _wrap_transform(transform)

    @parser(name=name)
    def parse_transform(context: ParseContext) -> ParseResult[U]:
        r = in_parser(context)
        return transform(r, context)

    return parse_transform


def transform_result[T, U](
    in_parser: Parser[T],
    /,
    *,
    transform: Callable[[ParseResult[T]], ParseResult[U]]
    | Callable[[ParseResult[T], ParseContext], ParseResult[U]],
    name: str | None = None,
) -> Parser[U]:
    """Creates a parser that behaves like the provided parser but transforms the result

    Args:
        in_parser: The base parser
        transform: The transformation function
        name: Optional parser name

    Returns:
        Composed parser
    """

    name = defaulted(name, f"transform({in_parser.name}, {transform.__name__})")

    return _transform_result(in_parser, transform=transform, name=name)


def transform_success[T, U](
    in_parser: Parser[T],
    /,
    *,
    transform: Callable[[T], U] | Callable[[T, ParseContext], U],
    name: str | None = None,
) -> Parser[U]:
    """Creates a parser that behaves like the provided parser but transforms the result, if successful

        Args:
        in_parser: The base parser
        transform: The transformation function
        name: Optional parser name

    Returns:
        Composed parser
    """

    name = defaulted(name, f"transform_success({in_parser.name}, {transform.__name__})")
    transform = _wrap_transform(transform)

    def _transform(result: ParseResult[T], context: ParseContext) -> ParseResult[U]:
        if result.is_success:
            transformed = transform(result.success.result, context)
            return ParseResult.make_success(context=result.context, result=transformed)
        return ParseResult(result.failure, context=result.context)

    return _transform_result(in_parser, transform=_transform, name=name)


@cache
def _transform_consumed[T, U](
    in_parser: Parser[T],
    /,
    *,
    transform: Callable[[str], U] | Callable[[str, ParseContext], U],
    name: str,
) -> Parser[U]:
    transform = _wrap_transform(transform)

    @parser(name=name)
    def parse_transform(context: ParseContext) -> ParseResult[U]:
        r = in_parser(context)
        if r.is_success:
            consumed = context[: (r.context.index - context.index)]
            transformed = transform(consumed, context)
            return ParseResult.make_success(context=r.context, result=transformed)
        return ParseResult(r.failure, context=r.context)

    return parse_transform


def transform_consumed[T, U](
    in_parser: Parser[T],
    /,
    *,
    transform: Callable[[str], U] | Callable[[str, ParseContext], U],
    name: str | None = None,
) -> Parser[U]:
    """Creates a parser that behaves like the provided parser but transforms the result, if successful

        Args:
        in_parser: The base parser
        transform: The transformation function
        name: Optional parser name

    Returns:
        Composed parser
    """

    name = defaulted(
        name,
        f"transform_consumed({in_parser.name}, {transform.__name__})",
    )

    return _transform_consumed(in_parser, transform=transform, name=name)
