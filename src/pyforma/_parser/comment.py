from functools import cache

from .template_syntax_config import BlockSyntaxConfig
from .parser import Parser
from .sequence import sequence
from .literal import literal
from .until import until
from .transform_result import transform_success
from pyforma._ast import Comment
from pyforma._util import defaulted


@cache
def comment(
    syntax: BlockSyntaxConfig,
    /,
    *,
    name: str | None = None,
) -> Parser[Comment]:
    """Creates a comment parser using the provided open and close markers

    Args:
        syntax: Syntax config to use
        name: Optional parser name

    Returns:
        The comment parser.
    """

    name = defaulted(name, f'comment("{syntax.open}", "{syntax.close}")')

    return transform_success(
        sequence(
            literal(syntax.open),
            until(literal(syntax.close)),
            literal(syntax.close),
        ),
        transform=lambda s: Comment(s[1]),
        name=name,
    )
