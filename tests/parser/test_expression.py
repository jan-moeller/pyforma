from contextlib import nullcontext
from typing import ContextManager

import pytest

from pyforma._ast import IdentifierExpression, ValueExpression
from pyforma._parser import ParseContext, ParseError
from pyforma._parser.expression import expression


@pytest.mark.parametrize(
    "source,expected,result_idx",
    [
        ("", pytest.raises(ParseError), 0),
        (" ", pytest.raises(ParseError), 0),
        ("foo bar", nullcontext(IdentifierExpression("foo")), 3),
        ("'foo ' bar", nullcontext(ValueExpression("foo ")), 6),
        ('"foo " bar', nullcontext(ValueExpression("foo ")), 6),
        ('"foo', pytest.raises(ParseError), 0),
    ],
)
def test_expression(
    source: str,
    expected: ContextManager[str],
    result_idx: int,
):
    with expected as e:
        r = expression(ParseContext(source))
        assert r.result == e
        assert r.context == ParseContext(source, result_idx)
