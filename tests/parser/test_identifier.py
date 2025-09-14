import pytest

from pyforma._parser import (
    ParseContext,
    identifier,
    ParseFailure,
    ParseSuccess,
)


@pytest.mark.parametrize(
    "source,expected",
    [
        ("", ParseFailure(expected="identifier")),
        ("foo", ParseSuccess("foo")),
        ("foo123 0", ParseSuccess("foo123")),
        ("123", ParseFailure(expected="identifier")),
    ],
)
def test_identifier(
    source: str,
    expected: ParseSuccess[str] | ParseFailure,
):
    context = ParseContext(source)
    result = identifier(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=len(expected.result))
    else:
        assert result.context == context
