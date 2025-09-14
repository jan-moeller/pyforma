from functools import cache
from typing import LiteralString, overload

from .parse_context import ParseContext
from .parse_result import ParseResult
from .parser import Parser, parser


@overload
def literal[T: LiteralString](s: T, /) -> Parser[T]: ...


@overload
def literal(s: str, /) -> Parser[str]: ...


@cache
def literal(s: str, /) -> Parser[str]:
    """Creates a parser for a string literal.

    Args:
        s: The string literal.

    Returns:
        The parser for the given string.
    """

    name = f'"{s}"'

    @parser(name=name)
    def literal_parser(context: ParseContext) -> ParseResult[str]:
        if context[: len(s)] == s:
            return ParseResult.make_success(context=context.consume(len(s)), result=s)

        return ParseResult.make_failure(
            context=context,
            expected=name,
        )

    return literal_parser
