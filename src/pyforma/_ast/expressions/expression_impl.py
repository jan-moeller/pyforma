from abc import ABC
from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import Any, override

from .expression import Expression
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class ExpressionImpl(Expression, ABC):
    """Expression base class with default implementations"""

    @override
    def evaluate(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Any:
        match self.simplify(variables, renderers=renderers):
            case ValueExpression() as expr:
                return expr.value
            case _:
                raise ValueError(f"{self.origin}: Failed to evaluate expression {self}")
