from pathlib import Path
from typing import final, Any, cast

from ._parser import ParseError, ParseContext, Expression, Comment, template


@final
class Template:
    """Represents a templated text file and provides functionality to manipulate it"""

    def __init__(
        self,
        content: str | Path,
        /,
        *,
        open_comment: str = "{#",
        close_comment: str = "#}",
        open_expression: str = "{{",
        close_expression: str = "}}",
    ) -> None:
        """Initialize a templated text file

        Args:
            content: The contents of the template file as string, or a file path to read.
            open_comment: The comment open indicator to use
            close_comment: The comment close indicator to use
            open_expression: The expression open indicator to use
            close_expression: The expression close indicator to use

        Raises:
            ParseError: If the contents cannot be parsed
        """
        if isinstance(content, Path):
            content = content.read_text()

        parse = template(
            open_comment,
            close_comment,
            open_expression,
            close_expression,
        )
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
    ) -> "Template":
        """Substitute variables into this template and return the result

        Args:
            variables: The variables to substitute
            keep_comments: Whether to keep comments in the result

        Returns:
            The resulting template
        """

        result = Template("")

        def append_str(s: str):
            if len(result._content) > 0 and isinstance(result._content[-1], str):
                result._content[-1] += s
            else:
                result._content.append(s)

        for elem in self._content:
            match elem:
                case Expression():
                    if elem.identifier in variables:
                        append_str(str(variables[elem.identifier]))
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

    def render(self, variables: dict[str, Any]) -> str:
        """Render the template to string

        Args:
            variables: The variables to substitute

        Returns:
            The rendered template as string

        Raises:
            ValueError: If some variables in the template remain unresolved after substitution
        """

        t = self.substitute(variables, keep_comments=False)
        if len(t.unresolved_identifiers()) != 0:
            raise ValueError(f"Unresolved identifiers: {t.unresolved_identifiers()}")
        return "".join(cast(list[str], t._content))
