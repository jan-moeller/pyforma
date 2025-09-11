from pyforma._ast import Expression

from .parser import Parser
from .alternation import alternation
from .identifier_expression import identifier_expression
from .string_literal_expression import string_literal_expression

expression: Parser[Expression] = alternation(
    identifier_expression,
    string_literal_expression,
)
