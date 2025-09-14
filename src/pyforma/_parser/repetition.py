from functools import cache

from pyforma._parser.parse_error import ParseError
from .parse_context import ParseContext
from .parse_result import ParseResult
from .parser import Parser, parser


@cache
def _repetition[T](in_parser: Parser[T]) -> Parser[tuple[T, ...]]:
    @parser
    def parse_repetition(context: ParseContext) -> ParseResult[tuple[T, ...]]:
        cur_context = context
        results: list[T] = []
        while not cur_context.at_eof():
            try:
                r = in_parser(cur_context)
                results.append(r.result)
                cur_context = r.context
            except ParseError:
                break

        return ParseResult(context=cur_context, result=tuple(results))

    return parse_repetition


def repetition[T](in_parser: Parser[T]) -> Parser[tuple[T, ...]]:
    """Creates a parser that repeatedly runs the provided parser

    Args:
        in_parser: The parser to run repeatedly

    Returns:
        A parser repeatedly running the provided parser while it matches. If it never matches, an empty match is returned.
    """

    return _repetition(in_parser)
