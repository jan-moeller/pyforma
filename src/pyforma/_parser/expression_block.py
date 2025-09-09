from dataclasses import dataclass

from .whitespace import whitespace
from .parse_context import ParseContext
from .parse_result import ParseResult
from .identifier import identifier
from .literal import literal
from .sequence import sequence
from .parser import Parser, parser


@dataclass(frozen=True)
class Expression:
    """Holds a pyforma expression."""

    identifier: str  # TODO: extend expression definition


def expression_block(open: str, close: str) -> Parser[Expression]:
    """Creates an expression block parser using the provided open and close markers

    Args:
        open: The opening marker.
        close: The closing marker.

    Returns:
        The expression block parser.

    Raises:
        ValueError: If the open and close markers are the same or one of them is empty.
    """

    if open == close:
        raise ValueError("open and close markers cannot be the same")
    if len(open) == 0 or len(close) == 0:
        raise ValueError("open and close markers cannot be empty")

    base_parser = sequence(
        literal(open), whitespace, identifier, whitespace, literal(close)
    )

    @parser
    def expression(context: ParseContext) -> ParseResult[Expression]:
        r = base_parser(context)
        return ParseResult(context=r.context, result=Expression(r.result[2]))

    return expression
