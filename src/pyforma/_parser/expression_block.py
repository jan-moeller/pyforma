from functools import cache

from pyforma._parser.transform_result import transform_success

from .whitespace import whitespace
from .literal import literal
from .sequence import sequence
from .parser import Parser
from .expression import expression
from .template_syntax_config import TemplateSyntaxConfig
from pyforma._ast.expressions import Expression, TemplateExpression


@cache
def expression_block(
    syntax: TemplateSyntaxConfig,
    template_parser: Parser[TemplateExpression],
) -> Parser[Expression]:
    """Creates an expression block parser using the provided open and close markers

    Args:
        syntax: The syntax config to use
        template_parser: The template parser to use

    Returns:
        The expression block parser.
    """

    return transform_success(
        sequence(
            literal(syntax.expression.open),
            whitespace,
            expression(template_parser),
            whitespace,
            literal(syntax.expression.close),
            name="expression-block",
        ),
        transform=lambda result: result[2],
    )
