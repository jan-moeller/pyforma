import pytest

from pyforma._parser import (
    ParseContext,
    nothing,
)


@pytest.mark.parametrize(
    "source",
    [
        "",
        "foo",
    ],
)
def test_nothing(
    source: str,
):
    context = ParseContext(source)
    result = nothing(context)
    assert result.is_success
    assert result.context == ParseContext(source, index=0)
