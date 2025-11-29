from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import override, Any

from pyforma._util import destructure_value

from .expression import Expression
from .expression_impl import ExpressionImpl
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class WithExpression(ExpressionImpl):
    """With expression."""

    bindings: tuple[tuple[tuple[str, ...], Expression], ...]
    expr: Expression

    def __post_init__(self):
        names = [n for ns, _ in self.bindings for n in ns]
        if len(names) != len(set(names)):
            raise ValueError(f"With-expression contains duplicate names: {names}")

    @override
    def unresolved_identifiers(self) -> set[str]:
        names = {n for ns, _ in self.bindings for n in ns}
        return set[str]().union(
            id for _, expr in self.bindings for id in expr.unresolved_identifiers()
        ) | (self.expr.unresolved_identifiers() - names)

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        names = {n for ns, _ in self.bindings for n in ns}
        _bindings = tuple(
            (n, e.simplify(variables, renderers=renderers)) for n, e in self.bindings
        )
        _expr = self.expr.simplify(
            {k: v for k, v in variables.items() if k not in names},
            renderers=renderers,
        )

        drop_indices: list[int] = []
        for i, t in enumerate(_bindings):
            _names, binding = t
            if isinstance(binding, ValueExpression):
                _values = destructure_value(_names, binding.value)
                _expr = _expr.simplify(_values, renderers=renderers)
                drop_indices.append(i)

        _bindings = tuple(b for i, b in enumerate(_bindings) if i not in drop_indices)

        if len(_bindings) == 0 or len(_expr.unresolved_identifiers()) == 0:
            return _expr

        return WithExpression(origin=self.origin, bindings=_bindings, expr=_expr)
