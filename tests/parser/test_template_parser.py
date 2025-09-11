import pytest

from pyforma._ast import Expression, Comment
from pyforma._parser import (
    ParseContext,
    template,
    TemplateSyntaxConfig,
)


@pytest.mark.parametrize(
    "source,expected,remaining",
    [
        ("", [], ""),
        ("{#bar#}baz", [Comment("bar"), "baz"], ""),
        ("foo {#bar#}baz", ["foo ", Comment("bar"), "baz"], ""),
        (
            "foo {#bar#}{{baz}} bam",
            ["foo ", Comment("bar"), Expression("baz"), " bam"],
            "",
        ),
    ],
)
def test_template(source: str, expected: list[str | Comment], remaining: str):
    result = template(TemplateSyntaxConfig())(ParseContext(source))
    assert result.context[:] == remaining
    assert result.result == expected
