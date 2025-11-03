from dataclasses import dataclass
from typing import override, Any

from .expression import Expression
from .value_expression import ValueExpression


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
                    origin=self.origin,
                    value=getattr(object.value, attribute),
                )

            except Exception as ex:
                raise TypeError(
                    f"{self.origin}: Invalid attribute expression for value {object.value} of type {type(object.value)} and attribute {attribute}"
                ) from ex

        return AttributeExpression(
            origin=self.origin,
            object=object,
            attribute=attribute,
        )
