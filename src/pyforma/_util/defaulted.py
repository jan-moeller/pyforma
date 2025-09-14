def defaulted[T](value: T | None, default: T) -> T:
    """Returns value as-is, except when it's None."""
    if value is None:
        return default
    return value
