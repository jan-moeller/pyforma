from contextlib import nullcontext
from typing import ContextManager

import pytest

from pyforma._parser import ParseContext, literal, ParseResult, ParseError


@pytest.mark.parametrize(
    "source,lit,expected",
    [
        ("", "", nullcontext("")),
        ("", "foo", pytest.raises(ParseError)),
        ("foo", "foo", nullcontext("foo")),
        ("foobar", "foo", nullcontext("foo")),
        ("fobar", "foo", pytest.raises(ParseError)),
    ],
)
def test_literal(
    source: str,
    lit: str,
    expected: ContextManager[str],
):
    with expected as e:
        assert literal(lit)(ParseContext(source)) == ParseResult(
            context=ParseContext(source, index=len(e)),
            result=e,
        )
