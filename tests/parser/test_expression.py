import pytest

from pyforma._ast import IdentifierExpression, ValueExpression
from pyforma._ast.expression import (
    BinOpExpression,
    CallExpression,
    IndexExpression,
    UnOpExpression,
    AttributeExpression,
)
from pyforma._parser.parse_context import ParseContext
from pyforma._parser.expression import expression
from pyforma._parser.parse_result import ParseFailure, ParseSuccess, ParseResult


@pytest.mark.parametrize(
    "source,expected,result_idx",
    [
        ("", ParseFailure(expected="expression"), 0),
        (
            " ",
            ParseFailure(
                expected="expression",
                cause=ParseResult(
                    ParseFailure(
                        expected='binary-expression("or")',
                        cause=ParseResult(
                            ParseFailure(
                                expected='sequence(binary-expression("and"), repetition(sequence(whitespace, alternation("or"), whitespace, binary-expression("and"))))',
                                cause=ParseResult(
                                    ParseFailure(
                                        expected='binary-expression("and")',
                                        cause=ParseResult(
                                            ParseFailure(
                                                expected='sequence(unary-expression("not"), repetition(sequence(whitespace, alternation("and"), whitespace, unary-expression("not"))))',
                                                cause=ParseResult(
                                                    ParseFailure(
                                                        expected='unary-expression("not")',
                                                        cause=ParseResult(
                                                            ParseFailure(
                                                                expected='alternation(sequence(alternation("not"), whitespace, unary-expression("not")), comparison-expression)',
                                                            ),
                                                            context=ParseContext(
                                                                source=" ", index=0
                                                            ),
                                                        ),
                                                    ),
                                                    context=ParseContext(
                                                        source=" ", index=0
                                                    ),
                                                ),
                                            ),
                                            context=ParseContext(source=" ", index=0),
                                        ),
                                    ),
                                    context=ParseContext(source=" ", index=0),
                                ),
                            ),
                            context=ParseContext(source=" ", index=0),
                        ),
                    ),
                    context=ParseContext(source=" ", index=0),
                ),
            ),
            0,
        ),
        (
            '"foo',
            ParseFailure(
                expected="expression",
                cause=ParseResult(
                    ParseFailure(
                        expected='binary-expression("or")',
                        cause=ParseResult(
                            ParseFailure(
                                expected='sequence(binary-expression("and"), repetition(sequence(whitespace, alternation("or"), whitespace, binary-expression("and"))))',
                                cause=ParseResult(
                                    ParseFailure(
                                        expected='binary-expression("and")',
                                        cause=ParseResult(
                                            ParseFailure(
                                                expected='sequence(unary-expression("not"), repetition(sequence(whitespace, alternation("and"), whitespace, unary-expression("not"))))',
                                                cause=ParseResult(
                                                    ParseFailure(
                                                        expected='unary-expression("not")',
                                                        cause=ParseResult(
                                                            ParseFailure(
                                                                expected='alternation(sequence(alternation("not"), whitespace, unary-expression("not")), comparison-expression)',
                                                            ),
                                                            context=ParseContext(
                                                                source='"foo', index=0
                                                            ),
                                                        ),
                                                    ),
                                                    context=ParseContext(
                                                        source='"foo', index=0
                                                    ),
                                                ),
                                            ),
                                            context=ParseContext(
                                                source='"foo', index=0
                                            ),
                                        ),
                                    ),
                                    context=ParseContext(source='"foo', index=0),
                                ),
                            ),
                            context=ParseContext(source='"foo', index=0),
                        ),
                    ),
                    context=ParseContext(source='"foo', index=0),
                ),
            ),
            0,
        ),
        ("foo bar", ParseSuccess(IdentifierExpression("foo")), 3),
        ("'foo ' bar", ParseSuccess(ValueExpression("foo ")), 6),
        ('"foo " bar', ParseSuccess(ValueExpression("foo ")), 6),
        (r'"foo\nbar"', ParseSuccess(ValueExpression("foo\nbar")), 10),
        ("42", ParseSuccess(ValueExpression(42)), 2),
        ("1_000", ParseSuccess(ValueExpression(1000)), 5),
        ("0xdeadbeef", ParseSuccess(ValueExpression(0xDEADBEEF)), 10),
        ("0o1234", ParseSuccess(ValueExpression(0o1234)), 6),
        ("0b0010", ParseSuccess(ValueExpression(0b0010)), 6),
        ("1.", ParseSuccess(ValueExpression(1.0)), 2),
        ("1.234", ParseSuccess(ValueExpression(1.234)), 5),
        ("1_000.234_567", ParseSuccess(ValueExpression(1000.234567)), 13),
        ("1e3", ParseSuccess(ValueExpression(1e3)), 3),
        ("1e-3", ParseSuccess(ValueExpression(1e-3)), 4),
        ("True", ParseSuccess(ValueExpression(True)), 4),
        ("False", ParseSuccess(ValueExpression(False)), 5),
        (
            "-a",
            ParseSuccess(UnOpExpression(op="-", operand=IdentifierExpression("a"))),
            2,
        ),
        (
            "--a",
            ParseSuccess(
                UnOpExpression(
                    op="-",
                    operand=UnOpExpression(op="-", operand=IdentifierExpression("a")),
                )
            ),
            3,
        ),
        (
            'a+"b"',
            ParseSuccess(
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
            ParseSuccess(
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
            ParseSuccess(
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
            ParseSuccess(
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
        (
            "(a+b)*c",
            ParseSuccess(
                BinOpExpression(
                    op="*",
                    lhs=BinOpExpression(
                        op="+",
                        lhs=IdentifierExpression("a"),
                        rhs=IdentifierExpression("b"),
                    ),
                    rhs=IdentifierExpression("c"),
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
                    expression=IdentifierExpression("a"), index=ValueExpression(0)
                )
            ),
            4,
        ),
        (
            "a[:][b]",
            ParseSuccess(
                IndexExpression(
                    expression=IndexExpression(
                        expression=IdentifierExpression("a"),
                        index=CallExpression(
                            callee=ValueExpression(slice),
                            arguments=(
                                ValueExpression(None),
                                ValueExpression(None),
                                ValueExpression(None),
                            ),
                            kw_arguments=(),
                        ),
                    ),
                    index=IdentifierExpression("b"),
                )
            ),
            7,
        ),
        (
            "a()",
            ParseSuccess(
                CallExpression(IdentifierExpression("a"), arguments=(), kw_arguments=())
            ),
            3,
        ),
        (
            "a(1)",
            ParseSuccess(
                CallExpression(
                    IdentifierExpression("a"),
                    arguments=(ValueExpression(1),),
                    kw_arguments=(),
                )
            ),
            4,
        ),
        (
            "a(1 ,)",
            ParseSuccess(
                CallExpression(
                    IdentifierExpression("a"),
                    arguments=(ValueExpression(1),),
                    kw_arguments=(),
                )
            ),
            6,
        ),
        (
            "a(1, 2)",
            ParseSuccess(
                CallExpression(
                    IdentifierExpression("a"),
                    arguments=(ValueExpression(1), ValueExpression(2)),
                    kw_arguments=(),
                )
            ),
            7,
        ),
        (
            "a(1,b=2)",
            ParseSuccess(
                CallExpression(
                    IdentifierExpression("a"),
                    arguments=(ValueExpression(1),),
                    kw_arguments=(("b", ValueExpression(2)),),
                )
            ),
            8,
        ),
        (
            "a(b=1)",
            ParseSuccess(
                CallExpression(
                    IdentifierExpression("a"),
                    arguments=(),
                    kw_arguments=(("b", ValueExpression(1)),),
                )
            ),
            6,
        ),
        (
            "a(b=1,)",
            ParseSuccess(
                CallExpression(
                    IdentifierExpression("a"),
                    arguments=(),
                    kw_arguments=(("b", ValueExpression(1)),),
                )
            ),
            7,
        ),
        (
            "a(b=1,c=2)",
            ParseSuccess(
                CallExpression(
                    IdentifierExpression("a"),
                    arguments=(),
                    kw_arguments=(
                        ("b", ValueExpression(1)),
                        ("c", ValueExpression(2)),
                    ),
                )
            ),
            10,
        ),
        ("a.b", ParseSuccess(AttributeExpression(IdentifierExpression("a"), "b")), 3),
        (
            "a.b.c",
            ParseSuccess(
                AttributeExpression(
                    AttributeExpression(IdentifierExpression("a"), "b"), "c"
                )
            ),
            5,
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
