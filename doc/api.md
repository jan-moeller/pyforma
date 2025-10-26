# API

## `pyforma.Template(content, /, *, syntax)`

The primary template class.

**Parameters**:

- `content: str | Path`:  
  If `str`, parses the string as a template.  
  If `Path`, reads the file at that path and parses it as a template.
- `syntax: TemplateSyntaxConfig | None `:  
  Optional syntax definition.

**Return Value**:

Returns the template object.

**Exceptions**:

- `ValueError`: The provided input is not a valid template.
- `OSError`: If a path is passed and the file cannot be opened

### `pyforma.Template.unresolved_identifiers() -> set[str]`

Reports all identifiers that need to be substituted to render the template.

**Return Value**:

Returns the set of all remaining identifiers in the template.

### `pyforma.Template.substitute(variables, *, keep_comments, renderers) -> Template`

Partially substitutes variables in the template and evaluates expressions that can be evaluated.

**Parameters**:

- `variables: dict[str, Any]`:  
  Dictionary mapping variable identifiers to their values.
- `keep_comments: bool`:  
  By default, comments are kept until the final rendering. Set to `False` to strip all comments.
- `renderers: Sequence[tuple[type, Callable[[Any], str]]] | None`:  
  Optional sequence of renderers for stringification. By default, only `str`, `int` and `float` are
  rendered to `str` during template substitution. This argument can be used to automatically
  render additional types. Alternatively, the template needs to explicitly format other types as
  `str`.

**Return Value**:

A new template identical to self, but with the provided `variables` substituted.

**Exceptions**:

- `ValueError`: An expression evaluates to a type that can not be rendered.
- `TypeError`:  Variable substitution leads to an unsupported operation, such as an operator
  not supported for that type.

### `pyforma.Template.render(variables, *, renderers) -> str`

Renders a template to a string.

**Parameters**:

- `variables: dict[str, Any] | None`:  
  Optional dictionary mapping variable identifiers to their values.
- `renderers: Sequence[tuple[type, Callable[[Any], str]]] | None`:  
  Optional sequence of renderers for stringification. See `substitute()` for details.

**Return Value**:

The rendered string with all variables substituted.

**Exceptions**:

- `ValueError`:
    - Some unresolved variables remain after substitution.
    - An expression evaluates to a type that can not be rendered.
- `TypeError`:  
  Variable substitution leads to an unsupported operation, such as an operator
  not supported for that type.

## `pyforma.TemplateSyntaxConfig(comment, expression, environment)`

Template syntax configuration class.

**Parameters**:

- `comment: BlockSyntaxConfig`:  
  Configuration for comment blocks.
  Defaults to `BlockSyntaxConfig("{#", "#}")`.
- `expression: BlockSyntaxConfig`:  
  Configuration for expression blocks.
  Defaults to `BlockSyntaxConfig("{{", "}}")`.
- `environment: BlockSyntaxConfig`:  
  Configuration for environment blocks.
  Defaults to `BlockSyntaxConfig("{%", "%}")`.

**Exceptions**:

- `ValueError`: The configured symbols are not sufficiently distinct.

## `pyforma.BlockSyntaxConfig(open, close)`

Class used for configuring the syntax of a block type.

**Parameters**:

- `open: str`:  
  Open block syntax. Must not be empty.
- `close: str`:  
  Close block syntax. Must not be empty.

**Exceptions**:

- `ValueError`:
    - Either of the parameters is empty.
    - The provided parameters are identical.

## `pyforma.TemplateContext(*, default_variables, default_renderers, base_path)`

This class can hold some default variables and renderers, and manages loading of templates
from disk.

**Parameters**:

- `default_variables: dict[str, Any] | None`:
  Optional variables to automatically pass in during template substitution.
- `default_renderers: Sequence[tuple[type, Callable[[Any], str]]] | None`:
  Optional renderers to use after template substitution.
- `base_path: Path | None`:
  Optional path of the root directory to resolve relative template paths from.

### `pyforma.TemplateContext.load_template(path, /, *, syntax) -> Template`

Loads a template from disk and caches it. Every unique file/syntax combination is only
loaded and parsed once, even if loaded via this function repeatedly.

**Parameters**:

- `path: Path`:
  Path to the template file. If this path is relative, it is assumed to be relative to
  the context's base path. If no base path was provided, the cwd is used as reference point.
- `syntax`:
  Optional syntax configuration.

**Return Value**:

The loaded template.

**Exceptions**:

- `ValueError`: The file contents cannot be parsed.
- `OSError`: The file cannot be read.

### `pyforma.TemplateContext.unresolved_identifiers(template) -> set[str]`

Returns the set of unresolved identifiers in the provided template when using this
context for substitution. This may result in a subset of identifiers when compared to
the template's `unresolved_identifiers()` method, if the template contains identifiers
provided via the context's defaults.

**Parameters**:

- `template: Template`:  
  The template to find unresolved identifiers in

**Return Value**:

A set of unresolved identifiers in the template without identifiers set as variables in
this context.

### `pyforma.TemplateContext.substitute(template, *, variables, keep_comments, renderers) -> Template`

Substitutes variables into the provided template, additionally using the context's defaults,
and returns the result.

**Parameters**:

- `template: Template`:  
  The template to substitute into.
- `variables: dict[str, Any] | None`:  
  Optional variables to substitute, in addition to the defaults.
- `keep_comments: bool`:  
  Optionally, whether to keep comments in the result.
- `renderers: Sequence[tuple[type, Callable[[Any], str]]] | None`:  
  Optional renderers to use for substitution, in addition to the defaults.

**Return Value**:

The resulting template.

**Exceptions**:

- `ValueError`: A variable cannot be substituted due to missing renderer.
- `TypeError`: Variable substitution leads to an unsupported operation, such as an operator
  not supported for that type.

### `pyforma.TemplateContext.render(template, *, variables, renderers) -> str`

Renders the provided template to string.

**Parameters**:

- `template: Template`:  
  The template to render.
- `variables: dict[str, Any] | None`:  
  Optional variables to substitute.
- `renderers: Sequence[tuple[type, Callable[[Any], str]]] | None`:  
  Optional renderers to use for substitution.

**Return Value**:

The rendered template as string.

**Exceptions**:

- `ValueError`:
    - Some variables in the template remain unresolved after substitution.
    - A variable cannot be substituted due to missing renderer.
- `TypeError`:  
  Variable substitution leads to an unsupported operation, such as an operator
  not supported for that type.

## `pyforma.DefaultTemplateContext(*, default_variables, default_renderers, base_path)`

A `TemplateContext` with preset defaults. The following variables are preset, all referring
to the respective python stdlib functionality.

- `abs`
- `aiter`
- `all`
- `anext`
- `any`
- `ascii`
- `bin`
- `bool`
- `breakpoint`
- `bytearray`
- `bytes`
- `callable`
- `chr`
- `complex`
- `dict`
- `divmod`
- `enumerate`
- `filter`
- `float`
- `format`
- `frozenset`
- `getattr`
- `hasattr`
- `hash`
- `hex`
- `id`
- `int`
- `isinstance`
- `issubclass`
- `iter`
- `len`
- `list`
- `map`
- `max`
- `memoryview`
- `min`
- `next`
- `object`
- `oct`
- `open`
- `ord`
- `pow`
- `range`
- `repr`
- `reversed`
- `round`
- `set`
- `slice`
- `sorted`
- `str`
- `sum`
- `tuple`
- `type`
- `vars`
- `zip`
- `Path`
- `date`
- `datetime`
- `timedelta`
- `deque`
- `namedtuple`
- `chain`
- `islice`
- `starmap`
- `product`
- `sqrt`
- `log`
- `sin`
- `cos`
- `tan`
- `hypot`
- `mean`
- `median`
- `stdev`
- `Decimal`
- `re`

