from dataclasses import dataclass
from typing import Any, override

from .expression import Expression


@dataclass(frozen=True, kw_only=True)
class ValueExpression(Expression):
    """Value expression"""

    value: Any

    @override
    def identifiers(self) -> set[str]:
        return set()

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        return self
