from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Origin:
    position: tuple[int, int]
    source_id: str = ""
