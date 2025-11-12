from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import cast, override, Any

from .expression import Expression
from .expression_impl import ExpressionImpl
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class CallExpression(ExpressionImpl):
    """Call expression"""

    callee: Expression
    arguments: tuple[Expression, ...]
    kw_arguments: tuple[tuple[str, Expression], ...]

    @override
    def unresolved_identifiers(self) -> set[str]:
        return self.callee.unresolved_identifiers().union(
            *[arg.unresolved_identifiers() for arg in self.arguments]
        )

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        callee = self.callee.simplify(variables, renderers=renderers)
        arguments = tuple(
            arg.simplify(variables, renderers=renderers) for arg in self.arguments
        )
        kw_arguments = tuple(
            (iden, arg.simplify(variables, renderers=renderers))
            for iden, arg in self.kw_arguments
        )

        callee_ready = isinstance(callee, ValueExpression)
        args_ready = all(isinstance(arg, ValueExpression) for arg in arguments)
        kwargs_ready = all(isinstance(arg, ValueExpression) for _, arg in kw_arguments)

        if callee_ready and args_ready and kwargs_ready:
            args = tuple(cast(ValueExpression, arg).value for arg in arguments)
            kwargs = {
                iden: cast(ValueExpression, arg).value for iden, arg in kw_arguments
            }
            try:
                return ValueExpression(
                    origin=self.origin,
                    value=callee.value(*args, **kwargs),
                )
            except Exception as ex:
                raise TypeError(
                    f"{self.origin}: Invalid call expression for callee {callee.value} of type {type(callee.value)} with args {args} and kwargs {kwargs}"
                ) from ex

        return CallExpression(
            origin=self.origin,
            callee=callee,
            arguments=arguments,
            kw_arguments=kw_arguments,
        )
