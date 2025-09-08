from .parse_result import ParseResult
from .parse_error import ParseError
from .parse_context import ParseContext
from .parser import Parser, parser


def not_in(*parsers: Parser) -> Parser[str]:
    """Creates a parser consuming any input until one of the provided parsers matches

    Args:
        parsers: Parsers that end this parser if they match

    Returns:
        A parser that matches any input until one of the provided parsers matches. The input that ends matching is not
        consumed by this parser.
    """

    @parser
    def parse(context: ParseContext) -> ParseResult[str]:
        cur_context = context
        result = ""
        while not cur_context.at_eof():
            for p in parsers:
                try:
                    _ = p(cur_context)
                except ParseError:
                    pass
                else:
                    return ParseResult(context=cur_context, result=result)

            result += cur_context.peek()
            cur_context = cur_context.consume()

        return ParseResult(context=cur_context, result=result)

    return parse
