from dataclasses import dataclass


@dataclass(frozen=True)
class Expression:
    """Holds a pyforma expression."""

    identifier: str  # TODO: extend expression definition
