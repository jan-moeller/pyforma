from contextlib import nullcontext
from typing import ContextManager, Any

import pytest

from pyforma._ast import Expression, ValueExpression
from pyforma._ast.origin import Origin
from pyforma._template import Template


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        (dict(value=42), set[str]()),
        (dict(value="foo"), set[str]()),
        (dict(value=True), set[str]()),
    ],
)
def test_unresolved_identifiers(
    kwargs: dict[str, Any],
    expected: set[str],
):
    expr = ValueExpression(origin=Origin(position=(1, 1)), **kwargs)
    assert expr.unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(value=42),
            {},
            nullcontext(ValueExpression(origin=Origin(position=(1, 1)), value=42)),
        ),
    ],
)
def test_simplify(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Expression],
):
    with expected as e:
        expr = ValueExpression(origin=Origin(position=(1, 1)), **kwargs)
        assert expr.simplify(vars, renderers=Template.default_renderers) == e


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (dict(value=42), {}, nullcontext(42)),
        (dict(value="foo"), {}, nullcontext("foo")),
        (dict(value=True), {}, nullcontext(True)),
    ],
)
def test_evaluate(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Any],
):
    with expected as e:
        expr = ValueExpression(origin=Origin(position=(1, 1)), **kwargs)
        assert expr.evaluate(vars, renderers=Template.default_renderers) == e
