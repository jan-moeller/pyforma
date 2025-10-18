from .parse_context import ParseContext
from .parse_result import ParseResult
from .parser import parser


@parser
def nothing(context: ParseContext) -> ParseResult[None]:
    return ParseResult.make_success(context=context, result=None)
