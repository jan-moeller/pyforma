from dataclasses import dataclass

from .whitespace import whitespace
from .parse_context import ParseContext
from .parse_result import ParseResult
from .identifier import identifier
from .literal import literal
from .sequence import sequence
from .parser import Parser, parser
from .template_syntax_config import BlockSyntaxConfig


@dataclass(frozen=True)
class Expression:
    """Holds a pyforma expression."""

    identifier: str  # TODO: extend expression definition


def expression_block(syntax: BlockSyntaxConfig) -> Parser[Expression]:
    """Creates an expression block parser using the provided open and close markers

    Args:
        syntax: The syntax config to use

    Returns:
        The expression block parser.
    """

    base_parser = sequence(
        literal(syntax.open), whitespace, identifier, whitespace, literal(syntax.close)
    )

    @parser
    def expression(context: ParseContext) -> ParseResult[Expression]:
        r = base_parser(context)
        return ParseResult(context=r.context, result=Expression(r.result[2]))

    return expression
