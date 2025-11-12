from functools import cache

from pyforma._ast.expressions import (
    Expression,
    ValueExpression,
    WithExpression,
    TemplateExpression,
)
from pyforma._ast.expressions.call_expression import CallExpression
from .parse_context import ParseContext
from .parse_result import ParseResult
from .until import until
from .delimited import delimited
from .identifier import identifier
from .repetition import repetition
from .option import option
from .alternation import alternation
from .non_empty import non_empty
from .sequence import sequence
from .literal import literal
from .whitespace import whitespace
from .transform_result import transform_success
from .expression import expression
from .parser import Parser, parser
from .template_syntax_config import TemplateSyntaxConfig
from .._ast import IfExpression, ForExpression
from pyforma._util import join

_destructuring = delimited(
    delim=sequence(whitespace, literal(","), whitespace),
    content=identifier,
    allow_trailing_delim=False,
)


@cache
def literal_environment(syntax: TemplateSyntaxConfig) -> Parser[ValueExpression]:
    parse_open = transform_success(
        sequence(
            literal(syntax.environment.open),
            whitespace,
            literal("literal"),
            option(
                transform_success(
                    sequence(non_empty(whitespace), identifier),
                    transform=lambda s: s[1],
                )
            ),
            whitespace,
            literal(syntax.environment.close),
        ),
        transform=lambda s: s[3],
    )

    @parser
    def parse_literal_env(context: ParseContext) -> ParseResult[ValueExpression]:
        iden = parse_open(context)
        if iden.is_failure:
            return ParseResult.make_failure(
                context=context,
                expected="literal environment",
                cause=iden,
            )

        if iden.success.result:
            iden_parser = sequence(whitespace, literal(iden.success.result))
        else:
            iden_parser = parser(
                lambda context: ParseResult[str].make_success(
                    context=context, result=""
                )
            )

        parse_close = transform_success(
            sequence(
                literal(syntax.environment.open),
                whitespace,
                literal("endliteral"),
                iden_parser,
                whitespace,
                literal(syntax.environment.close),
            ),
            transform=lambda s: None,
        )
        parse_content = until(parse_close)

        parse = sequence(parse_content, parse_close, name="literal-environment")
        result = parse(iden.context)

        return ParseResult[ValueExpression].make_success(
            context=result.context,
            result=ValueExpression(
                origin=context.origin(),
                value=result.success.result[0],
            ),
        )

    return parse_literal_env


@cache
def with_environment(
    syntax: TemplateSyntaxConfig,
    template_parser: Parser[tuple[Expression, ...]],
) -> Parser[WithExpression]:
    parse_open = transform_success(
        sequence(
            literal(syntax.environment.open),
            whitespace,
            literal("with"),
            non_empty(whitespace),
            delimited(
                delim=sequence(whitespace, literal(";"), whitespace),
                content=transform_success(
                    sequence(
                        _destructuring, whitespace, literal("="), whitespace, expression
                    ),
                    transform=lambda s: (s[0], s[4]),
                ),
                allow_trailing_delim=True,
            ),
            whitespace,
            literal(syntax.environment.close),
        ),
        transform=lambda s: s[4],
    )
    parse_close = transform_success(
        sequence(
            literal(syntax.environment.open),
            whitespace,
            literal("endwith"),
            whitespace,
            literal(syntax.environment.close),
        ),
        transform=lambda s: None,
    )

    parse = sequence(parse_open, template_parser, parse_close, name="with-environment")

    return transform_success(
        parse,
        transform=lambda s, c: WithExpression(
            origin=c.origin(),
            bindings=tuple((e[0], e[1]) for e in s[0]),
            expr=TemplateExpression(origin=c.origin(), content=s[1]),
        ),
    )


@cache
def if_environment(
    syntax: TemplateSyntaxConfig,
    template_parser: Parser[tuple[Expression, ...]],
) -> Parser[IfExpression]:
    parse_if = transform_success(
        sequence(
            literal(syntax.environment.open),
            whitespace,
            literal("if"),
            non_empty(whitespace),
            expression,
            whitespace,
            literal(syntax.environment.close),
        ),
        transform=lambda s: s[4],
    )
    parse_elif = transform_success(
        sequence(
            literal(syntax.environment.open),
            whitespace,
            literal("elif"),
            non_empty(whitespace),
            expression,
            whitespace,
            literal(syntax.environment.close),
        ),
        transform=lambda s: s[4],
    )
    parse_else = transform_success(
        sequence(
            literal(syntax.environment.open),
            whitespace,
            literal("else"),
            whitespace,
            literal(syntax.environment.close),
        ),
        transform=lambda s: None,
    )
    parse_close = transform_success(
        sequence(
            literal(syntax.environment.open),
            whitespace,
            literal("endif"),
            whitespace,
            literal(syntax.environment.close),
        ),
        transform=lambda s: None,
    )

    parse = transform_success(
        sequence(
            parse_if,
            template_parser,
            repetition(sequence(parse_elif, template_parser)),
            transform_success(
                option(sequence(parse_else, template_parser)),
                transform=lambda s, c: TemplateExpression(origin=c.origin(), content=())
                if s is None
                else TemplateExpression(origin=c.origin(), content=s[1]),
            ),
            parse_close,
        ),
        transform=lambda s, c: (
            tuple(
                (expr, TemplateExpression(origin=c.origin(), content=templ))
                for expr, templ in ((s[0], s[1]), *s[2])
            ),
            s[3],
        ),
        name="if-environment",
    )

    return transform_success(
        parse,
        transform=lambda s, c: IfExpression(
            origin=c.origin(),
            cases=(*s[0], (ValueExpression(origin=c.origin(), value=True), s[1])),
        ),
    )


@cache
def for_environment(
    syntax: TemplateSyntaxConfig,
    template_parser: Parser[tuple[Expression, ...]],
) -> Parser[Expression]:
    parse_open = transform_success(
        sequence(
            literal(syntax.environment.open),
            whitespace,
            literal("for"),
            non_empty(whitespace),
            _destructuring,
            non_empty(whitespace),
            literal("in"),
            non_empty(whitespace),
            expression,
            whitespace,
            literal(syntax.environment.close),
        ),
        transform=lambda s: (s[4], s[8]),
    )
    parse_close = transform_success(
        sequence(
            literal(syntax.environment.open),
            whitespace,
            literal("endfor"),
            whitespace,
            literal(syntax.environment.close),
        ),
        transform=lambda s: None,
    )

    parse = sequence(parse_open, template_parser, parse_close, name="for-environment")

    return transform_success(
        parse,
        transform=lambda s, c: CallExpression(
            origin=c.origin(),
            callee=ValueExpression(origin=c.origin(), value=join),
            arguments=(
                ValueExpression(origin=c.origin(), value=""),
                ForExpression(
                    origin=c.origin(),
                    var_names=s[0][0],
                    iter_expr=s[0][1],
                    expr=TemplateExpression(origin=c.origin(), content=s[1]),
                ),
            ),
            kw_arguments=(),
        ),
    )


@cache
def environment(
    syntax: TemplateSyntaxConfig,
    template_parser: Parser[tuple[Expression, ...]],
) -> Parser[Expression]:
    """Creates an environment parser using the provided template syntax

    Args:
        syntax: The syntax config to use

    Returns:
        The environment parser.
    """

    result = alternation(
        with_environment(syntax, template_parser),
        if_environment(syntax, template_parser),
        for_environment(syntax, template_parser),
        literal_environment(syntax),
        name="environment",
    )
    return result
