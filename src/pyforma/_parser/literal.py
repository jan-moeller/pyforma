from typing import LiteralString, overload

from .parse_error import ParseError
from .parse_context import ParseContext
from .parse_result import ParseResult
from .parser import Parser, parser


@overload
def literal[T: LiteralString](s: T) -> Parser[T]: ...


@overload
def literal(s: str) -> Parser[str]: ...


def literal(s: str) -> Parser[str]:
    """Creates a parser for a string literal.

    Args:
        s: The string literal.

    Returns:
        The parser for the given string.
    """

    @parser(name=f"literal_{s}")
    def literal_parser(context: ParseContext) -> ParseResult[str]:
        if context[: len(s)] == s:
            return ParseResult(context=context.consume(len(s)), result=s)

        raise ParseError(f"failed to parse literal {s}", context=context)

    return literal_parser
