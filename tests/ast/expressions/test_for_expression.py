from contextlib import nullcontext
from typing import ContextManager, Any

import pytest

from pyforma._ast import (
    Expression,
    IdentifierExpression,
    ForExpression,
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
                var_names=("foo",),
                iter_expr=_mk_expr(ValueExpression, value="foo"),
                expr=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            set[str](),
        ),
        (
            dict(
                var_names=("foo",),
                iter_expr=_mk_expr(IdentifierExpression, identifier="foo"),
                expr=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            {"foo"},
        ),
        (
            dict(
                var_names=("bar",),
                iter_expr=_mk_expr(IdentifierExpression, identifier="foo"),
                expr=_mk_expr(IdentifierExpression, identifier="bar"),
            ),
            {"foo"},
        ),
        (
            dict(
                var_names=("bar",),
                iter_expr=_mk_expr(IdentifierExpression, identifier="foo"),
                expr=_mk_expr(IdentifierExpression, identifier="bam"),
            ),
            {"foo", "bam"},
        ),
    ],
)
def test_unresolved_identifiers(
    kwargs: dict[str, Any],
    expected: set[str],
):
    expr = _mk_expr(ForExpression, **kwargs)
    assert expr.unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                var_names=("foo",),
                iter_expr=_mk_expr(ValueExpression, value="foo"),
                expr=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            {},
            nullcontext(_mk_expr(ValueExpression, value=["f", "o", "o"])),
        ),
        (
            dict(
                var_names=("foo",),
                iter_expr=_mk_expr(IdentifierExpression, identifier="bar"),
                expr=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            dict(bar=[1, 2, 3]),
            nullcontext(_mk_expr(ValueExpression, value=[1, 2, 3])),
        ),
        (
            dict(
                var_names=("foo",),
                iter_expr=_mk_expr(IdentifierExpression, identifier="bar"),
                expr=_mk_expr(
                    BinOpExpression,
                    op="+",
                    lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                    rhs=_mk_expr(IdentifierExpression, identifier="baz"),
                ),
            ),
            dict(bar=[1, 2, 3], baz=42),
            nullcontext(_mk_expr(ValueExpression, value=[43, 44, 45])),
        ),
        (
            dict(
                var_names=("foo", "bar"),
                iter_expr=_mk_expr(IdentifierExpression, identifier="bar"),
                expr=_mk_expr(
                    BinOpExpression,
                    op="+",
                    lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                    rhs=_mk_expr(IdentifierExpression, identifier="bar"),
                ),
            ),
            dict(bar=[(1, 2), (3, 4)]),
            nullcontext(_mk_expr(ValueExpression, value=[3, 7])),
        ),
    ],
)
def test_simplify(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Expression],
):
    with expected as e:
        expr = _mk_expr(ForExpression, **kwargs)
        assert expr.simplify(vars, renderers=Template.default_renderers) == e


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                var_names=("foo",),
                iter_expr=_mk_expr(ValueExpression, value="foo"),
                expr=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            {},
            nullcontext(["f", "o", "o"]),
        ),
        (
            dict(
                var_names=("foo",),
                iter_expr=_mk_expr(IdentifierExpression, identifier="bar"),
                expr=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            dict(bar=[1, 2, 3]),
            nullcontext([1, 2, 3]),
        ),
        (
            dict(
                var_names=("foo",),
                iter_expr=_mk_expr(IdentifierExpression, identifier="bar"),
                expr=_mk_expr(
                    BinOpExpression,
                    op="+",
                    lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                    rhs=_mk_expr(IdentifierExpression, identifier="baz"),
                ),
            ),
            dict(bar=[1, 2, 3], baz=42),
            nullcontext([43, 44, 45]),
        ),
        (
            dict(
                var_names=("foo", "bar"),
                iter_expr=_mk_expr(IdentifierExpression, identifier="bar"),
                expr=_mk_expr(
                    BinOpExpression,
                    op="+",
                    lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                    rhs=_mk_expr(IdentifierExpression, identifier="bar"),
                ),
            ),
            dict(bar=[(1, 2), (3, 4)]),
            nullcontext([3, 7]),
        ),
    ],
)
def test_evaluate(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Any],
):
    with expected as e:
        expr = _mk_expr(ForExpression, **kwargs)
        assert expr.evaluate(vars, renderers=Template.default_renderers) == e
