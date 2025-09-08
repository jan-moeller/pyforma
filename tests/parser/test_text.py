import pytest

from pyforma._parser import ParseContext, ParseResult, text


@pytest.mark.parametrize(
    "source,expected",
    [
        ("", ""),
        ("foo 123 !{# no #}", "foo 123 !"),
    ],
)
def test_text(
    source: str,
    expected: str,
):
    assert text("{#")(ParseContext(source)) == ParseResult(
        context=ParseContext(source, index=len(expected)),
        result=expected,
    )
