from dataclasses import dataclass
from typing import override, Any

from .expressions import Expression, ValueExpression


@dataclass(frozen=True, kw_only=True)
class LambdaExpression(Expression):
    """Lambda expression"""

    parameters: tuple[str, ...]
    return_value: Expression

    @override
    def identifiers(self) -> set[str]:
        return self.return_value.identifiers() - set(self.parameters)

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        value = self.return_value.substitute(
            {k: v for k, v in variables.items() if k not in self.parameters}
        )

        if value.identifiers().issubset(self.parameters):

            def fn(*args: Any, **kwargs: Any) -> Any:
                msg = f"{self.origin}: Invalid call of lambda expression with arguments {args} and {kwargs}"

                args_mapped = {k: v for k, v in zip(self.parameters, args)}
                if any(k in kwargs for k in args_mapped):
                    raise TypeError("")

                kwargs |= args_mapped

                try:
                    result = value.substitute(kwargs)
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
