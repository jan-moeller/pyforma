# Examples

## Avoiding template reparsing using `TemplateContext`

```python
from pathlib import Path
from pyforma import Template, TemplateContext

context = TemplateContext(base_path=Path("dir/with/templates/"))

# Read and parse file relative to base_path
template = context.load_template(Path("my_template.txt"))
# ... later: Resolves template from cache; no parsing happens here
template2 = context.load_template(Path("my_template.txt"))
```

## Getting convenient defaults using `DefaultTemplateContext`

```python
from pyforma import Template, DefaultTemplateContext

context = DefaultTemplateContext()
# This template has two unresolved identifiers: sum and numbers
template = Template("total = {{ sum(numbers) }}")
# Render using context, which comes with the sum function
print(context.render(template, variables=dict(numbers=[1, 2, 3])))
# Prints "total = 6"
```

## Inserting `Template`s into `Template`s

```python
from pyforma import Template

template = Template("<div>{{extension}}</div>")
extension = Template("<p>{{first}}</p><p>{{second}}</p>")
template2 = template.substitute(dict(extension=extension))
# template2 is equivalent to Template("<div><p>{{first}}</p><p>{{second}}</p></div>")
print(template2.render(dict(first="Hello, World!", second="This is an example.")))
# Prints "<div><p>Hello, World!</p><p>This is an example.</p></div>"
```
