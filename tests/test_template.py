from collections.abc import Callable
from contextlib import nullcontext
from pathlib import Path
from typing import Any, ContextManager, final

import pytest

from pyforma import Template, TemplateSyntaxConfig
from pyforma._ast import Expression, Comment, IdentifierExpression
from pyforma._ast.expression import (
    BinOpExpression,
    UnOpExpression,
    ValueExpression,
    IndexExpression,
    CallExpression,
)
from pyforma._parser.parse_error import ParseError
from pyforma._parser.template_syntax_config import BlockSyntaxConfig


@final
class Vec:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __matmul__(self, other: "Vec") -> int:
        return self.x * other.x + self.y * other.y


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
    ],
)
def test_unresolved_identifiers(
    source: str,
    expected: set[str],
):
    assert Template(source).unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "source,sub,keep_comments,renderers,expected",
    [
        ("", {}, True, None, nullcontext([])),
        ("foo", {}, True, None, nullcontext(["foo"])),
        (
            "foo{{bar}}",
            {},
            True,
            None,
            nullcontext(["foo", IdentifierExpression("bar")]),
        ),
        ("foo{{bar}}", {"bar": ""}, True, None, nullcontext(["foo"])),
        ("{{foo}}bar", {"foo": ""}, True, None, nullcontext(["bar"])),
        (
            "{{a}}{{b}}",
            {"a": 42},
            True,
            None,
            nullcontext(["42", IdentifierExpression("b")]),
        ),
        ("{{foo}}{{bar}}", {"foo": 42, "bar": "y"}, True, None, nullcontext(["42y"])),
        ("{#foo#}{{b}}", {"b": 42}, True, None, nullcontext([Comment("foo"), "42"])),
        ("{#foo#}{{bar}}", {"bar": 42}, False, None, nullcontext(["42"])),
        ("{#foo#}{{bar}}", {"bar": None}, False, None, pytest.raises(ValueError)),
        ("{{bar}}", {"bar": None}, False, {type(None): str}, nullcontext(["None"])),
        ("{{'bar'}}", {}, False, None, nullcontext(["bar"])),
        ("{{+a}}", {"a": 1}, False, None, nullcontext(["1"])),
        ("{{-a}}", {"a": 1}, False, None, nullcontext(["-1"])),
        ("{{~a}}", {"a": 0b0101}, False, None, nullcontext(["-6"])),
        ("{{not a}}", {"a": True}, False, {bool: str}, nullcontext(["False"])),
        (
            "{{-a+b}}",
            {"b": 1},
            False,
            None,
            nullcontext(
                [
                    BinOpExpression(
                        op="+",
                        lhs=UnOpExpression(
                            op="-",
                            operand=IdentifierExpression("a"),
                        ),
                        rhs=ValueExpression(1),
                    )
                ]
            ),
        ),
        ("{{a+'b'}}", {"a": "fo"}, False, None, nullcontext(["fob"])),
        ("{{a**b}}", {"a": 3, "b": 2}, False, None, nullcontext(["9"])),
        ("{{a+b}}", {"a": 1, "b": 2}, False, None, nullcontext(["3"])),
        ("{{a-b}}", {"a": 2, "b": 1}, False, None, nullcontext(["1"])),
        ("{{a*b}}", {"a": 2, "b": 1}, False, None, nullcontext(["2"])),
        ("{{a/b}}", {"a": 1, "b": 2}, False, None, nullcontext(["0.5"])),
        ("{{a//b}}", {"a": 1, "b": 2}, False, None, nullcontext(["0"])),
        ("{{a%b}}", {"a": 3, "b": 2}, False, None, nullcontext(["1"])),
        ("{{a@b}}", {"a": Vec(1, 2), "b": Vec(3, 4)}, False, None, nullcontext(["11"])),
        ("{{a<<b}}", {"a": 0b1, "b": 1}, False, None, nullcontext(["2"])),
        ("{{a>>b}}", {"a": 0b10, "b": 1}, False, None, nullcontext(["1"])),
        ("{{a&b}}", {"a": 0b10, "b": 1}, False, None, nullcontext(["0"])),
        ("{{a^b}}", {"a": 0b10, "b": 0b11}, False, None, nullcontext(["1"])),
        ("{{a|b}}", {"a": 0b10, "b": 0b01}, False, None, nullcontext(["3"])),
        ("{{a in b}}", {"a": 1, "b": []}, False, {bool: str}, nullcontext(["False"])),
        (
            "{{1<a<=b==2}}",
            {"a": 2, "b": 2},
            False,
            {bool: str},
            nullcontext(["True"]),
        ),
        (
            "{{1>a>=b!=2}}",
            {"a": 2, "b": 2},
            False,
            {bool: str},
            nullcontext(["False"]),
        ),
        (
            "{{a and b}}",
            {"a": True, "b": False},
            False,
            {bool: str},
            nullcontext(["False"]),
        ),
        (
            "{{a or b}}",
            {"a": True, "b": False},
            False,
            {bool: str},
            nullcontext(["True"]),
        ),
        (
            "{{a not in b}}",
            {"a": 1, "b": []},
            False,
            {bool: str},
            nullcontext(["True"]),
        ),
        (
            "{{a+b*c}}",
            {"b": 1},
            False,
            None,
            nullcontext(
                [
                    BinOpExpression(
                        op="+",
                        lhs=IdentifierExpression("a"),
                        rhs=BinOpExpression(
                            op="*",
                            lhs=ValueExpression(1),
                            rhs=IdentifierExpression("c"),
                        ),
                    )
                ]
            ),
        ),
        ("{{a[0]}}", {"a": [1, 2]}, False, None, nullcontext(["1"])),
        ("{{a[:]}}", {"a": [1, 2]}, False, {list: str}, nullcontext(["[1, 2]"])),
        ("{{a[1:]}}", {"a": [1, 2]}, False, {list: str}, nullcontext(["[2]"])),
        ("{{a[1:-1]}}", {"a": [1, 2, 3]}, False, {list: str}, nullcontext(["[2]"])),
        ("{{a[:-1]}}", {"a": [1, 2, 3]}, False, {list: str}, nullcontext(["[1, 2]"])),
        ("{{a[::2]}}", {"a": [1, 2, 3]}, False, {list: str}, nullcontext(["[1, 3]"])),
        (
            "{{a[b]}}",
            {"a": [1]},
            False,
            None,
            nullcontext(
                [
                    IndexExpression(
                        expression=ValueExpression([1]), index=IdentifierExpression("b")
                    )
                ]
            ),
        ),
        (
            "{{a[b:]}}",
            {},
            False,
            None,
            nullcontext(
                [
                    IndexExpression(
                        expression=IdentifierExpression("a"),
                        index=CallExpression(
                            callee=ValueExpression(slice),
                            arguments=[
                                IdentifierExpression("b"),
                                ValueExpression(None),
                                ValueExpression(None),
                            ],
                        ),
                    )
                ]
            ),
        ),
    ],
)
def test_substitute(
    source: str,
    sub: dict[str, Any],
    keep_comments: bool,
    renderers: dict[type, Callable[[Any], str]] | None,
    expected: ContextManager[list[str | Comment | Expression]],
):
    with expected as e:
        t = Template(source)
        assert (
            t.substitute(
                sub,
                keep_comments=keep_comments,
                renderers=renderers,
            )._content  # pyright: ignore[reportPrivateUsage]
            == e
        )


@pytest.mark.parametrize(
    "source,sub,expected",
    [
        ("", {}, nullcontext("")),
        ("foo", {}, nullcontext("foo")),
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
    sub: dict[str, Any],
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

    assert Template(Path())._content == ["mocked"]  # pyright: ignore[reportPrivateUsage]


def test_init_from_invalid():
    with pytest.raises(ParseError):
        _ = Template("foo{{barbau{{")
