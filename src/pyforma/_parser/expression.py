from dataclasses import dataclass
from functools import cache
from typing import LiteralString, cast

from pyforma._ast.expressions import (
    Expression,
    ValueExpression,
    UnOpExpression,
    BinOpExpression,
    IndexExpression,
    CallExpression,
    AttributeExpression,
    ListExpression,
    DictExpression,
    LambdaExpression,
    IfExpression,
    ForExpression,
    WithExpression,
    TemplateExpression,
)
from pyforma._util import defaulted
from .enclosed import enclosed
from .negative_lookahead import negative_lookahead
from .non_empty import non_empty
from .delimited import delimited
from .identifier import identifier
from .transform_result import transform_success, transform_result
from .option import option
from .repetition import repetition
from .whitespace import whitespace
from .sequence import sequence
from .literal import literal
from .parse_context import ParseContext
from pyforma._ast.origin import Origin
from .parse_result import ParseResult
from .parser import Parser, parser
from .alternation import alternation
from .identifier_expression import identifier_expression
from .string_literal_expression import string_literal_expression
from .integer_literal_expression import integer_literal_expression
from .floating_point_literal_expression import floating_point_literal_expression


@cache
def expression(
    template_parser: Parser[TemplateExpression],
) -> Parser[Expression]:
    @parser(name="expression")
    def parse_expression(context: ParseContext) -> ParseResult[Expression]:
        """Parse an expression."""

        if context.at_eof():
            return ParseResult.make_failure(
                context=context, expected=parse_expression.name
            )

        power_expression: Parser[Expression] = _binop_expression(
            primary_expression(template_parser), "**"
        )
        factor_expression: Parser[Expression] = _unop_expression(
            power_expression, "+", "-", "~"
        )
        term_expression: Parser[Expression] = _binop_expression(
            factor_expression, "*", "//", "/", "%", "@"
        )
        sum_expression: Parser[Expression] = _binop_expression(
            term_expression, "+", "-"
        )
        shift_expression: Parser[Expression] = _binop_expression(
            sum_expression, "<<", ">>"
        )
        bw_and_expression: Parser[Expression] = _binop_expression(shift_expression, "&")
        bw_xor_expression: Parser[Expression] = _binop_expression(
            bw_and_expression, "^"
        )
        bw_or_expression: Parser[Expression] = _binop_expression(bw_xor_expression, "|")
        in_expression: Parser[Expression] = _binop_expression(
            bw_or_expression, "in", "not in"
        )
        comparison_expression: Parser[Expression] = _comparison_expression(
            in_expression
        )
        inversion_expression: Parser[Expression] = _unop_expression(
            comparison_expression, "not"
        )
        conjunction_expression: Parser[Expression] = _binop_expression(
            inversion_expression, "and"
        )
        disjunction_expression: Parser[Expression] = _binop_expression(
            conjunction_expression, "or"
        )

        r = disjunction_expression(context)
        if r.is_failure:
            return ParseResult.make_failure(
                expected=parse_expression.name,
                context=context,
                cause=r,
            )
        return r

    return parse_expression


@cache
def paren_expression(
    template_parser: Parser[TemplateExpression],
) -> Parser[Expression]:
    paren_expression = transform_success(
        sequence(
            literal("("),
            whitespace,
            expression(template_parser),
            whitespace,
            literal(")"),
            name="paren-expression",
        ),
        transform=lambda s: s[2],
    )
    return paren_expression


@cache
def list_expression(
    template_parser: Parser[TemplateExpression],
) -> Parser[ListExpression]:
    list_expression = transform_success(
        sequence(
            literal("["),
            delimited(
                delim=sequence(whitespace, literal(","), whitespace),
                content=expression(template_parser),
                allow_trailing_delim=False,
            ),
            literal("]"),
            name="list-expression",
        ),
        transform=lambda s, c: ListExpression(origin=c.origin(), elements=s[1]),
    )
    return list_expression


@cache
def dict_expression(
    template_parser: Parser[TemplateExpression],
) -> Parser[DictExpression]:
    dict_expression = transform_success(
        sequence(
            literal("{"),
            delimited(
                delim=sequence(whitespace, literal(","), whitespace),
                content=transform_success(
                    sequence(
                        expression(template_parser),
                        whitespace,
                        literal(":"),
                        whitespace,
                        expression(template_parser),
                    ),
                    transform=lambda s: (s[0], s[4]),
                ),
                allow_trailing_delim=False,
            ),
            literal("}"),
            name="dict-expression",
        ),
        transform=lambda s, c: DictExpression(origin=c.origin(), elements=s[1]),
    )
    return dict_expression


@cache
def lambda_expression(
    template_parser: Parser[TemplateExpression],
) -> Parser[LambdaExpression]:
    lambda_expression = transform_success(
        sequence(
            literal("lambda"),
            whitespace,
            delimited(
                delim=sequence(whitespace, literal(","), whitespace),
                content=identifier,
                allow_trailing_delim=False,
            ),
            whitespace,
            literal(":"),
            whitespace,
            expression(template_parser),
        ),
        transform=lambda s, c: LambdaExpression(
            origin=c.origin(), parameters=s[2], return_value=s[6]
        ),
    )
    return lambda_expression


@cache
def if_expression(
    template_parser: Parser[TemplateExpression],
) -> Parser[IfExpression]:
    if_expression = transform_success(
        sequence(
            transform_success(
                sequence(
                    literal("if"),
                    non_empty(whitespace),
                    expression(template_parser),
                    whitespace,
                    literal(":"),
                    whitespace,
                    expression(template_parser),
                    whitespace,
                    name="if-branch",
                ),
                transform=lambda s: (s[2], s[6]),
            ),
            repetition(
                transform_success(
                    sequence(
                        literal("elif"),
                        non_empty(whitespace),
                        expression(template_parser),
                        whitespace,
                        literal(":"),
                        whitespace,
                        expression(template_parser),
                        whitespace,
                        name="elif-branch",
                    ),
                    transform=lambda s: (s[2], s[6]),
                )
            ),
            transform_success(
                option(
                    sequence(
                        literal("else"),
                        whitespace,
                        literal(":"),
                        whitespace,
                        expression(template_parser),
                        whitespace,
                        name="else-branch",
                    ),
                ),
                transform=lambda s, c: (
                    (
                        ValueExpression(origin=c.origin(), value=True),
                        s[4],
                    ),
                )
                if s is not None
                else (),
            ),
        ),
        transform=lambda s, c: IfExpression(
            origin=c.origin(), cases=(s[0], *s[1], *s[2])
        ),
    )
    return if_expression


@cache
def for_expression(
    template_parser: Parser[TemplateExpression],
) -> Parser[ForExpression]:
    for_expression = transform_success(
        sequence(
            literal("for"),
            whitespace,
            non_empty(
                delimited(
                    delim=sequence(whitespace, literal(","), whitespace),
                    content=identifier,
                    allow_trailing_delim=False,
                )
            ),
            whitespace,
            literal("in"),
            whitespace,
            expression(template_parser),
            whitespace,
            literal(":"),
            whitespace,
            expression(template_parser),
            whitespace,
        ),
        transform=lambda s, c: ForExpression(
            origin=c.origin(),
            var_names=(s[2]),
            iter_expr=s[6],
            expr=s[10],
        ),
    )
    return for_expression


@cache
def with_expression(
    template_parser: Parser[TemplateExpression],
) -> Parser[WithExpression]:
    with_expression = transform_success(
        sequence(
            literal("with"),
            whitespace,
            non_empty(
                delimited(
                    delim=sequence(whitespace, literal(";"), whitespace),
                    content=transform_success(
                        sequence(
                            non_empty(
                                delimited(
                                    delim=sequence(
                                        whitespace, literal(","), whitespace
                                    ),
                                    content=identifier,
                                    allow_trailing_delim=False,
                                )
                            ),
                            whitespace,
                            literal("="),
                            whitespace,
                            expression(template_parser),
                        ),
                        transform=lambda s: (s[0], s[4]),
                    ),
                    allow_trailing_delim=False,
                )
            ),
            whitespace,
            literal(":"),
            whitespace,
            expression(template_parser),
        ),
        transform=lambda s, c: WithExpression(
            origin=c.origin(),
            bindings=s[2],
            expr=s[6],
        ),
    )
    return with_expression


@cache
def simple_expression(
    template_parser: Parser[TemplateExpression],
) -> Parser[Expression]:
    simple_expression: Parser[Expression] = alternation(
        identifier_expression,
        string_literal_expression,
        floating_point_literal_expression,
        integer_literal_expression,
        template_expression(template_parser),
        paren_expression(template_parser),
        list_expression(template_parser),
        dict_expression(template_parser),
        lambda_expression(template_parser),
        if_expression(template_parser),
        for_expression(template_parser),
        with_expression(template_parser),
        name="simple-expression",
    )
    return simple_expression


@dataclass(frozen=True)
class Slice:
    start: Expression
    stop: Expression
    step: Expression


_none_expr = ValueExpression(
    origin=Origin(position=(0, 0), source_id=""),
    value=None,
)


@cache
def _slice(
    template_parser: Parser[TemplateExpression],
) -> Parser[Slice]:
    _slice = transform_success(
        sequence(
            option(expression(template_parser)),
            whitespace,
            literal(":"),
            whitespace,
            option(expression(template_parser)),
            option(
                sequence(
                    whitespace,
                    literal(":"),
                    option(expression(template_parser)),
                )
            ),
            name="slice",
        ),
        transform=lambda s: Slice(
            defaulted(s[0], _none_expr),
            defaulted(s[4], _none_expr),
            defaulted(s[5][2], _none_expr) if s[5] else _none_expr,
        ),
    )
    return _slice


@dataclass(frozen=True)
class Indexing:
    index: Expression | Slice


@cache
def _indexing(
    template_parser: Parser[TemplateExpression],
) -> Parser[Indexing]:
    _indexing = transform_success(
        sequence(
            literal("["),
            whitespace,
            alternation(_slice(template_parser), expression(template_parser)),
            whitespace,
            literal("]"),
            name="indexing",
        ),
        transform=lambda s: Indexing(s[2]),
    )
    return _indexing


@dataclass(frozen=True)
class CallArguments:
    args: tuple[Expression, ...] = ()
    kwargs: tuple[tuple[str, Expression], ...] = ()


@cache
def _call_args(
    template_parser: Parser[TemplateExpression],
    allow_trailing: bool,
) -> Parser[tuple[Expression, ...]]:
    return transform_success(
        delimited(
            delim=sequence(whitespace, literal(","), whitespace),
            content=sequence(
                negative_lookahead(sequence(identifier, whitespace, literal("="))),
                expression(template_parser),
            ),
            allow_trailing_delim=allow_trailing,
            name="call-arguments",
        ),
        transform=lambda s: tuple(e[1] for e in s),
    )


@cache
def _call_kwargs(
    template_parser: Parser[TemplateExpression],
    allow_trailing: bool,
) -> Parser[tuple[tuple[str, Expression], ...]]:
    return transform_success(
        option(
            transform_success(
                delimited(
                    delim=sequence(whitespace, literal(","), whitespace),
                    content=sequence(
                        identifier,
                        whitespace,
                        literal("="),
                        whitespace,
                        expression(template_parser),
                    ),
                    allow_trailing_delim=allow_trailing,
                    name="call-kw-arguments",
                ),
                transform=lambda s: tuple((e[0], e[4]) for e in s),
            )
        ),
        transform=lambda s: defaulted(s, cast(tuple[tuple[str, Expression], ...], ())),
    )


@dataclass(frozen=True)
class AttributeAccess:
    identifier: str


@cache
def _call(
    template_parser: Parser[TemplateExpression],
) -> Parser[CallArguments]:
    _call = transform_success(
        sequence(
            literal("("),
            whitespace,
            alternation(
                transform_success(
                    sequence(
                        non_empty(_call_args(template_parser, False)),
                        whitespace,
                        literal(","),
                        whitespace,
                        non_empty(_call_kwargs(template_parser, True)),
                        name="args-and-kwargs",
                    ),
                    transform=lambda s: CallArguments(s[0], s[4]),
                ),
                transform_success(
                    non_empty(_call_kwargs(template_parser, True)),
                    transform=lambda s: CallArguments((), s),
                    name="kwargs",
                ),
                transform_success(
                    _call_args(template_parser, True),
                    transform=lambda s: CallArguments(s, ()),
                    name="args",
                ),
            ),
            whitespace,
            literal(")"),
            name="call",
        ),
        transform=lambda s: s[2],
    )
    return _call


_attribute = transform_success(
    sequence(literal("."), whitespace, identifier),
    transform=lambda s: AttributeAccess(s[2]),
)


def _transform_primary_expression(
    result: ParseResult[
        tuple[Expression, tuple[Indexing | CallArguments | AttributeAccess, ...]]
    ],
    context: ParseContext,
) -> ParseResult[Expression]:
    """Transforms the basic parse result into an expression."""

    if result.is_failure:
        return ParseResult.make_failure(
            expected="primary_expression",
            context=result.context,
            cause=result,
        )

    expr = result.success.result[0]
    for e in result.success.result[1]:
        match e:
            case CallArguments():
                expr = CallExpression(
                    origin=context.origin(),
                    callee=expr,
                    arguments=e.args,
                    kw_arguments=e.kwargs,
                )
            case AttributeAccess():
                expr = AttributeExpression(
                    origin=context.origin(),
                    object=expr,
                    attribute=e.identifier,
                )
            case Indexing():  # pragma: no branch
                index = e.index
                if isinstance(index, Expression):
                    expr = IndexExpression(
                        origin=context.origin(),
                        expression=expr,
                        index=index,
                    )
                else:  # slice
                    args = (index.start, index.stop, index.step)
                    s = CallExpression(
                        origin=context.origin(),
                        callee=ValueExpression(origin=context.origin(), value=slice),
                        arguments=args,
                        kw_arguments=(),
                    )
                    expr = IndexExpression(
                        origin=context.origin(),
                        expression=expr,
                        index=s,
                    )

    return ParseResult.make_success(result=expr, context=result.context)


@cache
def primary_expression(
    template_parser: Parser[TemplateExpression],
) -> Parser[Expression]:
    primary_expression = transform_result(
        transform_success(
            sequence(
                simple_expression(template_parser),
                repetition(
                    sequence(
                        whitespace,
                        alternation(
                            _indexing(template_parser),
                            _call(template_parser),
                            _attribute,
                        ),
                    )
                ),
                name="primary-expression",
            ),
            transform=lambda s: (s[0], tuple(e[1] for e in s[1])),
        ),
        transform=_transform_primary_expression,
    )
    return primary_expression


@cache
def _unop_expression(
    base_expr: Parser[Expression],
    *operators: LiteralString,
) -> Parser[Expression]:
    """Implements generic unary operator parsing"""
    op_parsers = tuple(literal(op) for op in operators)

    @parser(name=f"unary-expression({', '.join(op.name for op in op_parsers)})")
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
        if r.is_failure:
            return ParseResult.make_failure(
                expected=parse_unary_expression.name,
                context=context,
                cause=r,
            )

        if isinstance(r.success.result, tuple):
            return ParseResult.make_success(
                result=UnOpExpression(
                    origin=context.origin(),
                    op=r.success.result[0],
                    operand=r.success.result[2],
                ),
                context=r.context,
            )
        return ParseResult.make_success(result=r.success.result, context=r.context)

    return parse_unary_expression


@cache
def _binop_expression(
    base_expr: Parser[Expression],
    *operators: LiteralString,
) -> Parser[Expression]:
    """Implements generic binary operator parsing"""
    op_parsers = tuple(literal(op) for op in operators)

    base_parser = transform_success(
        sequence(
            base_expr,
            repetition(
                sequence(
                    whitespace,
                    alternation(*op_parsers),
                    whitespace,
                    base_expr,
                )
            ),
        ),
        transform=lambda s: (s[0], tuple((e[1], e[3]) for e in s[1])),
    )

    @parser(name=f"binary-expression({', '.join(op.name for op in op_parsers)})")
    def parse_binop_expression(context: ParseContext) -> ParseResult[Expression]:
        """Parse a binary expression."""

        r = base_parser(context)
        if r.is_failure:
            return ParseResult.make_failure(
                expected=parse_binop_expression.name,
                context=context,
                cause=r,
            )

        lhs = r.success.result[0]
        for elem in r.success.result[1]:
            op = elem[0]
            rhs = elem[1]
            lhs = BinOpExpression(origin=context.origin(), op=op, lhs=lhs, rhs=rhs)
        return ParseResult.make_success(result=lhs, context=r.context)

    return parse_binop_expression


@cache
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

    base_parser = transform_success(
        sequence(
            base_expr,
            repetition(
                sequence(
                    whitespace,
                    cmp_op,
                    whitespace,
                    base_expr,
                )
            ),
        ),
        transform=lambda s: (s[0], tuple((e[1], e[3]) for e in s[1])),
    )

    @parser(name="comparison-expression")
    def parse_comparison_expression(context: ParseContext) -> ParseResult[Expression]:
        """Parse a comparison expression."""

        r = base_parser(context)
        if r.is_failure:
            return ParseResult.make_failure(
                expected=parse_comparison_expression.name,
                context=context,
                cause=r,
            )

        expressions = [r.success.result[0], *[e[1] for e in r.success.result[1]]]
        operators = [e[0] for e in r.success.result[1]]

        if len(expressions) == 1:
            return ParseResult.make_success(result=expressions[0], context=r.context)

        conjunction: list[Expression] = []
        for i in range(len(operators)):
            op = cast(BinOpExpression.OpType, operators[i])
            lhs = expressions[i]
            rhs = expressions[i + 1]
            expr = BinOpExpression(origin=context.origin(), op=op, lhs=lhs, rhs=rhs)
            conjunction.append(expr)

        result_expr = conjunction[0]
        for expr in conjunction[1:]:
            result_expr = BinOpExpression(
                origin=context.origin(),
                op="and",
                lhs=result_expr,
                rhs=expr,
            )

        return ParseResult.make_success(result=result_expr, context=r.context)

    return parse_comparison_expression


@cache
def template_expression(
    template_parser: Parser[TemplateExpression],
) -> Parser[TemplateExpression]:
    @parser
    def template_expr_parser(context: ParseContext) -> ParseResult[TemplateExpression]:
        was_in_template_expr = context.in_template_expr
        result = template_parser(
            ParseContext(
                source=context.source,
                index=context.index,
                position=context.position,
                source_id=context.source_id,
                in_template_expr=True,
            )
        )
        return ParseResult(
            result.value,
            context=ParseContext(
                source=result.context.source,
                index=result.context.index,
                position=result.context.position,
                source_id=result.context.source_id,
                in_template_expr=was_in_template_expr,
            ),
        )

    parse = transform_success(
        enclosed(delim=literal("```"), content=template_expr_parser),
        transform=lambda s: s[1],
    )

    return parse
