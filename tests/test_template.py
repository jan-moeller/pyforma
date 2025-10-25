from collections.abc import Callable, Sequence, Sized
from contextlib import nullcontext
from pathlib import Path
from typing import Any, ContextManager, final, override

import pytest

from pyforma import Template, TemplateSyntaxConfig
from pyforma._ast import Expression, Comment, IdentifierExpression
from pyforma._ast.environment import (
    IfEnvironment,
    TemplateEnvironment,
    WithEnvironment,
    ForEnvironment,
)
from pyforma._ast.expression import (
    BinOpExpression,
    UnOpExpression,
    ValueExpression,
    IndexExpression,
    CallExpression,
    AttributeExpression,
    ListExpression,
    DictExpression,
)
from pyforma._ast.origin import Origin
from pyforma._parser.template_syntax_config import BlockSyntaxConfig


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
    ],
)
def test_unresolved_identifiers(
    source: str,
    expected: set[str],
):
    assert Template(source).unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "source,sub,keep_comments,renderers,expected",
    [  # pyright: ignore[reportUnknownArgumentType]
        ("", {}, True, None, nullcontext(())),
        ("foo", {}, True, None, nullcontext(("foo",))),
        (
            "foo{{bar}}",
            {},
            True,
            None,
            nullcontext(
                (
                    "foo",
                    IdentifierExpression(
                        origin=Origin(position=(1, 6)), identifier="bar"
                    ),
                )
            ),
        ),
        ("foo{{bar}}", {"bar": ""}, True, None, nullcontext(("foo",))),
        ("{{foo}}bar", {"foo": ""}, True, None, nullcontext(("bar",))),
        (
            "{{a}}{{b}}",
            {"a": 42},
            True,
            None,
            nullcontext(
                (
                    "42",
                    IdentifierExpression(
                        origin=Origin(position=(1, 8)), identifier="b"
                    ),
                )
            ),
        ),
        ("{{foo}}{{bar}}", {"foo": 42, "bar": "y"}, True, None, nullcontext(("42y",))),
        ("{#foo#}{{b}}", {"b": 42}, True, None, nullcontext((Comment("foo"), "42"))),
        ("{#foo#}{{bar}}", {"bar": 42}, False, None, nullcontext(("42",))),
        (
            "{#foo#}{{bar}}",
            {"bar": None},
            False,
            None,
            pytest.raises(
                ValueError,
                match=":1:10: No renderer for value of type <class 'NoneType'>",
            ),
        ),
        ("{{bar}}", {"bar": None}, False, [(type(None), str)], nullcontext(("None",))),
        ("{{bar}}", {"bar": MyString("foo")}, False, None, nullcontext(("foo",))),
        ("{{'bar'}}", {}, False, None, nullcontext(("bar",))),
        ("{{+a}}", {"a": 1}, False, None, nullcontext(("1",))),
        ("{{-a}}", {"a": 1}, False, None, nullcontext(("-1",))),
        ("{{~a}}", {"a": 0b0101}, False, None, nullcontext(("-6",))),
        (
            "{{~a}}",
            {"a": "foo"},
            False,
            None,
            pytest.raises(
                TypeError,
                match=":1:3: Invalid unary operator ~ for value foo of type <class 'str'>",
            ),
        ),
        ("{{not a}}", {"a": True}, False, [(bool, str)], nullcontext(("False",))),
        (
            "{{-a+b}}",
            {"b": 1},
            False,
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
        ("{{a+'b'}}", {"a": "fo"}, False, None, nullcontext(("fob",))),
        ("{{a**b}}", {"a": 3, "b": 2}, False, None, nullcontext(("9",))),
        ("{{a+b}}", {"a": 1, "b": 2}, False, None, nullcontext(("3",))),
        ("{{a-b}}", {"a": 2, "b": 1}, False, None, nullcontext(("1",))),
        ("{{a*b}}", {"a": 2, "b": 1}, False, None, nullcontext(("2",))),
        ("{{a/b}}", {"a": 1, "b": 2}, False, None, nullcontext(("0.5",))),
        ("{{a//b}}", {"a": 1, "b": 2}, False, None, nullcontext(("0",))),
        ("{{a%b}}", {"a": 3, "b": 2}, False, None, nullcontext(("1",))),
        (
            "{{a@b}}",
            {"a": Vec(1, 2), "b": Vec(3, 4)},
            False,
            None,
            nullcontext(("11",)),
        ),
        (
            "{{a@b}}",
            {"a": 42, "b": "foo"},
            False,
            None,
            pytest.raises(
                TypeError,
                match=":1:3: Invalid binary operator @ for values 42 of type <class 'int'> and foo of type <class 'str'>",
            ),
        ),
        ("{{a<<b}}", {"a": 0b1, "b": 1}, False, None, nullcontext(("2",))),
        ("{{a>>b}}", {"a": 0b10, "b": 1}, False, None, nullcontext(("1",))),
        ("{{a&b}}", {"a": 0b10, "b": 1}, False, None, nullcontext(("0",))),
        ("{{a^b}}", {"a": 0b10, "b": 0b11}, False, None, nullcontext(("1",))),
        ("{{a|b}}", {"a": 0b10, "b": 0b01}, False, None, nullcontext(("3",))),
        (
            "{{a in b}}",
            {"a": 1, "b": []},
            False,
            [(bool, str)],
            nullcontext(("False",)),
        ),
        (
            "{{1<a<=b==2}}",
            {"a": 2, "b": 2},
            False,
            [(bool, str)],
            nullcontext(("True",)),
        ),
        (
            "{{1>a>=b!=2}}",
            {"a": 2, "b": 2},
            False,
            [(bool, str)],
            nullcontext(("False",)),
        ),
        (
            "{{a and b}}",
            {"a": True, "b": False},
            False,
            [(bool, str)],
            nullcontext(("False",)),
        ),
        (
            "{{a or b}}",
            {"a": True, "b": False},
            False,
            [(bool, str)],
            nullcontext(("True",)),
        ),
        (
            "{{a not in b}}",
            {"a": 1, "b": []},
            False,
            [(bool, str)],
            nullcontext(("True",)),
        ),
        (
            "{{a+b*c}}",
            {"b": 1},
            False,
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
        ("{{a[0]}}", {"a": [1, 2]}, False, None, nullcontext(("1",))),
        (
            "{{a[0]}}",
            {"a": 42},
            False,
            None,
            pytest.raises(
                TypeError,
                match=":1:3: Invalid indexing expression for value 42 of type <class 'int'> and index 0 of type <class 'int'>",
            ),
        ),
        ("{{a[:]}}", {"a": [1, 2]}, False, [(list, str)], nullcontext(("[1, 2]",))),
        ("{{a[1:]}}", {"a": [1, 2]}, False, [(list, str)], nullcontext(("[2]",))),
        ("{{a[1:-1]}}", {"a": [1, 2, 3]}, False, [(list, str)], nullcontext(("[2]",))),
        (
            "{{a[:-1]}}",
            {"a": [1, 2, 3]},
            False,
            [(list, str)],
            nullcontext(("[1, 2]",)),
        ),
        (
            "{{a[::2]}}",
            {"a": [1, 2, 3]},
            False,
            [(list, str)],
            nullcontext(("[1, 3]",)),
        ),
        (
            "{{a[b]}}",
            {"a": [1]},
            False,
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
            False,
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
            False,
            None,
            nullcontext(("foo",)),
        ),
        (
            "{{a()}}",
            {"a": 42},
            False,
            None,
            pytest.raises(
                TypeError,
                match=r":1:3: Invalid call expression for callee 42 of type <class 'int'> with args \(\) and kwargs \{\}",
            ),
        ),
        (
            "{{a(1)}}",
            {"a": lambda x: x + 2},  # pyright: ignore[reportUnknownLambdaType]
            False,
            None,
            nullcontext(("3",)),
        ),
        (
            "{{a(x=1)}}",
            {"a": lambda x: x + 2},  # pyright: ignore[reportUnknownLambdaType]
            False,
            None,
            nullcontext(("3",)),
        ),
        (
            "{{a()(1,y=2)}}",
            {"a": lambda: lambda x, y: x + y},  # pyright: ignore[reportUnknownLambdaType]
            False,
            None,
            nullcontext(("3",)),
        ),
        (
            '{{a.get("b")}}',
            {},
            False,
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
            False,
            None,
            pytest.raises(
                TypeError,
                match=":1:3: Invalid attribute expression for value 42 of type <class 'int'> and attribute get",
            ),
        ),
        ("{{len(a.keys())}}", {"a": {}, "len": len}, False, None, nullcontext(("0",))),
        ("{%with a=2 %}{{a}}{%endwith%}", {}, False, None, nullcontext(("2",))),
        ("{%with a=2 %}{{a}}{%endwith%}", {"a": 4}, False, None, nullcontext(("2",))),
        ("{%with a=2 %}{{a+b}}{%endwith%}", {"b": 4}, False, None, nullcontext(("6",))),
        (
            "{%with a=2 %}{{a+b}}{%endwith%}",
            {},
            False,
            None,
            nullcontext(
                (
                    TemplateEnvironment(
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
                        )
                    ),
                )
            ),
        ),
        (
            "{%with a=b+2 %}{{a}}{%endwith%}",
            {"b": 40},
            False,
            None,
            nullcontext(("42",)),
        ),
        (
            "{%with a=2; b=40 %}{{a+b}}{%endwith%}",
            {},
            False,
            None,
            nullcontext(("42",)),
        ),
        (
            "{%with a=b;c=d %}{{a+c}}{%endwith%}",
            {"b": 1},
            False,
            None,
            nullcontext(
                (
                    WithEnvironment(
                        variables=(
                            WithEnvironment.Destructuring(
                                identifiers=("c",),
                                expression=IdentifierExpression(
                                    origin=Origin(position=(1, 14)),
                                    identifier="d",
                                ),
                            ),
                        ),
                        content=TemplateEnvironment(
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
                            )
                        ),
                    ),
                )
            ),
        ),
        (
            "{%with a,b=c %}{{a+b}}{%endwith%}",
            {"c": (1, 2)},
            False,
            None,
            nullcontext(("3",)),
        ),
        (
            "{%with a,b=c;d,e=f %}{{a+b+d}}{%endwith%}",
            {"c": (1, 2)},
            False,
            None,
            nullcontext(
                (
                    WithEnvironment(
                        variables=(
                            WithEnvironment.Destructuring(
                                identifiers=("d", "e"),
                                expression=IdentifierExpression(
                                    origin=Origin(position=(1, 18)),
                                    identifier="f",
                                ),
                            ),
                        ),
                        content=TemplateEnvironment(
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
                            )
                        ),
                    ),
                )
            ),
        ),
        (
            "{%with a,b=c %}{{a+b}}{%endwith%}",
            {"c": 42},
            False,
            None,
            pytest.raises(TypeError),
        ),
        (
            "{%with a,b=c %}{{a+b}}{%endwith%}",
            {"c": SizedNotIterable()},
            False,
            None,
            pytest.raises(TypeError),
        ),
        ("{%if a %}1{%endif%}", {"a": True}, False, None, nullcontext(("1",))),
        ("{%if a %}1{%endif%}", {"a": False}, False, None, nullcontext(())),
        ("{%if a %}1{%else%}2{%endif%}", {"a": True}, False, None, nullcontext(("1",))),
        (
            "{%if a %}1{%else%}2{%endif%}",
            {"a": False},
            False,
            None,
            nullcontext(("2",)),
        ),
        (
            "{%if a %}1{%elif b%}2{%else%}3{%endif%}",
            {"a": False, "b": True},
            False,
            None,
            nullcontext(("2",)),
        ),
        (
            "{%if a %}1{%elif b%}2{%else%}3{%endif%}",
            {"a": False},
            False,
            None,
            nullcontext(
                (
                    IfEnvironment(
                        ifs=(
                            (
                                IdentifierExpression(
                                    origin=Origin(position=(1, 18)),
                                    identifier="b",
                                ),
                                TemplateEnvironment(content=("2",)),
                            ),
                        ),
                        else_content=TemplateEnvironment(content=("3",)),
                    ),
                )
            ),
        ),
        (
            "{%if a %}1{%elif b%}2{%else%}3{%endif%}",
            {"b": False},
            False,
            None,
            nullcontext(
                (
                    IfEnvironment(
                        ifs=(
                            (
                                IdentifierExpression(
                                    origin=Origin(position=(1, 6)),
                                    identifier="a",
                                ),
                                TemplateEnvironment(content=("1",)),
                            ),
                        ),
                        else_content=TemplateEnvironment(content=("3",)),
                    ),
                )
            ),
        ),
        (
            "{%if a %}1{%elif b%}2{%else%}3{%endif%}",
            {"b": True},
            False,
            None,
            nullcontext(
                (
                    IfEnvironment(
                        ifs=(
                            (
                                IdentifierExpression(
                                    origin=Origin(position=(1, 6)),
                                    identifier="a",
                                ),
                                TemplateEnvironment(content=("1",)),
                            ),
                            (
                                ValueExpression(
                                    origin=Origin(position=(1, 18)),
                                    value=True,
                                ),
                                TemplateEnvironment(content=("2",)),
                            ),
                        ),
                        else_content=TemplateEnvironment(content=("3",)),
                    ),
                )
            ),
        ),
        (
            "{%for a in b%}{{a}}{%endfor%}",
            {"b": [1, 2, 3]},
            False,
            None,
            nullcontext(("123",)),
        ),
        (
            "{%for a in b%}{{a}}{%endfor%}",
            {"a": 1, "b": [1, 2, 3]},
            False,
            None,
            nullcontext(("123",)),
        ),
        (
            "{%for a , b in c%}{{a}}{%endfor%}",
            {"c": [(1, 2), (3, 4)]},
            False,
            None,
            nullcontext(("13",)),
        ),
        (
            "{%for a, b in c%}{{a}}{%endfor%}",
            {"c": [1, 2]},
            False,
            None,
            pytest.raises(TypeError),
        ),
        (
            "{%for a, b in c%}{{a}}{%endfor%}",
            {"c": [(1, 2, 3), (4, 5, 6)]},
            False,
            None,
            pytest.raises(TypeError),
        ),
        (
            "{%for a in b%}{{a}}{%endfor%}",
            {"a": 1},
            False,
            None,
            nullcontext(
                (
                    ForEnvironment(
                        identifier=("a",),
                        expression=IdentifierExpression(
                            origin=Origin(position=(1, 12)),
                            identifier="b",
                        ),
                        content=TemplateEnvironment(
                            content=(
                                IdentifierExpression(
                                    origin=Origin(position=(1, 17)),
                                    identifier="a",
                                ),
                            )
                        ),
                    ),
                )
            ),
        ),
        (
            "{%literal%}{{a}}{%endliteral%}",
            {},
            False,
            None,
            nullcontext(("{{a}}",)),
        ),
        (
            "{%literal foo%}{%endliteral%}{%endliteral foo%}",
            {},
            False,
            None,
            nullcontext(("{%endliteral%}",)),
        ),
        ("{{ [] }}", {}, False, [(list, str)], nullcontext(("[]",))),
        ("{{ [1] }}", {}, False, [(list, str)], nullcontext(("[1]",))),
        ("{{ [1,2] }}", {}, False, [(list, str)], nullcontext(("[1, 2]",))),
        (
            "{{ [a] }}",
            {},
            False,
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
            False,
            [(list, str)],
            nullcontext(("[42]",)),
        ),
        (
            "{{ {} }}",
            {},
            False,
            [(dict, str)],
            nullcontext(("{}",)),
        ),
        (
            "{{ {1:2} }}",
            {},
            False,
            [(dict, str)],
            nullcontext(("{1: 2}",)),
        ),
        (
            "{{ {1:2, 3:4} }}",
            {},
            False,
            [(dict, str)],
            nullcontext(("{1: 2, 3: 4}",)),
        ),
        (
            "{{ {a:b} }}",
            {},
            False,
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
            False,
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
            False,
            [(dict, str)],
            nullcontext(("{'a': 'b'}",)),
        ),
        (
            "{{t}}",
            {"t": Template("{{a+b}}"), "a": 40, "b": 2},
            False,
            None,
            nullcontext(
                (
                    BinOpExpression(
                        origin=Origin(position=(1, 3)),
                        op="+",
                        lhs=IdentifierExpression(
                            origin=Origin(position=(1, 3)), identifier="a"
                        ),
                        rhs=IdentifierExpression(
                            origin=Origin(position=(1, 5)), identifier="b"
                        ),
                    ),
                )
            ),
        ),
        (
            "{{t}}",
            {"t": Template("{{a+b}}"), "a": 40},
            False,
            None,
            nullcontext(
                (
                    BinOpExpression(
                        origin=Origin(position=(1, 3)),
                        op="+",
                        lhs=IdentifierExpression(
                            origin=Origin(position=(1, 3)), identifier="a"
                        ),
                        rhs=IdentifierExpression(
                            origin=Origin(position=(1, 5)), identifier="b"
                        ),
                    ),
                )
            ),
        ),
        (
            "{{t}}",
            {"t": Template("{{t}}")},
            False,
            None,
            nullcontext(
                (IdentifierExpression(origin=Origin(position=(1, 3)), identifier="t"),)
            ),
        ),
    ],
)
def test_substitute(
    source: str,
    sub: dict[str, Any],
    keep_comments: bool,
    renderers: Sequence[tuple[type, Callable[[Any], str]]] | None,
    expected: ContextManager[tuple[str | Comment | Expression, ...]],
):
    with expected as e:
        t = Template(source)
        assert (
            t.substitute(
                sub,
                keep_comments=keep_comments,
                renderers=renderers,
            )._content.content  # pyright: ignore[reportPrivateUsage]
            == e
        )


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

    assert Template(Path())._content.content == ("mocked",)  # pyright: ignore[reportPrivateUsage]


def test_init_from_invalid():
    with pytest.raises(ValueError):
        _ = Template("foo{{barbau{{")


def test_eq():
    assert Template("{{foo}}") == Template("{{foo}}")
    assert Template("{{foo}}") != Template("{{bar}}")
    assert Template("{{foo}}") != "{{foo}}"


def test_repr():
    assert (
        repr(Template("{{foo}}"))
        == "Template(TemplateEnvironment(content=(IdentifierExpression(origin=Origin(position=(1, 3), source_id=''), identifier='foo'),)))"
    )
