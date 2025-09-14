from typing import Any

import pytest

from pyforma._parser import (
    alternation,
    Parser,
    literal,
    ParseContext,
    ParseSuccess,
    ParseFailure,
)


@pytest.mark.parametrize(
    "source,parsers,expected",
    [
        ("", (), ParseFailure(expected="alternation()")),
        ("foobar", (), ParseFailure(expected="alternation()")),
        ("foobar", (literal("foo"),), ParseSuccess("foo")),
        ("foobar", (literal("bar"), literal("foo")), ParseSuccess("foo")),
        (
            "fob",
            (literal("foo"), literal("bar")),
            ParseFailure(expected='alternation("foo", "bar")'),
        ),
    ],
)
def test_alternation(
    source: str,
    parsers: tuple[Parser[Any], ...],
    expected: ParseSuccess | ParseFailure,
):
    context = ParseContext(source)
    result = alternation(*parsers)(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=len(expected.result))
    else:
        assert result.context == context
