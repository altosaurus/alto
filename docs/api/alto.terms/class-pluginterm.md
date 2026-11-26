---
title: PluginTerm
parent: alto.terms
api_module: alto.terms
package: alto
permalink: /api/alto.terms/class-pluginterm/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PluginTerm(
    name: str,
    pack: str,
    definition: str,
    guide: str = '',
    picture: PicturePosition | None = None,
    caption: str = '',
    exercises: tuple[str, ...] = (),
    lessons: tuple[str, ...] = (),
)
```

{% endraw %}{% include api-source.html name="PluginTerm" line=55 %}{% raw %}

</div>

One glossary entry from a plugin.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `name` | `str` | The term, as listed. |
| `pack` | `str` | The plugin's display name. |
| `definition` | `str` | What the term means, as simple HTML. |
| `guide` | `str` | How to recognize or use it, as simple HTML. May be empty. |
| `picture` | `PicturePosition or None` | An instrument picture to show beside the text, with the term marked on it. None for none. |
| `caption` | `str` | The words under the picture. May be empty. |
| `exercises` | `tuple of str` | The registered keys of the exercises to offer as practice. |
| `lessons` | `tuple of str` | The keys of the lessons to offer. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> PluginTerm(
...     name="nut",
...     pack="Demo",
...     definition="It holds the strings.",
... ).exercises
()
```
{% endraw %}
