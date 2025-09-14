from typing import final

from .parse_context import ParseContext


@final
class ParseError(Exception):
    def __init__(self, msg: str, /, *, context: ParseContext):
        super().__init__(msg)
        self.context = context
