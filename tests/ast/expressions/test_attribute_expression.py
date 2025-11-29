from contextlib import nullcontext
from typing import ContextManager, Any

import pytest

from pyforma._ast import Expression, AttributeExpression, IdentifierExpression
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
            dict(object=_mk_expr(ValueExpression, value="foo"), attribute="format"),
            set[str](),
        ),
        (
            dict(
                object=_mk_expr(IdentifierExpression, identifier="foo"),
                attribute="format",
            ),
            {"foo"},
        ),
    ],
)
def test_unresolved_identifiers(
    kwargs: dict[str, Any],
    expected: set[str],
):
    expr = AttributeExpression(origin=Origin(position=(1, 1)), **kwargs)
    assert expr.unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(object=_mk_expr(ValueExpression, value="foo"), attribute="format"),
            {},
            nullcontext(
                _mk_expr(
                    ValueExpression,
                    value="foo".format,
                )
            ),
        ),
        (
            dict(
                object=_mk_expr(IdentifierExpression, identifier="foo"),
                attribute="format",
            ),
            {},
            nullcontext(
                _mk_expr(
                    AttributeExpression,
                    object=_mk_expr(IdentifierExpression, identifier="foo"),
                    attribute="format",
                )
            ),
        ),
    ],
)
def test_simplify(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Expression],
):
    with expected as e:
        expr = AttributeExpression(origin=Origin(position=(1, 1)), **kwargs)
        assert expr.simplify(vars, renderers=Template.default_renderers) == e


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                object=_mk_expr(ValueExpression, value="foo"),
                attribute="format",
            ),
            {},
            nullcontext("foo".format),
        ),
        (
            dict(
                object=_mk_expr(IdentifierExpression, identifier="foo"),
                attribute="format",
            ),
            dict(foo="foo"),
            nullcontext("foo".format),
        ),
    ],
)
def test_evaluate(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Any],
):
    with expected as e:
        expr = AttributeExpression(origin=Origin(position=(1, 1)), **kwargs)
        assert expr.evaluate(vars, renderers=Template.default_renderers) == e
