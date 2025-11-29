from contextlib import nullcontext
from typing import ContextManager, Any

import pytest

from pyforma._ast import (
    Expression,
    IdentifierExpression,
    TemplateExpression,
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
        (dict(content=()), set[str]()),
        (
            dict(content=(_mk_expr(ValueExpression, value="foo"),)),
            set[str](),
        ),
        (
            dict(
                content=(
                    _mk_expr(IdentifierExpression, identifier="foo"),
                    _mk_expr(ValueExpression, value=42),
                )
            ),
            {"foo"},
        ),
        (
            dict(
                content=(
                    _mk_expr(IdentifierExpression, identifier="foo"),
                    _mk_expr(IdentifierExpression, identifier="bar"),
                )
            ),
            {"foo", "bar"},
        ),
    ],
)
def test_unresolved_identifiers(
    kwargs: dict[str, Any],
    expected: set[str],
):
    expr = _mk_expr(TemplateExpression, **kwargs)
    assert expr.unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(content=()),
            {},
            nullcontext(_mk_expr(ValueExpression, value="")),
        ),
        (
            dict(
                content=(
                    _mk_expr(ValueExpression, value="foo"),
                    _mk_expr(ValueExpression, value=42),
                )
            ),
            {},
            nullcontext(_mk_expr(ValueExpression, value="foo42")),
        ),
        (
            dict(
                content=(
                    _mk_expr(IdentifierExpression, identifier="foo"),
                    _mk_expr(ValueExpression, value=42),
                )
            ),
            dict(foo=42),
            nullcontext(_mk_expr(ValueExpression, value="4242")),
        ),
        (
            dict(
                content=(
                    _mk_expr(IdentifierExpression, identifier="foo"),
                    _mk_expr(IdentifierExpression, identifier="bar"),
                )
            ),
            dict(foo=42, bar="bar"),
            nullcontext(_mk_expr(ValueExpression, value="42bar")),
        ),
    ],
)
def test_simplify(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Expression],
):
    with expected as e:
        expr = _mk_expr(TemplateExpression, **kwargs)
        assert expr.simplify(vars, renderers=Template.default_renderers) == e


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (dict(content=()), {}, nullcontext("")),
        (
            dict(
                content=(
                    _mk_expr(ValueExpression, value="foo"),
                    _mk_expr(ValueExpression, value=42),
                )
            ),
            {},
            nullcontext("foo42"),
        ),
        (
            dict(
                content=(
                    _mk_expr(IdentifierExpression, identifier="foo"),
                    _mk_expr(ValueExpression, value=42),
                )
            ),
            dict(foo=42),
            nullcontext("4242"),
        ),
        (
            dict(
                content=(
                    _mk_expr(IdentifierExpression, identifier="foo"),
                    _mk_expr(IdentifierExpression, identifier="bar"),
                )
            ),
            dict(foo=42, bar="bar"),
            nullcontext("42bar"),
        ),
    ],
)
def test_evaluate(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Any],
):
    with expected as e:
        expr = _mk_expr(TemplateExpression, **kwargs)
        assert expr.evaluate(vars, renderers=Template.default_renderers) == e
