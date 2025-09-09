from dataclasses import dataclass
from .parser import parser, Parser
from .parse_context import ParseContext
from .parse_error import ParseError
from .parse_result import ParseResult


@dataclass
class Comment:
    """Tagged string for comments."""

    text: str


def comment(open: str, close: str) -> Parser[Comment]:
    """Creates a comment parser using the provided open and close markers

    Args:
        open: The opening marker.
        close: The closing marker.

    Returns:
        The comment parser.

    Raises:
        ValueError: If the open and close markers are the same or one of them is empty.
    """

    if open == close:
        raise ValueError("open and close markers cannot be the same")
    if len(open) == 0 or len(close) == 0:
        raise ValueError("open and close markers cannot be empty")

    @parser(name="comment")
    def parse_comment(context: ParseContext) -> ParseResult[Comment]:
        cur_context = context

        if not cur_context[:].startswith(open):
            raise ParseError(
                f"expected {open} to start a comment",
                parser=parse_comment,
                context=context,
            )

        cur_context = cur_context.consume(len(open))

        result = ""
        while not cur_context.at_eof():
            if cur_context[:].startswith(open):
                r = parse_comment(cur_context)
                result += f"{open}{r.result.text}{close}"
                cur_context = r.context
            elif cur_context[:].startswith(close):
                return ParseResult(
                    context=cur_context.consume(len(close)),
                    result=Comment(result),
                )
            else:
                result += cur_context.peek()
                cur_context = cur_context.consume()

        raise ParseError("Unclosed comment", parser=parse_comment, context=context)

    return parse_comment
