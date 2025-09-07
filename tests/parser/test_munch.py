from collections.abc import Callable
from contextlib import nullcontext
from itertools import pairwise
from typing import Any, ContextManager, final, override

import pytest

from pyforma._parser import munch, ParseError, ParseResult, ParseInput


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
        ("", str.isidentifier, nullcontext("")),
        ("foo", str.isdigit, nullcontext("")),
        ("foo", str.isidentifier, nullcontext("foo")),
        ("123foo", str.isdigit, nullcontext("123")),
        ("12356", ConsecutiveDigits(4), nullcontext("123")),
        ("12356", ConsecutiveDigits(2), nullcontext("12")),
        ("123foo", ConsecutiveDigits(0), nullcontext("")),
        ("foo", Weird(), nullcontext("")),
        ("123foo", lambda: None, pytest.raises(ParseError)),
    ],
)
def test_munch(
    source: str,
    predicate: Callable[[str], bool],
    expected: ContextManager[str],
):
    with expected as e:
        assert munch(predicate)(ParseInput(source)) == ParseResult(
            remaining=ParseInput(source, index=len(e)),
            result=e,
        )
