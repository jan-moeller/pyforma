import pytest

from pyforma._parser import (
    ParseContext,
    ParseFailure,
    ParseSuccess,
    delimited,
    literal,
    Parser,
    identifier,
)


@pytest.mark.parametrize(
    "source,parser,allow_trailing,expected,expect_idx",
    [
        ("", identifier, False, ParseSuccess(()), 0),
        (",", identifier, False, ParseSuccess(()), 0),
        (",", identifier, True, ParseSuccess(()), 0),
        ("foo", identifier, False, ParseSuccess(("foo",)), 3),
        ("foo", identifier, True, ParseSuccess(("foo",)), 3),
        ("foo,bar", identifier, True, ParseSuccess(("foo", "bar")), 7),
        ("foo,bar,", identifier, True, ParseSuccess(("foo", "bar")), 8),
        ("foo,bar,", identifier, False, ParseSuccess(("foo", "bar")), 7),
    ],
)
def test_delimited(
    source: str,
    parser: Parser[str],
    allow_trailing: bool,
    expected: ParseSuccess[str] | ParseFailure,
    expect_idx: int,
):
    context = ParseContext(source)
    result = delimited(
        delim=literal(","),
        content=parser,
        allow_trailing_delim=allow_trailing,
    )(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=expect_idx)
    else:
        assert result.context == context
