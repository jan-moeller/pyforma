from contextlib import nullcontext
from typing import ContextManager, Any

import pytest

from pyforma._ast import (
    Expression,
    IdentifierExpression,
    WithExpression,
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
        (dict(bindings=(), expr=_mk_expr(ValueExpression, value=42)), set[str]()),
        (
            dict(
                bindings=(
                    (
                        ("foo",),
                        _mk_expr(ValueExpression, value=42),
                    ),
                ),
                expr=_mk_expr(ValueExpression, value=42),
            ),
            set[str](),
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo", "bar"),
                        _mk_expr(ValueExpression, value=(1, 2)),
                    ),
                ),
                expr=_mk_expr(ValueExpression, value=42),
            ),
            set[str](),
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo", "bar"),
                        _mk_expr(IdentifierExpression, identifier="bam"),
                    ),
                ),
                expr=_mk_expr(ValueExpression, value=42),
            ),
            {"bam"},
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo", "bar"),
                        _mk_expr(IdentifierExpression, identifier="bam"),
                    ),
                ),
                expr=_mk_expr(IdentifierExpression, identifier="baz"),
            ),
            {"bam", "baz"},
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo", "bar"),
                        _mk_expr(IdentifierExpression, identifier="foo"),
                    ),
                ),
                expr=_mk_expr(IdentifierExpression, identifier="bar"),
            ),
            {"foo"},
        ),
    ],
)
def test_unresolved_identifiers(
    kwargs: dict[str, Any],
    expected: set[str],
):
    expr = _mk_expr(WithExpression, **kwargs)
    assert expr.unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(bindings=(), expr=_mk_expr(ValueExpression, value=42)),
            {},
            nullcontext(_mk_expr(ValueExpression, value=42)),
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo",),
                        _mk_expr(ValueExpression, value=42),
                    ),
                ),
                expr=_mk_expr(ValueExpression, value=42),
            ),
            {},
            nullcontext(_mk_expr(ValueExpression, value=42)),
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo", "bar"),
                        _mk_expr(ValueExpression, value=(1, 2)),
                    ),
                ),
                expr=_mk_expr(ValueExpression, value=42),
            ),
            {},
            nullcontext(_mk_expr(ValueExpression, value=42)),
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo", "bar"),
                        _mk_expr(IdentifierExpression, identifier="bam"),
                    ),
                ),
                expr=_mk_expr(ValueExpression, value=42),
            ),
            dict(bam=(1, 2)),
            nullcontext(_mk_expr(ValueExpression, value=42)),
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo", "bar"),
                        _mk_expr(IdentifierExpression, identifier="bam"),
                    ),
                ),
                expr=_mk_expr(IdentifierExpression, identifier="baz"),
            ),
            dict(bam=(1, 2), baz=(3, 4)),
            nullcontext(_mk_expr(ValueExpression, value=(3, 4))),
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo", "bar"),
                        _mk_expr(IdentifierExpression, identifier="foo"),
                    ),
                ),
                expr=_mk_expr(IdentifierExpression, identifier="bar"),
            ),
            dict(foo=(1, 2)),
            nullcontext(_mk_expr(ValueExpression, value=2)),
        ),
    ],
)
def test_simplify(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Expression],
):
    with expected as e:
        expr = _mk_expr(WithExpression, **kwargs)
        assert expr.simplify(vars, renderers=Template.default_renderers) == e


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(bindings=(), expr=_mk_expr(ValueExpression, value=42)),
            {},
            nullcontext(42),
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo",),
                        _mk_expr(ValueExpression, value=42),
                    ),
                ),
                expr=_mk_expr(ValueExpression, value=42),
            ),
            {},
            nullcontext(42),
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo", "bar"),
                        _mk_expr(ValueExpression, value=(1, 2)),
                    ),
                ),
                expr=_mk_expr(ValueExpression, value=42),
            ),
            {},
            nullcontext(42),
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo", "bar"),
                        _mk_expr(IdentifierExpression, identifier="bam"),
                    ),
                ),
                expr=_mk_expr(ValueExpression, value=42),
            ),
            dict(bam=(1, 2)),
            nullcontext(42),
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo", "bar"),
                        _mk_expr(IdentifierExpression, identifier="bam"),
                    ),
                ),
                expr=_mk_expr(IdentifierExpression, identifier="baz"),
            ),
            dict(bam=(1, 2), baz=(3, 4)),
            nullcontext((3, 4)),
        ),
        (
            dict(
                bindings=(
                    (
                        ("foo", "bar"),
                        _mk_expr(IdentifierExpression, identifier="foo"),
                    ),
                ),
                expr=_mk_expr(IdentifierExpression, identifier="bar"),
            ),
            dict(foo=(1, 2)),
            nullcontext(2),
        ),
    ],
)
def test_evaluate(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Any],
):
    with expected as e:
        expr = _mk_expr(WithExpression, **kwargs)
        assert expr.evaluate(vars, renderers=Template.default_renderers) == e
