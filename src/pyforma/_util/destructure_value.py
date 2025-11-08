from collections.abc import Sized, Iterable
from typing import Any


def destructure_value(identifiers: tuple[str, ...], value: Any) -> dict[str, Any]:
    if len(identifiers) > 1:
        if not isinstance(value, Sized):
            raise TypeError(f"Can't unpack {value}: not sized")
        elif len(identifiers) != len(value):
            raise TypeError(
                f"Can't unpack {value}: has length {len(identifiers)} instead of {len(identifiers)}"
            )
        if not isinstance(value, Iterable):
            raise TypeError(f"Can't unpack {value}: not iterable")
        vs = {k: v for k, v in zip(identifiers, value)}
    else:
        vs = {identifiers[0]: value}  # pyright: ignore[reportGeneralTypeIssues]

    return vs
