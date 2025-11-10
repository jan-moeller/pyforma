import pytest

from pyforma._parser import (
    ParseContext,
    comment,
    ParseFailure,
    ParseSuccess,
    ParseResult,
)
from pyforma._parser.template_syntax_config import BlockSyntaxConfig


@pytest.mark.parametrize(
    "source,expected,result_idx",
    [
        (
            "",
            ParseFailure(
                expected='sequence("{#", until("#}"), "#}")',
                cause=ParseResult(
                    ParseFailure(
                        expected='"{#"',
                        cause=ParseResult(
                            ParseFailure(expected='"{"'),
                            context=ParseContext(source="", index=0, position=(1, 1)),
                        ),
                    ),
                    context=ParseContext(source="", index=0, position=(1, 1)),
                ),
            ),
            0,
        ),
        ("{#foo#}", ParseSuccess(None), 7),
        ("{#foo#}bar", ParseSuccess(None), 7),
        ("{# foo bar #} baz", ParseSuccess(None), 13),
        ("{# foo {# bar #} #} baz", ParseSuccess(None), 16),
        (
            "{# foo",
            ParseFailure(
                expected='sequence("{#", until("#}"), "#}")',
                cause=ParseResult(
                    ParseFailure(
                        expected='"#}"',
                        cause=ParseResult(
                            ParseFailure(expected='"#"'),
                            context=ParseContext(
                                source="{# foo", index=6, position=(1, 7)
                            ),
                        ),
                    ),
                    context=ParseContext(source="{# foo", index=6, position=(1, 7)),
                ),
            ),
            0,
        ),
        ("{# {# #}", ParseSuccess(None), 8),
    ],
)
def test_comment(
    source: str,
    expected: ParseSuccess | ParseFailure,
    result_idx: int,
):
    context = ParseContext(source)
    result = comment(BlockSyntaxConfig("{#", "#}"))(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=result_idx)
    else:
        assert result.context == context
