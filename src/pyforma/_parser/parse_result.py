from dataclasses import dataclass
from typing import Any

from .parse_context import ParseContext


@dataclass(frozen=True)
class ParseResult[T = Any]:
    context: ParseContext  # Remaining input
    result: T  # Parse result
