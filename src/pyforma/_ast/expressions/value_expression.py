from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import Any, override

from .expression import Expression


@dataclass(frozen=True, kw_only=True)
class ValueExpression(Expression):
    """Value expression"""

    value: Any

    @override
    def unresolved_identifiers(self) -> set[str]:
        return set()

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        return self

    @override
    def evaluate(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Any:
        return self.value
