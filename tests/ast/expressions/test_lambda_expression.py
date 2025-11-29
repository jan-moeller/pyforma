from collections.abc import Callable
from contextlib import nullcontext
from typing import ContextManager, Any

import pytest

from pyforma._ast import (
    Expression,
    IdentifierExpression,
    LambdaExpression,
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
                parameters=(),
                return_value=_mk_expr(ValueExpression, value=0),
            ),
            set[str](),
        ),
        (
            dict(
                parameters=(),
                return_value=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            {"foo"},
        ),
        (
            dict(
                parameters=("foo",),
                return_value=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            set[str](),
        ),
        (
            dict(
                parameters=("foo",),
                return_value=_mk_expr(
                    BinOpExpression,
                    op="+",
                    lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                    rhs=_mk_expr(IdentifierExpression, identifier="bar"),
                ),
            ),
            {"bar"},
        ),
        (
            dict(
                parameters=("foo", "bar"),
                return_value=_mk_expr(
                    BinOpExpression,
                    op="+",
                    lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                    rhs=_mk_expr(IdentifierExpression, identifier="bar"),
                ),
            ),
            set[str](),
        ),
    ],
)
def test_unresolved_identifiers(
    kwargs: dict[str, Any],
    expected: set[str],
):
    expr = _mk_expr(LambdaExpression, **kwargs)
    assert expr.unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "kwargs,vars,validator",
    [  # pyright: ignore[reportUnknownArgumentType]
        (
            dict(
                parameters=(),
                return_value=_mk_expr(ValueExpression, value=0),
            ),
            {},
            nullcontext(lambda e: isinstance(e, ValueExpression) and e.value() == 0),  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
        ),
        (
            dict(
                parameters=("foo",),
                return_value=_mk_expr(ValueExpression, value=0),
            ),
            {},
            nullcontext(
                lambda e: isinstance(e, ValueExpression)  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
                and e.value(0) == 0
                and e.value(1) == 0
            ),
        ),
        (
            dict(
                parameters=("foo",),
                return_value=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            {},
            nullcontext(
                lambda e: isinstance(e, ValueExpression)  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
                and e.value(0) == 0
                and e.value(1) == 1
            ),
        ),
        (
            dict(
                parameters=("foo",),
                return_value=_mk_expr(
                    BinOpExpression,
                    op="+",
                    lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                    rhs=_mk_expr(IdentifierExpression, identifier="bar"),
                ),
            ),
            dict(bar=1),
            nullcontext(
                lambda e: isinstance(e, ValueExpression)  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
                and e.value(0) == 1
                and e.value(1) == 2
            ),
        ),
        (
            dict(
                parameters=("foo", "bar"),
                return_value=_mk_expr(
                    BinOpExpression,
                    op="+",
                    lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                    rhs=_mk_expr(IdentifierExpression, identifier="bar"),
                ),
            ),
            {},
            nullcontext(
                lambda e: isinstance(e, ValueExpression)  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
                and e.value(0, 1) == 1
                and e.value(1, 2) == 3
            ),
        ),
    ],
)
def test_simplify(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    validator: ContextManager[Callable[[Expression], bool]],
):
    with validator as e:
        expr = _mk_expr(LambdaExpression, **kwargs)
        assert e(expr.simplify(vars, renderers=Template.default_renderers))


@pytest.mark.parametrize(
    "kwargs,vars,validator",
    [  # pyright: ignore[reportUnknownArgumentType]
        (
            dict(
                parameters=(),
                return_value=_mk_expr(ValueExpression, value=0),
            ),
            {},
            nullcontext(lambda e: e() == 0),  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
        ),
        (
            dict(
                parameters=("foo",),
                return_value=_mk_expr(ValueExpression, value=0),
            ),
            {},
            nullcontext(
                lambda e: e(0) == 0 and e(1) == 0  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
            ),
        ),
        (
            dict(
                parameters=("foo",),
                return_value=_mk_expr(IdentifierExpression, identifier="foo"),
            ),
            {},
            nullcontext(
                lambda e: e(0) == 0 and e(1) == 1  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
            ),
        ),
        (
            dict(
                parameters=("foo",),
                return_value=_mk_expr(
                    BinOpExpression,
                    op="+",
                    lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                    rhs=_mk_expr(IdentifierExpression, identifier="bar"),
                ),
            ),
            dict(bar=1),
            nullcontext(
                lambda e: e(0) == 1 and e(1) == 2  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
            ),
        ),
        (
            dict(
                parameters=("foo", "bar"),
                return_value=_mk_expr(
                    BinOpExpression,
                    op="+",
                    lhs=_mk_expr(IdentifierExpression, identifier="foo"),
                    rhs=_mk_expr(IdentifierExpression, identifier="bar"),
                ),
            ),
            {},
            nullcontext(
                lambda e: e(0, 1) == 1 and e(1, 2) == 3  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
            ),
        ),
    ],
)
def test_evaluate(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    validator: ContextManager[Callable[[Any], bool]],
):
    with validator as e:
        expr = _mk_expr(LambdaExpression, **kwargs)
        assert e(expr.evaluate(vars, renderers=Template.default_renderers))
