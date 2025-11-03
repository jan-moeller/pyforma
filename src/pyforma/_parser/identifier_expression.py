from pyforma._ast.expressions import ValueExpression
from .parser import parser
from .identifier import identifier
from .parse_context import ParseContext
from .parse_result import ParseResult
from pyforma._ast import IdentifierExpression, Expression


@parser
def identifier_expression(context: ParseContext) -> ParseResult[Expression]:
    """Parse an identifier expression."""

    r = identifier(context)
    if r.is_failure:
        return ParseResult.make_failure(
            expected=identifier.name,
            context=context,
            cause=r,
        )
    match r.success.result:
        case "True":
            return ParseResult.make_success(
                result=ValueExpression(origin=context.origin(), value=True),
                context=r.context,
            )
        case "False":
            return ParseResult.make_success(
                result=ValueExpression(origin=context.origin(), value=False),
                context=r.context,
            )
        case "None":
            return ParseResult.make_success(
                result=ValueExpression(origin=context.origin(), value=None),
                context=r.context,
            )
        case "lambda":
            return ParseResult.make_failure(
                context=context,
                expected="identifier",
                cause=r,
            )
        case _:
            return ParseResult.make_success(
                result=IdentifierExpression(
                    origin=context.origin(),
                    identifier=r.success.result,
                ),
                context=r.context,
            )
