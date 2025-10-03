from collections.abc import Callable
from contextlib import nullcontext
from typing import Any, ContextManager

import pytest

from pyforma._util import defaulted, pipeable


def fn() -> int:
    return 42


def fn_p(arg: int, /) -> int:
    return arg


def fn_pk(arg: int) -> int:
    return arg


def fn_k(*, arg: int) -> int:
    return arg


def fn_pd(arg: int = 42, /) -> int:
    return arg


def fn_pkd(arg: int = 42) -> int:
    return arg


def fn_kd(*, arg: int = 42) -> int:
    return arg


def fn_p_p(arg1: int, arg2: int, /) -> int:
    return arg1 + arg2


def fn_p_pk(arg1: int, /, arg2: int) -> int:
    return arg1 + arg2


def fn_p_k(arg1: int, /, *, arg2: int) -> int:
    return arg1 + arg2


def fn_pk_pk(arg1: int, arg2: int) -> int:
    return arg1 + arg2


def fn_pk_k(arg1: int, *, arg2: int) -> int:
    return arg1 + arg2


def fn_k_k(*, arg1: int, arg2: int) -> int:
    return arg1 + arg2


def fn_p_pd(arg1: int, arg2: int = 42, /) -> int:
    return arg1 + arg2


def fn_pd_pd(arg1: int = 42, arg2: int = 42, /) -> int:
    return arg1 + arg2


def fn_p_pkd(arg1: int, /, arg2: int = 42) -> int:
    return arg1 + arg2


def fn_pd_pkd(arg1: int = 42, /, arg2: int = 42) -> int:
    return arg1 + arg2


def fn_p_kd(arg1: int, /, *, arg2: int = 42) -> int:
    return arg1 + arg2


def fn_pd_kd(arg1: int = 42, /, *, arg2: int = 42) -> int:
    return arg1 + arg2


def fn_pk_pkd(arg1: int, arg2: int = 42) -> int:
    return arg1 + arg2


def fn_pkd_pkd(arg1: int = 42, arg2: int = 42) -> int:
    return arg1 + arg2


def fn_pk_kd(arg1: int, *, arg2: int = 42) -> int:
    return arg1 + arg2


def fn_pkd_kd(arg1: int = 42, *, arg2: int = 42) -> int:
    return arg1 + arg2


def fn_k_kd(*, arg1: int, arg2: int = 42) -> int:
    return arg1 + arg2


def fn_kd_kd(*, arg1: int = 42, arg2: int = 42) -> int:
    return arg1 + arg2


def fn_pv_kv(*args: int, **kwargs: int) -> int:
    return sum(args) + sum(kwargs.values())


def fn_p_pv_k_kv(arg1: int, /, *args: int, arg2: int, **kwargs: int) -> int:
    return arg1 + sum(args) + arg2 + sum(kwargs.values())


@pytest.mark.parametrize(
    "fn,pipe_arg,value,args,kwargs,expectation",
    [
        # 0 params
        (fn, 0, 42, None, None, pytest.raises(TypeError)),
        # 1 param
        (fn_p, 0, 42, None, None, nullcontext(42)),
        (fn_p, 0, 42, (), None, nullcontext(42)),
        (fn_pk, 0, 42, None, None, nullcontext(42)),
        (fn_pk, 0, 42, (), None, nullcontext(42)),
        (fn_pk, "arg", 42, None, None, nullcontext(42)),
        (fn_pk, "arg", 42, (), None, nullcontext(42)),
        (fn_k, "arg", 42, None, None, pytest.raises(TypeError)),
        (fn_k, "arg", 42, (), None, pytest.raises(TypeError)),
        (fn_pd, 0, 42, None, None, pytest.raises(TypeError)),
        (fn_pkd, 0, 42, None, None, pytest.raises(TypeError)),
        (fn_kd, 0, 42, None, None, pytest.raises(TypeError)),
        # 2 params
        (fn_p_p, 0, 40, None, None, pytest.raises(TypeError)),
        (fn_p_p, 0, 40, (), None, pytest.raises(TypeError)),
        (fn_pd_pd, 0, 40, None, None, pytest.raises(TypeError)),
        (fn_pd_pd, 1, 40, None, None, pytest.raises(TypeError)),
        (fn_p_pkd, 0, 40, (2,), None, nullcontext(44)),  # because 40 | 44 == 44
        (fn_p_pkd, 0, 40, None, dict(arg2=2), nullcontext(42)),
        (fn_p_pkd, 0, 40, None, None, nullcontext(82)),
        (fn_p_p, 0, 40, (2,), None, nullcontext(42)),
        (fn_p_p, 1, 40, (2,), None, nullcontext(42)),
        (fn_p_pd, 0, 40, (2,), None, nullcontext(44)),  # because 40 | 44 == 44
        (fn_p_pd, 0, 40, None, None, nullcontext(82)),
        (fn_p_pk, 0, 40, (2,), None, nullcontext(42)),
        (fn_p_pk, 0, 40, None, dict(arg2=2), nullcontext(42)),
        (fn_p_pk, 1, 40, (2,), None, nullcontext(42)),
        (fn_p_pkd, 0, 40, (2,), None, nullcontext(44)),  # because 40 | 44 == 44
        (fn_p_pkd, 0, 40, None, dict(arg2=2), nullcontext(42)),
        (fn_p_pkd, 0, 40, None, None, nullcontext(82)),
        (fn_p_k, 0, 40, None, dict(arg2=2), nullcontext(42)),
        (fn_p_k, "arg2", 40, (2,), None, pytest.raises(TypeError)),
        (fn_p_kd, 0, 40, None, None, nullcontext(82)),
        (fn_p_kd, 0, 40, None, dict(arg2=2), nullcontext(42)),
        (fn_pk_pk, 0, 40, (2,), None, nullcontext(42)),
        (fn_pk_pk, 0, 40, None, dict(arg2=2), nullcontext(42)),
        (fn_pk_pk, 1, 40, (2,), None, nullcontext(42)),
        (fn_pk_pk, 1, 40, None, dict(arg1=2), nullcontext(42)),
        (fn_pk_pk, "arg1", 40, (2,), None, nullcontext(42)),
        (fn_pk_pk, "arg1", 40, None, dict(arg2=2), nullcontext(42)),
        (fn_pk_pk, "arg2", 40, (2,), None, nullcontext(42)),
        (fn_pk_pk, "arg2", 40, None, dict(arg1=2), nullcontext(42)),
        (fn_pk_pkd, 0, 40, (2,), None, nullcontext(44)),  # because 40 | 44 == 44
        (fn_pk_pkd, 0, 40, None, dict(arg2=2), nullcontext(42)),
        (fn_pk_pkd, 0, 40, None, None, nullcontext(82)),
        (fn_pk_k, 0, 40, None, dict(arg2=2), nullcontext(42)),
        (fn_pk_k, "arg2", 40, (2,), None, pytest.raises(TypeError)),
        (fn_pk_k, "arg2", 40, None, dict(arg1=2), pytest.raises(TypeError)),
        (fn_pk_kd, 0, 40, None, dict(arg2=2), nullcontext(42)),
        (fn_pk_kd, 0, 40, None, None, nullcontext(82)),
        (fn_k_k, "arg1", 40, None, dict(arg2=2), pytest.raises(TypeError)),
        (fn_k_k, "arg2", 40, None, dict(arg1=2), pytest.raises(TypeError)),
        (fn_k_kd, "arg1", 40, None, dict(arg2=2), pytest.raises(TypeError)),
        (fn_k_kd, "arg1", 40, None, None, pytest.raises(TypeError)),
        (fn_k_kd, "", 40, None, None, pytest.raises(TypeError)),
        (fn_p, "arg", 40, None, None, pytest.raises(TypeError)),
        (fn_pv_kv, 0, 40, (2,), None, pytest.raises(TypeError)),
        (fn_pv_kv, 1, 40, (2,), None, pytest.raises(TypeError)),
        (fn_p_pv_k_kv, 0, 40, None, dict(arg2=2), nullcontext(42)),
        (fn_p_pv_k_kv, "arg2", 40, (1, 1), None, pytest.raises(TypeError)),
    ],
)
def test_pipe_syntax(
    fn: Callable[..., Any],
    pipe_arg: int | str,
    value: Any,
    args: tuple[Any, ...] | None,
    kwargs: dict[str, Any] | None,
    expectation: ContextManager[Any],
):
    with expectation as e:
        pfn = pipeable(fn, pipe_arg=pipe_arg)

        if args is None and kwargs is None:
            assert value | pfn == e
        else:
            _args = defaulted(args, ())
            _kwargs = defaulted(kwargs, dict[str, Any]())
            assert value | pfn(*_args, **_kwargs) == e


def test_multi_pipe():
    assert (
        2 | pipeable(fn_pk_pk, pipe_arg=0)(28) | pipeable(fn_p_p, pipe_arg=0)(12) == 42
    )


@pytest.mark.parametrize(
    "fn,pipe_arg,args,kwargs,expectation",
    [
        # 0 params
        (fn, 0, None, None, pytest.raises(TypeError)),
        # 1 param
        (fn_p, 0, (42,), None, nullcontext(42)),
        (fn_p, 0, None, dict(arg=42), pytest.raises(TypeError)),
        (fn_pk, 0, (42,), None, nullcontext(42)),
        (fn_pk, 0, None, dict(arg=42), nullcontext(42)),
        (fn_pk, "arg", (42,), None, nullcontext(42)),
        (fn_pk, "arg", None, dict(arg=42), nullcontext(42)),
        (fn_k, "arg", None, dict(arg=42), pytest.raises(TypeError)),
        (fn_pd, 0, None, None, pytest.raises(TypeError)),  # pipe arg can't be defaulted
        (fn_pkd, 0, None, None, pytest.raises(TypeError)),
        (fn_kd, 0, None, None, pytest.raises(TypeError)),
        # 2 params
        (fn_p_p, 0, None, None, pytest.raises(TypeError)),
        (fn_p_p, 0, (), None, pytest.raises(TypeError)),
        (fn_pd_pd, 0, None, None, pytest.raises(TypeError)),
        (fn_pd_pd, 1, None, None, pytest.raises(TypeError)),
        (fn_p_pkd, 0, (2,), None, nullcontext(44)),
        (fn_p_pkd, 0, (2, 40), None, nullcontext(42)),
        (fn_p_pkd, 0, (40,), dict(arg2=2), nullcontext(42)),
        (fn_p_p, 0, (2, 40), None, nullcontext(42)),
        (fn_p_p, 1, (2, 40), None, nullcontext(42)),
        (fn_p_pd, 0, (2,), None, nullcontext(44)),
        (fn_p_pk, 0, (40,), dict(arg2=2), nullcontext(42)),
        (fn_p_pk, 1, (2, 40), None, nullcontext(42)),
        (fn_p_pkd, 0, (2,), None, nullcontext(44)),
        (fn_p_pkd, 0, (40,), dict(arg2=2), nullcontext(42)),
        (fn_p_k, 0, (40,), dict(arg2=2), nullcontext(42)),
        (fn_p_k, "arg2", (2,), dict(arg2=40), pytest.raises(TypeError)),
        (fn_p_kd, 0, (2,), None, nullcontext(44)),
        (fn_p_kd, 0, (40,), dict(arg2=2), nullcontext(42)),
        (fn_pk_pk, 0, (2, 40), None, nullcontext(42)),
        (fn_pk_pk, 0, (40,), dict(arg2=2), nullcontext(42)),
        (fn_pk_pk, 1, None, dict(arg1=2, arg2=40), nullcontext(42)),
        (fn_pk_pk, "arg1", (2, 40), None, nullcontext(42)),
        (fn_pk_pk, "arg1", (40,), dict(arg2=2), nullcontext(42)),
        (fn_pk_pk, "arg2", None, dict(arg1=2, arg2=40), nullcontext(42)),
        (fn_pk_pkd, 0, (2,), None, nullcontext(44)),
        (fn_pk_pkd, 0, None, dict(arg1=2), nullcontext(44)),
        (fn_pk_pkd, 0, (2,), None, nullcontext(44)),
        (fn_pk_k, 0, (40,), dict(arg2=2), nullcontext(42)),
        (fn_pk_k, "arg2", (2,), dict(arg2=40), pytest.raises(TypeError)),
        (fn_pk_kd, 0, (40,), dict(arg2=2), nullcontext(42)),
        (fn_pk_kd, 0, (2,), None, nullcontext(44)),
        (fn_k_k, "arg1", None, dict(arg1=40, arg2=2), pytest.raises(TypeError)),
        (fn_k_kd, "arg1", None, dict(arg1=2), pytest.raises(TypeError)),
        (fn_k_kd, "arg1", None, dict(arg1=2, arg2=40), pytest.raises(TypeError)),
        (
            str,
            0,
            (42,),
            None,
            pytest.raises(ValueError),
        ),  # built-ins don't have signatures
    ],
)
def test_call_syntax(
    fn: Callable[..., Any],
    pipe_arg: int | str,
    args: tuple[Any, ...] | None,
    kwargs: dict[str, Any] | None,
    expectation: ContextManager[Any],
):
    with expectation as e:
        pfn = pipeable(fn, pipe_arg=pipe_arg)
        _args = defaulted(args, ())
        _kwargs = defaulted(kwargs, dict[str, Any]())

        assert pfn(*_args, **_kwargs) == e
