from contextlib import nullcontext
from typing import Any, ContextManager

import pytest

from pyforma._parser import sequence, Parser, literal, ParseInput, ParseError


@pytest.mark.parametrize(
    "source,parsers,expected",
    [
        ("", (), nullcontext(())),
        ("foobar", (), nullcontext(())),
        ("foobar", (literal("foo"),), nullcontext(("foo",))),
        ("foobar", (literal("foo"), literal("bar")), nullcontext(("foo", "bar"))),
        ("foob", (literal("foo"), literal("bar")), pytest.raises(ParseError)),
    ],
)
def test_sequence(
    source: str,
    parsers: tuple[Parser[Any], ...],
    expected: ContextManager[tuple[str, ...]],
):
    with expected as e:
        result = sequence(*parsers)(ParseInput(source))
        assert result.result == e
