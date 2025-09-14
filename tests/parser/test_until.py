import pytest

from pyforma._parser import (
    ParseContext,
    not_in,
    Parser,
    literal,
    ParseFailure,
    ParseSuccess,
    until,
)


@pytest.mark.parametrize(
    "source,parser,expected",
    [
        ("foo", literal("o"), ParseSuccess("f")),
        ("foobars", literal("b"), ParseSuccess("foo")),
    ],
)
def test_until(
    source: str,
    parser: Parser,
    expected: ParseSuccess | ParseFailure,
):
    context = ParseContext(source)
    result = until(parser)(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=len(expected.result))
    else:
        assert result.context == context


@pytest.mark.parametrize(
    "source,parsers,expected",
    [
        ("", (), ParseSuccess("")),
        ("foo", (), ParseSuccess("foo")),
        ("foo", (literal("o"),), ParseSuccess("f")),
        ("foobars", (literal("s"), literal("bar")), ParseSuccess("foo")),
    ],
)
def test_not_in(
    source: str,
    parsers: tuple[Parser, ...],
    expected: ParseSuccess | ParseFailure,
):
    context = ParseContext(source)
    result = not_in(*parsers)(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=len(expected.result))
    else:
        assert result.context == context
