from dataclasses import dataclass
from typing import override, Any

from pyforma._util import destructure_value

from .expression import Expression
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class WithExpression(Expression):
    """With expression."""

    bindings: tuple[tuple[tuple[str, ...], Expression], ...]
    expr: Expression

    def __post_init__(self):
        names = [n for ns, _ in self.bindings for n in ns]
        if len(names) != len(set(names)):
            raise ValueError(f"With-expression contains duplicate names: {names}")

    @override
    def identifiers(self) -> set[str]:
        names = {n for ns, _ in self.bindings for n in ns}
        return set[str]().union(
            id for _, expr in self.bindings for id in expr.identifiers()
        ) | (self.expr.identifiers() - names)

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        names = {n for ns, _ in self.bindings for n in ns}
        _bindings = tuple((n, e.substitute(variables)) for n, e in self.bindings)
        _expr = self.expr.substitute(
            {k: v for k, v in variables.items() if k not in names}
        )

        drop_indices: list[int] = []
        for i, t in enumerate(_bindings):
            _names, binding = t
            if isinstance(binding, ValueExpression):
                _values = destructure_value(_names, binding.value)
                _expr = _expr.substitute(_values)
                drop_indices.append(i)

        _bindings = tuple(b for i, b in enumerate(_bindings) if i not in drop_indices)

        if len(_bindings) == 0 or len(_expr.identifiers()) == 0:
            return _expr

        return WithExpression(origin=self.origin, bindings=_bindings, expr=_expr)
