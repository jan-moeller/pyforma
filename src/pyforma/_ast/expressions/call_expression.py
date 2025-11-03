from dataclasses import dataclass
from typing import cast, override, Any

from .expression import Expression
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class CallExpression(Expression):
    """Call expression"""

    callee: Expression
    arguments: tuple[Expression, ...]
    kw_arguments: tuple[tuple[str, Expression], ...]

    @override
    def identifiers(self) -> set[str]:
        return self.callee.identifiers().union(
            *[arg.identifiers() for arg in self.arguments]
        )

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        callee = self.callee.substitute(variables)
        arguments = tuple(arg.substitute(variables) for arg in self.arguments)
        kw_arguments = tuple(
            (iden, arg.substitute(variables)) for iden, arg in self.kw_arguments
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
