from typing import Any

import pytest

from pyforma._parser import (
    Parser,
    ParseContext,
    ParseSuccess,
    ParseFailure,
    literal,
    ParseResult,
)
from pyforma._parser.switch import switch


@pytest.mark.parametrize(
    "source,parser_map,default,expected",
    [
        ("", (), None, ParseFailure(expected="switch()")),
        (
            "",
            ((literal("a"), literal("b")),),
            None,
            ParseFailure(expected='switch("a" => "b")'),
        ),
        (
            "bc",
            ((literal("a"), literal("b")),),
            None,
            ParseFailure(expected='switch("a" => "b")'),
        ),
        (
            "ac",
            ((literal("a"), literal("b")),),
            None,
            ParseFailure(
                expected='switch("a" => "b")',
                cause=ParseResult(
                    ParseFailure(
                        expected='"b"',
                        cause=ParseResult(
                            ParseFailure(expected='"b"'),
                            context=ParseContext(source="ac", index=1),
                        ),
                    ),
                    context=ParseContext(source="ac", index=1),
                ),
            ),
        ),
        (
            "ab",
            ((literal("a"), literal("b")),),
            None,
            ParseSuccess(("a", "b")),
        ),
        (
            "bc",
            ((literal("a"), literal("b")), (literal("b"), literal("c"))),
            None,
            ParseSuccess(("b", "c")),
        ),
        (
            "bd",
            ((literal("a"), literal("b")), (literal("b"), literal("c"))),
            None,
            ParseFailure(
                expected='switch("a" => "b", "b" => "c")',
                cause=ParseResult(
                    ParseFailure(
                        expected='"c"',
                        cause=ParseResult(
                            ParseFailure(expected='"c"'),
                            context=ParseContext(source="bd", index=1),
                        ),
                    ),
                    context=ParseContext(source="bd", index=1),
                ),
            ),
        ),
        (
            "de",
            ((literal("a"), literal("b")), (literal("b"), literal("c"))),
            None,
            ParseFailure(
                expected='switch("a" => "b", "b" => "c")',
            ),
        ),
        (
            "de",
            ((literal("a"), literal("b")), (literal("b"), literal("c"))),
            literal("de"),
            ParseSuccess("de"),
        ),
    ],
)
def test_switch(
    source: str,
    parser_map: tuple[tuple[Parser[Any], Parser[Any]], ...],
    default: Parser[Any] | None,
    expected: ParseSuccess | ParseFailure,
):
    context = ParseContext(source)
    result = switch(*parser_map, default=default)(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=len(expected.result))
    else:
        assert result.context == context
