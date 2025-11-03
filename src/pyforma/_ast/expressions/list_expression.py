from dataclasses import dataclass
from typing import override, Any, cast

from .expression import Expression
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class ListExpression(Expression):
    """List expression"""

    elements: tuple[Expression, ...]

    @override
    def identifiers(self) -> set[str]:
        return set[str]().union(*(e.identifiers() for e in self.elements))

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        _elements = tuple(e.substitute(variables) for e in self.elements)

        if all(isinstance(e, ValueExpression) for e in _elements):
            return ValueExpression(
                origin=self.origin,
                value=[cast(ValueExpression, e).value for e in _elements],
            )

        return ListExpression(origin=self.origin, elements=_elements)
