import pytest

from pyforma._parser import ParseContext, whitespace


@pytest.mark.parametrize(
    "source,expected",
    [
        ("", ""),
        ("   ", "   "),
        ("\t foo", "\t "),
    ],
)
def test_whitespace(
    source: str,
    expected: str,
):
    context = ParseContext(source)
    result = whitespace(context)
    assert result.is_success
    assert result.success.result == expected
    assert result.context == ParseContext(source, index=len(expected))
