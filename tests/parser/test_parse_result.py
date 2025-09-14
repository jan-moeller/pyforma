from copy import deepcopy
import pytest

from pyforma._parser import ParseResult, ParseContext


def test_success():
    result = ParseResult.make_success(result=42, context=ParseContext(""))
    assert result.is_success
    assert not result.is_failure
    assert result.success.result == 42
    with pytest.raises(ValueError):
        _ = result.failure


def test_failure():
    result = ParseResult.make_failure(context=ParseContext(""), expected="42")
    assert not result.is_success
    assert result.is_failure
    with pytest.raises(ValueError):
        _ = result.success
    assert result.failure.expected == "42"


def test_repr():
    context = ParseContext("")
    result = ParseResult.make_success(result=42, context=context)
    assert repr(result) == f"ParseResult({repr(result.value)}, context={repr(context)})"


def test_eq():
    success = ParseResult.make_success(result=42, context=ParseContext(""))
    failure = ParseResult.make_failure(context=ParseContext(""), expected="42")

    assert success != failure
    assert success == deepcopy(success)
    assert failure == deepcopy(failure)
    assert success != 42
    assert failure != 42


def test_hash():
    success = ParseResult.make_success(result=42, context=ParseContext(""))
    failure = ParseResult.make_failure(context=ParseContext(""), expected="42")
    d = {success: 1, failure: 2}
    assert success in d
    assert failure in d
    assert hash(success) != hash(failure)
    assert hash(success) == hash(deepcopy(success))
