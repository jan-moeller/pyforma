from dataclasses import dataclass
from typing import override, Any, cast

from .expression import Expression
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class DictExpression(Expression):
    """Dictionary expression"""

    elements: tuple[tuple[Expression, Expression], ...]

    @override
    def identifiers(self) -> set[str]:
        return set[str]().union(
            *(e[0].identifiers() for e in self.elements),
            *(e[1].identifiers() for e in self.elements),
        )

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        _elements = tuple(
            (k.substitute(variables), v.substitute(variables)) for k, v in self.elements
        )

        if all(
            isinstance(k, ValueExpression) and isinstance(v, ValueExpression)
            for k, v in _elements
        ):
            return ValueExpression(
                origin=self.origin,
                value={
                    cast(ValueExpression, k).value: cast(ValueExpression, v).value
                    for k, v in _elements
                },
            )

        return DictExpression(origin=self.origin, elements=_elements)
