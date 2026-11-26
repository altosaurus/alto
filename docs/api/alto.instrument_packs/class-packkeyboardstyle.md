---
title: PackKeyboardStyle
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/class-packkeyboardstyle/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PackKeyboardStyle(
    colors: tuple[tuple[str, str | tuple[str, str]], ...] = (),
    numbers: tuple[tuple[str, float], ...] = (),
)
```

{% endraw %}{% include api-source.html name="PackKeyboardStyle" line=192 %}{% raw %}

</div>

How a plugin's keyboards look: the colors of the keys and case, and
the proportions of the keys.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `colors` | `tuple of tuple of str and str or tuple of str` | Each color field the plugin set, with its value as ``#rrggbb``. A natural or sharp key has two, for its top and bottom. |
| `numbers` | `tuple of tuple of str and float` | Each numeric field the plugin set, with its value. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> style = PackKeyboardStyle(
...     (("cap", "#eee3c8"),),
...     (("length", 4.5),),
... )
>>> dict(style.colors), dict(style.numbers)
({'cap': '#eee3c8'}, {'length': 4.5})
```
{% endraw %}
