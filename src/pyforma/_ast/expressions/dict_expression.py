from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import override, Any, cast

from .expression import Expression
from .expression_impl import ExpressionImpl
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class DictExpression(ExpressionImpl):
    """Dictionary expression"""

    elements: tuple[tuple[Expression, Expression], ...]

    @override
    def unresolved_identifiers(self) -> set[str]:
        return set[str]().union(
            *(e[0].unresolved_identifiers() for e in self.elements),
            *(e[1].unresolved_identifiers() for e in self.elements),
        )

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        _elements = tuple(
            (
                k.simplify(variables, renderers=renderers),
                v.simplify(variables, renderers=renderers),
            )
            for k, v in self.elements
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
