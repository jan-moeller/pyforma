from contextlib import nullcontext
from typing import Any, ContextManager

import pytest

from pyforma._parser import alternation, Parser, literal, ParseContext, ParseError


@pytest.mark.parametrize(
    "source,parsers,expected",
    [
        ("", (), pytest.raises(ParseError)),
        ("foobar", (), pytest.raises(ParseError)),
        ("foobar", (literal("foo"),), nullcontext("foo")),
        ("foobar", (literal("bar"), literal("foo")), nullcontext("foo")),
        ("fob", (literal("foo"), literal("bar")), pytest.raises(ParseError)),
    ],
)
def test_alternation(
    source: str,
    parsers: tuple[Parser[Any], ...],
    expected: ContextManager[str],
):
    with expected as e:
        result = alternation(*parsers)(ParseContext(source))
        assert result.result == e
