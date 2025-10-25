import pytest

from pyforma._ast.expression import Expression, IdentifierExpression, ValueExpression
from pyforma._parser import (
    ParseContext,
    expression_block,
    BlockSyntaxConfig,
    ParseFailure,
    ParseSuccess,
    ParseResult,
)


@pytest.mark.parametrize(
    "source,expected,result_idx",
    [
        (
            "",
            ParseFailure(
                expected="expression-block",
                cause=ParseResult(
                    ParseFailure(
                        expected='"{{"',
                        cause=ParseResult(
                            ParseFailure(expected='"{"'),
                            context=ParseContext(source="", index=0),
                        ),
                    ),
                    context=ParseContext(source="", index=0),
                ),
            ),
            0,
        ),
        ("{{foo}}", ParseSuccess(IdentifierExpression(identifier="foo")), 7),
        ("{{ foo }}", ParseSuccess(IdentifierExpression(identifier="foo")), 9),
        ("{{ foo }}bar", ParseSuccess(IdentifierExpression(identifier="foo")), 9),
        ("{{'foo'}}bar", ParseSuccess(ValueExpression(value="foo")), 9),
        (
            "{{ foo",
            ParseFailure(
                expected="expression-block",
                cause=ParseResult(
                    ParseFailure(
                        expected='"}}"',
                        cause=ParseResult(
                            ParseFailure(expected='"}"'),
                            context=ParseContext(source="{{ foo", index=6),
                        ),
                    ),
                    context=ParseContext(source="{{ foo", index=6),
                ),
            ),
            0,
        ),
    ],
)
def test_expression_block(
    source: str,
    expected: ParseSuccess[Expression] | ParseFailure,
    result_idx: int,
):
    context = ParseContext(source)
    result = expression_block(BlockSyntaxConfig("{{", "}}"))(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=result_idx)
    else:
        assert result.context == context
