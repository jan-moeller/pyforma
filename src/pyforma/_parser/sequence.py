from typing import Any, overload

from .parse_error import ParseError
from .parse_result import ParseResult
from .parse_context import ParseContext
from .parser import Parser, parser


@overload
def sequence() -> Parser[tuple[()]]: ...


@overload
def sequence[T](
    p: Parser[T],
    /,
) -> Parser[tuple[T]]: ...


@overload
def sequence[T1, T2](
    p1: Parser[T1],
    p2: Parser[T2],
    /,
) -> Parser[tuple[T1, T2]]: ...


@overload
def sequence[T1, T2, T3](
    p1: Parser[T1],
    p2: Parser[T2],
    p3: Parser[T3],
    /,
) -> Parser[tuple[T1, T2, T3]]: ...


@overload
def sequence[T1, T2, T3, T4](
    p1: Parser[T1],
    p2: Parser[T2],
    p3: Parser[T3],
    p4: Parser[T4],
    /,
) -> Parser[tuple[T1, T2, T3, T4]]: ...


@overload
def sequence[T1, T2, T3, T4, T5](
    p1: Parser[T1],
    p2: Parser[T2],
    p3: Parser[T3],
    p4: Parser[T4],
    p5: Parser[T5],
    /,
) -> Parser[tuple[T1, T2, T3, T4, T5]]: ...


@overload
def sequence(*parsers: Parser[Any]) -> Parser[tuple[Any, ...]]: ...


def sequence(*in_parsers: Parser[Any]) -> Parser[tuple[Any, ...]]:
    """Creates a parser that runs the provided parsers in sequence.

    Args:
        in_parsers: the parsers to run in sequence

    Returns:
        Parser that runs the provided parsers in sequence
    """

    @parser(name=f"sequence_{'__'.join(p.name for p in in_parsers)}")
    def sequence_parser(context: ParseContext) -> ParseResult[tuple[Any, ...]]:
        cur_context = context
        results: list[Any] = []
        try:
            for p in in_parsers:
                r = p(cur_context)
                cur_context = r.context
                results.append(r.result)

        except ParseError as e:
            raise ParseError("", parser=sequence_parser, context=context) from e

        return ParseResult(context=cur_context, result=tuple(results))

    return sequence_parser
