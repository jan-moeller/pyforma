from contextlib import nullcontext
from typing import ContextManager
import pytest

from pyforma._parser import ParseInput


@pytest.mark.parametrize(
    "source,index,length",
    [
        ("", 0, 0),
        ("foo", 0, 3),
        ("foo", 1, 2),
        ("foo", 3, 0),
    ],
)
def test_simple(source: str, index: int, length: int):
    input = ParseInput(source, index)
    assert input.source == source
    assert input.index == index
    assert input.at_bof() == (index == 0)
    assert input.at_eof() == (index == len(source))
    assert input[:] == source[index:]
    assert list(input) == list(source[index:])
    assert len(input) == length
    assert str(input) == source[index:]


@pytest.mark.parametrize(
    "source,index",
    [
        ("", -1),
        ("", 1),
        ("foo", -1),
        ("foo", 4),
    ],
)
def test_invalid_initialization(source: str, index: int):
    with pytest.raises(ValueError):
        _ = ParseInput(source, index)


@pytest.mark.parametrize(
    "source,index,item,expected",
    [
        ("", 0, 0, pytest.raises(IndexError)),
        ("", 0, -1, pytest.raises(IndexError)),
        ("bar", 0, 0, nullcontext("b")),
        ("bar", 0, 1, nullcontext("a")),
        ("bar", 0, -1, nullcontext("r")),
        ("bar", 0, 3, pytest.raises(IndexError)),
        ("", 0, slice(0, 0, 0), pytest.raises(ValueError)),
        ("", 0, slice(0, 0, 1), nullcontext("")),
        ("", 0, slice(1, 5, 1), nullcontext("")),
        ("bar", 0, slice(0, 3, 1), nullcontext("bar")),
        ("bar", 1, slice(0, 1, 1), nullcontext("a")),
        ("bar", 1, slice(0, 2, 1), nullcontext("ar")),
        ("foobar", 1, slice(-3, -1, 1), nullcontext("ba")),
        ("barfoo", 3, slice(None, None, -1), nullcontext("oof")),
        ("foo", 0, "blurb", pytest.raises(TypeError)),
    ],
)
def test_indexing(
    source: str,
    index: int,
    item: int | slice,
    expected: ContextManager[str],
):
    input = ParseInput(source, index)
    with expected as e:
        assert input[item] == e


@pytest.mark.parametrize(
    "source,index,count,expected",
    [
        ("", 0, 1, pytest.raises(ValueError)),
        ("", 0, 0, nullcontext("")),
        ("foo", 0, 4, pytest.raises(ValueError)),
        ("foo", 0, -4, pytest.raises(ValueError)),
    ],
)
def test_peek(
    source: str,
    index: int,
    count: int,
    expected: ContextManager[str],
):
    input = ParseInput(source, index)
    with expected as e:
        assert input.peek(count) == e


@pytest.mark.parametrize(
    "source,index,count,expected",
    [
        ("", 0, 1, pytest.raises(ValueError)),
        ("", 0, 0, nullcontext(0)),
        ("foo", 0, 4, pytest.raises(ValueError)),
        ("foo", 0, -4, pytest.raises(ValueError)),
        ("foo", 0, 1, nullcontext(1)),
        ("foo", 1, 1, nullcontext(2)),
        ("foo", 1, 2, nullcontext(3)),
    ],
)
def test_consume(
    source: str,
    index: int,
    count: int,
    expected: ContextManager[int],
):
    input = ParseInput(source, index)
    with expected as e:
        assert input.consume(count) == ParseInput(source, e)


@pytest.mark.parametrize(
    "source,index,line,col",
    [
        ("", 0, 1, 1),
        ("foo", 0, 1, 1),
        ("foo", 1, 1, 2),
        ("foo\nbar", 3, 1, 4),
        ("foo\nbar", 4, 2, 1),
    ],
)
def test_line_and_column(
    source: str,
    index: int,
    line: int,
    col: int,
):
    input = ParseInput(source, index)
    assert input.line_and_column() == (line, col)
