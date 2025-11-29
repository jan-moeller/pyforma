from contextlib import nullcontext
from typing import ContextManager, Any

import pytest

from pyforma._ast import (
    Expression,
    IdentifierExpression,
    BinOpExpression,
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
                lhs=_mk_expr(ValueExpression, value=2),
                rhs=_mk_expr(ValueExpression, value=40),
            ),
            set[str](),
        ),
        (
            dict(
                op="+",
                lhs=_mk_expr(ValueExpression, value=2),
                rhs=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            {"foo"},
        ),
        (
            dict(
                op="+",
                lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                rhs=_mk_expr(ValueExpression, value=2),
            ),
            {"foo"},
        ),
        (
            dict(
                op="+",
                lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                rhs=_mk_expr(IdentifierExpression, identifier="bar"),
            ),
            {"foo", "bar"},
        ),
    ],
)
def test_unresolved_identifiers(
    kwargs: dict[str, Any],
    expected: set[str],
):
    expr = _mk_expr(BinOpExpression, **kwargs)
    assert expr.unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                op="+",
                lhs=_mk_expr(ValueExpression, value=2),
                rhs=_mk_expr(ValueExpression, value=40),
            ),
            {},
            nullcontext(_mk_expr(ValueExpression, value=42)),
        ),
        (
            dict(
                op="+",
                lhs=_mk_expr(ValueExpression, value=2),
                rhs=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            dict(foo=40),
            nullcontext(_mk_expr(ValueExpression, value=42)),
        ),
        (
            dict(
                op="+",
                lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                rhs=_mk_expr(ValueExpression, value=2),
            ),
            dict(foo=40),
            nullcontext(_mk_expr(ValueExpression, value=42)),
        ),
        (
            dict(
                op="+",
                lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                rhs=_mk_expr(IdentifierExpression, identifier="bar"),
            ),
            dict(foo=40, bar=2),
            nullcontext(_mk_expr(ValueExpression, value=42)),
        ),
        (
            dict(
                op="+",
                lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                rhs=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            dict(foo=21),
            nullcontext(_mk_expr(ValueExpression, value=42)),
        ),
    ],
)
def test_simplify(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Expression],
):
    with expected as e:
        expr = _mk_expr(BinOpExpression, **kwargs)
        assert expr.simplify(vars, renderers=Template.default_renderers) == e


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                op="+",
                lhs=_mk_expr(ValueExpression, value=2),
                rhs=_mk_expr(ValueExpression, value=40),
            ),
            {},
            nullcontext(42),
        ),
        (
            dict(
                op="+",
                lhs=_mk_expr(ValueExpression, value=2),
                rhs=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            dict(foo=40),
            nullcontext(42),
        ),
        (
            dict(
                op="+",
                lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                rhs=_mk_expr(ValueExpression, value=2),
            ),
            dict(foo=40),
            nullcontext(42),
        ),
        (
            dict(
                op="+",
                lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                rhs=_mk_expr(IdentifierExpression, identifier="bar"),
            ),
            dict(foo=40, bar=2),
            nullcontext(42),
        ),
        (
            dict(
                op="+",
                lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                rhs=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            dict(foo=21),
            nullcontext(42),
        ),
        (
            dict(
                op="+",
                lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                rhs=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            dict(bar=21),
            pytest.raises(ValueError),
        ),
    ],
)
def test_evaluate(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Any],
):
    with expected as e:
        expr = _mk_expr(BinOpExpression, **kwargs)
        assert expr.evaluate(vars, renderers=Template.default_renderers) == e
