from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import Literal, override, Any

from .expression import Expression
from .expression_impl import ExpressionImpl
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class UnOpExpression(ExpressionImpl):
    """Unary operator expression"""

    op: Literal["+", "-", "~", "not"]
    operand: Expression

    @override
    def unresolved_identifiers(self) -> set[str]:
        return self.operand.unresolved_identifiers()

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        operand = self.operand.simplify(variables, renderers=renderers)
        if isinstance(operand, ValueExpression):
            try:
                match self.op:
                    case "+":
                        return ValueExpression(origin=self.origin, value=+operand.value)
                    case "-":
                        return ValueExpression(origin=self.origin, value=-operand.value)
                    case "~":
                        return ValueExpression(origin=self.origin, value=~operand.value)
                    case "not":  # pragma: no branch
                        return ValueExpression(
                            origin=self.origin, value=not operand.value
                        )
            except Exception as ex:
                raise TypeError(
                    f"{self.origin}: Invalid unary operator {self.op} for value {operand.value} of type {type(operand.value)}"
                ) from ex

        return UnOpExpression(origin=self.origin, op=self.op, operand=operand)
