import pytest

from pyforma._parser import ParseContext, text


@pytest.mark.parametrize(
    "source,expected",
    [
        ("", ""),
        ("foo 123 !{# no #}", "foo 123 !"),
        ("foo 123 !{{ no }}", "foo 123 !"),
    ],
)
def test_text(
    source: str,
    expected: str,
):
    context = ParseContext(source)
    result = text("{#", "{{")(context)
    assert result.is_success
    assert result.success.result == expected
    assert result.context == ParseContext(source, index=len(expected))
