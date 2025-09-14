from functools import cache

from .literal import literal
from .not_in import not_in
from .parser import Parser


@cache
def text(*end_strs: str) -> Parser[str]:
    """Creates a parser of unstructured text

    Args:
        end_strs: syntax indicators that end unstructured text

    Returns:
        A parser for unstructured text
    """
    return not_in(*(literal(s) for s in end_strs))
