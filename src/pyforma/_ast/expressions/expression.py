from abc import ABC, abstractmethod
from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import Any

from ..origin import Origin


@dataclass(frozen=True, kw_only=True)
class Expression(ABC):
    """Expression base class"""

    origin: Origin

    @abstractmethod
    def unresolved_identifiers(self) -> set[str]: ...

    @abstractmethod
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> "Expression": ...

    @abstractmethod
    def evaluate(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Any: ...
