from functools import cache

from .parse_context import ParseContext
from .parse_result import ParseResult
from .whitespace import whitespace
from .sequence import sequence
from .transform_result import transform_success
from .eof import eof
from .expression_block import expression_block
from .non_empty import non_empty
from .alternation import alternation
from .text import text
from .repetition import repetition
from .parser import Parser, parser
from .comment import comment
from .template_syntax_config import TemplateSyntaxConfig
from pyforma._ast.expression import Expression
from pyforma._ast.comment import Comment
from pyforma._ast.environment import Environment


@cache
def template(
    syntax: TemplateSyntaxConfig,
) -> Parser[tuple[str | Comment | Expression | Environment, ...]]:
    """Create a template parser

    Args:
        syntax: syntax config

    Returns:
        The template parser
    """

    _parse_text = non_empty(
        text(
            syntax.comment.open,
            syntax.expression.open,
            syntax.environment.open,
        )
    )

    @parser
    def _parse_template(context: ParseContext) -> ParseResult:
        from .environment import environment

        return repetition(
            alternation(
                _parse_text,
                comment(syntax.comment),
                expression_block(syntax.expression),
                environment(syntax, _parse_template),
            ),
            name="template",
        )(context)

    return transform_success(
        sequence(_parse_template, whitespace, eof), transform=lambda s: s[0]
    )
