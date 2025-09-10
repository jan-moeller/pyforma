from contextlib import nullcontext
from pathlib import Path
from typing import Any, ContextManager

import pytest

from pyforma import Template, TemplateSyntaxConfig
from pyforma._parser import Expression, Comment
from pyforma._parser.parse_error import ParseError
from pyforma._parser.template_syntax_config import BlockSyntaxConfig


@pytest.mark.parametrize(
    "source,expected",
    [  # pyright: ignore[reportUnknownArgumentType]
        ("", set()),
        ("foo", set()),
        ("foo{{bar}}", {"bar"}),
        ("{{foo}}{{bar}}", {"foo", "bar"}),
        ("{#foo#}{{bar}}", {"bar"}),
    ],
)
def test_unresolved_identifiers(
    source: str,
    expected: set[str],
):
    assert Template(source).unresolved_identifiers() == expected


@pytest.mark.parametrize(
    "source,sub,keep_comments,expected",
    [
        ("", {}, True, []),
        ("foo", {}, True, ["foo"]),
        ("foo{{bar}}", {}, True, ["foo", Expression("bar")]),
        ("foo{{bar}}", {"bar": ""}, True, ["foo"]),
        ("{{foo}}bar", {"foo": ""}, True, ["bar"]),
        ("{{foo}}{{bar}}", {"foo": 42}, True, ["42", Expression("bar")]),
        ("{{foo}}{{bar}}", {"foo": 42, "bar": "y"}, True, ["42y"]),
        ("{#foo#}{{bar}}", {"bar": 42}, True, [Comment("foo"), "42"]),
        ("{#foo#}{{bar}}", {"bar": 42}, False, ["42"]),
    ],
)
def test_substitute(
    source: str,
    sub: dict[str, Any],
    keep_comments: bool,
    expected: list[str | Comment | Expression],
):
    assert (
        Template(source).substitute(sub, keep_comments=keep_comments)._content  # pyright: ignore[reportPrivateUsage]
        == expected
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


def test_willfully_borked_template():
    """Make sure we have safety check in place that will raise TypeError in case of unexpected template type"""

    t = Template("")
    t._content.append(42)  # pyright: ignore[reportPrivateUsage,reportArgumentType]
    with pytest.raises(TypeError):
        _ = t.substitute({})
