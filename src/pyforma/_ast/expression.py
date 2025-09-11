from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override, Any


class Expression(ABC):
    """Expression base class"""

    @abstractmethod
    def identifiers(self) -> set[str]: ...

    @abstractmethod
    def substitute(self, variables: dict[str, Any]) -> "Expression": ...


@dataclass(frozen=True)
class ValueExpression(Expression):
    """Value expression"""

    value: Any

    @override
    def identifiers(self) -> set[str]:
        return set()

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        return self


@dataclass(frozen=True)
class IdentifierExpression(Expression):
    """Identifier expression."""

    identifier: str

    @override
    def identifiers(self) -> set[str]:
        return {self.identifier}

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        if self.identifier in variables:
            return ValueExpression(variables[self.identifier])
        return self
