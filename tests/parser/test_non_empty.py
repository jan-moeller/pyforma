import pytest

from pyforma._parser import (
    ParseContext,
    Parser,
    whitespace,
    non_empty,
    ParseFailure,
    ParseSuccess,
)


@pytest.mark.parametrize(
    "source,parser,expected",
    [
        ("", whitespace, ParseFailure(expected="non-empty(whitespace)")),
        ("   ", whitespace, ParseSuccess("   ")),
        ("foo  bar", whitespace, ParseFailure(expected="non-empty(whitespace)")),
    ],
)
def test_non_empty(
    source: str,
    parser: Parser[str],
    expected: ParseSuccess | ParseFailure,
):
    context = ParseContext(source)
    result = non_empty(parser)(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=len(expected.result))
    else:
        assert result.context == context
