from pyforma._ast import (
    Expression,
    BinOpExpression,
    UnOpExpression,
    CallExpression,
    IndexExpression,
    ValueExpression,
)
from .option import option
from .repetition import repetition
from .whitespace import whitespace
from .sequence import sequence
from .literal import literal
from .parse_context import ParseContext
from .parse_result import ParseResult
from .parser import Parser, parser
from .alternation import alternation
from .identifier_expression import identifier_expression
from .string_literal_expression import string_literal_expression
from .integer_literal_expression import integer_literal_expression
from .floating_point_literal_expression import floating_point_literal_expression


@parser
def paren_expression(context: ParseContext) -> ParseResult[Expression]:
    """Parse a parenthesised expression."""

    parser = sequence(literal("("), whitespace, expression, whitespace, literal(")"))
    r = parser(context)

    return ParseResult(result=r.result[2], context=r.context)


simple_expression: Parser[Expression] = alternation(
    identifier_expression,
    string_literal_expression,
    floating_point_literal_expression,
    integer_literal_expression,
    paren_expression,
)


@parser
def primary_expression(context: ParseContext) -> ParseResult[Expression]:
    _slice = sequence(
        option(expression),
        whitespace,
        literal(":"),
        whitespace,
        option(expression),
        option(sequence(whitespace, literal(":"), option(expression))),
    )
    indexing = sequence(
        literal("["),
        whitespace,
        alternation(_slice, expression),
        whitespace,
        literal("]"),
    )
    p = sequence(simple_expression, repetition(sequence(whitespace, indexing)))
    r = p(context)

    if len(r.result[1]) == 0:
        return ParseResult(result=r.result[0], context=r.context)

    expr = r.result[0]
    for e in r.result[1]:
        index = e[1][2]
        if isinstance(index, Expression):
            expr = IndexExpression(expr, index)
        else:  # slice
            args = [index[0], index[4], index[5][2] if index[5] else None]
            s = CallExpression(
                callee=ValueExpression(slice),
                arguments=[a if a else ValueExpression(None) for a in args],
            )
            expr = IndexExpression(expr, s)

    return ParseResult(result=expr, context=r.context)


def _unop_expression(
    base_expr: Parser[Expression],
    *operators: str,
) -> Parser[Expression]:
    """Implements generic unary operator parsing"""
    op_parsers = tuple(literal(op) for op in operators)

    @parser
    def parse_unary_expression(context: ParseContext) -> ParseResult[Expression]:
        parser = alternation(
            sequence(
                alternation(*op_parsers),
                whitespace,
                parse_unary_expression,
            ),
            base_expr,
        )
        r = parser(context)
        if isinstance(r.result, tuple):
            return ParseResult(
                result=UnOpExpression(op=r.result[0], operand=r.result[2]),
                context=r.context,
            )
        return ParseResult(result=r.result, context=r.context)

    return parse_unary_expression


def _binop_expression(
    base_expr: Parser[Expression],
    *operators: str,
) -> Parser[Expression]:
    """Implements generic binary operator parsing"""
    op_parsers = tuple(literal(op) for op in operators)

    base_parser = sequence(
        base_expr,
        repetition(
            sequence(
                whitespace,
                alternation(*op_parsers),
                whitespace,
                base_expr,
            )
        ),
    )

    @parser
    def parse_binop_expression(context: ParseContext) -> ParseResult[Expression]:
        """Parse a binary expression."""

        r = base_parser(context)
        if len(r.result[1]) == 0:
            return ParseResult(result=r.result[0], context=r.context)
        lhs = r.result[0]
        for elem in r.result[1]:
            op = elem[1]
            rhs = elem[3]
            lhs = BinOpExpression(op=op, lhs=lhs, rhs=rhs)
        return ParseResult(result=lhs, context=r.context)

    return parse_binop_expression


def _comparison_expression(base_expr: Parser[Expression]) -> Parser[Expression]:
    """Implements chained comparison operator parsing"""

    cmp_op = alternation(
        literal("=="),
        literal("!="),
        literal("<="),
        literal("<"),
        literal(">="),
        literal(">"),
    )

    p = sequence(
        base_expr,
        repetition(
            sequence(
                whitespace,
                cmp_op,
                whitespace,
                base_expr,
            )
        ),
    )

    @parser
    def parse_comparison_expression(context: ParseContext) -> ParseResult[Expression]:
        """Parse a comparison expression."""

        r = p(context)
        expressions = [r.result[0], *[e[3] for e in r.result[1]]]
        operators = [e[1] for e in r.result[1]]

        if len(expressions) == 1:
            return ParseResult(result=expressions[0], context=r.context)

        conjunction: list[Expression] = []
        for i in range(len(operators)):
            op = operators[i]
            lhs = expressions[i]
            rhs = expressions[i + 1]
            expr = BinOpExpression(op=op, lhs=lhs, rhs=rhs)
            conjunction.append(expr)

        result_expr = conjunction[0]
        for expr in conjunction[1:]:
            result_expr = BinOpExpression(op="and", lhs=result_expr, rhs=expr)

        return ParseResult(result=result_expr, context=r.context)

    return parse_comparison_expression


@parser
def expression(context: ParseContext) -> ParseResult[Expression]:
    """Parse an expression."""

    power_expression: Parser[Expression] = _binop_expression(primary_expression, "**")
    factor_expression: Parser[Expression] = _unop_expression(
        power_expression, "+", "-", "~"
    )
    term_expression: Parser[Expression] = _binop_expression(
        factor_expression, "*", "//", "/", "%", "@"
    )
    sum_expression: Parser[Expression] = _binop_expression(term_expression, "+", "-")
    shift_expression: Parser[Expression] = _binop_expression(sum_expression, "<<", ">>")
    bw_and_expression: Parser[Expression] = _binop_expression(shift_expression, "&")
    bw_xor_expression: Parser[Expression] = _binop_expression(bw_and_expression, "^")
    bw_or_expression: Parser[Expression] = _binop_expression(bw_xor_expression, "|")
    in_expression: Parser[Expression] = _binop_expression(
        bw_or_expression, "in", "not in"
    )
    comparison_expression: Parser[Expression] = _comparison_expression(in_expression)
    inversion_expression: Parser[Expression] = _unop_expression(
        comparison_expression, "not"
    )
    conjunction_expression: Parser[Expression] = _binop_expression(
        inversion_expression, "and"
    )
    disjunction_expression: Parser[Expression] = _binop_expression(
        conjunction_expression, "or"
    )

    return disjunction_expression(context)
