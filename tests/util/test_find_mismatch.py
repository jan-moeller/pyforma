import pytest

from pyforma._util import find_mismatch


@pytest.mark.parametrize(
    "a,b,idx",
    [
        ("", "", -1),
        ("foo", "foo", -1),
        ("fob", "foo", 2),
        ("foo", "fob", 2),
        ("foobar", "foo", 3),
        ("foo", "foobar", 3),
    ],
)
def test_find_mismatch(a: str, b: str, idx: int):
    assert find_mismatch(a, b) == idx
