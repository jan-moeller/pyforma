from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import override, Any

from .expression import Expression
from .expression_impl import ExpressionImpl
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class IndexExpression(ExpressionImpl):
    """Slice expression"""

    expression: Expression
    index: Expression

    @override
    def unresolved_identifiers(self) -> set[str]:
        return (
            self.expression.unresolved_identifiers()
            | self.index.unresolved_identifiers()
        )

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        expression = self.expression.simplify(variables, renderers=renderers)
        index = self.index.simplify(variables, renderers=renderers)
        if isinstance(expression, ValueExpression) and isinstance(
            index, ValueExpression
        ):
            try:
                value = expression.value[index.value]
            except Exception as ex:
                raise TypeError(
                    f"{self.origin}: Invalid indexing expression for value {expression.value} of type {type(expression.value)} and index {index.value} of type {type(index.value)}"
                ) from ex
            return ValueExpression(origin=self.origin, value=value)
        return IndexExpression(origin=self.origin, expression=expression, index=index)
