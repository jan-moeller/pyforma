import pytest

from pyforma._parser import literal, option, sequence, indirect, eof
from pyforma._parser.parse_context import ParseContext

parser = sequence(literal("("), option(indirect(f"{__name__}.parser")), literal(")"))


@pytest.mark.parametrize(
    "source,success",
    [
        ("()", True),
        ("(())", True),
        ("((()))", True),
        ("", False),
        ("(", False),
        ("()()", False),
        ("(()", False),
        ("())", False),
    ],
)
def test_indirect(source: str, success: bool):
    assert sequence(parser, eof)(ParseContext(source)).is_success == success
