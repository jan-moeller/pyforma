from collections.abc import Callable, Sequence, Sized
from contextlib import nullcontext
from pathlib import Path
from typing import Any, ContextManager, final, override

import pytest

from pyforma import Template, TemplateSyntaxConfig
from pyforma._ast import (
    Expression,
    IdentifierExpression,
    IfExpression,
    ForExpression,
    WithExpression,
    TemplateExpression,
)
from pyforma._ast.expressions import (
    ValueExpression,
    UnOpExpression,
    BinOpExpression,
    IndexExpression,
    CallExpression,
    AttributeExpression,
    ListExpression,
    DictExpression,
    LambdaExpression,
)
from pyforma._ast.origin import Origin
from pyforma._parser.template_syntax_config import BlockSyntaxConfig
from pyforma._util import join


@final
class Vec:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __matmul__(self, other: "Vec") -> int:
        return self.x * other.x + self.y * other.y


class MyString(str): ...


class SizedNotIterable(Sized):
    @override
    def __len__(self) -> int:
        return 2


@pytest.mark.parametrize(
    "source,expected",
    [  # pyright: ignore[reportUnknownArgumentType]
        ("", set()),
        ("foo", set()),
        ("foo{{bar}}", {"bar"}),
        ("{{foo}}{{bar}}", {"foo", "bar"}),
        ("{#foo#}{{bar}}", {"bar"}),
        ("{{'bar'}}", set()),
        ("{{+-~bar}}", {"bar"}),
        ("{{foo+bar-baz}}", {"foo", "bar", "baz"}),
        ("{{a[b][c:d:e]}}", {"a", "b", "c", "d", "e"}),
        ("{{a.items()}}", {"a"}),
        ("{%with a=2 %}{{a+b}}{%endwith%}", {"b"}),
        (
            "{%if a %}{{b}}{%elif c%}{{d}}{%else%}{{e}}{%endif%}",
            {"a", "b", "c", "d", "e"},
        ),
        ("{%for a in b %}{{a}}{%endfor%}", {"b"}),
        ("{%for a in a %}{{a+b}}{%endfor%}", {"a", "b"}),
        ("{{[]}}", set()),
        ("{{[a, b]}}", {"a", "b"}),
        ("{{{}}}", set()),
        ("{{{a: 1}}}", {"a"}),
        ("{{{1: a}}}", {"a"}),
        ("{{{a: b}}}", {"a", "b"}),
        ("{{lambda: a}}", {"a"}),
        ("{{lambda a: a}}", set[str]()),
        ("{{lambda a: a + b + c}}", {"b", "c"}),
        ("{{if a: b}}", {"a", "b"}),
        ("{{if a: b else: c}}", {"a", "b", "c"}),
        ("{{if a: b elif c: d else: e}}", {"a", "b", "c", "d", "e"}),
        ("{{for a in b: a}}", {"b"}),
        ("{{for a in b: a + c}}", {"b", "c"}),
        ("{{for a in a: a}}", {"a"}),
        ("{{for a, b in c: a + b}}", {"c"}),
        ("{{with a=b: a}}", {"b"}),
        ("{{with a,b=c: a}}", {"c"}),
        ("{{with a, b=b: a}}", {"b"}),
        ("{{with a, b=c; d,e=f: a}}", {"c", "f"}),
    ],
)
def test_unresolved_identifiers(
    source: str,
    expected: set[str],
):
    assert Template(source).unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "source,sub,renderers,expected",
    [  # pyright: ignore[reportUnknownArgumentType]
        (
            "",
            {},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 1)), value=""),)),
        ),
        (
            "foo",
            {},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 1)), value="foo"),)
            ),
        ),
        (
            "foo{{bar}}",
            {},
            None,
            nullcontext(
                (
                    ValueExpression(origin=Origin(position=(1, 1)), value="foo"),
                    IdentifierExpression(
                        origin=Origin(position=(1, 6)), identifier="bar"
                    ),
                )
            ),
        ),
        (
            "foo{{bar}}",
            {"bar": ""},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 1)), value="foo"),)
            ),
        ),
        (
            "{{foo}}bar",
            {"foo": ""},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="bar"),)
            ),
        ),
        (
            "{{a}}{{b}}",
            {"a": 42},
            None,
            nullcontext(
                (
                    ValueExpression(origin=Origin(position=(1, 3)), value="42"),
                    IdentifierExpression(
                        origin=Origin(position=(1, 8)), identifier="b"
                    ),
                )
            ),
        ),
        (
            "{{foo}}{{bar}}",
            {"foo": 42, "bar": "y"},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="42y"),)
            ),
        ),
        (
            "{#foo#}{{b}}",
            {"b": 42},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 10)), value="42"),)
            ),
        ),
        (
            "{#foo#}{{bar}}",
            {"bar": 42},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 10)), value="42"),)
            ),
        ),
        (
            "{#foo#}{{bar}}",
            {"bar": None},
            None,
            pytest.raises(
                ValueError,
                match=":1:10: No renderer for value of type <class 'NoneType'>",
            ),
        ),
        (
            "{{bar}}",
            {"bar": None},
            [(type(None), str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="None"),)
            ),
        ),
        (
            "{{bar}}",
            {"bar": MyString("foo")},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="foo"),)
            ),
        ),
        (
            "{{'bar'}}",
            {},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="bar"),)
            ),
        ),
        (
            "{{+a}}",
            {"a": 1},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="1"),)),
        ),
        (
            "{{-a}}",
            {"a": 1},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="-1"),)),
        ),
        (
            "{{~a}}",
            {"a": 0b0101},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="-6"),)),
        ),
        (
            "{{~a}}",
            {"a": "foo"},
            None,
            pytest.raises(
                TypeError,
                match=":1:3: Invalid unary operator ~ for value foo of type <class 'str'>",
            ),
        ),
        (
            "{{not a}}",
            {"a": True},
            [(bool, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="False"),)
            ),
        ),
        (
            "{{-a+b}}",
            {"b": 1},
            None,
            nullcontext(
                (
                    BinOpExpression(
                        origin=Origin(position=(1, 3)),
                        op="+",
                        lhs=UnOpExpression(
                            origin=Origin(position=(1, 3)),
                            op="-",
                            operand=IdentifierExpression(
                                origin=Origin(position=(1, 4)),
                                identifier="a",
                            ),
                        ),
                        rhs=ValueExpression(origin=Origin(position=(1, 6)), value=1),
                    ),
                )
            ),
        ),
        (
            "{{a+'b'}}",
            {"a": "fo"},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="fob"),)
            ),
        ),
        (
            "{{a**b}}",
            {"a": 3, "b": 2},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="9"),)),
        ),
        (
            "{{a+b}}",
            {"a": 1, "b": 2},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="3"),)),
        ),
        (
            "{{a-b}}",
            {"a": 2, "b": 1},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="1"),)),
        ),
        (
            "{{a*b}}",
            {"a": 2, "b": 1},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="2"),)),
        ),
        (
            "{{a/b}}",
            {"a": 1, "b": 2},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="0.5"),)
            ),
        ),
        (
            "{{a//b}}",
            {"a": 1, "b": 2},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="0"),)),
        ),
        (
            "{{a%b}}",
            {"a": 3, "b": 2},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="1"),)),
        ),
        (
            "{{a@b}}",
            {"a": Vec(1, 2), "b": Vec(3, 4)},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="11"),)),
        ),
        (
            "{{a@b}}",
            {"a": 42, "b": "foo"},
            None,
            pytest.raises(
                TypeError,
                match=":1:3: Invalid binary operator @ for values 42 of type <class 'int'> and foo of type <class 'str'>",
            ),
        ),
        (
            "{{a<<b}}",
            {"a": 0b1, "b": 1},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="2"),)),
        ),
        (
            "{{a>>b}}",
            {"a": 0b10, "b": 1},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="1"),)),
        ),
        (
            "{{a&b}}",
            {"a": 0b10, "b": 1},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="0"),)),
        ),
        (
            "{{a^b}}",
            {"a": 0b10, "b": 0b11},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="1"),)),
        ),
        (
            "{{a|b}}",
            {"a": 0b10, "b": 0b01},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="3"),)),
        ),
        (
            "{{a in b}}",
            {"a": 1, "b": []},
            [(bool, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="False"),)
            ),
        ),
        (
            "{{1<a<=b==2}}",
            {"a": 2, "b": 2},
            [(bool, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="True"),)
            ),
        ),
        (
            "{{1>a>=b!=2}}",
            {"a": 2, "b": 2},
            [(bool, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="False"),)
            ),
        ),
        (
            "{{a and b}}",
            {"a": True, "b": False},
            [(bool, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="False"),)
            ),
        ),
        (
            "{{a or b}}",
            {"a": True, "b": False},
            [(bool, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="True"),)
            ),
        ),
        (
            "{{a not in b}}",
            {"a": 1, "b": []},
            [(bool, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="True"),)
            ),
        ),
        (
            "{{a+b*c}}",
            {"b": 1},
            None,
            nullcontext(
                (
                    BinOpExpression(
                        origin=Origin(position=(1, 3)),
                        op="+",
                        lhs=IdentifierExpression(
                            origin=Origin(position=(1, 3)), identifier="a"
                        ),
                        rhs=BinOpExpression(
                            origin=Origin(position=(1, 5)),
                            op="*",
                            lhs=ValueExpression(
                                origin=Origin(position=(1, 5)), value=1
                            ),
                            rhs=IdentifierExpression(
                                origin=Origin(position=(1, 7)),
                                identifier="c",
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{{a[0]}}",
            {"a": [1, 2]},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="1"),)),
        ),
        (
            "{{a[0]}}",
            {"a": 42},
            None,
            pytest.raises(
                TypeError,
                match=":1:3: Invalid indexing expression for value 42 of type <class 'int'> and index 0 of type <class 'int'>",
            ),
        ),
        (
            "{{a[:]}}",
            {"a": [1, 2]},
            [(list, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="[1, 2]"),)
            ),
        ),
        (
            "{{a[1:]}}",
            {"a": [1, 2]},
            [(list, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="[2]"),)
            ),
        ),
        (
            "{{a[1:-1]}}",
            {"a": [1, 2, 3]},
            [(list, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="[2]"),)
            ),
        ),
        (
            "{{a[:-1]}}",
            {"a": [1, 2, 3]},
            [(list, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="[1, 2]"),)
            ),
        ),
        (
            "{{a[::2]}}",
            {"a": [1, 2, 3]},
            [(list, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="[1, 3]"),)
            ),
        ),
        (
            "{{a[b]}}",
            {"a": [1]},
            None,
            nullcontext(
                (
                    IndexExpression(
                        origin=Origin(position=(1, 3)),
                        expression=ValueExpression(
                            origin=Origin(position=(1, 3)), value=[1]
                        ),
                        index=IdentifierExpression(
                            origin=Origin(position=(1, 5)), identifier="b"
                        ),
                    ),
                )
            ),
        ),
        (
            "{{a[b:]}}",
            {},
            None,
            nullcontext(
                (
                    IndexExpression(
                        origin=Origin(position=(1, 3)),
                        expression=IdentifierExpression(
                            origin=Origin(position=(1, 3)), identifier="a"
                        ),
                        index=CallExpression(
                            origin=Origin(position=(1, 3)),
                            callee=ValueExpression(
                                origin=Origin(position=(1, 3)),
                                value=slice,
                            ),
                            arguments=(
                                IdentifierExpression(
                                    origin=Origin(position=(1, 5)),
                                    identifier="b",
                                ),
                                ValueExpression(
                                    origin=Origin(position=(0, 0)),
                                    value=None,
                                ),
                                ValueExpression(
                                    origin=Origin(position=(0, 0)),
                                    value=None,
                                ),
                            ),
                            kw_arguments=(),
                        ),
                    ),
                )
            ),
        ),
        (
            "{{a()}}",
            {"a": lambda: "foo"},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="foo"),)
            ),
        ),
        (
            "{{a()}}",
            {"a": 42},
            None,
            pytest.raises(
                TypeError,
                match=r":1:3: Invalid call expression for callee 42 of type <class 'int'> with args \(\) and kwargs \{\}",
            ),
        ),
        (
            "{{a(1)}}",
            {"a": lambda x: x + 2},  # pyright: ignore[reportUnknownLambdaType]
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="3"),)),
        ),
        (
            "{{a(x=1)}}",
            {"a": lambda x: x + 2},  # pyright: ignore[reportUnknownLambdaType]
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="3"),)),
        ),
        (
            "{{a()(1,y=2)}}",
            {"a": lambda: lambda x, y: x + y},  # pyright: ignore[reportUnknownLambdaType]
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="3"),)),
        ),
        (
            '{{a.get("b")}}',
            {},
            None,
            nullcontext(
                (
                    CallExpression(
                        origin=Origin(position=(1, 3)),
                        callee=AttributeExpression(
                            origin=Origin(position=(1, 3)),
                            object=IdentifierExpression(
                                origin=Origin(position=(1, 3)),
                                identifier="a",
                            ),
                            attribute="get",
                        ),
                        arguments=(
                            ValueExpression(origin=Origin(position=(1, 9)), value="b"),
                        ),
                        kw_arguments=(),
                    ),
                )
            ),
        ),
        (
            '{{a.get("b")}}',
            {"a": 42},
            None,
            pytest.raises(
                TypeError,
                match=":1:3: Invalid attribute expression for value 42 of type <class 'int'> and attribute get",
            ),
        ),
        (
            "{{len(a.keys())}}",
            {"a": {}, "len": len},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="0"),)),
        ),
        (
            "{%with a=2 %}{{a}}{%endwith%}",
            {},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 16)), value="2"),)),
        ),
        (
            "{%with a=2 %}{{a}}{%endwith%}",
            {"a": 4},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 16)), value="2"),)),
        ),
        (
            "{%with a=2 %}{{a+b}}{%endwith%}",
            {"b": 4},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 16)), value="6"),)),
        ),
        (
            "{%with a=2 %}{{a+b}}{%endwith%}",
            {},
            None,
            nullcontext(
                (
                    TemplateExpression(
                        origin=Origin(position=(1, 1)),
                        content=(
                            BinOpExpression(
                                origin=Origin(position=(1, 16)),
                                op="+",
                                lhs=ValueExpression(
                                    origin=Origin(position=(1, 16)),
                                    value=2,
                                ),
                                rhs=IdentifierExpression(
                                    origin=Origin(position=(1, 18)),
                                    identifier="b",
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{%with a=b+2 %}{{a}}{%endwith%}",
            {"b": 40},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 18)), value="42"),)
            ),
        ),
        (
            "{%with a=2; b=40 %}{{a+b}}{%endwith%}",
            {},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 22)), value="42"),)
            ),
        ),
        (
            "{%with a=b;c=d %}{{a+c}}{%endwith%}",
            {"b": 1},
            None,
            nullcontext(
                (
                    WithExpression(
                        origin=Origin(position=(1, 1)),
                        bindings=(
                            (
                                ("c",),
                                IdentifierExpression(
                                    origin=Origin(position=(1, 14)),
                                    identifier="d",
                                ),
                            ),
                        ),
                        expr=TemplateExpression(
                            origin=Origin(position=(1, 1)),
                            content=(
                                BinOpExpression(
                                    origin=Origin(position=(1, 20)),
                                    op="+",
                                    lhs=ValueExpression(
                                        origin=Origin(position=(1, 20)),
                                        value=1,
                                    ),
                                    rhs=IdentifierExpression(
                                        origin=Origin(position=(1, 22)),
                                        identifier="c",
                                    ),
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{%with a,b=c %}{{a+b}}{%endwith%}",
            {"c": (1, 2)},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 18)), value="3"),)),
        ),
        (
            "{%with a,b=c;d,e=f %}{{a+b+d}}{%endwith%}",
            {"c": (1, 2)},
            None,
            nullcontext(
                (
                    WithExpression(
                        origin=Origin(position=(1, 1)),
                        bindings=(
                            (
                                ("d", "e"),
                                IdentifierExpression(
                                    origin=Origin(position=(1, 18)),
                                    identifier="f",
                                ),
                            ),
                        ),
                        expr=TemplateExpression(
                            origin=Origin(position=(1, 1)),
                            content=(
                                BinOpExpression(
                                    origin=Origin(position=(1, 24)),
                                    op="+",
                                    lhs=ValueExpression(
                                        origin=Origin(position=(1, 24)),
                                        value=3,
                                    ),
                                    rhs=IdentifierExpression(
                                        origin=Origin(position=(1, 28)),
                                        identifier="d",
                                    ),
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{%with a,b=c %}{{a+b}}{%endwith%}",
            {"c": 42},
            None,
            pytest.raises(TypeError),
        ),
        (
            "{%with a,b=c %}{{a+b}}{%endwith%}",
            {"c": SizedNotIterable()},
            None,
            pytest.raises(TypeError),
        ),
        (
            "{%if a %}1{%endif%}",
            {"a": True},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 10)), value="1"),)),
        ),
        (
            "{%if a %}1{%endif%}",
            {"a": False},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 11)), value=""),)),
        ),
        (
            "{%if a %}1{%else%}2{%endif%}",
            {"a": True},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 10)), value="1"),)),
        ),
        (
            "{%if a %}1{%else%}2{%endif%}",
            {"a": False},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 19)), value="2"),)),
        ),
        (
            "{%if a %}1{%elif b%}2{%else%}3{%endif%}",
            {"a": False, "b": True},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 21)), value="2"),)),
        ),
        (
            "{%if a %}1{%elif b%}2{%else%}3{%endif%}",
            {"a": False},
            None,
            nullcontext(
                (
                    IfExpression(
                        origin=Origin(position=(1, 1)),
                        cases=(
                            (
                                IdentifierExpression(
                                    origin=Origin(position=(1, 18)),
                                    identifier="b",
                                ),
                                ValueExpression(
                                    origin=Origin(position=(1, 21)), value="2"
                                ),
                            ),
                            (
                                ValueExpression(
                                    origin=Origin(position=(1, 1)), value=True
                                ),
                                ValueExpression(
                                    origin=Origin(position=(1, 30)), value="3"
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{%if a %}1{%elif b%}2{%else%}3{%endif%}",
            {"b": False},
            None,
            nullcontext(
                (
                    IfExpression(
                        origin=Origin(position=(1, 1)),
                        cases=(
                            (
                                IdentifierExpression(
                                    origin=Origin(position=(1, 6)),
                                    identifier="a",
                                ),
                                ValueExpression(
                                    origin=Origin(position=(1, 10)), value="1"
                                ),
                            ),
                            (
                                ValueExpression(
                                    origin=Origin(position=(1, 1)), value=True
                                ),
                                ValueExpression(
                                    origin=Origin(position=(1, 30)), value="3"
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{%if a %}1{%elif b%}2{%else%}3{%endif%}",
            {"b": True},
            None,
            nullcontext(
                (
                    IfExpression(
                        origin=Origin(position=(1, 1)),
                        cases=(
                            (
                                IdentifierExpression(
                                    origin=Origin(position=(1, 6)),
                                    identifier="a",
                                ),
                                ValueExpression(
                                    origin=Origin(position=(1, 10)), value="1"
                                ),
                            ),
                            (
                                ValueExpression(
                                    origin=Origin(position=(1, 18)),
                                    value=True,
                                ),
                                ValueExpression(
                                    origin=Origin(position=(1, 21)), value="2"
                                ),
                            ),
                            (
                                ValueExpression(
                                    origin=Origin(position=(1, 1)), value=True
                                ),
                                ValueExpression(
                                    origin=Origin(position=(1, 30)), value="3"
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{%for a in b%}{{a}}{%endfor%}",
            {"b": [1, 2, 3]},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 1)), value="123"),)
            ),
        ),
        (
            "{%for a in b%}{{a}}{%endfor%}",
            {"a": 1, "b": [1, 2, 3]},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 1)), value="123"),)
            ),
        ),
        (
            "{%for a , b in c%}{{a}}{%endfor%}",
            {"c": [(1, 2), (3, 4)]},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 1)), value="13"),)),
        ),
        (
            "{%for a, b in c%}{{a}}{%endfor%}",
            {"c": [1, 2]},
            None,
            pytest.raises(TypeError),
        ),
        (
            "{%for a, b in c%}{{a}}{%endfor%}",
            {"c": [(1, 2, 3), (4, 5, 6)]},
            None,
            pytest.raises(TypeError),
        ),
        (
            "{%for a in b%}{{a}}{%endfor%}",
            {"a": 1},
            None,
            nullcontext(
                (
                    CallExpression(
                        origin=Origin(position=(1, 1)),
                        callee=ValueExpression(
                            origin=Origin(position=(1, 1)), value=join
                        ),
                        arguments=(
                            ValueExpression(origin=Origin(position=(1, 1)), value=""),
                            ForExpression(
                                origin=Origin(position=(1, 1)),
                                var_names=("a",),
                                iter_expr=IdentifierExpression(
                                    origin=Origin(position=(1, 12)),
                                    identifier="b",
                                ),
                                expr=TemplateExpression(
                                    origin=Origin(position=(1, 1)),
                                    content=(
                                        IdentifierExpression(
                                            origin=Origin(position=(1, 17)),
                                            identifier="a",
                                        ),
                                    ),
                                ),
                            ),
                        ),
                        kw_arguments=(),
                    ),
                )
            ),
        ),
        (
            "{%literal%}{{a}}{%endliteral%}",
            {},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 1)), value="{{a}}"),)
            ),
        ),
        (
            "{%literal foo%}{%endliteral%}{%endliteral foo%}",
            {},
            None,
            nullcontext(
                (
                    ValueExpression(
                        origin=Origin(position=(1, 1)),
                        value="{%endliteral%}",
                    ),
                )
            ),
        ),
        (
            "{{ [] }}",
            {},
            [(list, str)],
            nullcontext((ValueExpression(origin=Origin(position=(1, 4)), value="[]"),)),
        ),
        (
            "{{ [1] }}",
            {},
            [(list, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 4)), value="[1]"),)
            ),
        ),
        (
            "{{ [1,2] }}",
            {},
            [(list, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 4)), value="[1, 2]"),)
            ),
        ),
        (
            "{{ [a] }}",
            {},
            None,
            nullcontext(
                (
                    ListExpression(
                        origin=Origin(position=(1, 4)),
                        elements=(
                            IdentifierExpression(
                                origin=Origin(position=(1, 5)),
                                identifier="a",
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{{ [a] }}",
            {"a": 42},
            [(list, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 4)), value="[42]"),)
            ),
        ),
        (
            "{{ {} }}",
            {},
            [(dict, str)],
            nullcontext((ValueExpression(origin=Origin(position=(1, 4)), value="{}"),)),
        ),
        (
            "{{ {1:2} }}",
            {},
            [(dict, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 4)), value="{1: 2}"),)
            ),
        ),
        (
            "{{ {1:2, 3:4} }}",
            {},
            [(dict, str)],
            nullcontext(
                (
                    ValueExpression(
                        origin=Origin(position=(1, 4)),
                        value="{1: 2, 3: 4}",
                    ),
                )
            ),
        ),
        (
            "{{ {a:b} }}",
            {},
            [(dict, str)],
            nullcontext(
                (
                    DictExpression(
                        origin=Origin(position=(1, 4)),
                        elements=(
                            (
                                IdentifierExpression(
                                    origin=Origin(position=(1, 5)),
                                    identifier="a",
                                ),
                                IdentifierExpression(
                                    origin=Origin(position=(1, 7)),
                                    identifier="b",
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{{ {a:b} }}",
            {"a": "a"},
            [(dict, str)],
            nullcontext(
                (
                    DictExpression(
                        origin=Origin(position=(1, 4)),
                        elements=(
                            (
                                ValueExpression(
                                    origin=Origin(position=(1, 5)),
                                    value="a",
                                ),
                                IdentifierExpression(
                                    origin=Origin(position=(1, 7)),
                                    identifier="b",
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{{ {a:b} }}",
            {"a": "a", "b": "b"},
            [(dict, str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 4)), value="{'a': 'b'}"),)
            ),
        ),
        (
            "{{t}}",
            {"t": Template("{{a+b}}"), "a": 40, "b": 2},
            None,
            nullcontext(
                (
                    Template(
                        TemplateExpression(
                            origin=Origin(position=(1, 1)),
                            content=(
                                BinOpExpression(
                                    origin=Origin(position=(1, 3)),
                                    op="+",
                                    lhs=IdentifierExpression(
                                        origin=Origin(position=(1, 3)),
                                        identifier="a",
                                    ),
                                    rhs=IdentifierExpression(
                                        origin=Origin(position=(1, 5)),
                                        identifier="b",
                                    ),
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{{t}}",
            {"t": Template("{{a+b}}"), "a": 40},
            None,
            nullcontext(
                (
                    Template(
                        TemplateExpression(
                            origin=Origin(position=(1, 1)),
                            content=(
                                BinOpExpression(
                                    origin=Origin(position=(1, 3)),
                                    op="+",
                                    lhs=IdentifierExpression(
                                        origin=Origin(position=(1, 3)),
                                        identifier="a",
                                    ),
                                    rhs=IdentifierExpression(
                                        origin=Origin(position=(1, 5)),
                                        identifier="b",
                                    ),
                                ),
                            ),
                        )
                    ),
                )
            ),
        ),
        (
            "{{t}}",
            {"t": Template("{{t}}")},
            None,
            nullcontext(
                (
                    Template(
                        TemplateExpression(
                            origin=Origin(position=(1, 1)),
                            content=(
                                IdentifierExpression(
                                    origin=Origin(position=(1, 3)),
                                    identifier="t",
                                ),
                            ),
                        )
                    ),
                )
            ),
        ),
        (
            "{{(lambda: 42)()}}",
            {},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="42"),)),
        ),
        (
            "{{(lambda x: 40 + x)(2)}}",
            {},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="42"),)),
        ),
        (
            "{{(lambda x: 40 + x)(x=2)}}",
            {},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="42"),)),
        ),
        (
            "{{(lambda x, y: x + y)(2, 40)}}",
            {},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="42"),)),
        ),
        (
            "{{(lambda x, y: x + y)(2, y=40)}}",
            {},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="42"),)),
        ),
        (
            "{{(lambda x, y: x + y)(x=2, y=40)}}",
            {},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="42"),)),
        ),
        (
            "{{(lambda x, y: 42)(0, 0)}}",
            {},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="42"),)),
        ),
        ("{{(lambda x, y: x + y)()}}", {}, None, pytest.raises(TypeError)),
        ("{{(lambda x: x)(1, x=2)}}", {}, None, pytest.raises(TypeError)),
        ("{{(lambda x: 1/x)(0)}}", {}, None, pytest.raises(TypeError)),
        (
            "{{(lambda x: x + y)(1)}}",
            {},
            None,
            nullcontext(
                (
                    CallExpression(
                        origin=Origin(position=(1, 3)),
                        callee=LambdaExpression(
                            origin=Origin(position=(1, 4)),
                            parameters=("x",),
                            return_value=BinOpExpression(
                                origin=Origin(position=(1, 14)),
                                op="+",
                                lhs=IdentifierExpression(
                                    origin=Origin(position=(1, 14)),
                                    identifier="x",
                                ),
                                rhs=IdentifierExpression(
                                    origin=Origin(position=(1, 18)),
                                    identifier="y",
                                ),
                            ),
                        ),
                        arguments=(
                            ValueExpression(origin=Origin(position=(1, 21)), value=1),
                        ),
                        kw_arguments=(),
                    ),
                )
            ),
        ),
        (
            "{{(lambda x: x + y)(1)}}",
            {"y": 41},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="42"),)),
        ),
        (
            "{{(lambda x: x)(1)}}",
            {"x": 42},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 3)), value="1"),)),
        ),
        (
            "{{if True: 42}}",
            {},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 12)), value="42"),)
            ),
        ),
        (
            "{{if False: 42}}",
            {},
            [(type(None), str)],
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="None"),)
            ),
        ),
        (
            "{{if a: 42 else: 40}}",
            {"a": True},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 9)), value="42"),)),
        ),
        (
            "{{if a: 42 else: 40}}",
            {"a": False},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 18)), value="40"),)
            ),
        ),
        (
            "{{if a: 42 elif b: 41 else: 40}}",
            {"a": True},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 9)), value="42"),)),
        ),
        (
            "{{if a: 42 elif b: 41 else: 40}}",
            {"a": False},
            None,
            nullcontext(
                (
                    IfExpression(
                        origin=Origin(position=(1, 3)),
                        cases=(
                            (
                                IdentifierExpression(
                                    origin=Origin(position=(1, 17)),
                                    identifier="b",
                                ),
                                ValueExpression(
                                    origin=Origin(position=(1, 20)),
                                    value=41,
                                ),
                            ),
                            (
                                ValueExpression(
                                    origin=Origin(position=(1, 23)),
                                    value=True,
                                ),
                                ValueExpression(
                                    origin=Origin(position=(1, 29)),
                                    value=40,
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{{if a: 42 elif b: 41 else: 40}}",
            {"a": False, "b": True},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 20)), value="41"),)
            ),
        ),
        (
            "{{if a: 42 elif b: 41 else: 40}}",
            {"a": False, "b": False},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 29)), value="40"),)
            ),
        ),
        (
            "{{if a: 42 elif b: 41 else: 40}}",
            {"b": False},
            None,
            nullcontext(
                (
                    IfExpression(
                        origin=Origin(position=(1, 3)),
                        cases=(
                            (
                                IdentifierExpression(
                                    origin=Origin(position=(1, 6)),
                                    identifier="a",
                                ),
                                ValueExpression(
                                    origin=Origin(position=(1, 9)),
                                    value=42,
                                ),
                            ),
                            (
                                ValueExpression(
                                    origin=Origin(position=(1, 23)),
                                    value=True,
                                ),
                                ValueExpression(
                                    origin=Origin(position=(1, 29)),
                                    value=40,
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{{for a in b: a}}",
            {"b": [1, 2]},
            {(list, str)},
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="[1, 2]"),)
            ),
        ),
        (
            "{{for a, b in c: a+b}}",
            {"c": [(1, 2), (3, 4)]},
            {(list, str)},
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="[3, 7]"),)
            ),
        ),
        (
            "{{for a in a: a+2}}",
            {"a": [1, 2]},
            {(list, str)},
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 3)), value="[3, 4]"),)
            ),
        ),
        (
            "{{for a in b: a+2}}",
            {},
            None,
            nullcontext(
                (
                    ForExpression(
                        origin=Origin(position=(1, 3)),
                        var_names=("a",),
                        iter_expr=IdentifierExpression(
                            origin=Origin(position=(1, 12)),
                            identifier="b",
                        ),
                        expr=BinOpExpression(
                            origin=Origin(position=(1, 15)),
                            op="+",
                            lhs=IdentifierExpression(
                                origin=Origin(position=(1, 15)),
                                identifier="a",
                            ),
                            rhs=ValueExpression(
                                origin=Origin(position=(1, 17)), value=2
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{{for a in b: a+c}}",
            {"b": [1, 2]},
            None,
            nullcontext(
                (
                    ListExpression(
                        origin=Origin(position=(1, 3)),
                        elements=(
                            BinOpExpression(
                                origin=Origin(position=(1, 15)),
                                op="+",
                                lhs=ValueExpression(
                                    origin=Origin(position=(1, 15)),
                                    value=1,
                                ),
                                rhs=IdentifierExpression(
                                    origin=Origin(position=(1, 17)),
                                    identifier="c",
                                ),
                            ),
                            BinOpExpression(
                                origin=Origin(position=(1, 15)),
                                op="+",
                                lhs=ValueExpression(
                                    origin=Origin(position=(1, 15)),
                                    value=2,
                                ),
                                rhs=IdentifierExpression(
                                    origin=Origin(position=(1, 17)),
                                    identifier="c",
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
        (
            "{{for a in b: a+c}}",
            {"c": 2},
            None,
            nullcontext(
                (
                    ForExpression(
                        origin=Origin(position=(1, 3)),
                        var_names=("a",),
                        iter_expr=IdentifierExpression(
                            origin=Origin(position=(1, 12)),
                            identifier="b",
                        ),
                        expr=BinOpExpression(
                            origin=Origin(position=(1, 15)),
                            op="+",
                            lhs=IdentifierExpression(
                                origin=Origin(position=(1, 15)),
                                identifier="a",
                            ),
                            rhs=ValueExpression(
                                origin=Origin(position=(1, 17)), value=2
                            ),
                        ),
                    ),
                )
            ),
        ),
        ("{{for a in b: a+2}}", {"b": None}, None, pytest.raises(TypeError)),
        ("{{for a, b in c: a+b}}", {"c": [1, 2, 3]}, None, pytest.raises(TypeError)),
        ("{{for a, b in c: a+b}}", {"c": [[]]}, None, pytest.raises(TypeError)),
        (
            "{{for a, b in c: a+b}}",
            {"c": SizedNotIterable()},
            None,
            pytest.raises(TypeError),
        ),
        (
            "{{with a=c: a}}",
            {"c": 1},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 13)), value="1"),)),
        ),
        (
            "{{with a,b=c: a+b}}",
            {"c": (1, 2)},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 15)), value="3"),)),
        ),
        (
            "{{with a,b=c: a+b+d}}",
            {"c": (1, 2), "d": 3},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 15)), value="6"),)),
        ),
        (
            "{{with a , b = c ; c , d = e: a+c}}",
            {"c": (1, 2), "e": (3, 4)},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 31)), value="4"),)),
        ),
        (
            "{{with a = a + 2: a}}",
            {"a": 40},
            None,
            nullcontext(
                (ValueExpression(origin=Origin(position=(1, 19)), value="42"),)
            ),
        ),
        (
            "{{with a,b = a; c=b: a+b+c}}",
            {"a": (1, 2), "b": 1},
            None,
            nullcontext((ValueExpression(origin=Origin(position=(1, 22)), value="4"),)),
        ),
        (
            "{{with a, b = [a, b]; c=c: a + b + c}}",
            {"a": 40, "c": -2},
            None,
            nullcontext(
                (
                    WithExpression(
                        origin=Origin(position=(1, 3)),
                        bindings=(
                            (
                                ("a", "b"),
                                ListExpression(
                                    origin=Origin(position=(1, 15)),
                                    elements=(
                                        ValueExpression(
                                            origin=Origin(position=(1, 16)),
                                            value=40,
                                        ),
                                        IdentifierExpression(
                                            origin=Origin(position=(1, 19)),
                                            identifier="b",
                                        ),
                                    ),
                                ),
                            ),
                        ),
                        expr=BinOpExpression(
                            origin=Origin(position=(1, 28)),
                            op="+",
                            lhs=BinOpExpression(
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
                            rhs=ValueExpression(
                                origin=Origin(position=(1, 36)),
                                value=-2,
                            ),
                        ),
                    ),
                )
            ),
        ),
        ("{{with: c}}", {}, None, pytest.raises(ValueError)),
        ("{{with a=b; a=c: a}}", {}, None, pytest.raises(ValueError)),
    ],
)
def test_substitute(
    source: str,
    sub: dict[str, Any],
    renderers: Sequence[tuple[type, Callable[[Any], str]]] | None,
    expected: ContextManager[tuple[str | Expression, ...]],
):
    with expected as e:
        t = Template(source)
        assert t.substitute(sub, renderers=renderers).content == e


@pytest.mark.parametrize(
    "source,sub,expected",
    [
        ("", {}, nullcontext("")),
        ("foo", {}, nullcontext("foo")),
        ("foo", None, nullcontext("foo")),
        ("foo{{bar}}", {}, pytest.raises(ValueError)),
        ("foo{{bar}}", {"bar": ""}, nullcontext("foo")),
        ("{{foo}}bar", {"foo": ""}, nullcontext("bar")),
        ("{{foo}}{{bar}}", {"foo": 42}, pytest.raises(ValueError)),
        ("{{foo}}{{bar}}", {"foo": 42, "bar": "y"}, nullcontext("42y")),
        ("{#foo#}{{bar}}", {"bar": 42}, nullcontext("42")),
    ],
)
def test_render(
    source: str,
    sub: dict[str, Any] | None,
    expected: ContextManager[str],
):
    with expected as e:
        assert Template(source).render(sub) == e


def test_init_with_custom_syntax():
    template = Template(
        "foo{{barbau/*comment*/no[[var]]bom#}",
        syntax=TemplateSyntaxConfig(
            comment=BlockSyntaxConfig("/*", "*/"),
            expression=BlockSyntaxConfig("[[", "]]"),
        ),
    )
    assert template.render(variables={"var": "test"}) == "foo{{barbaunotestbom#}"


def test_init_from_path(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(Path, "read_text", lambda self: "mocked")  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]

    assert Template(Path()).content == (
        ValueExpression(origin=Origin(position=(1, 1), source_id="."), value="mocked"),
    )


def test_init_from_invalid():
    with pytest.raises(ValueError):
        _ = Template("foo{{barbau{{")


def test_eq():
    assert Template("{{foo}}") == Template("{{foo}}")
    assert Template("{{foo}}") != Template("{{bar}}")
    assert Template("{{foo}}") != "{{foo}}"


def test_repr():
    assert repr(Template("{{foo}}")) == (
        "Template(origin=Origin(position=(1, 1), source_id=''), "
        "content=(IdentifierExpression(origin=Origin(position=(1, 3), source_id=''), "
        "identifier='foo'),))"
    )
