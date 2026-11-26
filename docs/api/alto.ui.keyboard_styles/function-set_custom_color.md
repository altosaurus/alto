---
title: set_custom_color
parent: alto.ui.keyboard_styles
api_module: alto.ui.keyboard_styles
package: alto.ui
permalink: /api/alto.ui.keyboard_styles/function-set_custom_color/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def set_custom_color(
    part: str,
    *,
    color: str | None,
) -> None
```

{% endraw %}{% include api-source.html name="set_custom_color" line=487 %}{% raw %}

</div>

Color one part of the custom keyboard and switch to the custom
style.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `part` | `str` | One of "naturals", "sharps", "case", "felt" or "caps". |
| `color` | `str or None` | A color such as '#336699', or None to leave an optional part (case, felt or caps) out. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> set_custom_color(
...     "naturals", color="#ffffff"
... )
>>> current().key, custom_colors()["naturals"]
('custom', '#ffffff')
>>> set_custom_color(
...     "naturals",
...     color=DEFAULT_CUSTOM["naturals"],
... )
>>> set_style(DEFAULT)
```
{% endraw %}
