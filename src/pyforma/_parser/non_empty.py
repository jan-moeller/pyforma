from functools import cache
from .parser import Parser, parser
from .parse_error import ParseError
from .parse_result import ParseResult
from .parse_context import ParseContext


@cache
def _non_empty[T](in_parser: Parser[T], /) -> Parser[T]:
    @parser(name=f"non_empty_{in_parser.name}")
    def parse_non_empty(context: ParseContext) -> ParseResult[T]:
        r = in_parser(context)
        if r.context == context:
            raise ParseError("expected non-empty result", context=context)
        return r

    return parse_non_empty


def non_empty[T](in_parser: Parser[T], /) -> Parser[T]:
    """Creates a parser that behaves like the provided parser but fails on empty matches

    Args:
        in_parser: The base parser

    Returns:
        Composed parser
    """

    return _non_empty(in_parser)
