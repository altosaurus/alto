---
title: NotationStyle
parent: alto.ui.notation
api_module: alto.ui.notation
package: alto.ui
permalink: /api/alto.ui.notation/class-notationstyle/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
NotationStyle(
    key: str,
    *,
    label: str,
    note: str,
    font: str | None,
    line: float = 1.4,
)
```

{% endraw %}{% include api-source.html name="NotationStyle" line=31 %}{% raw %}

</div>

One look for the music: a font and how heavy the staff lines are.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `key` | `str` | The identifier saved in the settings. |
| `label` | `str` | The name shown in the interface. Keyword-only. |
| `note` | `str` | A few words on where this look comes from. Keyword-only. |
| `font` | `str or None` | A key in engraving.json, or None for the built-in Noto Music drawing. Keyword-only. |
| `line` | `float, default 1.4` | The staff line weight in pixels, for the built-in drawing (the SMuFL fonts state their own). Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> style = BY_KEY["noto"]
>>> style.label, style.font
('Noto Music', None)
```
{% endraw %}
