import ast

from .alternation import alternation
from .non_empty import non_empty
from .digits import bindigits, octdigits, hexdigits, digits
from .repetition import repetition
from .sequence import sequence
from .literal import literal
from .parser import parser
from .parse_context import ParseContext
from .parse_result import ParseResult
from pyforma._ast import ValueExpression


@parser
def integer_literal_expression(context: ParseContext) -> ParseResult[ValueExpression]:
    """Parse an integer literal expression."""

    bin_prefix = sequence(literal("0"), alternation(literal("b"), literal("B")))
    oct_prefix = sequence(literal("0"), alternation(literal("o"), literal("O")))
    hex_prefix = sequence(literal("0"), alternation(literal("x"), literal("X")))
    dec_prefix = literal("")

    bin_int = sequence(
        bin_prefix,
        non_empty(bindigits),
        repetition(sequence(literal("_"), non_empty(bindigits))),
    )
    oct_int = sequence(
        oct_prefix,
        non_empty(octdigits),
        repetition(sequence(literal("_"), non_empty(octdigits))),
    )
    hex_int = sequence(
        hex_prefix,
        non_empty(hexdigits),
        repetition(sequence(literal("_"), non_empty(hexdigits))),
    )
    dec_int = sequence(
        dec_prefix,
        non_empty(digits),
        repetition(sequence(literal("_"), non_empty(digits))),
    )

    integer = alternation(bin_int, oct_int, hex_int, dec_int)

    r = integer(context)
    int_text = context[: (r.context.index - context.index)]

    return ParseResult(
        result=ValueExpression(ast.literal_eval(int_text)),
        context=r.context,
    )
