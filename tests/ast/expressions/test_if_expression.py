from contextlib import nullcontext
from typing import ContextManager, Any

import pytest

from pyforma._ast import (
    Expression,
    IdentifierExpression,
    IfExpression,
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
        (dict(cases=()), set[str]()),
        (
            dict(
                cases=(
                    (
                        _mk_expr(ValueExpression, value=True),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            set[str](),
        ),
        (
            dict(
                cases=(
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
                cases=(
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
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(IdentifierExpression, identifier="bar"),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="baz"),
                        _mk_expr(IdentifierExpression, identifier="bam"),
                    ),
                )
            ),
            {"foo", "bar", "baz", "bam"},
        ),
    ],
)
def test_unresolved_identifiers(
    kwargs: dict[str, Any],
    expected: set[str],
):
    expr = _mk_expr(IfExpression, **kwargs)
    assert expr.unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                cases=(
                    (
                        _mk_expr(ValueExpression, value=True),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            {},
            nullcontext(_mk_expr(ValueExpression, value=42)),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(ValueExpression, value=False),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            {},
            nullcontext(_mk_expr(ValueExpression, value=None)),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            dict(foo=True),
            nullcontext(_mk_expr(ValueExpression, value=42)),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            dict(foo=False),
            nullcontext(_mk_expr(ValueExpression, value=None)),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bar"),
                        _mk_expr(ValueExpression, value=0),
                    ),
                )
            ),
            dict(foo=True),
            nullcontext(_mk_expr(ValueExpression, value=42)),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bar"),
                        _mk_expr(ValueExpression, value=0),
                    ),
                )
            ),
            dict(foo=False),
            nullcontext(
                _mk_expr(
                    IfExpression,
                    cases=(
                        (
                            _mk_expr(IdentifierExpression, identifier="bar"),
                            _mk_expr(ValueExpression, value=0),
                        ),
                    ),
                )
            ),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bar"),
                        _mk_expr(ValueExpression, value=0),
                    ),
                )
            ),
            dict(foo=False, bar=True),
            nullcontext(_mk_expr(ValueExpression, value=0)),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bar"),
                        _mk_expr(ValueExpression, value=0),
                    ),
                )
            ),
            dict(foo=False, bar=False),
            nullcontext(_mk_expr(ValueExpression, value=None)),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bar"),
                        _mk_expr(ValueExpression, value=0),
                    ),
                )
            ),
            dict(bar=False),
            nullcontext(
                _mk_expr(
                    IfExpression,
                    cases=(
                        (
                            _mk_expr(IdentifierExpression, identifier="foo"),
                            _mk_expr(ValueExpression, value=42),
                        ),
                    ),
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
        expr = _mk_expr(IfExpression, **kwargs)
        assert expr.simplify(vars, renderers=Template.default_renderers) == e


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                cases=(
                    (
                        _mk_expr(ValueExpression, value=True),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            {},
            nullcontext(42),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(ValueExpression, value=False),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            {},
            nullcontext(None),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            dict(foo=True),
            nullcontext(42),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                )
            ),
            dict(foo=False),
            nullcontext(None),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bar"),
                        _mk_expr(ValueExpression, value=0),
                    ),
                )
            ),
            dict(foo=True),
            nullcontext(42),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bar"),
                        _mk_expr(ValueExpression, value=0),
                    ),
                )
            ),
            dict(foo=False),
            pytest.raises(ValueError),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bar"),
                        _mk_expr(ValueExpression, value=0),
                    ),
                )
            ),
            dict(foo=False, bar=True),
            nullcontext(0),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bar"),
                        _mk_expr(ValueExpression, value=0),
                    ),
                )
            ),
            dict(foo=False, bar=False),
            nullcontext(None),
        ),
        (
            dict(
                cases=(
                    (
                        _mk_expr(IdentifierExpression, identifier="foo"),
                        _mk_expr(ValueExpression, value=42),
                    ),
                    (
                        _mk_expr(IdentifierExpression, identifier="bar"),
                        _mk_expr(ValueExpression, value=0),
                    ),
                )
            ),
            dict(bar=False),
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
        expr = _mk_expr(IfExpression, **kwargs)
        assert expr.evaluate(vars, renderers=Template.default_renderers) == e
