from dataclasses import dataclass
from typing import override, Any

from .expression import Expression
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class IfExpression(Expression):
    """If expression."""

    cases: tuple[tuple[Expression, Expression], ...]  # Condition -> expression

    @override
    def identifiers(self) -> set[str]:
        return set[str]().union(
            id
            for condition, expr in self.cases
            for id in condition.identifiers().union(expr.identifiers())
        )

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        _cases: list[tuple[Expression, Expression]] = []
        for condition, expr in self.cases:
            _condition = condition.substitute(variables)

            if isinstance(_condition, ValueExpression):
                if _condition.value:
                    if len(_cases) == 0:
                        return expr.substitute(variables)
                else:  # False cases don't matter
                    continue

            _cases.append((_condition, expr.substitute(variables)))

        if len(_cases) == 0:
            return ValueExpression(origin=self.origin, value=None)

        return IfExpression(origin=self.origin, cases=tuple(_cases))
