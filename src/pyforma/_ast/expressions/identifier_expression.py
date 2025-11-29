from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import override, Any

from .expression import Expression
from .expression_impl import ExpressionImpl
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class IdentifierExpression(ExpressionImpl):
    """Identifier expression."""

    identifier: str

    @override
    def unresolved_identifiers(self) -> set[str]:
        return {self.identifier}

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        if self.identifier in variables:
            return ValueExpression(origin=self.origin, value=variables[self.identifier])
        return self
