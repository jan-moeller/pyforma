from collections.abc import Callable
from itertools import pairwise
from typing import Any, final, override

import pytest

from pyforma._parser import (
    munch,
    ParseContext,
    ParseFailure,
    ParseSuccess,
)


@final
class ConsecutiveDigits:
    def __init__(self, max: int):
        self.max = max

    def __call__(self, s: str) -> bool:
        return len(s) <= self.max and all(int(a) == int(b) - 1 for a, b in pairwise(s))


class Weird:
    @override
    def __getattribute__(self, name: str) -> Any:
        if name == "__class__":
            raise AttributeError("__class__ hidden")
        return super().__getattribute__(name)

    def __call__(self, s: str) -> bool:
        return False


@pytest.mark.parametrize(
    "source,predicate,expected",
    [  # type: ignore
        ("", str.isidentifier, ParseSuccess("")),
        ("foo", str.isdigit, ParseSuccess("")),
        ("foo", str.isidentifier, ParseSuccess("foo")),
        ("123foo", str.isdigit, ParseSuccess("123")),
        ("12356", ConsecutiveDigits(4), ParseSuccess("123")),
        ("12356", ConsecutiveDigits(2), ParseSuccess("12")),
        ("123foo", ConsecutiveDigits(0), ParseSuccess("")),
        ("foo", Weird(), ParseSuccess("")),
    ],
)
def test_munch(
    source: str,
    predicate: Callable[[str], bool],
    expected: ParseSuccess | ParseFailure,
):
    context = ParseContext(source)
    result = munch(predicate)(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=len(expected.result))
    else:
        assert result.context == context
