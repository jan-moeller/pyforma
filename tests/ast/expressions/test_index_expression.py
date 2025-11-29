from contextlib import nullcontext
from typing import ContextManager, Any

import pytest

from pyforma._ast import (
    Expression,
    IdentifierExpression,
    IndexExpression,
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
                expression=_mk_expr(ValueExpression, value=[1, 2, 3]),
                index=_mk_expr(ValueExpression, value=0),
            ),
            set[str](),
        ),
        (
            dict(
                expression=_mk_expr(IdentifierExpression, identifier="foo"),
                index=_mk_expr(ValueExpression, value=0),
            ),
            {"foo"},
        ),
        (
            dict(
                expression=_mk_expr(ValueExpression, value=[1, 2, 3]),
                index=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            {"foo"},
        ),
        (
            dict(
                expression=_mk_expr(IdentifierExpression, identifier="foo"),
                index=_mk_expr(IdentifierExpression, identifier="bar"),
            ),
            {"foo", "bar"},
        ),
    ],
)
def test_unresolved_identifiers(
    kwargs: dict[str, Any],
    expected: set[str],
):
    expr = _mk_expr(IndexExpression, **kwargs)
    assert expr.unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                expression=_mk_expr(ValueExpression, value=[1, 2, 3]),
                index=_mk_expr(ValueExpression, value=0),
            ),
            {},
            nullcontext(_mk_expr(ValueExpression, value=1)),
        ),
        (
            dict(
                expression=_mk_expr(ValueExpression, value=[1, 2, 3]),
                index=_mk_expr(ValueExpression, value=-1),
            ),
            {},
            nullcontext(_mk_expr(ValueExpression, value=3)),
        ),
        (
            dict(
                expression=_mk_expr(IdentifierExpression, identifier="foo"),
                index=_mk_expr(ValueExpression, value=1),
            ),
            dict(foo=[1, 2, 3]),
            nullcontext(_mk_expr(ValueExpression, value=2)),
        ),
        (
            dict(
                expression=_mk_expr(ValueExpression, value=[1, 2, 3]),
                index=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            dict(foo=2),
            nullcontext(_mk_expr(ValueExpression, value=3)),
        ),
        (
            dict(
                expression=_mk_expr(IdentifierExpression, identifier="foo"),
                index=_mk_expr(IdentifierExpression, identifier="bar"),
            ),
            dict(foo=[1, 2, 3], bar=slice(1, 3)),
            nullcontext(_mk_expr(ValueExpression, value=[2, 3])),
        ),
    ],
)
def test_simplify(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Expression],
):
    with expected as e:
        expr = _mk_expr(IndexExpression, **kwargs)
        assert expr.simplify(vars, renderers=Template.default_renderers) == e


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                expression=_mk_expr(ValueExpression, value=[1, 2, 3]),
                index=_mk_expr(ValueExpression, value=0),
            ),
            {},
            nullcontext(1),
        ),
        (
            dict(
                expression=_mk_expr(ValueExpression, value=[1, 2, 3]),
                index=_mk_expr(ValueExpression, value=-1),
            ),
            {},
            nullcontext(3),
        ),
        (
            dict(
                expression=_mk_expr(IdentifierExpression, identifier="foo"),
                index=_mk_expr(ValueExpression, value=1),
            ),
            dict(foo=[1, 2, 3]),
            nullcontext(2),
        ),
        (
            dict(
                expression=_mk_expr(ValueExpression, value=[1, 2, 3]),
                index=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            dict(foo=2),
            nullcontext(3),
        ),
        (
            dict(
                expression=_mk_expr(IdentifierExpression, identifier="foo"),
                index=_mk_expr(IdentifierExpression, identifier="bar"),
            ),
            dict(foo=[1, 2, 3], bar=slice(1, 3)),
            nullcontext([2, 3]),
        ),
    ],
)
def test_evaluate(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Any],
):
    with expected as e:
        expr = _mk_expr(IndexExpression, **kwargs)
        assert expr.evaluate(vars, renderers=Template.default_renderers) == e
