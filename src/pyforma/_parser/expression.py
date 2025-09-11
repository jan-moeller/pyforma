from pyforma._ast import Expression

from .identifier_expression import identifier_expression
from .parser import Parser


expression: Parser[Expression] = identifier_expression
