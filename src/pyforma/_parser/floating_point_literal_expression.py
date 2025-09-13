import ast

from .alternation import alternation
from .option import option
from .non_empty import non_empty
from .digits import digits
from .repetition import repetition
from .sequence import sequence
from .literal import literal
from .parser import parser
from .parse_context import ParseContext
from .parse_result import ParseResult
from pyforma._ast import ValueExpression


@parser
def floating_point_literal_expression(
    context: ParseContext,
) -> ParseResult[ValueExpression]:
    """Parse a float literal expression."""

    dec = sequence(
        non_empty(digits), repetition(sequence(literal("_"), non_empty(digits)))
    )

    floating_point = sequence(
        dec,
        alternation(
            sequence(
                literal("."),
                option(dec),
            ),
            sequence(
                alternation(literal("e"), literal("E")),
                option(alternation(literal("-"), literal("+"))),
                dec,
            ),
        ),
    )

    r = floating_point(context)
    float_text = context[: (r.context.index - context.index)]

    return ParseResult(
        result=ValueExpression(ast.literal_eval(float_text)),
        context=r.context,
    )
