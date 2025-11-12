from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import override, Any, cast

from .expression import Expression
from .expression_impl import ExpressionImpl
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class ListExpression(ExpressionImpl):
    """List expression"""

    elements: tuple[Expression, ...]

    @override
    def unresolved_identifiers(self) -> set[str]:
        return set[str]().union(*(e.unresolved_identifiers() for e in self.elements))

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        _elements = tuple(
            e.simplify(variables, renderers=renderers) for e in self.elements
        )

        if all(isinstance(e, ValueExpression) for e in _elements):
            return ValueExpression(
                origin=self.origin,
                value=[cast(ValueExpression, e).value for e in _elements],
            )

        return ListExpression(origin=self.origin, elements=_elements)
