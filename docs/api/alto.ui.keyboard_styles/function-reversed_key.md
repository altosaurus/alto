---
title: reversed_key
parent: alto.ui.keyboard_styles
api_module: alto.ui.keyboard_styles
package: alto.ui
permalink: /api/alto.ui.keyboard_styles/function-reversed_key/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def reversed_key(
    style: KeyboardStyle,
    *,
    midi: int,
) -> bool
```

{% endraw %}{% include api-source.html name="reversed_key" line=570 %}{% raw %}

</div>

Report whether a key has swapped colors, as the low preset keys of
an organ do.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `style` | `KeyboardStyle` | The style. |
| `midi` | `int` | The key's MIDI number. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if the style swaps colors below some key and this key is below it. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from dataclasses import replace
>>> reversed_key(BY_KEY["classic"], midi=40)
False
>>> reversed_key(
...     replace(
...         BY_KEY["classic"], reverse_below=50
...     ),
...     midi=40,
... )
True
```
{% endraw %}
