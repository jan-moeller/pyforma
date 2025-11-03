from dataclasses import dataclass
from typing import override, Any

from .expression import Expression
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class IdentifierExpression(Expression):
    """Identifier expression."""

    identifier: str

    @override
    def identifiers(self) -> set[str]:
        return {self.identifier}

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        if self.identifier in variables:
            return ValueExpression(origin=self.origin, value=variables[self.identifier])
        return self
