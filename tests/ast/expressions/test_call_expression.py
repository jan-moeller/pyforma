from contextlib import nullcontext
from typing import ContextManager, Any

import pytest

from pyforma._ast import (
    Expression,
    IdentifierExpression,
    CallExpression,
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
                callee=_mk_expr(ValueExpression, value=str),
                arguments=(_mk_expr(ValueExpression, value=2),),
                kw_arguments=(("encoding", _mk_expr(ValueExpression, value="utf-8")),),
            ),
            set[str](),
        ),
        (
            dict(
                callee=_mk_expr(IdentifierExpression, identifier="str"),
                arguments=(_mk_expr(ValueExpression, value=2),),
                kw_arguments=(("encoding", _mk_expr(ValueExpression, value="utf-8")),),
            ),
            {"str"},
        ),
        (
            dict(
                callee=_mk_expr(IdentifierExpression, identifier="str"),
                arguments=(_mk_expr(IdentifierExpression, identifier="foo"),),
                kw_arguments=(("encoding", _mk_expr(ValueExpression, value="utf-8")),),
            ),
            {"str", "foo"},
        ),
        (
            dict(
                callee=_mk_expr(IdentifierExpression, identifier="str"),
                arguments=(_mk_expr(IdentifierExpression, identifier="foo"),),
                kw_arguments=(
                    ("encoding", _mk_expr(IdentifierExpression, identifier="bar")),
                ),
            ),
            {"str", "foo", "bar"},
        ),
    ],
)
def test_unresolved_identifiers(
    kwargs: dict[str, Any],
    expected: set[str],
):
    expr = _mk_expr(CallExpression, **kwargs)
    assert expr.unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                callee=_mk_expr(ValueExpression, value=str),
                arguments=(_mk_expr(ValueExpression, value=b"42"),),
                kw_arguments=(("encoding", _mk_expr(ValueExpression, value="utf-8")),),
            ),
            {},
            nullcontext(_mk_expr(ValueExpression, value="42")),
        ),
        (
            dict(
                callee=_mk_expr(IdentifierExpression, identifier="foo"),
                arguments=(_mk_expr(ValueExpression, value=b"42"),),
                kw_arguments=(("encoding", _mk_expr(ValueExpression, value="utf-8")),),
            ),
            dict(foo=str),
            nullcontext(_mk_expr(ValueExpression, value="42")),
        ),
        (
            dict(
                callee=_mk_expr(IdentifierExpression, identifier="foo"),
                arguments=(_mk_expr(IdentifierExpression, identifier="bar"),),
                kw_arguments=(("encoding", _mk_expr(ValueExpression, value="utf-8")),),
            ),
            dict(foo=str, bar=b"bar"),
            nullcontext(_mk_expr(ValueExpression, value="bar")),
        ),
        (
            dict(
                callee=_mk_expr(IdentifierExpression, identifier="foo"),
                arguments=(_mk_expr(IdentifierExpression, identifier="bar"),),
                kw_arguments=(
                    ("encoding", _mk_expr(IdentifierExpression, identifier="baz")),
                ),
            ),
            dict(foo=str, bar=b"bar", baz="utf-8"),
            nullcontext(_mk_expr(ValueExpression, value="bar")),
        ),
    ],
)
def test_simplify(
    kwargs: dict[str, Any],
    vars: dict[str, Any],
    expected: ContextManager[Expression],
):
    with expected as e:
        expr = _mk_expr(CallExpression, **kwargs)
        assert expr.simplify(vars, renderers=Template.default_renderers) == e


@pytest.mark.parametrize(
    "kwargs,vars,expected",
    [
        (
            dict(
                callee=_mk_expr(ValueExpression, value=str),
                arguments=(_mk_expr(ValueExpression, value=b"42"),),
                kw_arguments=(("encoding", _mk_expr(ValueExpression, value="utf-8")),),
            ),
            {},
            nullcontext("42"),
        ),
        (
            dict(
                callee=_mk_expr(IdentifierExpression, identifier="foo"),
                arguments=(_mk_expr(ValueExpression, value=b"42"),),
                kw_arguments=(("encoding", _mk_expr(ValueExpression, value="utf-8")),),
            ),
            dict(foo=str),
            nullcontext("42"),
        ),
        (
            dict(
                callee=_mk_expr(IdentifierExpression, identifier="foo"),
                arguments=(_mk_expr(IdentifierExpression, identifier="bar"),),
                kw_arguments=(("encoding", _mk_expr(ValueExpression, value="utf-8")),),
            ),
            dict(foo=str, bar=b"bar"),
            nullcontext("bar"),
        ),
        (
            dict(
                callee=_mk_expr(IdentifierExpression, identifier="foo"),
                arguments=(_mk_expr(IdentifierExpression, identifier="bar"),),
                kw_arguments=(
                    ("encoding", _mk_expr(IdentifierExpression, identifier="baz")),
                ),
            ),
            dict(foo=str, bar=b"bar", baz="utf-8"),
            nullcontext("bar"),
        ),
        (
            dict(
                callee=_mk_expr(IdentifierExpression, identifier="foo"),
                arguments=(_mk_expr(IdentifierExpression, identifier="bar"),),
                kw_arguments=(
                    ("encoding", _mk_expr(IdentifierExpression, identifier="baz")),
                ),
            ),
            dict(bar=b"bar", baz="utf-8"),
            pytest.raises(ValueError),
        ),
        (
            dict(
                callee=_mk_expr(IdentifierExpression, identifier="foo"),
                arguments=(_mk_expr(IdentifierExpression, identifier="bar"),),
                kw_arguments=(
                    ("encoding", _mk_expr(IdentifierExpression, identifier="baz")),
                ),
            ),
            dict(foo=str, baz="utf-8"),
            pytest.raises(ValueError),
        ),
        (
            dict(
                callee=_mk_expr(IdentifierExpression, identifier="foo"),
                arguments=(_mk_expr(IdentifierExpression, identifier="bar"),),
                kw_arguments=(
                    ("encoding", _mk_expr(IdentifierExpression, identifier="baz")),
                ),
            ),
            dict(foo=str, bar=b"bar"),
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
        expr = _mk_expr(CallExpression, **kwargs)
        assert expr.evaluate(vars, renderers=Template.default_renderers) == e
