from dataclasses import dataclass

from .template_syntax_config import BlockSyntaxConfig
from .parser import parser, Parser
from .parse_context import ParseContext
from .parse_error import ParseError
from .parse_result import ParseResult


@dataclass
class Comment:
    """Tagged string for comments."""

    text: str


def comment(syntax: BlockSyntaxConfig) -> Parser[Comment]:
    """Creates a comment parser using the provided open and close markers

    Args:
        syntax: Syntax config to use

    Returns:
        The comment parser.
    """

    @parser(name="comment")
    def parse_comment(context: ParseContext) -> ParseResult[Comment]:
        cur_context = context

        if not cur_context[:].startswith(syntax.open):
            raise ParseError(
                f"expected {syntax.open} to start a comment",
                parser=parse_comment,
                context=context,
            )

        cur_context = cur_context.consume(len(syntax.open))

        result = ""
        while not cur_context.at_eof():
            if cur_context[:].startswith(syntax.open):
                r = parse_comment(cur_context)
                result += f"{syntax.open}{r.result.text}{syntax.close}"
                cur_context = r.context
            elif cur_context[:].startswith(syntax.close):
                return ParseResult(
                    context=cur_context.consume(len(syntax.close)),
                    result=Comment(result),
                )
            else:
                result += cur_context.peek()
                cur_context = cur_context.consume()

        raise ParseError("Unclosed comment", parser=parse_comment, context=context)

    return parse_comment
