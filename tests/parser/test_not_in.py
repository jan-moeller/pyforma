import pytest

from pyforma._parser import (
    ParseContext,
    ParseResult,
    not_in,
    Parser,
    literal,
)


@pytest.mark.parametrize(
    "source,parsers,expected",
    [
        ("", (), ""),
        ("foo", (), "foo"),
        ("foo", (literal("o"),), "f"),
        ("foobars", (literal("s"), literal("bar")), "foo"),
    ],
)
def test_not_in(
    source: str,
    parsers: tuple[Parser, ...],
    expected: str,
):
    assert not_in(*parsers)(ParseContext(source)) == ParseResult(
        context=ParseContext(source, index=len(expected)),
        result=expected,
    )
