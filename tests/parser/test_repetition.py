import pytest

from pyforma._parser import (
    ParseContext,
    literal,
    repetition,
    ParseFailure,
    ParseSuccess,
)


@pytest.mark.parametrize(
    "source,lit,expected",
    [
        ("", "", ParseSuccess(())),
        ("aaa", "a", ParseSuccess(("a", "a", "a"))),
        ("aaa", "aa", ParseSuccess(("aa",))),
        ("foofoobar", "foo", ParseSuccess(("foo", "foo"))),
        ("foo", "bar", ParseSuccess(())),
    ],
)
def test_repetition(
    source: str,
    lit: str,
    expected: ParseSuccess[tuple[str, ...]] | ParseFailure,
):
    context = ParseContext(source)
    result = repetition(literal(lit))(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        expect_len = len("".join(expected.result))
        assert result.context == ParseContext(source, index=expect_len)
    else:
        assert result.context == context
