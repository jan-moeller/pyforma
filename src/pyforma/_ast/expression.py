from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override, Any, Literal


class Expression(ABC):
    """Expression base class"""

    @abstractmethod
    def identifiers(self) -> set[str]: ...

    @abstractmethod
    def substitute(self, variables: dict[str, Any]) -> "Expression": ...


@dataclass(frozen=True)
class ValueExpression(Expression):
    """Value expression"""

    value: Any

    @override
    def identifiers(self) -> set[str]:
        return set()

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        return self


@dataclass(frozen=True)
class IdentifierExpression(Expression):
    """Identifier expression."""

    identifier: str

    @override
    def identifiers(self) -> set[str]:
        return {self.identifier}

    @override
    def substitute(self, variables: dict[str, Any]) -> Expression:
        if self.identifier in variables:
            return ValueExpression(variables[self.identifier])
        return self


@dataclass(frozen=True)
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
                    return ValueExpression(+operand.value)
                case "-":
                    return ValueExpression(-operand.value)
                case "~":
                    return ValueExpression(~operand.value)
                case "not":  # pragma: no branch
                    return ValueExpression(not operand.value)

        return UnOpExpression(op=self.op, operand=operand)


@dataclass(frozen=True)
class BinOpExpression(Expression):
    """Binary operator expression"""

    op: Literal[
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
                    return ValueExpression(lhs.value**rhs.value)
                case "+":
                    return ValueExpression(lhs.value + rhs.value)
                case "-":
                    return ValueExpression(lhs.value - rhs.value)
                case "*":
                    return ValueExpression(lhs.value * rhs.value)
                case "/":
                    return ValueExpression(lhs.value / rhs.value)
                case "//":
                    return ValueExpression(lhs.value // rhs.value)
                case "%":
                    return ValueExpression(lhs.value % rhs.value)
                case "@":
                    return ValueExpression(lhs.value @ rhs.value)
                case "<<":
                    return ValueExpression(lhs.value << rhs.value)
                case ">>":
                    return ValueExpression(lhs.value >> rhs.value)
                case "&":
                    return ValueExpression(lhs.value & rhs.value)
                case "^":
                    return ValueExpression(lhs.value ^ rhs.value)
                case "|":
                    return ValueExpression(lhs.value | rhs.value)
                case "==":
                    return ValueExpression(lhs.value == rhs.value)
                case "!=":
                    return ValueExpression(lhs.value != rhs.value)
                case "<=":
                    return ValueExpression(lhs.value <= rhs.value)
                case "<":
                    return ValueExpression(lhs.value < rhs.value)
                case ">=":
                    return ValueExpression(lhs.value >= rhs.value)
                case ">":
                    return ValueExpression(lhs.value > rhs.value)
                case "in":
                    return ValueExpression(lhs.value in rhs.value)
                case "not in":
                    return ValueExpression(lhs.value not in rhs.value)
                case "and":
                    return ValueExpression(lhs.value and rhs.value)
                case "or":  # pragma: no branch
                    return ValueExpression(lhs.value or rhs.value)
        else:
            return BinOpExpression(self.op, lhs, rhs)
