import pytest

from pyforma._parser import ParseResult, ParseContext, whitespace


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
    assert whitespace(ParseContext(source)) == ParseResult(
        context=ParseContext(source, index=len(expected)),
        result=expected,
    )
