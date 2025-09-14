import pytest

from pyforma._parser import (
    ParseContext,
    ParseSuccess,
    ParseFailure,
    Parser,
    literal,
    ParseResult,
    non_empty,
    transform_result,
    transform_success,
    digits,
    transform_consumed,
)


def force_success(result: ParseResult[str]) -> ParseResult[str]:
    if result.is_success:
        return result
    return ParseResult.make_success(context=result.context, result="")


@pytest.mark.parametrize(
    "source,parser,expected",
    [
        (
            "",
            transform_result(
                literal("foo"),
                transform=force_success,
            ),
            ParseSuccess(""),
        ),
        (
            "foobar",
            transform_result(
                literal("foo"),
                transform=force_success,
            ),
            ParseSuccess("foo"),
        ),
    ],
)
def test_transform_result(
    source: str,
    parser: Parser[str],
    expected: ParseSuccess[str] | ParseFailure,
):
    context = ParseContext(source)
    result = parser(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=len(expected.result))
    else:
        assert result.context == context


@pytest.mark.parametrize(
    "source,parser,expected",
    [
        (
            "123",
            transform_success(
                digits,
                transform=int,
            ),
            ParseSuccess(123),
        ),
        (
            "foobar",
            transform_success(
                non_empty(digits),
                transform=int,
            ),
            ParseFailure(expected="non-empty(digits)"),
        ),
    ],
)
def test_transform_success(
    source: str,
    parser: Parser[str],
    expected: ParseSuccess[str] | ParseFailure,
):
    context = ParseContext(source)
    result = parser(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=len(source))
    else:
        assert result.context == context


@pytest.mark.parametrize(
    "source,parser,expected",
    [
        (
            "123",
            transform_consumed(
                digits,
                transform=int,
            ),
            ParseSuccess(123),
        ),
        (
            "foobar",
            transform_consumed(
                non_empty(digits),
                transform=int,
            ),
            ParseFailure(expected="non-empty(digits)"),
        ),
    ],
)
def test_transform_consumed(
    source: str,
    parser: Parser[str],
    expected: ParseSuccess[str] | ParseFailure,
):
    context = ParseContext(source)
    result = parser(context)
    assert type(result.value) is type(expected)
    assert result.value == expected
    if isinstance(expected, ParseSuccess):
        assert result.context == ParseContext(source, index=len(source))
    else:
        assert result.context == context
