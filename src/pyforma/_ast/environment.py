from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, override, Annotated

from annotated_types import MinLen

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
        content_ids = self.content.identifiers() - self.variables.keys()
        var_ids = set[str]().union(*[e.identifiers() for e in self.variables.values()])
        return content_ids | var_ids

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


@dataclass(frozen=True)
class DefaultEnvironment(Environment):
    """Default-Environment"""

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
            iden: expr.value
            for iden, expr in _variables.items()
            if isinstance(expr, ValueExpression)
        } | variables
        _content = self.content.substitute(relevant_variables)
        _remaining_identifiers = _content.identifiers()
        _variables = {
            iden: expr
            for iden, expr in _variables.items()
            if iden in _remaining_identifiers
        }

        if len(_variables) == 0:
            return _content

        return DefaultEnvironment(_variables, _content)


@dataclass(frozen=True)
class IfEnvironment(Environment):
    """If-Environment"""

    ifs: tuple[tuple[Expression, TemplateEnvironment], ...]
    else_content: TemplateEnvironment

    @override
    def identifiers(self) -> set[str]:
        return (
            set[str]().union(
                *[expr.identifiers() | env.identifiers() for expr, env in self.ifs]
            )
            | self.else_content.identifiers()
        )

    @override
    def substitute(self, variables: dict[str, Any]) -> "Environment":
        _ifs: tuple[tuple[Expression, TemplateEnvironment], ...] = ()

        for expr, env in self.ifs:
            _expr = expr.substitute(variables)

            if isinstance(_expr, ValueExpression):
                if _expr.value:
                    if len(_ifs) == 0:
                        return env.substitute(variables)
                    else:
                        _ifs += ((_expr, env.substitute(variables)),)
            else:
                _ifs += ((_expr, env.substitute(variables)),)

        _else_content = self.else_content.substitute(variables)

        if len(_ifs) == 0:
            return _else_content
        return IfEnvironment(_ifs, _else_content)


@dataclass(frozen=True)
class ForEnvironment(Environment):
    """For-Environment"""

    identifier: Annotated[tuple[str, ...], MinLen(1)]
    expression: Expression
    content: TemplateEnvironment

    @override
    def identifiers(self) -> set[str]:
        content_ids = self.content.identifiers() - set(self.identifier)
        return self.expression.identifiers() | content_ids

    @override
    def substitute(self, variables: dict[str, Any]) -> "Environment":
        _expression = self.expression.substitute(variables)
        _content = self.content.substitute(
            {k: v for k, v in variables.items() if k not in self.identifier}
        )

        if isinstance(_expression, ValueExpression):
            _contents: list[TemplateEnvironment] = []
            for value in _expression.value:
                if len(self.identifier) > 1:
                    if len(self.identifier) != len(value):
                        raise ValueError(
                            f"Can't unpack {len(value)} values: expected {len(self.identifier)}"
                        )
                    vs = {k: v for k, v in zip(self.identifier, value)}
                else:
                    vs = {self.identifier[0]: value}  # pyright: ignore[reportGeneralTypeIssues]
                c = _content.substitute(vs)
                _contents.append(c)
            return TemplateEnvironment(tuple(_contents)).substitute({})
        else:
            return ForEnvironment(self.identifier, _expression, _content)
