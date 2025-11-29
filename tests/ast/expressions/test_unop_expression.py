from contextlib import nullcontext
from typing import ContextManager, Any

import pytest

from pyforma._ast import (
    Expression,
    IdentifierExpression,
    UnOpExpression,
)
from pyforma._ast.expressions.value_expression import ValueExpression
from pyforma._ast.origin import Origin
from pyforma._template import Template


_origin = Origin(position=(1, 1))


def _mk_expr[T: Expression](cls: type[T], **kwargs: Any) -> T:
    return cls(origin=_origin, **kwargs)


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        (
            dict(
                op="+",
                operand=_mk_expr(ValueExpression, value=2),
            ),
            set[str](),
        ),
        (
            dict(
                op="+",
                operand=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            {"foo"},
        ),
    ],
)
def test_unresolved_identifiers(
    kwargs: dict[str, Any],
    expected: set[str],
):
    expr = _mk_expr(UnOpExpression, **kwargs)
    assert expr.unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                op="+",
                operand=_mk_expr(ValueExpression, value=2),
            ),
            {},
            nullcontext(_mk_expr(ValueExpression, value=2)),
        ),
        (
            dict(
                op="-",
                operand=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            dict(foo=40),
            nullcontext(_mk_expr(ValueExpression, value=-40)),
        ),
    ],
)
def test_simplify(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Expression],
):
    with expected as e:
        expr = _mk_expr(UnOpExpression, **kwargs)
        assert expr.simplify(vars, renderers=Template.default_renderers) == e


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                op="+",
                operand=_mk_expr(ValueExpression, value=2),
            ),
            {},
            nullcontext(2),
        ),
        (
            dict(
                op="-",
                operand=_mk_expr(ValueExpression, value=2),
            ),
            {},
            nullcontext(-2),
        ),
        (
            dict(
                op="+",
                operand=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            dict(foo=42),
            nullcontext(42),
        ),
    ],
)
def test_evaluate(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Any],
):
    with expected as e:
        expr = _mk_expr(UnOpExpression, **kwargs)
        assert expr.evaluate(vars, renderers=Template.default_renderers) == e
