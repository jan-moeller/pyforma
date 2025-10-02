from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from pyforma import DefaultTemplateContext, Template, TemplateContext


def test_load_template(mocker: MockerFixture) -> None:
    mock_read_text = MagicMock(name="mock_read_text")

    def fake_read_text(self: Path, *args: Any, **kwargs: Any):
        mock_read_text(self, *args, **kwargs)
        return "mocked"

    _ = mocker.patch.object(Path, "read_text", new=fake_read_text)

    base_path = Path("/foo/bar")
    context = TemplateContext(base_path=base_path)
    t1 = context.load_template(Path("baz"))
    t2 = context.load_template(Path("baz"))

    assert t1 is t2
    assert mock_read_text.call_count == 1
    mock_read_text.assert_called_with(base_path / "baz")

    t3 = context.load_template(Path("bam"))

    assert t1 is not t3
    assert mock_read_text.call_count == 2
    mock_read_text.assert_called_with(base_path / "bam")

    t4 = context.load_template(Path("/boom"))
    assert t1 is not t4
    assert mock_read_text.call_count == 3
    mock_read_text.assert_called_with(Path("/boom"))


@pytest.mark.parametrize(
    "variables,template,expected",
    [
        (None, Template(""), set[str]()),
        (None, Template("{{min(1, 2)}}"), set[str]()),
        (None, Template("{{foo}}"), {"foo"}),
        (dict(foo="foo"), Template("{{foo}}"), set[str]()),
    ],
)
def test_unresolved_identifiers(
    variables: dict[str, Any] | None,
    template: Template,
    expected: set[str],
):
    context = DefaultTemplateContext(default_variables=variables)
    assert context.unresolved_identifiers(template) == expected


@pytest.mark.parametrize(
    "variables,template,expected",
    [
        (None, Template(""), Template("")),
        (None, Template("{{min(1, 2)}}"), Template("1")),
        (None, Template("{{foo}}"), Template("{{foo}}")),
        (dict(foo="foo"), Template("{{foo}}"), Template("foo")),
    ],
)
def test_substitute(
    variables: dict[str, Any] | None,
    template: Template,
    expected: Template,
):
    context = DefaultTemplateContext(default_variables=variables)
    assert context.substitute(template) == expected


@pytest.mark.parametrize(
    "variables,template,expected",
    [
        (None, Template(""), ""),
        (None, Template("{{min(1, 2)}}"), "1"),
        (dict(min=max), Template("{{min(1, 2)}}"), "2"),
        (
            dict(foo="barfoo"),
            Template('{% if re.fullmatch(".*foo", foo)%}1{%else%}1{%endif%}'),
            "1",
        ),
        (
            dict(foo="foobar"),
            Template('{% if re.fullmatch(".*foo", foo)%}1{%else%}2{%endif%}'),
            "2",
        ),
    ],
)
def test_render(
    variables: dict[str, Any] | None,
    template: Template,
    expected: str,
):
    context = DefaultTemplateContext(default_variables=variables)
    assert context.render(template) == expected
