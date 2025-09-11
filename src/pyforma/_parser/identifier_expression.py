from .parser import parser
from .identifier import identifier
from .parse_context import ParseContext
from .parse_result import ParseResult
from pyforma._ast import IdentifierExpression


@parser
def identifier_expression(context: ParseContext) -> ParseResult[IdentifierExpression]:
    """Parse an identifier expression."""

    r = identifier(context)
    return ParseResult(result=IdentifierExpression(r.result), context=r.context)
