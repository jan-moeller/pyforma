import pytest

from pyforma._parser import (
    Parser,
    literal,
    ParseContext,
    option,
    ParseFailure,
    ParseSuccess,
)


@pytest.mark.parametrize(
    "source,parser,expected",
    [
        ("", literal("foo"), ParseSuccess(None)),
        ("foo", literal("bar"), ParseSuccess(None)),
        ("foobar", literal("fob"), ParseSuccess(None)),
        ("foo", literal("foo"), ParseSuccess("foo")),
        ("foobar", literal("foo"), ParseSuccess("foo")),
    ],
)
def test_option(
    source: str,
    parser: Parser[str],
    expected: ParseSuccess | ParseFailure,
):
    context = ParseContext(source)
    result = option(parser)(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        expect_idx = len(expected.result) if expected.result else 0
        assert result.context == ParseContext(source, index=expect_idx)
    else:
        assert result.context == context
