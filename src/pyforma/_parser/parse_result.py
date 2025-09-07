from dataclasses import dataclass
from typing import Any

from .parse_input import ParseInput


@dataclass(frozen=True)
class ParseResult[T = Any]:
    remaining: ParseInput  # Remaining input
    result: T  # Parse result
