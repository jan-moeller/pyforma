from contextlib import nullcontext
from typing import ContextManager

import pytest

from pyforma._parser import ParseResult, ParseContext, identifier, ParseError


@pytest.mark.parametrize(
    "source,expected",
    [
        ("", pytest.raises(ParseError)),
        ("foo", nullcontext("foo")),
        ("foo123 0", nullcontext("foo123")),
        ("123", pytest.raises(ParseError)),
    ],
)
def test_identifier(
    source: str,
    expected: ContextManager[str],
):
    with expected as e:
        assert identifier(ParseContext(source)) == ParseResult(
            context=ParseContext(source, index=len(e)),
            result=e,
        )
