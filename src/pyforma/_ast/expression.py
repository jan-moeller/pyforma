from dataclasses import dataclass
from typing import override, Any, cast

from .expressions import Expression, ValueExpression


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


@dataclass(frozen=True, kw_only=True)
class AttributeExpression(Expression):
    """Attribute expression"""

    object: Expression
    attribute: str

    @override
    def identifiers(self) -> set[str]:
        return self.object.identifiers()

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        object = self.object.substitute(variables)
        attribute = self.attribute

        if isinstance(object, ValueExpression):
            try:
                return ValueExpression(
                    origin=self.origin, value=getattr(object.value, attribute)
                )
            except Exception as ex:
                raise TypeError(
                    f"{self.origin}: Invalid attribute expression for value {object.value} of type {type(object.value)} and attribute {attribute}"
                ) from ex

        return AttributeExpression(
            origin=self.origin, object=object, attribute=attribute
        )


@dataclass(frozen=True, kw_only=True)
class ListExpression(Expression):
    """List expression"""

    elements: tuple[Expression, ...]

    @override
    def identifiers(self) -> set[str]:
        return set[str]().union(*(e.identifiers() for e in self.elements))

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        _elements = tuple(e.substitute(variables) for e in self.elements)

        if all(isinstance(e, ValueExpression) for e in _elements):
            return ValueExpression(
                origin=self.origin,
                value=[cast(ValueExpression, e).value for e in _elements],
            )

        return ListExpression(origin=self.origin, elements=_elements)


@dataclass(frozen=True, kw_only=True)
class DictExpression(Expression):
    """Dictionary expression"""

    elements: tuple[tuple[Expression, Expression], ...]

    @override
    def identifiers(self) -> set[str]:
        return set[str]().union(
            *(e[0].identifiers() for e in self.elements),
            *(e[1].identifiers() for e in self.elements),
        )

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        _elements = tuple(
            (k.substitute(variables), v.substitute(variables)) for k, v in self.elements
        )

        if all(
            isinstance(k, ValueExpression) and isinstance(v, ValueExpression)
            for k, v in _elements
        ):
            return ValueExpression(
                origin=self.origin,
                value={
                    cast(ValueExpression, k).value: cast(ValueExpression, v).value
                    for k, v in _elements
                },
            )

        return DictExpression(origin=self.origin, elements=_elements)


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
