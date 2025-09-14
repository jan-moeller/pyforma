from functools import cache

from .parse_error import ParseError
from .parse_result import ParseResult
from .parse_context import ParseContext
from .parser import Parser, parser


@cache
def _option[T](in_parser: Parser[T], /) -> Parser[T | None]:
    @parser(name=f"optional_{in_parser.name}")
    def parse_option(context: ParseContext) -> ParseResult[T | None]:
        try:
            r = in_parser(context)
        except ParseError:
            return ParseResult(context=context, result=None)
        return r

    return parse_option


def option[T](in_parser: Parser[T], /) -> Parser[T | None]:
    """Creates a parser that behaves like the provided parser but returns an empty match on failure

    Args:
        in_parser: The base parser

    Returns:
        Composed parser
    """

    return _option(in_parser)
