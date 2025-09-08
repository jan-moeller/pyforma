import pytest

from pyforma._parser import ParseContext, template, Comment


@pytest.mark.parametrize(
    "source,expected,remaining",
    [
        ("", [], ""),
        ("{#bar#}baz", [Comment("bar"), "baz"], ""),
        ("foo {#bar#}baz", ["foo ", Comment("bar"), "baz"], ""),
        (
            "foo {#bar#}{#baz#} bam",
            ["foo ", Comment("bar"), Comment("baz"), " bam"],
            "",
        ),
    ],
)
def test_template(source: str, expected: list[str | Comment], remaining: str):
    result = template("{#", "#}")(ParseContext(source))
    assert result.context[:] == remaining
    assert result.result == expected
