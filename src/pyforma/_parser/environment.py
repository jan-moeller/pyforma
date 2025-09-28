from functools import cache

from pyforma._ast.environment import (
    Environment,
    IfEnvironment,
    TemplateEnvironment,
    WithEnvironment,
    DefaultEnvironment,
)
from pyforma._ast.comment import Comment
from pyforma._ast.expression import Expression
from .repetition import repetition
from .option import option
from .alternation import alternation
from .non_empty import non_empty
from .sequence import sequence
from .literal import literal
from .whitespace import whitespace
from .transform_result import transform_success
from .expression import _call_kwargs, expression  # pyright: ignore[reportPrivateUsage]
from .parser import Parser
from .template_syntax_config import TemplateSyntaxConfig


@cache
def with_environment(
    syntax: TemplateSyntaxConfig,
    template_parser: Parser[tuple[str | Comment | Expression | Environment, ...]],
) -> Parser[WithEnvironment]:
    parse_open = transform_success(
        sequence(
            literal(syntax.environment.open),
            whitespace,
            literal("with"),
            non_empty(whitespace),
            _call_kwargs(True),
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
        transform=lambda s: WithEnvironment(
            variables={e[0]: e[1] for e in s[0]},
            content=TemplateEnvironment(s[1]),
        ),
    )


@cache
def default_environment(
    syntax: TemplateSyntaxConfig,
    template_parser: Parser[tuple[str | Comment | Expression | Environment, ...]],
) -> Parser[DefaultEnvironment]:
    parse_open = transform_success(
        sequence(
            literal(syntax.environment.open),
            whitespace,
            literal("default"),
            non_empty(whitespace),
            _call_kwargs(True),
            whitespace,
            literal(syntax.environment.close),
        ),
        transform=lambda s: s[4],
    )
    parse_close = transform_success(
        sequence(
            literal(syntax.environment.open),
            whitespace,
            literal("enddefault"),
            whitespace,
            literal(syntax.environment.close),
        ),
        transform=lambda s: None,
    )

    parse = sequence(
        parse_open, template_parser, parse_close, name="default-environment"
    )

    return transform_success(
        parse,
        transform=lambda s: DefaultEnvironment(
            variables={e[0]: e[1] for e in s[0]},
            content=TemplateEnvironment(s[1]),
        ),
    )


@cache
def if_environment(
    syntax: TemplateSyntaxConfig,
    template_parser: Parser[tuple[str | Comment | Expression | Environment, ...]],
) -> Parser[IfEnvironment]:
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
                transform=lambda s: TemplateEnvironment(())
                if s is None
                else TemplateEnvironment(s[1]),
            ),
            parse_close,
        ),
        transform=lambda s: (
            tuple(
                (expr, TemplateEnvironment(templ))
                for expr, templ in ((s[0], s[1]), *s[2])
            ),
            s[3],
        ),
        name="if-environment",
    )

    return transform_success(
        parse,
        transform=lambda s: IfEnvironment(
            ifs=s[0],
            else_content=s[1],
        ),
    )


@cache
def environment(
    syntax: TemplateSyntaxConfig,
    template_parser: Parser[tuple[str | Comment | Expression | Environment, ...]],
) -> Parser[Environment]:
    """Creates an environment parser using the provided template syntax

    Args:
        syntax: The syntax config to use

    Returns:
        The environment parser.
    """

    result = alternation(
        with_environment(syntax, template_parser),
        default_environment(syntax, template_parser),
        if_environment(syntax, template_parser),
        name="environment",
    )
    return result
