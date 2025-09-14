from functools import cache

from .expression_block import expression_block
from .non_empty import non_empty
from .alternation import alternation
from .text import text
from .repetition import repetition
from .parser import Parser
from .comment import comment
from .template_syntax_config import TemplateSyntaxConfig
from pyforma._ast.expression import Expression
from pyforma._ast.comment import Comment


@cache
def template(
    syntax: TemplateSyntaxConfig,
) -> Parser[tuple[str | Comment | Expression, ...]]:
    """Create a template parser

    Args:
        syntax: syntax config

    Returns:
        The template parser
    """

    return repetition(
        alternation(
            non_empty(text(syntax.comment.open, syntax.expression.open)),
            comment(syntax.comment),
            expression_block(syntax.expression),
        )
    )
