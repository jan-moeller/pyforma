from collections.abc import Sequence, Callable
from dataclasses import dataclass
from typing import override, Any

from .expression import Expression
from .expression_impl import ExpressionImpl
from .value_expression import ValueExpression


@dataclass(frozen=True, kw_only=True)
class AttributeExpression(ExpressionImpl):
    """Attribute expression"""

    object: Expression
    attribute: str

    @override
    def unresolved_identifiers(self) -> set[str]:
        return self.object.unresolved_identifiers()

    @override
    def simplify(
        self,
        variables: dict[str, Any],
        *,
        renderers: Sequence[tuple[type, Callable[[Any], str]]],
    ) -> Expression:
        object = self.object.simplify(variables, renderers=renderers)
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
