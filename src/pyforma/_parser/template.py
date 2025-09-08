from .non_empty import non_empty
from .alternation import alternation
from .text import text
from .repetition import repetition
from .parser import Parser
from .comment import Comment, comment


def template(open_comment: str, close_comment: str) -> Parser[list[str | Comment]]:
    return repetition(
        alternation(
            non_empty(text(open_comment)),
            comment(open_comment, close_comment),
        )
    )
