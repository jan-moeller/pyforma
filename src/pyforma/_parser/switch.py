from functools import cache
from typing import Any, overload

from .parser import Parser, parser
from .parse_result import ParseResult
from .parse_context import ParseContext
from pyforma._util import defaulted


@cache
def _switch[T, U, V](
    parser_map: tuple[tuple[Parser[T], Parser[U]], ...],
    /,
    *,
    default: Parser[V] | None,
    name: str,
) -> Parser[tuple[T, U] | V]:
    @parser(name=name)
    def parse_switch(context: ParseContext) -> ParseResult:
        for sp, cp in parser_map:
            switch_result = sp(context)
            if switch_result.is_success:
                case_result = cp(switch_result.context)
                if case_result.is_success:
                    return ParseResult[tuple[T, U]].make_success(
                        context=case_result.context,
                        result=(
                            switch_result.success.result,
                            case_result.success.result,
                        ),
                    )
                return ParseResult.make_failure(
                    expected=name, context=context, cause=case_result
                )

        if default is None:
            return ParseResult.make_failure(expected=name, context=context)
        return default(context)

    return parse_switch


@overload
def switch[
    SP1,
    CP1,
    D,
](
    args1: tuple[Parser[SP1], Parser[CP1]],
    /,
    *,
    default: Parser[D],
    name: str | None = None,
) -> Parser[tuple[SP1, CP1] | D]: ...


@overload
def switch[
    SP1,
    CP1,
](
    args1: tuple[Parser[SP1], Parser[CP1]],
    /,
    *,
    name: str | None = None,
) -> Parser[tuple[SP1, CP1]]: ...


@overload
def switch[
    SP1,
    CP1,
    SP2,
    CP2,
    D,
](
    args1: tuple[Parser[SP1], Parser[CP1]],
    args2: tuple[Parser[SP2], Parser[CP2]],
    /,
    *,
    default: Parser[D],
    name: str | None = None,
) -> Parser[tuple[SP1, CP1] | tuple[SP2, CP2] | D]: ...


@overload
def switch[
    SP1,
    CP1,
    SP2,
    CP2,
](
    args1: tuple[Parser[SP1], Parser[CP1]],
    args2: tuple[Parser[SP2], Parser[CP2]],
    /,
    *,
    name: str | None = None,
) -> Parser[tuple[SP1, CP1] | tuple[SP2, CP2]]: ...


@overload
def switch[
    SP1,
    CP1,
    SP2,
    CP2,
    SP3,
    CP3,
    D,
](
    args1: tuple[Parser[SP1], Parser[CP1]],
    args2: tuple[Parser[SP2], Parser[CP2]],
    args3: tuple[Parser[SP3], Parser[CP3]],
    /,
    *,
    default: Parser[D],
    name: str | None = None,
) -> Parser[tuple[SP1, CP1] | tuple[SP2, CP2] | tuple[SP3, CP3] | D]: ...


@overload
def switch[
    SP1,
    CP1,
    SP2,
    CP2,
    SP3,
    CP3,
](
    args1: tuple[Parser[SP1], Parser[CP1]],
    args2: tuple[Parser[SP2], Parser[CP2]],
    args3: tuple[Parser[SP3], Parser[CP3]],
    /,
    *,
    name: str | None = None,
) -> Parser[tuple[SP1, CP1] | tuple[SP2, CP2] | tuple[SP3, CP3]]: ...


@overload
def switch[
    SP1,
    CP1,
    SP2,
    CP2,
    SP3,
    CP3,
    SP4,
    CP4,
    D,
](
    args1: tuple[Parser[SP1], Parser[CP1]],
    args2: tuple[Parser[SP2], Parser[CP2]],
    args3: tuple[Parser[SP3], Parser[CP3]],
    args4: tuple[Parser[SP4], Parser[CP4]],
    /,
    *,
    default: Parser[D],
    name: str | None = None,
) -> Parser[
    tuple[SP1, CP1] | tuple[SP2, CP2] | tuple[SP3, CP3] | tuple[SP4, CP4] | D
]: ...


@overload
def switch[
    SP1,
    CP1,
    SP2,
    CP2,
    SP3,
    CP3,
    SP4,
    CP4,
](
    args1: tuple[Parser[SP1], Parser[CP1]],
    args2: tuple[Parser[SP2], Parser[CP2]],
    args3: tuple[Parser[SP3], Parser[CP3]],
    args4: tuple[Parser[SP4], Parser[CP4]],
    /,
    *,
    name: str | None = None,
) -> Parser[tuple[SP1, CP1] | tuple[SP2, CP2] | tuple[SP3, CP3] | tuple[SP3, CP3]]: ...


@overload
def switch[
    SP1,
    CP1,
    SP2,
    CP2,
    SP3,
    CP3,
    SP4,
    CP4,
    SP5,
    CP5,
    D,
](
    args1: tuple[Parser[SP1], Parser[CP1]],
    args2: tuple[Parser[SP2], Parser[CP2]],
    args3: tuple[Parser[SP3], Parser[CP3]],
    args4: tuple[Parser[SP4], Parser[CP4]],
    args5: tuple[Parser[SP5], Parser[CP5]],
    /,
    *,
    default: Parser[D],
    name: str | None = None,
) -> Parser[
    tuple[SP1, CP1]
    | tuple[SP2, CP2]
    | tuple[SP3, CP3]
    | tuple[SP4, CP4]
    | tuple[SP5, CP5]
    | D
]: ...


@overload
def switch[
    SP1,
    CP1,
    SP2,
    CP2,
    SP3,
    CP3,
    SP4,
    CP4,
    SP5,
    CP5,
](
    args1: tuple[Parser[SP1], Parser[CP1]],
    args2: tuple[Parser[SP2], Parser[CP2]],
    args3: tuple[Parser[SP3], Parser[CP3]],
    args4: tuple[Parser[SP4], Parser[CP4]],
    args5: tuple[Parser[SP5], Parser[CP5]],
    /,
    *,
    name: str | None = None,
) -> Parser[
    tuple[SP1, CP1]
    | tuple[SP2, CP2]
    | tuple[SP3, CP3]
    | tuple[SP3, CP3]
    | tuple[SP3, CP3]
]: ...


@overload
def switch(
    *args: tuple[Parser, Parser],
    default: Parser | None = None,
    name: str | None = None,
) -> Parser[tuple[Any, Any] | Any]: ...


def switch(
    *args: tuple[Parser, Parser],
    default: Parser | None = None,
    name: str | None = None,
) -> Parser[tuple[Any, Any] | Any]:
    """Creates a parser that tries all switch parsers in sequence until one matches, and then follows with the case parser

    Args:
        args: A sequence of switch-parser, case-parser pairs
        default: Parser expected to match if none of the switch parsers matched
        name: Optionally, the name of the parser

    Returns:
        Composed parser
    """

    default_name = f"switch({', '.join(f'{sp.name} => {cp.name}' for sp, cp in args)})"
    name = defaulted(name, default_name)

    return _switch(args, default=default, name=name)
