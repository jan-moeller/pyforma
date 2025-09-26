from functools import cache

from pyforma._ast.environment import Environment, TemplateEnvironment
from pyforma._ast.environment import WithEnvironment
from pyforma._ast.comment import Comment
from pyforma._ast.expression import Expression
from .alternation import alternation
from .non_empty import non_empty
from .sequence import sequence
from .literal import literal
from .whitespace import whitespace
from .transform_result import transform_success
from .expression import _call_kwargs  # pyright: ignore[reportPrivateUsage]
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
        name="environment",
    )
    return result
