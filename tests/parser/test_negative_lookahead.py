import pytest

from pyforma._parser import (
    ParseContext,
    literal,
    ParseSuccess,
    ParseFailure,
    negative_lookahead,
    ParseResult,
)


@pytest.mark.parametrize(
    "source,lit,expected",
    [
        (
            "",
            "",
            ParseFailure(
                expected='negative-lookahead("")',
                cause=ParseResult(
                    ParseSuccess(result=""), context=ParseContext(source="", index=0)
                ),
            ),
        ),
        ("", "foo", ParseSuccess(None)),
        (
            "foo",
            "foo",
            ParseFailure(
                expected='negative-lookahead("foo")',
                cause=ParseResult(
                    ParseSuccess(result="foo"),
                    context=ParseContext(source="foo", index=3),
                ),
            ),
        ),
        (
            "foobar",
            "foo",
            ParseFailure(
                expected='negative-lookahead("foo")',
                cause=ParseResult(
                    ParseSuccess(result="foo"),
                    context=ParseContext(source="foobar", index=3),
                ),
            ),
        ),
        ("fobar", "foo", ParseSuccess(None)),
    ],
)
def test_negative_lookahead(
    source: str,
    lit: str,
    expected: ParseSuccess[str] | ParseFailure,
):
    context = ParseContext(source)
    result = negative_lookahead(literal(lit))(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=0)
    else:
        assert result.context == context
