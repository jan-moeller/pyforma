from dataclasses import dataclass
from typing import Any, TypeVar, Generic

from .parse_context import ParseContext

T = TypeVar("T", covariant=True, default=Any)


@dataclass(frozen=True)
class ParseResult(Generic[T]):
    context: ParseContext  # Remaining input
    result: T  # Parse result
