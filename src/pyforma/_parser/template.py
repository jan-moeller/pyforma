from functools import cache

from pyforma._parser.transform_result import transform_success

from .parse_context import ParseContext
from .parse_result import ParseResult
from .environment import environment
from .sequence import sequence
from .eof import eof
from .expression_block import expression_block
from .non_empty import non_empty
from .text import text
from .parser import Parser, parser
from .comment import comment
from .template_syntax_config import TemplateSyntaxConfig
from pyforma._ast.expressions import Expression, ValueExpression, TemplateExpression


@cache
def inner_template(
    syntax: TemplateSyntaxConfig,
) -> Parser[TemplateExpression]:
    """Create a template parser

    Args:
        syntax: syntax config

    Returns:
        The template parser
    """

    @parser(name="template")
    def _template(context: ParseContext) -> ParseResult[TemplateExpression]:
        orig_context = context
        exprs: list[Expression] = []
        while not context.at_eof():
            if context[: len(syntax.expression.open)] == syntax.expression.open:
                result = expression_block(syntax, _template)(context)
                if result.is_failure:
                    return ParseResult.make_failure(
                        expected="expression block",
                        context=result.context,
                        cause=result,
                    )
                exprs.append(result.success.result)

            elif context[: len(syntax.environment.open)] == syntax.environment.open:
                result = environment(syntax, _template)(context)
                if result.is_failure:
                    break
                exprs.append(result.success.result)

            elif context[: len(syntax.comment.open)] == syntax.comment.open:
                result = comment(syntax.comment)(context)
                if result.is_failure:
                    return ParseResult.make_failure(
                        expected="comment block", context=result.context, cause=result
                    )

            elif context.in_template_expr and context[:3] == "```":
                break

            else:
                end_strs = [
                    syntax.comment.open,
                    syntax.expression.open,
                    syntax.environment.open,
                ]
                if context.in_template_expr:
                    end_strs.append("```")
                _parse_text = transform_success(
                    non_empty(text(*end_strs)),
                    transform=lambda s, c: ValueExpression(origin=c.origin(), value=s),
                )
                result = _parse_text(context)
                if result.is_failure:  # pragma: no cover # should never happen
                    return ParseResult.make_failure(
                        expected="text block", context=result.context, cause=result
                    )
                exprs.append(result.success.result)

            context = result.context

        return ParseResult.make_success(
            context=context,
            result=TemplateExpression(
                origin=orig_context.origin(), content=tuple(exprs)
            ),
        )

    return _template


@cache
def template(
    syntax: TemplateSyntaxConfig,
) -> Parser[TemplateExpression]:
    """Create a template parser

    Args:
        syntax: syntax config

    Returns:
        The template parser
    """

    _template = inner_template(syntax)

    return transform_success(sequence(_template, eof), transform=lambda s: s[0])
