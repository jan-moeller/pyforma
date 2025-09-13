import ast

from .literal import literal
from .not_in import not_in
from .parse_error import ParseError
from .parser import parser
from .parse_context import ParseContext
from .parse_result import ParseResult
from pyforma._ast import ValueExpression


@parser
def string_literal_expression(context: ParseContext) -> ParseResult[ValueExpression]:
    """Parse a string literal expression."""

    if context.at_eof():
        raise ParseError(
            "expected string literal but found EOF",
            context=context,
            parser=string_literal_expression,
        )

    delim = context.peek()
    if delim not in ['"', "'"]:
        raise ParseError(
            f"expected string literal but found '{delim}'",
            context=context,
            parser=string_literal_expression,
        )

    cur_context = context.consume()
    text_result = not_in(literal(delim))(cur_context)
    cur_context = text_result.context

    if cur_context.at_eof():
        raise ParseError(
            "unterminated string", context=context, parser=string_literal_expression
        )

    cur_context = cur_context.consume()

    return ParseResult(
        result=ValueExpression(ast.literal_eval(f"{delim}{text_result.result}{delim}")),
        context=cur_context,
    )
