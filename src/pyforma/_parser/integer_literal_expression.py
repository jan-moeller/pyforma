import ast

from .nothing import nothing
from .switch import switch
from .transform_result import transform_consumed
from .alternation import alternation
from .non_empty import non_empty
from .digits import bindigits, octdigits, hexdigits, digits
from .repetition import repetition
from .sequence import sequence
from .literal import literal
from pyforma._ast import ValueExpression

_bin_prefix = alternation(literal("b"), literal("B"))
_oct_prefix = alternation(literal("o"), literal("O"))
_hex_prefix = alternation(literal("x"), literal("X"))

_bin_int = sequence(
    non_empty(bindigits),
    repetition(sequence(literal("_"), non_empty(bindigits))),
)
_oct_int = sequence(
    non_empty(octdigits),
    repetition(sequence(literal("_"), non_empty(octdigits))),
)
_hex_int = sequence(
    non_empty(hexdigits),
    repetition(sequence(literal("_"), non_empty(hexdigits))),
)
_dec_int = sequence(
    non_empty(digits),
    repetition(sequence(literal("_"), non_empty(digits))),
)

integer_literal_expression = transform_consumed(
    switch(
        (
            literal("0"),
            switch(
                (_bin_prefix, _bin_int),
                (_oct_prefix, _oct_int),
                (_hex_prefix, _hex_int),
                default=nothing,
            ),
        ),
        default=_dec_int,
        name="integer literal",
    ),
    transform=lambda s: ValueExpression(value=ast.literal_eval(s)),
)
"""Parser for python-like integer literals"""
