from collections.abc import Callable
from pathlib import Path
from typing import final, Any, cast

from ._parser import (
    ParseError,
    ParseContext,
    Expression,
    Comment,
    template,
    TemplateSyntaxConfig,
)


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
            ParseError: If the contents cannot be parsed
        """
        if isinstance(content, Path):
            content = content.read_text()

        if syntax is None:
            syntax = TemplateSyntaxConfig()

        parse = template(syntax)
        result = parse(ParseContext(content))
        if not result.context.at_eof():
            raise ParseError(
                "Excess content at end of file", parser=parse, context=result.context
            )

        self._content = result.result

    def unresolved_identifiers(self) -> set[str]:
        """Provides access to the set of unresolved identifiers in this template"""

        return {e.identifier for e in self._content if isinstance(e, Expression)}

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

        result = Template("")

        def render(identifier: str) -> str:
            v = variables[identifier]
            try:
                return renderers[type(v)](v)
            except KeyError as e:
                raise ValueError(
                    f"No renderer for variable {identifier} of type {type(v)}"
                ) from e

        def append_str(s: str):
            if len(result._content) > 0 and isinstance(result._content[-1], str):
                result._content[-1] += s
            else:
                result._content.append(s)

        for elem in self._content:
            match elem:
                case Expression():
                    if elem.identifier in variables:
                        append_str(render(elem.identifier))
                    else:
                        result._content.append(elem)
                case Comment() if keep_comments:
                    result._content.append(elem)
                case Comment():
                    continue
                case str():
                    append_str(elem)
                case _:  # pyright: ignore[reportUnnecessaryComparison]
                    raise TypeError(f"Unexpected type {type(elem)}")  # pyright: ignore[reportUnreachable]

        return result

    def render(
        self,
        variables: dict[str, Any],
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

        t = self.substitute(variables, keep_comments=False, renderers=renderers)
        if len(t.unresolved_identifiers()) != 0:
            raise ValueError(f"Unresolved identifiers: {t.unresolved_identifiers()}")
        return "".join(cast(list[str], t._content))
