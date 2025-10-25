import pytest

from pyforma._ast import IdentifierExpression, ValueExpression
from pyforma._ast.expression import (
    BinOpExpression,
    CallExpression,
    IndexExpression,
    ListExpression,
    UnOpExpression,
    AttributeExpression,
)
from pyforma._parser.parse_context import ParseContext
from pyforma._parser.expression import expression
from pyforma._parser.parse_result import ParseFailure, ParseSuccess


@pytest.mark.parametrize(
    "source,expected,result_idx",
    [
        ("", ParseFailure(expected="expression"), 0),
        ("foo bar", ParseSuccess(IdentifierExpression(identifier="foo")), 3),
        ("'foo ' bar", ParseSuccess(ValueExpression(value="foo ")), 6),
        ('"foo " bar', ParseSuccess(ValueExpression(value="foo ")), 6),
        (r'"foo\nbar"', ParseSuccess(ValueExpression(value="foo\nbar")), 10),
        ("42", ParseSuccess(ValueExpression(value=42)), 2),
        ("1_000", ParseSuccess(ValueExpression(value=1000)), 5),
        ("0xdeadbeef", ParseSuccess(ValueExpression(value=0xDEADBEEF)), 10),
        ("0o1234", ParseSuccess(ValueExpression(value=0o1234)), 6),
        ("0b0010", ParseSuccess(ValueExpression(value=0b0010)), 6),
        ("1.", ParseSuccess(ValueExpression(value=1.0)), 2),
        ("1.234", ParseSuccess(ValueExpression(value=1.234)), 5),
        ("1_000.234_567", ParseSuccess(ValueExpression(value=1000.234567)), 13),
        ("1e3", ParseSuccess(ValueExpression(value=1e3)), 3),
        ("1e-3", ParseSuccess(ValueExpression(value=1e-3)), 4),
        ("True", ParseSuccess(ValueExpression(value=True)), 4),
        ("False", ParseSuccess(ValueExpression(value=False)), 5),
        ("None", ParseSuccess(ValueExpression(value=None)), 4),
        (
            "-a",
            ParseSuccess(
                UnOpExpression(op="-", operand=IdentifierExpression(identifier="a"))
            ),
            2,
        ),
        (
            "--a",
            ParseSuccess(
                UnOpExpression(
                    op="-",
                    operand=UnOpExpression(
                        op="-", operand=IdentifierExpression(identifier="a")
                    ),
                )
            ),
            3,
        ),
        (
            'a+"b"',
            ParseSuccess(
                BinOpExpression(
                    op="+",
                    lhs=IdentifierExpression(identifier="a"),
                    rhs=ValueExpression(value="b"),
                )
            ),
            5,
        ),
        (
            "a * b + c / d",
            ParseSuccess(
                BinOpExpression(
                    op="+",
                    lhs=BinOpExpression(
                        op="*",
                        lhs=IdentifierExpression(identifier="a"),
                        rhs=IdentifierExpression(identifier="b"),
                    ),
                    rhs=BinOpExpression(
                        op="/",
                        lhs=IdentifierExpression(identifier="c"),
                        rhs=IdentifierExpression(identifier="d"),
                    ),
                )
            ),
            13,
        ),
        (
            "a + b * c - d",
            ParseSuccess(
                BinOpExpression(
                    op="-",
                    lhs=BinOpExpression(
                        op="+",
                        lhs=IdentifierExpression(identifier="a"),
                        rhs=BinOpExpression(
                            op="*",
                            lhs=IdentifierExpression(identifier="b"),
                            rhs=IdentifierExpression(identifier="c"),
                        ),
                    ),
                    rhs=IdentifierExpression(identifier="d"),
                )
            ),
            13,
        ),
        (
            "a and b or c in d ** e ^ f & g << h + -i * j | k",
            ParseSuccess(
                BinOpExpression(
                    op="or",
                    lhs=BinOpExpression(
                        op="and",
                        lhs=IdentifierExpression(identifier="a"),
                        rhs=IdentifierExpression(identifier="b"),
                    ),
                    rhs=BinOpExpression(
                        op="in",
                        lhs=IdentifierExpression(identifier="c"),
                        rhs=BinOpExpression(
                            op="|",
                            lhs=BinOpExpression(
                                op="^",
                                lhs=BinOpExpression(
                                    op="**",
                                    lhs=IdentifierExpression(identifier="d"),
                                    rhs=IdentifierExpression(identifier="e"),
                                ),
                                rhs=BinOpExpression(
                                    op="&",
                                    lhs=IdentifierExpression(identifier="f"),
                                    rhs=BinOpExpression(
                                        op="<<",
                                        lhs=IdentifierExpression(identifier="g"),
                                        rhs=BinOpExpression(
                                            op="+",
                                            lhs=IdentifierExpression(identifier="h"),
                                            rhs=BinOpExpression(
                                                op="*",
                                                lhs=UnOpExpression(
                                                    op="-",
                                                    operand=IdentifierExpression(
                                                        identifier="i"
                                                    ),
                                                ),
                                                rhs=IdentifierExpression(
                                                    identifier="j"
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                            rhs=IdentifierExpression(identifier="k"),
                        ),
                    ),
                )
            ),
            48,
        ),
        (
            "(a+b)*c",
            ParseSuccess(
                BinOpExpression(
                    op="*",
                    lhs=BinOpExpression(
                        op="+",
                        lhs=IdentifierExpression(identifier="a"),
                        rhs=IdentifierExpression(identifier="b"),
                    ),
                    rhs=IdentifierExpression(identifier="c"),
                )
            ),
            7,
        ),
        (
            "a<b<=c==d",
            ParseSuccess(
                BinOpExpression(
                    op="and",
                    lhs=BinOpExpression(
                        op="and",
                        lhs=BinOpExpression(
                            op="<",
                            lhs=IdentifierExpression(identifier="a"),
                            rhs=IdentifierExpression(identifier="b"),
                        ),
                        rhs=BinOpExpression(
                            op="<=",
                            lhs=IdentifierExpression(identifier="b"),
                            rhs=IdentifierExpression(identifier="c"),
                        ),
                    ),
                    rhs=BinOpExpression(
                        op="==",
                        lhs=IdentifierExpression(identifier="c"),
                        rhs=IdentifierExpression(identifier="d"),
                    ),
                )
            ),
            9,
        ),
        (
            "a[0]",
            ParseSuccess(
                IndexExpression(
                    expression=IdentifierExpression(identifier="a"),
                    index=ValueExpression(value=0),
                )
            ),
            4,
        ),
        (
            "a[:][b]",
            ParseSuccess(
                IndexExpression(
                    expression=IndexExpression(
                        expression=IdentifierExpression(identifier="a"),
                        index=CallExpression(
                            callee=ValueExpression(value=slice),
                            arguments=(
                                ValueExpression(value=None),
                                ValueExpression(value=None),
                                ValueExpression(value=None),
                            ),
                            kw_arguments=(),
                        ),
                    ),
                    index=IdentifierExpression(identifier="b"),
                )
            ),
            7,
        ),
        (
            "a()",
            ParseSuccess(
                CallExpression(
                    callee=IdentifierExpression(identifier="a"),
                    arguments=(),
                    kw_arguments=(),
                )
            ),
            3,
        ),
        (
            "a(1)",
            ParseSuccess(
                CallExpression(
                    callee=IdentifierExpression(identifier="a"),
                    arguments=(ValueExpression(value=1),),
                    kw_arguments=(),
                )
            ),
            4,
        ),
        (
            "a(1 ,)",
            ParseSuccess(
                CallExpression(
                    callee=IdentifierExpression(identifier="a"),
                    arguments=(ValueExpression(value=1),),
                    kw_arguments=(),
                )
            ),
            6,
        ),
        (
            "a(1, 2)",
            ParseSuccess(
                CallExpression(
                    callee=IdentifierExpression(identifier="a"),
                    arguments=(ValueExpression(value=1), ValueExpression(value=2)),
                    kw_arguments=(),
                )
            ),
            7,
        ),
        (
            "a(1,b=2)",
            ParseSuccess(
                CallExpression(
                    callee=IdentifierExpression(identifier="a"),
                    arguments=(ValueExpression(value=1),),
                    kw_arguments=(("b", ValueExpression(value=2)),),
                )
            ),
            8,
        ),
        (
            "a(b=1)",
            ParseSuccess(
                CallExpression(
                    callee=IdentifierExpression(identifier="a"),
                    arguments=(),
                    kw_arguments=(("b", ValueExpression(value=1)),),
                )
            ),
            6,
        ),
        (
            "a(b=1,)",
            ParseSuccess(
                CallExpression(
                    callee=IdentifierExpression(identifier="a"),
                    arguments=(),
                    kw_arguments=(("b", ValueExpression(value=1)),),
                )
            ),
            7,
        ),
        (
            "a(b=1,c=2)",
            ParseSuccess(
                CallExpression(
                    callee=IdentifierExpression(identifier="a"),
                    arguments=(),
                    kw_arguments=(
                        ("b", ValueExpression(value=1)),
                        ("c", ValueExpression(value=2)),
                    ),
                )
            ),
            10,
        ),
        (
            "a.b",
            ParseSuccess(
                AttributeExpression(
                    object=IdentifierExpression(identifier="a"), attribute="b"
                )
            ),
            3,
        ),
        (
            "a.b.c",
            ParseSuccess(
                AttributeExpression(
                    object=AttributeExpression(
                        object=IdentifierExpression(identifier="a"), attribute="b"
                    ),
                    attribute="c",
                )
            ),
            5,
        ),
        ("[]", ParseSuccess(ListExpression(elements=())), 2),
        (
            "[1, 2]",
            ParseSuccess(
                ListExpression(
                    elements=(ValueExpression(value=1), ValueExpression(value=2))
                )
            ),
            6,
        ),
        (
            "[a]",
            ParseSuccess(
                ListExpression(elements=(IdentifierExpression(identifier="a"),))
            ),
            3,
        ),
    ],
)
def test_expression(
    source: str,
    expected: ParseSuccess | ParseFailure,
    result_idx: int,
):
    context = ParseContext(source)
    result = expression(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=result_idx)
    else:
        assert result.context == context
