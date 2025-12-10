# Template Syntax

PyForma borrows the default syntax from Jinja:

- **Comments** are enclosed in `{#`, `#}`: `{# This is a comment #}`.
- **Expressions** are enclosed in `{{`, `}}`: `{{ x + y }}`.
- **Environments** are enclosed in `{%`, `{%`: `{% for e in things %}{{e}}{% endfor %}`.

## Expressions

Expressions in PyForma are inspired by Python, but not identical. For the most part,
PyForma expressions are a subset of Python expressions.

- **Identifier**: Python-identifiers are expressions. The most common way to associate
  them with values is via the `variables` argument of `template.substitute()`.
- **Integers**: Integer syntax is identical to Python's: `123` is an `int`, and the
  prefixes `0x`, `0o`, and `0b` turn it into a hex, octal, or binary integer. Underscores
  can be used to separate digits: `123_456`.
- **Floats**: Similarly, `123.45` is a float. Scientific syntax like `123e-4` is supported.
- **Strings**: Anything enclosed by `"` or `'` is treated as a string.
- **Booleans**: `True` and `False` are the two boolean constants.
- **None**: `None` indicates, well, `None`.
- **Lists**: `[ expr1, expr2, ... ]` instantiates a list. Note that generator expressions
  like in Python are not supported.
- **Dictionaries**: `{ expr1: expr2, ...}` instantiates a dictionary. As with lists, generator
  expressions are not supported.
- **Parentheses**: Expressions can be parenthesized to enforce operation order: `(expr)`.
- **Unary operators**: The unary operators are: `+`, `-`, `~`, `not`.
- **Binary operators**: The binary operators are: `**`, `+`, `-`, `*`, `/`, `//`, `%`, `@`,
  `|`, `&`, `^`, `<<`, `>>`, `in`, `==`, `!=`, `<=`, `<`, `>=`, `>`, `not in`, `and`, `or`.
  Note that the comparison operators are chained, so `a < b < c` is equivalent to
  `a < b and b < c`.
- **Slicing**: As in regular python, `expr[start:stop:step]` slices containers that support it.
- **Indexing**: Similarly, `expr[i]` is used to index into a container.
- **Function Calls**: The python call syntax `expr(arg_expr, ..., kw=arg_expr, ...)` is supported.
- **Attribute Access**: The dot-operator works as expected: `expr.attribute`.
- **Lambda Functions**: Short functions can be defined using the `lambda arg1, ...: expr` syntax.
- **If-Expressions**: Unlike Python, PyForma supports conditions of the form
  `if expr1: expr2 elif expr3: expr4 else: expr5`. The `elif` and `else` cases are optional. If
  no case matches, the expression evaluates to `None`.
- **For-Expressions**: Analogous to if expressions, for expressions also use statement syntax:
  `for identifier in expr1: expr2`. Instead of a plain identifier, the iterable can be decomposed
  immediately: `for a, b in expr1: a + b`. Neither `continue` not `break` are supported.
- **With-Expressions**: Since the template language is not meant to introduce mutable state, and
  therefore doesn't have assignment operators, the one way to introduce temporary names is the
  with expression: `with name=expr1: expr2`. It can also be used to destructure values:
  `with a, b=c: a+b`. It is possible to introduce several names in one go, by separating them via
  `;`: `with a,b=c; d=e+4: a+b+d`
- **Template Strings**: Unrelated to the Python feature of the same name, PyForma supports
  template string expressions, enclosed in \```. These are evaluated as templates, and automatically
  rendered to strings. Example: ` ```Hello {{name}}!``` `.

The operator precedence follows Python's example.

## Environments

Environments are generally introduced with a keyword, and closed by a block called "end<keyword>".
In the opening example, the `for`-environment was introduced using that keyword, and closed using
`endfor`.

The following environments are supported:

### The "Literal"-Environment

The "literal"-environment can be used to simply emit its content as string:

```
{% literal %}This is a {{literal}} string{% endliteral %}
```

Note, that the `{{literal}}` isn't an expression, it's just that string, _literally_.

If the content should contain a string that conflicts with the `endliteral` marker, an additional
keyword can be provided:

```
{% literal wow %}This is a {% endliteral %} string{% endliteral wow %}
```

### The "With"-Environment

This environment can be used to set some variables for a part of the template.

```
{% with a=40+2 %}The answer is {{a}}.{% endwith %}
```

Multiple values can be separated via `;`:

```
{% with a=40; b=2 %}The answer is {{a+b}}.{% endwith %}
```

This also supports python-like destructuring:

```
{% with a, b = a_tuple %}The answer is {{a+b}}.{% endwith %}
```

The usual scoping rules apply. If a "with"-environment defines a variable `a`, then any outer
`a` is shadowed and inaccessible within the environment. It is possible to shadow an outer
variable using the same name:

```
{% with a = a + 2 %}The answer is {{a}}.{% endwith %}
```

Here, after the `endwith`, any expressions or environments still observe `a` with its
original value.

### The "If"-Environment

To conditionally add some output, use the "if"-environment. It follows the obvious syntax:

```
{% if expr1 %} This is only included if the `expr1` is truthy.
{% elif expr2 %} This is only included if the `expr2` is truthy.
{% else %} This is only included if none of the above cases were truthy.
{% endif %}
```

Only the `if` block is required; the `elif` and `else` blocks are optional. If necessary,
multiple `elif` blocks are supported.

### The "For"-Environment

This environment can be used to add a template block several times.

```
{% for value in expr %}
- {{value}}
{% endfor %}
```

Similar to the "with"-environment, destructuring is supported:

```
{% for k, v in expr.items() %}
- {{k}}: {{v}}
{% endfor %}
```