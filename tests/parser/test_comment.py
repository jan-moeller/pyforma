import pytest

from pyforma._ast import Comment
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
        ("", ParseFailure(expected='"{#"'), 0),
        ("{#foo#}", ParseSuccess(Comment("foo")), 7),
        ("{#foo#}bar", ParseSuccess(Comment("foo")), 7),
        ("{# foo bar #} baz", ParseSuccess(Comment(" foo bar ")), 13),
        ("{# foo {# bar #} #} baz", ParseSuccess(Comment(" foo {# bar #} ")), 19),
        (
            "{# foo",
            ParseFailure(
                expected='comment("{#", "#}")',
                cause=ParseResult.make_failure(
                    context=ParseContext("{# foo", index=6), expected='"#}"'
                ),
            ),
            0,
        ),
        (
            "{# {# #}",
            ParseFailure(
                expected='comment("{#", "#}")',
                cause=ParseResult.make_failure(
                    context=ParseContext("{# {# #}", index=8), expected='"#}"'
                ),
            ),
            0,
        ),
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
