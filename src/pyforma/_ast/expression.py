from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override, Any, Literal, cast

from pyforma._ast.origin import Origin


@dataclass(frozen=True, kw_only=True)
class Expression(ABC):
    """Expression base class"""

    origin: Origin

    @abstractmethod
    def identifiers(self) -> set[str]: ...

    @abstractmethod
    def substitute(self, variables: dict[str, Any]) -> "Expression": ...


@dataclass(frozen=True, kw_only=True)
class ValueExpression(Expression):
    """Value expression"""

    value: Any

    @override
    def identifiers(self) -> set[str]:
        return set()

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        return self


@dataclass(frozen=True, kw_only=True)
class IdentifierExpression(Expression):
    """Identifier expression."""

    identifier: str

    @override
    def identifiers(self) -> set[str]:
        return {self.identifier}

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        if self.identifier in variables:
            return ValueExpression(origin=self.origin, value=variables[self.identifier])
        return self


@dataclass(frozen=True, kw_only=True)
class UnOpExpression(Expression):
    """Unary operator expression"""

    op: Literal["+", "-", "~", "not"]
    operand: Expression

    @override
    def identifiers(self) -> set[str]:
        return self.operand.identifiers()

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        operand = self.operand.substitute(variables)
        if isinstance(operand, ValueExpression):
            match self.op:
                case "+":
                    return ValueExpression(origin=self.origin, value=+operand.value)
                case "-":
                    return ValueExpression(origin=self.origin, value=-operand.value)
                case "~":
                    return ValueExpression(origin=self.origin, value=~operand.value)
                case "not":  # pragma: no branch
                    return ValueExpression(origin=self.origin, value=not operand.value)

        return UnOpExpression(origin=self.origin, op=self.op, operand=operand)


@dataclass(frozen=True, kw_only=True)
class BinOpExpression(Expression):
    """Binary operator expression"""

    type OpType = Literal[
        "**",
        "+",
        "-",
        "*",
        "/",
        "//",
        "%",
        "@",
        "|",
        "&",
        "^",
        "<<",
        ">>",
        "in",
        "==",
        "!=",
        "<=",
        "<",
        ">=",
        ">",
        "not in",
        "and",
        "or",
    ]

    op: OpType
    lhs: Expression
    rhs: Expression

    @override
    def identifiers(self) -> set[str]:
        return self.lhs.identifiers() | self.rhs.identifiers()

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        lhs = self.lhs.substitute(variables)
        rhs = self.rhs.substitute(variables)
        if isinstance(lhs, ValueExpression) and isinstance(rhs, ValueExpression):
            match self.op:
                case "**":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value**rhs.value
                    )
                case "+":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value + rhs.value
                    )
                case "-":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value - rhs.value
                    )
                case "*":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value * rhs.value
                    )
                case "/":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value / rhs.value
                    )
                case "//":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value // rhs.value
                    )
                case "%":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value % rhs.value
                    )
                case "@":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value @ rhs.value
                    )
                case "<<":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value << rhs.value
                    )
                case ">>":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value >> rhs.value
                    )
                case "&":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value & rhs.value
                    )
                case "^":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value ^ rhs.value
                    )
                case "|":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value | rhs.value
                    )
                case "==":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value == rhs.value
                    )
                case "!=":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value != rhs.value
                    )
                case "<=":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value <= rhs.value
                    )
                case "<":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value < rhs.value
                    )
                case ">=":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value >= rhs.value
                    )
                case ">":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value > rhs.value
                    )
                case "in":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value in rhs.value
                    )
                case "not in":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value not in rhs.value
                    )
                case "and":
                    return ValueExpression(
                        origin=self.origin, value=lhs.value and rhs.value
                    )
                case "or":  # pragma: no branch
                    return ValueExpression(
                        origin=self.origin, value=lhs.value or rhs.value
                    )
        else:
            return BinOpExpression(origin=self.origin, op=self.op, lhs=lhs, rhs=rhs)


@dataclass(frozen=True, kw_only=True)
class IndexExpression(Expression):
    """Slice expression"""

    expression: Expression
    index: Expression

    @override
    def identifiers(self) -> set[str]:
        return self.expression.identifiers() | self.index.identifiers()

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        expression = self.expression.substitute(variables)
        index = self.index.substitute(variables)
        if isinstance(expression, ValueExpression) and isinstance(
            index, ValueExpression
        ):
            return ValueExpression(
                origin=self.origin, value=expression.value[index.value]
            )
        return IndexExpression(origin=self.origin, expression=expression, index=index)


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

        if isinstance(callee, ValueExpression) and all(
            isinstance(arg, ValueExpression) for arg in arguments
        ):
            args = [cast(ValueExpression, arg).value for arg in arguments]
            kwargs = {
                iden: cast(ValueExpression, arg).value for iden, arg in kw_arguments
            }
            return ValueExpression(
                origin=self.origin,
                value=callee.value(*args, **kwargs),
            )
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
            return ValueExpression(
                origin=self.origin, value=getattr(object.value, attribute)
            )

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
