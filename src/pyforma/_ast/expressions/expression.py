from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ..origin import Origin


@dataclass(frozen=True, kw_only=True)
class Expression(ABC):
    """Expression base class"""

    origin: Origin

    @abstractmethod
    def identifiers(self) -> set[str]: ...

    @abstractmethod
    def substitute(self, variables: dict[str, Any]) -> "Expression": ...
