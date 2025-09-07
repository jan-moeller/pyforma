import pytest

from pyforma._parser import ParseResult, ParseInput, whitespace


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
    assert whitespace(ParseInput(source)) == ParseResult(
        remaining=ParseInput(source, index=len(expected)),
        result=expected,
    )
