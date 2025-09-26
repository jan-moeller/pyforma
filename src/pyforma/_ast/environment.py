from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, override

from .expression import Expression, ValueExpression
from .comment import Comment


class Environment(ABC):
    """Environment base class"""

    @abstractmethod
    def identifiers(self) -> set[str]: ...

    @abstractmethod
    def substitute(self, variables: dict[str, Any]) -> "Environment": ...


@dataclass(frozen=True)
class TemplateEnvironment(Environment):
    """Template Environment class"""

    content: tuple[str | Comment | Expression | Environment, ...]

    @override
    def identifiers(self) -> set[str]:
        return set[str]().union(
            *(
                e.identifiers()
                for e in self.content
                if isinstance(e, Expression) or isinstance(e, Environment)
            )
        )

    @override
    def substitute(self, variables: dict[str, Any]) -> "TemplateEnvironment":
        def subs(
            e: str | Comment | Expression | Environment,
        ) -> str | Comment | Expression | Environment:
            match e:
                case str() | Comment():
                    return e
                case Expression() | Environment():  # pragma: no branch
                    return e.substitute(variables)

        return TemplateEnvironment(tuple(subs(e) for e in self.content))


@dataclass(frozen=True)
class WithEnvironment(Environment):
    """With-Environment"""

    variables: dict[str, Expression]
    content: TemplateEnvironment

    @override
    def identifiers(self) -> set[str]:
        return self.content.identifiers() | set().union(
            *[e.identifiers() for e in self.variables.values()]
        )

    @override
    def substitute(self, variables: dict[str, Any]) -> Environment:
        _variables = {
            iden: expr.substitute(variables) for iden, expr in self.variables.items()
        }
        relevant_variables = {
            key: val for key, val in variables.items() if key not in _variables
        }
        relevant_variables |= {
            iden: expr.value
            for iden, expr in _variables.items()
            if isinstance(expr, ValueExpression)
        }
        _content = self.content.substitute(relevant_variables)
        _remaining_identifiers = _content.identifiers()
        _variables = {
            iden: expr
            for iden, expr in _variables.items()
            if iden in _remaining_identifiers
        }

        if len(_variables) == 0:
            return _content

        return WithEnvironment(_variables, _content)
