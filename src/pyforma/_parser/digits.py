import string

from .munch import munch


digits = munch(str.isdigit)
"""Parses zero or more digit characters."""

hexdigits = munch(lambda s: all(c in string.hexdigits for c in s))
"""Parses zero or more hexadecimal digit characters."""

octdigits = munch(lambda s: all(c in string.octdigits for c in s))
"""Parses zero or more octal digit characters."""

bindigits = munch(lambda s: all(c in ["0", "1"] for c in s))
"""Parses zero or more binary digit characters."""
