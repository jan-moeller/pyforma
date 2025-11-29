from collections.abc import Iterable


def join(sep: str, things: Iterable[str]) -> str:
    """Free-function version of str.join"""
    return sep.join(things)
