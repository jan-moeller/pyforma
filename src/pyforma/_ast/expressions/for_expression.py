from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import override, Any, cast


from .expression import Expression
from .expression_impl import ExpressionImpl
from .list_expression import ListExpression
from .value_expression import ValueExpression
from pyforma._util import destructure_value


@dataclass(frozen=True, kw_only=True)
class ForExpression(ExpressionImpl):
    """For expression."""

    var_names: tuple[str, ...]
    iter_expr: Expression
    expr: Expression

    @override
    def unresolved_identifiers(self) -> set[str]:
        return self.iter_expr.unresolved_identifiers().union(
            self.expr.unresolved_identifiers() - set(self.var_names)
        )

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        _iter_expr = self.iter_expr.simplify(variables, renderers=renderers)
        _expr = self.expr.simplify(
            {k: v for k, v in variables.items() if k not in self.var_names},
            renderers=renderers,
        )

        if isinstance(_iter_expr, ValueExpression):
            _elems: list[Expression] = []
            all_values = True
            for value in _iter_expr.value:
                vs = destructure_value(self.var_names, value)
                c = _expr.simplify(vs, renderers=renderers)
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
