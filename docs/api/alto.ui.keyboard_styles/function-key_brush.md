---
title: key_brush
parent: alto.ui.keyboard_styles
api_module: alto.ui.keyboard_styles
package: alto.ui
permalink: /api/alto.ui.keyboard_styles/function-key_brush/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def key_brush(
    style: KeyboardStyle,
    *,
    midi: int,
    black: bool,
    y: float,
    height: float,
) -> QBrush
```

{% endraw %}{% include api-source.html name="key_brush" line=608 %}{% raw %}

</div>

Return the fill for a key.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `style` | `KeyboardStyle` | The style. |
| `midi` | `int` | The key's MIDI number. Keyword-only. |
| `black` | `bool` | True for a sharp or flat, False for a natural. Keyword-only. |
| `y` | `float` | The key's top edge, in pixels. Keyword-only. |
| `height` | `float` | The key's height, in pixels. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QBrush` | A solid color, a top-to-bottom gradient, or (for styles that color keys by note) a color that depends on the note. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> key_brush(
...     BY_KEY["classic"],
...     midi=60,
...     black=False,
...     y=0,
...     height=100,
... ).color().name()
'#fbfbfc'
>>> key_brush(
...     BY_KEY["modern"],
...     midi=60,
...     black=False,
...     y=0,
...     height=100,
... ).gradient() is not None
True
```
{% endraw %}
