import pytest

from pyforma._parser import ParseContext, literal, ParseResult, repetition


@pytest.mark.parametrize(
    "source,lit,expected",
    [
        ("", "", []),
        ("aaa", "a", ["a", "a", "a"]),
        ("aaa", "aa", ["aa"]),
        ("foofoobar", "foo", ["foo", "foo"]),
        ("foo", "bar", []),
    ],
)
def test_repetition(
    source: str,
    lit: str,
    expected: list[str],
):
    assert repetition(literal(lit))(ParseContext(source)) == ParseResult(
        context=ParseContext(source, index=len("".join(expected))),
        result=expected,
    )
