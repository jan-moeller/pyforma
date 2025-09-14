from collections.abc import Callable
from functools import cache

from .parse_error import ParseError
from .parse_context import ParseContext
from .parse_result import ParseResult
from .parser import Parser, parser


@cache
def munch(predicate: Callable[[str], bool]) -> Parser[str]:
    """Creates a parser that consumes the maximal prefix for which the predicate returns True

    Args:
        predicate: Predicate that determines parsed prefix

    Returns:
        A parser that consumes the maximal prefix for which the predicate returns True. The predicate is only called for
        non-empty prefixes. If no non-empty prefix passes the predicate, the parser returns an empty match.
    """

    name = "munch"
    if hasattr(predicate, "__name__"):
        name = f"munch_{predicate.__name__}"
    elif hasattr(predicate, "__class__"):
        name = f"munch_{predicate.__class__.__name__}"

    @parser(name=name)
    def parse_munching(context: ParseContext) -> ParseResult[str]:
        try:
            return _munch_impl(context, predicate)

        except Exception as e:
            raise ParseError(
                f"Failed to munch with predicate {predicate.__name__}",
                context=context,
            ) from e

    return parse_munching


def _munch_impl(
    source: ParseContext,
    predicate: Callable[[str], bool],
) -> ParseResult[str]:
    remaining = source
    offset = 0
    while not remaining.at_eof():
        if predicate(source.peek(offset + 1)):
            offset += 1
            remaining = remaining.consume()
        else:
            break
    return ParseResult(context=remaining, result=source.peek(offset))
