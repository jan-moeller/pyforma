from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import override, Any

from .expression import Expression
from .expression_impl import ExpressionImpl
from .value_expression import ValueExpression


def render(
    expr: ValueExpression,
    renderers: tuple[tuple[type, Callable[[Any], str]], ...],
) -> str:
    v = expr.value
    for t, r in renderers:
        if isinstance(v, t):
            return r(v)

    raise ValueError(f"{expr.origin}: No renderer for value of type {type(v)}")


@dataclass(frozen=True, kw_only=True)
class TemplateExpression(ExpressionImpl):
    """Template expression"""

    content: tuple[Expression, ...]

    @override
    def unresolved_identifiers(self) -> set[str]:
        return set[str]().union(*[arg.unresolved_identifiers() for arg in self.content])

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        _content: list[Expression] = []

        for e in self.content:
            _expr = e.simplify(variables, renderers=renderers)

            if isinstance(_expr, ValueExpression):
                match _expr.value:
                    case Expression():
                        _content.append(_expr.value)
                        continue
                    case str() as s:
                        pass
                    case _:
                        s = render(_expr, renderers=tuple(renderers))

                if len(_content) > 0:
                    prev = _content[-1]
                    if isinstance(prev, ValueExpression) and isinstance(
                        prev.value, str
                    ):
                        _content[-1] = ValueExpression(
                            origin=prev.origin,
                            value=prev.value + s,
                        )
                        continue

                _content.append(ValueExpression(origin=_expr.origin, value=s))
                continue

            _content.append(_expr)

        if len(_content) == 1 and isinstance(_content[0], ValueExpression):
            return _content[0]

        if len(_content) == 0:
            return ValueExpression(origin=self.origin, value="")

        return TemplateExpression(origin=self.origin, content=tuple(_content))
