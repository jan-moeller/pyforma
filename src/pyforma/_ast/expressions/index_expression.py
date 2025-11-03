from dataclasses import dataclass
from typing import override, Any

from .expression import Expression
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class IndexExpression(Expression):
    """Slice expression"""

    expression: Expression
    index: Expression

    @override
    def identifiers(self) -> set[str]:
        return self.expression.identifiers() | self.index.identifiers()

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        expression = self.expression.substitute(variables)
        index = self.index.substitute(variables)
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
