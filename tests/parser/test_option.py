import pytest

from pyforma._parser import (
    Parser,
    literal,
    ParseContext,
    option,
)


@pytest.mark.parametrize(
    "source,parser,expected",
    [
        ("", literal("foo"), None),
        ("foo", literal("bar"), None),
        ("foobar", literal("fob"), None),
        ("foo", literal("foo"), "foo"),
        ("foobar", literal("foo"), "foo"),
    ],
)
def test_option(
    source: str,
    parser: Parser[str],
    expected: str | None,
):
    result = option(parser)(ParseContext(source))
    assert result.result == expected
