from contextlib import nullcontext
from typing import ContextManager

import pytest

from pyforma._ast import IdentifierExpression, ValueExpression
from pyforma._ast.expression import BinOpExpression, UnOpExpression
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
        (
            "-a",
            nullcontext(UnOpExpression(op="-", operand=IdentifierExpression("a"))),
            2,
        ),
        (
            "--a",
            nullcontext(
                UnOpExpression(
                    op="-",
                    operand=UnOpExpression(op="-", operand=IdentifierExpression("a")),
                )
            ),
            3,
        ),
        (
            'a+"b"',
            nullcontext(
                BinOpExpression(
                    op="+",
                    lhs=IdentifierExpression("a"),
                    rhs=ValueExpression("b"),
                )
            ),
            5,
        ),
        (
            "a * b + c / d",
            nullcontext(
                BinOpExpression(
                    op="+",
                    lhs=BinOpExpression(
                        op="*",
                        lhs=IdentifierExpression("a"),
                        rhs=IdentifierExpression("b"),
                    ),
                    rhs=BinOpExpression(
                        op="/",
                        lhs=IdentifierExpression("c"),
                        rhs=IdentifierExpression("d"),
                    ),
                )
            ),
            13,
        ),
        (
            "a + b * c - d",
            nullcontext(
                BinOpExpression(
                    op="-",
                    lhs=BinOpExpression(
                        op="+",
                        lhs=IdentifierExpression("a"),
                        rhs=BinOpExpression(
                            op="*",
                            lhs=IdentifierExpression("b"),
                            rhs=IdentifierExpression("c"),
                        ),
                    ),
                    rhs=IdentifierExpression("d"),
                )
            ),
            13,
        ),
        (
            "a and b or c in d ** e ^ f & g << h + -i * j | k",
            nullcontext(
                BinOpExpression(
                    op="or",
                    lhs=BinOpExpression(
                        op="and",
                        lhs=IdentifierExpression("a"),
                        rhs=IdentifierExpression("b"),
                    ),
                    rhs=BinOpExpression(
                        op="in",
                        lhs=IdentifierExpression("c"),
                        rhs=BinOpExpression(
                            op="|",
                            lhs=BinOpExpression(
                                op="^",
                                lhs=BinOpExpression(
                                    op="**",
                                    lhs=IdentifierExpression("d"),
                                    rhs=IdentifierExpression("e"),
                                ),
                                rhs=BinOpExpression(
                                    op="&",
                                    lhs=IdentifierExpression("f"),
                                    rhs=BinOpExpression(
                                        op="<<",
                                        lhs=IdentifierExpression("g"),
                                        rhs=BinOpExpression(
                                            op="+",
                                            lhs=IdentifierExpression("h"),
                                            rhs=BinOpExpression(
                                                op="*",
                                                lhs=UnOpExpression(
                                                    op="-",
                                                    operand=IdentifierExpression("i"),
                                                ),
                                                rhs=IdentifierExpression("j"),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                            rhs=IdentifierExpression("k"),
                        ),
                    ),
                )
            ),
            48,
        ),
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
