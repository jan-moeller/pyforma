import pytest

from pyforma._parser import (
    ParseContext,
    literal,
    ParseSuccess,
    ParseFailure,
    lookahead,
    ParseResult,
)


@pytest.mark.parametrize(
    "source,lit,expected",
    [
        ("", "", ParseSuccess(None)),
        (
            "",
            "foo",
            ParseFailure(
                expected='lookahead("foo")',
                cause=ParseResult(
                    ParseFailure(expected='"foo"'),
                    context=ParseContext(source="", index=0),
                ),
            ),
        ),
        ("foo", "foo", ParseSuccess(None)),
        ("foobar", "foo", ParseSuccess(None)),
        (
            "fobar",
            "foo",
            ParseFailure(
                expected='lookahead("foo")',
                cause=ParseResult(
                    ParseFailure(expected='"foo"'),
                    context=ParseContext(source="fobar", index=0),
                ),
            ),
        ),
    ],
)
def test_lookahead(
    source: str,
    lit: str,
    expected: ParseSuccess[str] | ParseFailure,
):
    context = ParseContext(source)
    result = lookahead(literal(lit))(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=0)
    else:
        assert result.context == context
