import pytest

from pyforma._parser import (
    ParseContext,
    literal,
    ParseSuccess,
    ParseFailure,
    ParseResult,
)


@pytest.mark.parametrize(
    "source,lit,expected",
    [
        ("", "", ParseSuccess("")),
        (
            "",
            "foo",
            ParseFailure(
                expected='"foo"',
                cause=ParseResult(
                    ParseFailure(expected='"f"'),
                    context=ParseContext(source="", index=0),
                ),
            ),
        ),
        ("foo", "foo", ParseSuccess("foo")),
        ("foobar", "foo", ParseSuccess("foo")),
        (
            "fobar",
            "foo",
            ParseFailure(
                expected='"foo"',
                cause=ParseResult(
                    ParseFailure(expected='"o"'),
                    context=ParseContext(source="fobar", index=2),
                ),
            ),
        ),
    ],
)
def test_literal(
    source: str,
    lit: str,
    expected: ParseSuccess[str] | ParseFailure,
):
    context = ParseContext(source)
    result = literal(lit)(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=len(expected.result))
    else:
        assert result.context == context
