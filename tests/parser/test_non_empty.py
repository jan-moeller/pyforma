from contextlib import nullcontext
from typing import ContextManager

import pytest

from pyforma._parser import (
    ParseError,
    ParseResult,
    ParseContext,
    Parser,
    whitespace,
    non_empty,
)


@pytest.mark.parametrize(
    "source,parser,expected",
    [
        ("", whitespace, pytest.raises(ParseError)),
        ("   ", whitespace, nullcontext("   ")),
        ("foo  bar", whitespace, pytest.raises(ParseError)),
    ],
)
def test_non_empty(
    source: str,
    parser: Parser[str],
    expected: ContextManager[str],
):
    with expected as e:
        assert non_empty(parser)(ParseContext(source)) == ParseResult(
            context=ParseContext(source, index=len(e)),
            result=e,
        )
