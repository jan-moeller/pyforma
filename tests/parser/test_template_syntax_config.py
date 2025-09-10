from contextlib import nullcontext
from typing import ContextManager

import pytest

from pyforma import BlockSyntaxConfig, TemplateSyntaxConfig


@pytest.mark.parametrize(
    "open,close,expected",
    [
        ("{", "}", nullcontext()),
        ("", "}", pytest.raises(ValueError)),
        ("#", "#", pytest.raises(ValueError)),
    ],
)
def test_block_syntax(
    open: str,
    close: str,
    expected: ContextManager[None],
):
    with expected:
        _ = BlockSyntaxConfig(open, close)


@pytest.mark.parametrize(
    "comment,expression,expected",
    [
        (
            TemplateSyntaxConfig().comment,
            TemplateSyntaxConfig().expression,
            nullcontext(),
        ),
        (
            TemplateSyntaxConfig().comment,
            TemplateSyntaxConfig().comment,
            pytest.raises(ValueError),
        ),
        (
            BlockSyntaxConfig("{", "}"),
            BlockSyntaxConfig("{", "#"),
            pytest.raises(ValueError),
        ),
    ],
)
def test_template_syntax(
    comment: BlockSyntaxConfig,
    expression: BlockSyntaxConfig,
    expected: ContextManager[None],
):
    with expected:
        _ = TemplateSyntaxConfig(comment=comment, expression=expression)
