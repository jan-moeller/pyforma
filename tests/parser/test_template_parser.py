import pytest

from pyforma._ast import Comment, IdentifierExpression
from pyforma._parser import (
    ParseContext,
    template,
    TemplateSyntaxConfig,
)
from pyforma._ast.origin import Origin


@pytest.mark.parametrize(
    "source,expected,remaining",
    [
        ("", (), ""),
        ("{#bar#}baz", (Comment("bar"), "baz"), ""),
        ("foo {#bar#}baz", ("foo ", Comment("bar"), "baz"), ""),
        (
            "foo {#bar#}{{baz}} bam",
            (
                "foo ",
                Comment(text="bar"),
                IdentifierExpression(origin=Origin(position=(1, 14)), identifier="baz"),
                " bam",
            ),
            "",
        ),
    ],
)
def test_template(source: str, expected: list[str | Comment], remaining: str):
    result = template(TemplateSyntaxConfig())(ParseContext(source))
    assert result.context[:] == remaining
    assert result.success.result == expected
