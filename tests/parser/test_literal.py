import pytest

from pyforma._parser import ParseContext, literal, ParseSuccess, ParseFailure


@pytest.mark.parametrize(
    "source,lit,expected",
    [
        ("", "", ParseSuccess("")),
        ("", "foo", ParseFailure('"foo"')),
        ("foo", "foo", ParseSuccess("foo")),
        ("foobar", "foo", ParseSuccess("foo")),
        ("fobar", "foo", ParseFailure('"foo"')),
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
