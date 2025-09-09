from .literal import literal
from .not_in import not_in
from .parser import Parser


def text(open_comment: str, open_expression: str) -> Parser[str]:
    """Creates a parser of unstructured text

    Args:
        open_comment: comment indicator (ends unstructured text)
        open_expression: expression indicator (ends unstructured text)

    Returns:
        A parser for unstructured text
    """
    return not_in(literal(open_comment), literal(open_expression))
