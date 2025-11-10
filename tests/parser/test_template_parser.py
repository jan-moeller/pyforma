import pytest

from pyforma._ast import IdentifierExpression
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
        ("{#bar#}baz", ("baz",), ""),
        ("foo {#bar#}baz", ("foo ", "baz"), ""),
        (
            "foo {#bar#}{{baz}} bam",
            (
                "foo ",
                IdentifierExpression(origin=Origin(position=(1, 14)), identifier="baz"),
                " bam",
            ),
            "",
        ),
    ],
)
def test_template(source: str, expected: list[str], remaining: str):
    result = template(TemplateSyntaxConfig())(ParseContext(source))
    assert result.context[:] == remaining
    assert result.success.result == expected
