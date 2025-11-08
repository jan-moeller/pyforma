from dataclasses import dataclass
from typing import override, Any, cast


from .expression import Expression
from .list_expression import ListExpression
from .value_expression import ValueExpression
from pyforma._util import destructure_value


@dataclass(frozen=True, kw_only=True)
class ForExpression(Expression):
    """For expression."""

    var_names: tuple[str, ...]
    iter_expr: Expression
    expr: Expression

    @override
    def identifiers(self) -> set[str]:
        return self.iter_expr.identifiers().union(
            self.expr.identifiers() - set(self.var_names)
        )

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        _iter_expr = self.iter_expr.substitute(variables)
        _expr = self.expr.substitute(
            {k: v for k, v in variables.items() if k not in self.var_names}
        )

        if isinstance(_iter_expr, ValueExpression):
            _elems: list[Expression] = []
            all_values = True
            for value in _iter_expr.value:
                vs = destructure_value(self.var_names, value)
                c = _expr.substitute(vs)
                if all_values and not isinstance(c, ValueExpression):
                    all_values = False
                _elems.append(c)

            if all_values:
                return ValueExpression(
                    origin=self.origin,
                    value=[cast(ValueExpression, e).value for e in _elems],
                )

            return ListExpression(
                origin=self.origin,
                elements=tuple(_elems),
            )

        return ForExpression(
            origin=self.origin,
            var_names=self.var_names,
            iter_expr=_iter_expr,
            expr=_expr,
        )
