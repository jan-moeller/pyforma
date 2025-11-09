import pytest

from pyforma._ast import (
    IdentifierExpression,
    ValueExpression,
    UnOpExpression,
    BinOpExpression,
    IndexExpression,
    CallExpression,
    AttributeExpression,
    ListExpression,
    IfExpression,
    ForExpression,
    WithExpression,
)
from pyforma._parser.parse_context import ParseContext
from pyforma._ast.origin import Origin
from pyforma._parser.expression import expression, _none_expr  # pyright: ignore[reportPrivateUsage]
from pyforma._parser.parse_result import ParseFailure, ParseSuccess

_origin = Origin(position=(1, 1))


@pytest.mark.parametrize(
    "source,expected,result_idx",
    [
        ("", ParseFailure(expected="expression"), 0),
        (
            "foo bar",
            ParseSuccess(IdentifierExpression(origin=_origin, identifier="foo")),
            3,
        ),
        ("'foo ' bar", ParseSuccess(ValueExpression(origin=_origin, value="foo ")), 6),
        ('"foo " bar', ParseSuccess(ValueExpression(origin=_origin, value="foo ")), 6),
        (
            r'"foo\nbar"',
            ParseSuccess(ValueExpression(origin=_origin, value="foo\nbar")),
            10,
        ),
        ("42", ParseSuccess(ValueExpression(origin=_origin, value=42)), 2),
        ("1_000", ParseSuccess(ValueExpression(origin=_origin, value=1000)), 5),
        (
            "0xdeadbeef",
            ParseSuccess(ValueExpression(origin=_origin, value=0xDEADBEEF)),
            10,
        ),
        ("0o1234", ParseSuccess(ValueExpression(origin=_origin, value=0o1234)), 6),
        ("0b0010", ParseSuccess(ValueExpression(origin=_origin, value=0b0010)), 6),
        ("1.", ParseSuccess(ValueExpression(origin=_origin, value=1.0)), 2),
        ("1.234", ParseSuccess(ValueExpression(origin=_origin, value=1.234)), 5),
        (
            "1_000.234_567",
            ParseSuccess(ValueExpression(origin=_origin, value=1000.234567)),
            13,
        ),
        ("1e3", ParseSuccess(ValueExpression(origin=_origin, value=1e3)), 3),
        ("1e-3", ParseSuccess(ValueExpression(origin=_origin, value=1e-3)), 4),
        ("True", ParseSuccess(ValueExpression(origin=_origin, value=True)), 4),
        ("False", ParseSuccess(ValueExpression(origin=_origin, value=False)), 5),
        ("None", ParseSuccess(ValueExpression(origin=_origin, value=None)), 4),
        (
            "-a",
            ParseSuccess(
                UnOpExpression(
                    origin=_origin,
                    op="-",
                    operand=IdentifierExpression(
                        origin=Origin(position=(1, 2)), identifier="a"
                    ),
                )
            ),
            2,
        ),
        (
            "--a",
            ParseSuccess(
                UnOpExpression(
                    origin=_origin,
                    op="-",
                    operand=UnOpExpression(
                        origin=Origin(position=(1, 2)),
                        op="-",
                        operand=IdentifierExpression(
                            origin=Origin(position=(1, 3)),
                            identifier="a",
                        ),
                    ),
                )
            ),
            3,
        ),
        (
            'a+"b"',
            ParseSuccess(
                BinOpExpression(
                    origin=_origin,
                    op="+",
                    lhs=IdentifierExpression(origin=_origin, identifier="a"),
                    rhs=ValueExpression(origin=Origin(position=(1, 3)), value="b"),
                )
            ),
            5,
        ),
        (
            "a * b + c / d",
            ParseSuccess(
                BinOpExpression(
                    origin=_origin,
                    op="+",
                    lhs=BinOpExpression(
                        origin=_origin,
                        op="*",
                        lhs=IdentifierExpression(origin=_origin, identifier="a"),
                        rhs=IdentifierExpression(
                            origin=Origin(position=(1, 5)), identifier="b"
                        ),
                    ),
                    rhs=BinOpExpression(
                        origin=Origin(position=(1, 9)),
                        op="/",
                        lhs=IdentifierExpression(
                            origin=Origin(position=(1, 9)), identifier="c"
                        ),
                        rhs=IdentifierExpression(
                            origin=Origin(position=(1, 13)), identifier="d"
                        ),
                    ),
                )
            ),
            13,
        ),
        (
            "a + b * c - d",
            ParseSuccess(
                BinOpExpression(
                    origin=_origin,
                    op="-",
                    lhs=BinOpExpression(
                        origin=_origin,
                        op="+",
                        lhs=IdentifierExpression(origin=_origin, identifier="a"),
                        rhs=BinOpExpression(
                            origin=Origin(position=(1, 5)),
                            op="*",
                            lhs=IdentifierExpression(
                                origin=Origin(position=(1, 5)),
                                identifier="b",
                            ),
                            rhs=IdentifierExpression(
                                origin=Origin(position=(1, 9)),
                                identifier="c",
                            ),
                        ),
                    ),
                    rhs=IdentifierExpression(
                        origin=Origin(position=(1, 13)),
                        identifier="d",
                    ),
                )
            ),
            13,
        ),
        (
            "a and b or c in d ** e ^ f & g << h + -i * j | k",
            ParseSuccess(
                result=BinOpExpression(
                    origin=_origin,
                    op="or",
                    lhs=BinOpExpression(
                        origin=_origin,
                        op="and",
                        lhs=IdentifierExpression(origin=_origin, identifier="a"),
                        rhs=IdentifierExpression(
                            origin=Origin(position=(1, 7)), identifier="b"
                        ),
                    ),
                    rhs=BinOpExpression(
                        origin=Origin(position=(1, 12)),
                        op="in",
                        lhs=IdentifierExpression(
                            origin=Origin(position=(1, 12)),
                            identifier="c",
                        ),
                        rhs=BinOpExpression(
                            origin=Origin(position=(1, 17)),
                            op="|",
                            lhs=BinOpExpression(
                                origin=Origin(position=(1, 17)),
                                op="^",
                                lhs=BinOpExpression(
                                    origin=Origin(position=(1, 17)),
                                    op="**",
                                    lhs=IdentifierExpression(
                                        origin=Origin(position=(1, 17)),
                                        identifier="d",
                                    ),
                                    rhs=IdentifierExpression(
                                        origin=Origin(position=(1, 22)),
                                        identifier="e",
                                    ),
                                ),
                                rhs=BinOpExpression(
                                    origin=Origin(position=(1, 26)),
                                    op="&",
                                    lhs=IdentifierExpression(
                                        origin=Origin(position=(1, 26)),
                                        identifier="f",
                                    ),
                                    rhs=BinOpExpression(
                                        origin=Origin(position=(1, 30)),
                                        op="<<",
                                        lhs=IdentifierExpression(
                                            origin=Origin(position=(1, 30)),
                                            identifier="g",
                                        ),
                                        rhs=BinOpExpression(
                                            origin=Origin(position=(1, 35)),
                                            op="+",
                                            lhs=IdentifierExpression(
                                                origin=Origin(position=(1, 35)),
                                                identifier="h",
                                            ),
                                            rhs=BinOpExpression(
                                                origin=Origin(position=(1, 39)),
                                                op="*",
                                                lhs=UnOpExpression(
                                                    origin=Origin(position=(1, 39)),
                                                    op="-",
                                                    operand=IdentifierExpression(
                                                        origin=Origin(
                                                            position=(1, 40),
                                                            source_id="",
                                                        ),
                                                        identifier="i",
                                                    ),
                                                ),
                                                rhs=IdentifierExpression(
                                                    origin=Origin(position=(1, 44)),
                                                    identifier="j",
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                            rhs=IdentifierExpression(
                                origin=Origin(position=(1, 48)),
                                identifier="k",
                            ),
                        ),
                    ),
                )
            ),
            48,
        ),
        (
            "(a+b)*c",
            ParseSuccess(
                result=BinOpExpression(
                    origin=_origin,
                    op="*",
                    lhs=BinOpExpression(
                        origin=Origin(position=(1, 2)),
                        op="+",
                        lhs=IdentifierExpression(
                            origin=Origin(position=(1, 2)), identifier="a"
                        ),
                        rhs=IdentifierExpression(
                            origin=Origin(position=(1, 4)), identifier="b"
                        ),
                    ),
                    rhs=IdentifierExpression(
                        origin=Origin(position=(1, 7)), identifier="c"
                    ),
                )
            ),
            7,
        ),
        (
            "a<b<=c==d",
            ParseSuccess(
                result=BinOpExpression(
                    origin=_origin,
                    op="and",
                    lhs=BinOpExpression(
                        origin=_origin,
                        op="and",
                        lhs=BinOpExpression(
                            origin=_origin,
                            op="<",
                            lhs=IdentifierExpression(
                                origin=_origin,
                                identifier="a",
                            ),
                            rhs=IdentifierExpression(
                                origin=Origin(position=(1, 3)),
                                identifier="b",
                            ),
                        ),
                        rhs=BinOpExpression(
                            origin=_origin,
                            op="<=",
                            lhs=IdentifierExpression(
                                origin=Origin(position=(1, 3)),
                                identifier="b",
                            ),
                            rhs=IdentifierExpression(
                                origin=Origin(position=(1, 6)),
                                identifier="c",
                            ),
                        ),
                    ),
                    rhs=BinOpExpression(
                        origin=_origin,
                        op="==",
                        lhs=IdentifierExpression(
                            origin=Origin(position=(1, 6)), identifier="c"
                        ),
                        rhs=IdentifierExpression(
                            origin=Origin(position=(1, 9)), identifier="d"
                        ),
                    ),
                )
            ),
            9,
        ),
        (
            "a[0]",
            ParseSuccess(
                result=IndexExpression(
                    origin=_origin,
                    expression=IdentifierExpression(origin=_origin, identifier="a"),
                    index=ValueExpression(origin=Origin(position=(1, 3)), value=0),
                )
            ),
            4,
        ),
        (
            "a[:][b]",
            ParseSuccess(
                result=IndexExpression(
                    origin=_origin,
                    expression=IndexExpression(
                        origin=_origin,
                        expression=IdentifierExpression(origin=_origin, identifier="a"),
                        index=CallExpression(
                            origin=_origin,
                            callee=ValueExpression(
                                origin=_origin,
                                value=slice,
                            ),
                            arguments=(
                                _none_expr,
                                _none_expr,
                                _none_expr,
                            ),
                            kw_arguments=(),
                        ),
                    ),
                    index=IdentifierExpression(
                        origin=Origin(position=(1, 6)), identifier="b"
                    ),
                )
            ),
            7,
        ),
        (
            "a()",
            ParseSuccess(
                result=CallExpression(
                    origin=_origin,
                    callee=IdentifierExpression(origin=_origin, identifier="a"),
                    arguments=(),
                    kw_arguments=(),
                )
            ),
            3,
        ),
        (
            "a(1)",
            ParseSuccess(
                result=CallExpression(
                    origin=_origin,
                    callee=IdentifierExpression(origin=_origin, identifier="a"),
                    arguments=(
                        ValueExpression(origin=Origin(position=(1, 3)), value=1),
                    ),
                    kw_arguments=(),
                )
            ),
            4,
        ),
        (
            "a(1 ,)",
            ParseSuccess(
                result=CallExpression(
                    origin=_origin,
                    callee=IdentifierExpression(origin=_origin, identifier="a"),
                    arguments=(
                        ValueExpression(origin=Origin(position=(1, 3)), value=1),
                    ),
                    kw_arguments=(),
                )
            ),
            6,
        ),
        (
            "a(1, 2)",
            ParseSuccess(
                result=CallExpression(
                    origin=_origin,
                    callee=IdentifierExpression(origin=_origin, identifier="a"),
                    arguments=(
                        ValueExpression(origin=Origin(position=(1, 3)), value=1),
                        ValueExpression(origin=Origin(position=(1, 6)), value=2),
                    ),
                    kw_arguments=(),
                )
            ),
            7,
        ),
        (
            "a(1,b=2)",
            ParseSuccess(
                result=CallExpression(
                    origin=_origin,
                    callee=IdentifierExpression(origin=_origin, identifier="a"),
                    arguments=(
                        ValueExpression(origin=Origin(position=(1, 3)), value=1),
                    ),
                    kw_arguments=(
                        (
                            "b",
                            ValueExpression(origin=Origin(position=(1, 7)), value=2),
                        ),
                    ),
                )
            ),
            8,
        ),
        (
            "a(b=1)",
            ParseSuccess(
                result=CallExpression(
                    origin=_origin,
                    callee=IdentifierExpression(origin=_origin, identifier="a"),
                    arguments=(),
                    kw_arguments=(
                        (
                            "b",
                            ValueExpression(origin=Origin(position=(1, 5)), value=1),
                        ),
                    ),
                )
            ),
            6,
        ),
        (
            "a(b=1,)",
            ParseSuccess(
                result=CallExpression(
                    origin=_origin,
                    callee=IdentifierExpression(origin=_origin, identifier="a"),
                    arguments=(),
                    kw_arguments=(
                        (
                            "b",
                            ValueExpression(origin=Origin(position=(1, 5)), value=1),
                        ),
                    ),
                )
            ),
            7,
        ),
        (
            "a(b=1,c=2)",
            ParseSuccess(
                result=CallExpression(
                    origin=_origin,
                    callee=IdentifierExpression(origin=_origin, identifier="a"),
                    arguments=(),
                    kw_arguments=(
                        (
                            "b",
                            ValueExpression(origin=Origin(position=(1, 5)), value=1),
                        ),
                        (
                            "c",
                            ValueExpression(origin=Origin(position=(1, 9)), value=2),
                        ),
                    ),
                )
            ),
            10,
        ),
        (
            "a.b",
            ParseSuccess(
                AttributeExpression(
                    origin=_origin,
                    object=IdentifierExpression(origin=_origin, identifier="a"),
                    attribute="b",
                )
            ),
            3,
        ),
        (
            "a.b.c",
            ParseSuccess(
                AttributeExpression(
                    origin=_origin,
                    object=AttributeExpression(
                        origin=_origin,
                        object=IdentifierExpression(origin=_origin, identifier="a"),
                        attribute="b",
                    ),
                    attribute="c",
                )
            ),
            5,
        ),
        ("[]", ParseSuccess(ListExpression(origin=_origin, elements=())), 2),
        (
            "[1, 2]",
            ParseSuccess(
                result=ListExpression(
                    origin=_origin,
                    elements=(
                        ValueExpression(origin=Origin(position=(1, 2)), value=1),
                        ValueExpression(origin=Origin(position=(1, 5)), value=2),
                    ),
                )
            ),
            6,
        ),
        (
            "[a]",
            ParseSuccess(
                result=ListExpression(
                    origin=_origin,
                    elements=(
                        IdentifierExpression(
                            origin=Origin(position=(1, 2)), identifier="a"
                        ),
                    ),
                )
            ),
            3,
        ),
        (
            "if True: 42",
            ParseSuccess(
                result=IfExpression(
                    origin=_origin,
                    cases=(
                        (
                            ValueExpression(origin=Origin(position=(1, 4)), value=True),
                            ValueExpression(origin=Origin(position=(1, 10)), value=42),
                        ),
                    ),
                )
            ),
            11,
        ),
        (
            "if a: 40 + b else: 0",
            ParseSuccess(
                result=IfExpression(
                    origin=_origin,
                    cases=(
                        (
                            IdentifierExpression(
                                origin=Origin(position=(1, 4)),
                                identifier="a",
                            ),
                            BinOpExpression(
                                origin=Origin(position=(1, 7)),
                                op="+",
                                lhs=ValueExpression(
                                    origin=Origin(position=(1, 7)),
                                    value=40,
                                ),
                                rhs=IdentifierExpression(
                                    origin=Origin(position=(1, 12)),
                                    identifier="b",
                                ),
                            ),
                        ),
                        (
                            ValueExpression(
                                origin=Origin(position=(1, 14)),
                                value=True,
                            ),
                            ValueExpression(origin=Origin(position=(1, 20)), value=0),
                        ),
                    ),
                )
            ),
            20,
        ),
        (
            "if a: b elif c : d else: e",
            ParseSuccess(
                result=IfExpression(
                    origin=_origin,
                    cases=(
                        (
                            IdentifierExpression(
                                origin=Origin(position=(1, 4)),
                                identifier="a",
                            ),
                            IdentifierExpression(
                                origin=Origin(position=(1, 7)),
                                identifier="b",
                            ),
                        ),
                        (
                            IdentifierExpression(
                                origin=Origin(position=(1, 14)),
                                identifier="c",
                            ),
                            IdentifierExpression(
                                origin=Origin(position=(1, 18)),
                                identifier="d",
                            ),
                        ),
                        (
                            ValueExpression(
                                origin=Origin(position=(1, 20)),
                                value=True,
                            ),
                            IdentifierExpression(
                                origin=Origin(position=(1, 26)),
                                identifier="e",
                            ),
                        ),
                    ),
                )
            ),
            26,
        ),
        (
            "for a in b : a",
            ParseSuccess(
                result=ForExpression(
                    origin=_origin,
                    var_names=("a",),
                    iter_expr=IdentifierExpression(
                        origin=Origin(position=(1, 10)), identifier="b"
                    ),
                    expr=IdentifierExpression(
                        origin=Origin(position=(1, 14)), identifier="a"
                    ),
                )
            ),
            14,
        ),
        (
            "for a, b in c : a + b",
            ParseSuccess(
                result=ForExpression(
                    origin=_origin,
                    var_names=("a", "b"),
                    iter_expr=IdentifierExpression(
                        origin=Origin(position=(1, 13)), identifier="c"
                    ),
                    expr=BinOpExpression(
                        origin=Origin(position=(1, 17)),
                        op="+",
                        lhs=IdentifierExpression(
                            origin=Origin(position=(1, 17)),
                            identifier="a",
                        ),
                        rhs=IdentifierExpression(
                            origin=Origin(position=(1, 21)),
                            identifier="b",
                        ),
                    ),
                )
            ),
            21,
        ),
        (
            "for a,b in [[1, 2],[3,4]]: a + b",
            ParseSuccess(
                result=ForExpression(
                    origin=_origin,
                    var_names=("a", "b"),
                    iter_expr=ListExpression(
                        origin=Origin(position=(1, 12)),
                        elements=(
                            ListExpression(
                                origin=Origin(position=(1, 13)),
                                elements=(
                                    ValueExpression(
                                        origin=Origin(position=(1, 14)),
                                        value=1,
                                    ),
                                    ValueExpression(
                                        origin=Origin(position=(1, 17)),
                                        value=2,
                                    ),
                                ),
                            ),
                            ListExpression(
                                origin=Origin(position=(1, 20)),
                                elements=(
                                    ValueExpression(
                                        origin=Origin(position=(1, 21)),
                                        value=3,
                                    ),
                                    ValueExpression(
                                        origin=Origin(position=(1, 23)),
                                        value=4,
                                    ),
                                ),
                            ),
                        ),
                    ),
                    expr=BinOpExpression(
                        origin=Origin(position=(1, 28)),
                        op="+",
                        lhs=IdentifierExpression(
                            origin=Origin(position=(1, 28)),
                            identifier="a",
                        ),
                        rhs=IdentifierExpression(
                            origin=Origin(position=(1, 32)),
                            identifier="b",
                        ),
                    ),
                )
            ),
            32,
        ),
        (
            "with a=40: a+2",
            ParseSuccess(
                result=WithExpression(
                    origin=_origin,
                    bindings=(
                        (
                            ("a",),
                            ValueExpression(origin=Origin(position=(1, 8)), value=40),
                        ),
                    ),
                    expr=BinOpExpression(
                        origin=Origin(position=(1, 12)),
                        op="+",
                        lhs=IdentifierExpression(
                            origin=Origin(position=(1, 12)),
                            identifier="a",
                        ),
                        rhs=ValueExpression(origin=Origin(position=(1, 14)), value=2),
                    ),
                )
            ),
            14,
        ),
        (
            "with a, b=c: a+b",
            ParseSuccess(
                result=WithExpression(
                    origin=_origin,
                    bindings=(
                        (
                            ("a", "b"),
                            IdentifierExpression(
                                origin=Origin(position=(1, 11)),
                                identifier="c",
                            ),
                        ),
                    ),
                    expr=BinOpExpression(
                        origin=Origin(position=(1, 14)),
                        op="+",
                        lhs=IdentifierExpression(
                            origin=Origin(position=(1, 14)),
                            identifier="a",
                        ),
                        rhs=IdentifierExpression(
                            origin=Origin(position=(1, 16)),
                            identifier="b",
                        ),
                    ),
                )
            ),
            16,
        ),
        (
            "with a, b=c; d,e = f: a+b+d+e",
            ParseSuccess(
                result=WithExpression(
                    origin=_origin,
                    bindings=(
                        (
                            ("a", "b"),
                            IdentifierExpression(
                                origin=Origin(position=(1, 11)),
                                identifier="c",
                            ),
                        ),
                        (
                            ("d", "e"),
                            IdentifierExpression(
                                origin=Origin(position=(1, 20)),
                                identifier="f",
                            ),
                        ),
                    ),
                    expr=BinOpExpression(
                        origin=Origin(position=(1, 23)),
                        op="+",
                        lhs=BinOpExpression(
                            origin=Origin(position=(1, 23)),
                            op="+",
                            lhs=BinOpExpression(
                                origin=Origin(position=(1, 23)),
                                op="+",
                                lhs=IdentifierExpression(
                                    origin=Origin(position=(1, 23)),
                                    identifier="a",
                                ),
                                rhs=IdentifierExpression(
                                    origin=Origin(position=(1, 25)),
                                    identifier="b",
                                ),
                            ),
                            rhs=IdentifierExpression(
                                origin=Origin(position=(1, 27)),
                                identifier="d",
                            ),
                        ),
                        rhs=IdentifierExpression(
                            origin=Origin(position=(1, 29)),
                            identifier="e",
                        ),
                    ),
                )
            ),
            29,
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
