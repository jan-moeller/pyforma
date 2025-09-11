from contextlib import nullcontext
from typing import ContextManager

import pytest

from pyforma._ast import Expression
from pyforma._parser import ParseContext, ParseError, expression_block, BlockSyntaxConfig


@pytest.mark.parametrize(
    "source,expected,result_idx",
    [
        ("", pytest.raises(ParseError), 0),
        ("{{foo}}", nullcontext(Expression("foo")), 7),
        ("{{ foo }}", nullcontext(Expression("foo")), 9),
        ("{{ foo }}bar", nullcontext(Expression("foo")), 9),
        ("{{ foo", pytest.raises(ParseError), 0),
    ],
)
def test_expression_block(
    source: str,
    expected: ContextManager[str],
    result_idx: int,
):
    with expected as e:
        r = expression_block(BlockSyntaxConfig("{{", "}}"))(ParseContext(source))
        assert r.result == e
        assert r.context == ParseContext(source, result_idx)
