from typing import Any, override
import pytest

from pyforma._parser import ParseResult, ParseInput, parser, Parser


@parser
def empty(source: ParseInput) -> ParseResult[str]:
    return ParseResult(remaining=source, result="")


@parser(name="empty")
def parse_empty(source: ParseInput) -> ParseResult[str]:
    return empty(source)


class EmptyParser:
    def __call__(self, source: ParseInput) -> ParseResult[str]:
        return empty(source)


empty_parser = parser(EmptyParser())
empty_parser2 = parser(EmptyParser(), name="empty")


@pytest.mark.parametrize(
    "parser,expected_name",
    [  # type: ignore
        (empty, "empty"),
        (parse_empty, "empty"),
        (empty_parser, "EmptyParser"),
        (empty_parser2, "empty"),
    ],
)
def test_parser(parser: Parser[str], expected_name: str):
    assert parser.name == expected_name
    assert parser(ParseInput("foo")).result == ""


def test_unsupported_parser():
    class WeirdParser:
        @override
        def __getattribute__(self, name: str) -> Any:
            if name == "__class__":
                raise AttributeError("__class__ hidden")
            return super().__getattribute__(name)

        def __call__(self, input: ParseInput) -> ParseResult[str]:
            return ParseResult(remaining=input, result="")

    with pytest.raises(TypeError):
        _ = parser(WeirdParser())
