---
title: edge_color
parent: alto.ui.keyboard_styles
api_module: alto.ui.keyboard_styles
package: alto.ui
permalink: /api/alto.ui.keyboard_styles/function-edge_color/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def edge_color(
    style: KeyboardStyle,
    *,
    midi: int,
    black: bool,
) -> QColor
```

{% endraw %}{% include api-source.html name="edge_color" line=677 %}{% raw %}

</div>

Return the outline color for a key.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `style` | `KeyboardStyle` | The style. |
| `midi` | `int` | The key's MIDI number. Keyword-only. |
| `black` | `bool` | True for a sharp or flat, False for a natural. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QColor` | The outline color. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> edge_color(
...     BY_KEY["classic"], midi=60, black=False
... ).name()
'#9a9a9f'
>>> edge_color(
...     BY_KEY["classic"], midi=61, black=True
... ).name()
'#111114'
```
{% endraw %}
