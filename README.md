# PyForma

A Python template engine featuring partial substitution.

[![Tests](https://github.com/jan-moeller/pyforma/actions/workflows/uv.yml/badge.svg)](https://github.com/jan-moeller/pyforma/actions/workflows/uv.yml)

## Example

```python
from pyforma import Template

template = Template("Hello, {{ subject }}! This is {{ lib_name }}.")
assert template.unresolved_identifiers() == {"subject", "lib_name"}

template = template.substitute({"lib_name": "PyForma"})
assert template.unresolved_identifiers() == {"subject"}

print(template.render({"subject": "World"}))  # Prints "Hello, World! This is PyForma."
```

## Features

- 100% Python
- Python-like expressions in templates
- Special-purpose environments for more expressive templates
- Templates can be inspected for what variables need to be substituted
- Can partially substitute variables within templates
- Rendering with undefined variables results in an error
- Fully statically typed

## Documentation

- [Examples](./doc/examples.md)
- [API Documentation](./doc/api.md)
- [Template Syntax Documentation](./doc/template_syntax.md)

## Alternatives

- **[Jinja2](https://pypi.org/project/Jinja2/)**:
  The de-facto standard Python template engine. It's popular, fast, expressive and extensible, but doesn't support
  partial template substitution.
- **[Mako](https://pypi.org/project/Mako/)**:
  Compiles templates to Python bytecode.
- **[Chameleon](https://pypi.org/project/Chameleon/)**:
  HTML/XML-compatible template engine.
- **[string.Template](https://docs.python.org/3/library/string.html#string.Template)**:
  The actual standard Python template engine. Pretty limited functionality.