from collections.abc import Callable, Sequence
from pathlib import Path
from typing import final, Any

from pyforma._ast.expressions.template_expression import TemplateExpression

from ._ast import Expression
from ._parser import ParseContext, template, TemplateSyntaxConfig


@final
class Template(TemplateExpression):  # pyright: ignore[reportUninitializedInstanceVariable] # This is a bug in pyright
    """Represents a templated text file and provides functionality to manipulate it"""

    default_renderers = ((str, str), (int, str), (float, str))

    def __init__(
        self,
        content: str | Path | Expression,
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
            OSError: If a path is passed and the file cannot be opened
        """
        match content:
            case TemplateExpression():
                super().__init__(origin=content.origin, content=content.content)
                return
            case Expression():
                super().__init__(origin=content.origin, content=(content,))
                return
            case Path():
                source_id = str(content)
                content = content.read_text()
            case _:
                source_id = ""

        if syntax is None:
            syntax = TemplateSyntaxConfig()

        parse = template(syntax)
        result = parse(ParseContext(source=content, source_id=source_id))

        if result.is_failure:
            exception_message = "Invalid template syntax"
            while result:
                line, column = result.context.line_and_column()
                exception_message += (
                    f"\n  at {line}:{column}: expected {result.failure.expected}"
                )
                result = result.failure.cause
            raise ValueError(exception_message)

        super().__init__(
            origin=result.success.result.origin,
            content=result.success.result.content,
        )

    def substitute(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]] | None = None,
    ) -> "Template":
        """Substitute variables into this template and return the result

        Args:
            variables: The variables to substitute
            renderers: Renderers to use for substitution

        Returns:
            The resulting template

        Raises:
            ValueError: If a variable cannot be substituted due to missing renderer
            TypeError: If variable substitution leads to an unsupported operation, such as an operator not supported for that type
        """

        if renderers is None:
            renderers = Template.default_renderers
        else:
            renderers = tuple(renderers) + Template.default_renderers

        expr = super().simplify(variables, renderers=renderers)
        return Template(expr)

    def render(
        self,
        variables: dict[str, Any] | None = None,
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]] | None = None,
    ) -> str:
        """Render the template to string

        Args:
            variables: The variables to substitute
            renderers: Renderers to use for substitution

        Returns:
            The rendered template as string

        Raises:
            ValueError: If some variables in the template remain unresolved after substitution
            ValueError: If a variable cannot be substituted due to missing renderer
            TypeError: If variable substitution leads to an unsupported operation, such as an operator not supported for that type
        """
        if variables is None:
            variables = {}

        if renderers is None:
            renderers = Template.default_renderers
        else:
            renderers = tuple(renderers) + Template.default_renderers

        value = self.evaluate(variables, renderers=renderers)
        # TemplateExpression.evaluate always returns a str
        assert isinstance(value, str)
        return value
