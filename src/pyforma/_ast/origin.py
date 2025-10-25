from dataclasses import dataclass
from typing import override


@dataclass(frozen=True, kw_only=True)
class Origin:
    position: tuple[int, int]
    source_id: str = ""

    @override
    def __str__(self) -> str:
        return f"{self.source_id}:{self.position[0]}:{self.position[1]}"
