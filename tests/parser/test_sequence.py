from typing import Any

import pytest

from pyforma._parser import (
    sequence,
    Parser,
    literal,
    ParseContext,
    ParseFailure,
    ParseSuccess,
    ParseResult,
)


@pytest.mark.parametrize(
    "source,parsers,expected",
    [
        ("", (), ParseSuccess(())),
        ("foobar", (), ParseSuccess(())),
        ("foobar", (literal("foo"),), ParseSuccess(("foo",))),
        ("foobar", (literal("foo"), literal("bar")), ParseSuccess(("foo", "bar"))),
        (
            "foob",
            (literal("foo"), literal("bar")),
            ParseFailure(
                expected='sequence("foo", "bar")',
                cause=ParseResult.make_failure(
                    context=ParseContext("foob", index=3),
                    expected='"bar"',
                ),
            ),
        ),
    ],
)
def test_sequence(
    source: str,
    parsers: tuple[Parser[Any], ...],
    expected: ParseSuccess[tuple[str, ...]] | ParseFailure,
):
    context = ParseContext(source)
    result = sequence(*parsers)(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        expect_len = len("".join(expected.result))
        assert result.context == ParseContext(source, index=expect_len)
    else:
        assert result.context == context
