from .expression_block import expression_block, Expression
from .non_empty import non_empty
from .alternation import alternation
from .text import text
from .repetition import repetition
from .parser import Parser
from .comment import Comment, comment


def template(
    open_comment: str,
    close_comment: str,
    open_expression: str,
    close_expression: str,
) -> Parser[list[str | Comment | Expression]]:
    """Create a template parser

    Args:
        open_comment: The comment open indicator
        close_comment: The comment close indicator
        open_expression: The expression open indicator
        close_expression: The expression close indicator

    Returns:
        The template parser
    """

    return repetition(
        alternation(
            non_empty(text(open_comment, open_expression)),
            comment(open_comment, close_comment),
            expression_block(open_expression, close_expression),
        )
    )
