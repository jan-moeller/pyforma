from typing import final

from .parser import Parser
from .parse_context import ParseContext


@final
class ParseError(Exception):
    def __init__(self, msg: str, /, *, context: ParseContext, parser: Parser):
        super().__init__(msg)
        self.context = context
        self.parser = parser
