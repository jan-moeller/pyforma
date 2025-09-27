from collections.abc import Callable
from pathlib import Path
from typing import final, Any, cast

from ._ast import Expression, Comment, ValueExpression
from ._ast.environment import TemplateEnvironment, Environment
from ._parser import ParseContext, template, TemplateSyntaxConfig


@final
class Template:
    """Represents a templated text file and provides functionality to manipulate it"""

    default_renderers: dict[type, Callable[[Any], str]] = {
        str: str,
        int: str,
        float: str,
    }

    def __init__(
        self,
        content: str | Path,
        /,
        *,
        syntax: TemplateSyntaxConfig | None = None,
    ) -> None:
        """Initialize a templated text file

        Args:
            content: The contents of the template file as string, or a file path to read.
            syntax: Syntax configuration if the default syntax is not applicable.

        Raises:
            ValueError: If the contents cannot be parsed
        """
        if isinstance(content, Path):
            content = content.read_text()

        if syntax is None:
            syntax = TemplateSyntaxConfig()

        parse = template(syntax)
        result = parse(ParseContext(content))

        if result.is_failure:
            # TODO: improve error reporting
            line, column = result.context.line_and_column()
            raise ValueError(f"Invalid template syntax at: {line}:{column}")

        self._content = TemplateEnvironment(result.success.result)

    def unresolved_identifiers(self) -> set[str]:
        """Provides access to the set of unresolved identifiers in this template"""

        return self._content.identifiers()

    def substitute(
        self,
        variables: dict[str, Any],
        *,
        keep_comments: bool = True,
        renderers: dict[type, Callable[[Any], str]] | None = None,
    ) -> "Template":
        """Substitute variables into this template and return the result

        Args:
            variables: The variables to substitute
            keep_comments: Whether to keep comments in the result
            renderers: Renderers to use for substitution

        Returns:
            The resulting template

        Raises:
            ValueError: If a variable cannot be substituted due to missing renderer
        """

        if renderers is None:
            renderers = Template.default_renderers

        subbed = self._content.substitute(variables).content
        content: list[str | Comment | Expression | Environment] = []

        def render(v: str) -> str:
            try:
                return renderers[type(v)](v)
            except KeyError as e:
                raise ValueError(f"No renderer for value of type {type(v)}") from e

        def append_str(s: str):
            if len(content) > 0 and isinstance(content[-1], str):
                content[-1] += s
            else:
                content.append(s)

        def combine_results(
            content: list[str | Comment | Expression | Environment],
            elems: tuple[str | Comment | Expression | Environment, ...],
        ):
            for elem in elems:
                match elem:
                    case ValueExpression():
                        append_str(render(elem.value))
                    case TemplateEnvironment() if len(elem.identifiers()) == 0:
                        combine_results(content, elem.content)
                    case Comment():
                        if keep_comments:
                            content.append(elem)
                    case str():
                        append_str(elem)
                    case _:
                        content.append(elem)

        combine_results(content, subbed)

        result = Template("")
        result._content = TemplateEnvironment(tuple(content))
        return result

    def render(
        self,
        variables: dict[str, Any] | None = None,
        *,
        renderers: dict[type, Callable[[Any], str]] | None = None,
    ) -> str:
        """Render the template to string

        Args:
            variables: The variables to substitute
            renderers: Renderers to use for substitution

        Returns:
            The rendered template as string

        Raises:
            ValueError: If some variables in the template remain unresolved after substitution
        """
        if variables is None:
            variables = {}

        t = self.substitute(variables, keep_comments=False, renderers=renderers)
        if len(t.unresolved_identifiers()) != 0:
            raise ValueError(f"Unresolved identifiers: {t.unresolved_identifiers()}")
        return "".join(cast(tuple[str, ...], t._content.content))
