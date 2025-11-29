from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import override, Any

from .expression import Expression
from .expression_impl import ExpressionImpl
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class LambdaExpression(ExpressionImpl):
    """Lambda expression"""

    parameters: tuple[str, ...]
    return_value: Expression

    @override
    def unresolved_identifiers(self) -> set[str]:
        return self.return_value.unresolved_identifiers() - set(self.parameters)

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        value = self.return_value.simplify(
            {k: v for k, v in variables.items() if k not in self.parameters},
            renderers=renderers,
        )

        if value.unresolved_identifiers().issubset(self.parameters):

            def fn(*args: Any, **kwargs: Any) -> Any:
                msg = f"{self.origin}: Invalid call of lambda expression with arguments {args} and {kwargs}"

                args_mapped = {k: v for k, v in zip(self.parameters, args)}
                if any(k in kwargs for k in args_mapped):
                    raise TypeError("")

                kwargs |= args_mapped

                try:
                    result = value.simplify(kwargs, renderers=renderers)
                    if isinstance(result, ValueExpression):
                        return result.value
                except Exception as ex:
                    raise TypeError(msg) from ex

                raise TypeError(msg)

            return ValueExpression(origin=self.origin, value=fn)

        return LambdaExpression(
            origin=self.origin,
            parameters=self.parameters,
            return_value=value,
        )
