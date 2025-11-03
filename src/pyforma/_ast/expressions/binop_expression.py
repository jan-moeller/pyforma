from dataclasses import dataclass
from typing import Literal, override, Any

from .expression import Expression
from .value_expression import ValueExpression


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
            try:
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
            except Exception as ex:
                raise TypeError(
                    f"{self.origin}: Invalid binary operator {self.op} for values {lhs.value} of type {type(lhs.value)} and {rhs.value} of type {type(rhs.value)}"
                ) from ex
        else:
            return BinOpExpression(origin=self.origin, op=self.op, lhs=lhs, rhs=rhs)
