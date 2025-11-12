import pytest

from pyforma._ast import IdentifierExpression, ValueExpression, TemplateExpression
from pyforma._parser import (
    ParseContext,
    template,
    TemplateSyntaxConfig,
)
from pyforma._ast.origin import Origin


@pytest.mark.parametrize(
    "source,expected,remaining",
    [
        ("", TemplateExpression(origin=Origin(position=(1, 1)), content=()), ""),
        (
            "{#bar#}baz",
            TemplateExpression(
                origin=Origin(position=(1, 1)),
                content=(ValueExpression(origin=Origin(position=(1, 8)), value="baz"),),
            ),
            "",
        ),
        (
            "foo {#bar#}baz",
            TemplateExpression(
                origin=Origin(position=(1, 1)),
                content=(
                    ValueExpression(origin=Origin(position=(1, 1)), value="foo "),
                    ValueExpression(origin=Origin(position=(1, 12)), value="baz"),
                ),
            ),
            "",
        ),
        (
            "foo {#bar#}{{baz}} bam",
            TemplateExpression(
                origin=Origin(position=(1, 1)),
                content=(
                    ValueExpression(origin=Origin(position=(1, 1)), value="foo "),
                    IdentifierExpression(
                        origin=Origin(position=(1, 14)), identifier="baz"
                    ),
                    ValueExpression(origin=Origin(position=(1, 19)), value=" bam"),
                ),
            ),
            "",
        ),
    ],
)
def test_template(source: str, expected: list[str], remaining: str):
    result = template(TemplateSyntaxConfig())(ParseContext(source))
    assert result.context[:] == remaining
    assert result.success.result == expected
