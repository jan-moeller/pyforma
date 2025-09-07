from .parse_error import ParseError
from .parse_input import ParseInput
from .parse_result import ParseResult
from .parser import Parser, parser


def literal(s: str) -> Parser[str]:
    """Creates a parser for a string literal.

    Args:
        s: The string literal.

    Returns:
        The parser for the given string.
    """

    @parser(name=f"literal_{s}")
    def literal_parser(input: ParseInput) -> ParseResult[str]:
        if input[: len(s)] == s:
            return ParseResult(remaining=input.consume(len(s)), result=s)

        raise ParseError(
            f"failed to parse literal {s}",
            parser=literal_parser,
            input=input,
        )

    return literal_parser
