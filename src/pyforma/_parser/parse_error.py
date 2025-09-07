from typing import final

from .parser import Parser
from .parse_input import ParseInput


@final
class ParseError(Exception):
    def __init__(self, msg: str, /, *, input: ParseInput, parser: Parser):
        super().__init__(msg)
        self.error_input = input
        self.parser = parser
