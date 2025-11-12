from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import override, Any

from .expression import Expression
from .expression_impl import ExpressionImpl
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class IfExpression(ExpressionImpl):
    """If expression."""

    cases: tuple[tuple[Expression, Expression], ...]  # Condition -> expression

    @override
    def unresolved_identifiers(self) -> set[str]:
        return set[str]().union(
            id
            for condition, expr in self.cases
            for id in condition.unresolved_identifiers().union(
                expr.unresolved_identifiers()
            )
        )

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        _cases: list[tuple[Expression, Expression]] = []
        for condition, expr in self.cases:
            _condition = condition.simplify(variables, renderers=renderers)

            if isinstance(_condition, ValueExpression):
                if _condition.value:
                    if len(_cases) == 0:
                        return expr.simplify(variables, renderers=renderers)
                else:  # False cases don't matter
                    continue

            _cases.append((_condition, expr.simplify(variables, renderers=renderers)))

        if len(_cases) == 0:
            return ValueExpression(origin=self.origin, value=None)

        return IfExpression(origin=self.origin, cases=tuple(_cases))
