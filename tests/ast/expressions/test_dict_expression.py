from contextlib import nullcontext
from typing import ContextManager, Any

import pytest

from pyforma._ast import (
    Expression,
    IdentifierExpression,
    DictExpression,
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
        (dict(elements=()), set[str]()),
        (
            dict(
                elements=(
                    (
                        _mk_expr(ValueExpression, value="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            set[str](),
        ),
        (
            dict(
                elements=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            {"foo"},
        ),
        (
            dict(
                elements=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(IdentifierExpression, identifier="bar"),
                    ),
                )
            ),
            {"foo", "bar"},
        ),
        (
            dict(
                elements=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(IdentifierExpression, identifier="bar"),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bam"),
                        _mk_expr(IdentifierExpression, identifier="baz"),
                    ),
                )
            ),
            {"foo", "bar", "bam", "baz"},
        ),
    ],
)
def test_unresolved_identifiers(
    kwargs: dict[str, Any],
    expected: set[str],
):
    expr = _mk_expr(DictExpression, **kwargs)
    assert expr.unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(elements=()),
            {},
            nullcontext(_mk_expr(ValueExpression, value={})),
        ),
        (
            dict(
                elements=(
                    (
                        _mk_expr(ValueExpression, value="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            {},
            nullcontext(_mk_expr(ValueExpression, value={"foo": 42})),
        ),
        (
            dict(
                elements=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            dict(foo=42),
            nullcontext(_mk_expr(ValueExpression, value={42: 42})),
        ),
        (
            dict(
                elements=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(IdentifierExpression, identifier="bar"),
                    ),
                )
            ),
            dict(foo=42, bar="bar"),
            nullcontext(_mk_expr(ValueExpression, value={42: "bar"})),
        ),
        (
            dict(
                elements=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(IdentifierExpression, identifier="bar"),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bam"),
                        _mk_expr(IdentifierExpression, identifier="baz"),
                    ),
                )
            ),
            dict(foo=42, bar="bar", bam=True, baz=3.141),
            nullcontext(_mk_expr(ValueExpression, value={42: "bar", True: 3.141})),
        ),
    ],
)
def test_simplify(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Expression],
):
    with expected as e:
        expr = _mk_expr(DictExpression, **kwargs)
        assert expr.simplify(vars, renderers=Template.default_renderers) == e


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (dict(elements=()), {}, nullcontext({})),
        (
            dict(
                elements=(
                    (
                        _mk_expr(ValueExpression, value="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            {},
            nullcontext({"foo": 42}),
        ),
        (
            dict(
                elements=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            dict(foo=42),
            nullcontext({42: 42}),
        ),
        (
            dict(
                elements=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(IdentifierExpression, identifier="bar"),
                    ),
                )
            ),
            dict(foo=42, bar="bar"),
            nullcontext({42: "bar"}),
        ),
        (
            dict(
                elements=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(IdentifierExpression, identifier="bar"),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bam"),
                        _mk_expr(IdentifierExpression, identifier="baz"),
                    ),
                )
            ),
            dict(foo=42, bar="bar", bam=True, baz=3.141),
            nullcontext({42: "bar", True: 3.141}),
        ),
    ],
)
def test_evaluate(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Any],
):
    with expected as e:
        expr = _mk_expr(DictExpression, **kwargs)
        assert expr.evaluate(vars, renderers=Template.default_renderers) == e
