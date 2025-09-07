from typing import overload, NoReturn

from .parse_error import ParseError
from .parse_context import ParseContext
from .parse_result import ParseResult
from .parser import Parser, parser


@overload
def alternation() -> NoReturn: ...


@overload
def alternation[T](
    p: Parser[T],
    /,
) -> Parser[T]: ...


@overload
def alternation[T1, T2](
    p1: Parser[T1],
    p2: Parser[T2],
    /,
) -> Parser[T1 | T2]: ...


@overload
def alternation[T1, T2, T3](
    p1: Parser[T1],
    p2: Parser[T2],
    p3: Parser[T3],
    /,
) -> Parser[T1 | T2 | T3]: ...


@overload
def alternation[T1, T2, T3, T4](
    p1: Parser[T1],
    p2: Parser[T2],
    p3: Parser[T3],
    p4: Parser[T4],
    /,
) -> Parser[T1 | T2 | T3 | T4]: ...


@overload
def alternation[T1, T2, T3, T4, T5](
    p1: Parser[T1],
    p2: Parser[T2],
    p3: Parser[T3],
    p4: Parser[T4],
    p5: Parser[T5],
    /,
) -> Parser[T1 | T2 | T3 | T4 | T5]: ...


@overload
def alternation(*parsers: Parser) -> Parser: ...


def alternation(*parsers: Parser) -> Parser:
    """Create a parser that runs the provided parsers in sequence until one matches, then returns that result.

    Args:
        *parsers: Parsers to try one after another.

    Returns:
        The alternation parser.
    """

    @parser(name=f"alternation_{'__'.join(p.name for p in parsers)}")
    def parse_alternations(context: ParseContext) -> ParseResult:
        for p in parsers:
            try:
                return p(context)
            except ParseError:
                pass
        raise ParseError(
            "none of the alternatives match",
            parser=parse_alternations,
            context=context,
        )

    return parse_alternations
