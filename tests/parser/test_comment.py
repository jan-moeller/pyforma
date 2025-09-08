from contextlib import nullcontext
from typing import ContextManager

import pytest

from pyforma._parser import ParseContext, ParseError, comment


@pytest.mark.parametrize(
    "source,expected,result_idx",
    [
        ("", pytest.raises(ParseError), 0),
        ("{#foo#}", nullcontext("foo"), 7),
        ("{#foo#}bar", nullcontext("foo"), 7),
        ("{# foo bar #} baz", nullcontext(" foo bar "), 13),
        ("{# foo {# bar #} #} baz", nullcontext(" foo {# bar #} "), 19),
        ("{# foo", pytest.raises(ParseError), 0),
        ("{# {# #}", pytest.raises(ParseError), 0),
    ],
)
def test_comment(
    source: str,
    expected: ContextManager[str],
    result_idx: int,
):
    with expected as e:
        r = comment("{#", "#}")(ParseContext(source))
        assert r.result == e
        assert r.context == ParseContext(source, result_idx)


def test_invalid_input():
    with pytest.raises(ValueError):
        _ = comment("#", "#")

    with pytest.raises(ValueError):
        _ = comment("#", "")
