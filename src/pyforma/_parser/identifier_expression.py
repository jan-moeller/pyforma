from pyforma._ast.expression import ValueExpression
from .parser import parser
from .identifier import identifier
from .parse_context import ParseContext
from .parse_result import ParseResult
from pyforma._ast import IdentifierExpression, Expression


@parser
def identifier_expression(context: ParseContext) -> ParseResult[Expression]:
    """Parse an identifier expression."""

    r = identifier(context)
    match r.result:
        case "True":
            return ParseResult(result=ValueExpression(True), context=r.context)
        case "False":
            return ParseResult(result=ValueExpression(False), context=r.context)
        case _:
            return ParseResult(result=IdentifierExpression(r.result), context=r.context)
