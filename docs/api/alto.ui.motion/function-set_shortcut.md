---
title: set_shortcut
parent: alto.ui.motion
api_module: alto.ui.motion
package: alto.ui
permalink: /api/alto.ui.motion/function-set_shortcut/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def set_shortcut(
    button: QAbstractButton,
    *,
    key: QKeySequence | str,
) -> None
```

{% endraw %}{% include api-source.html name="set_shortcut" line=572 %}{% raw %}

</div>

Give a button a key that presses it. In the app Qt handles the key;
with instant motion it clicks the button at once.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `button` | `QAbstractButton` | The button. |
| `key` | `QKeySequence or str` | The key, such as "Return" or "Shift+C". Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtWidgets import QPushButton
>>> button = QPushButton("Undo")
>>> set_shortcut(button, key="Backspace")
>>> button.shortcut().toString()
'Backspace'
>>> set_instant(True)
>>> held = QPushButton("Answer")
>>> set_shortcut(
...     held, key="Return"
... )  # in a test: the key clicks it at once
>>> set_instant(False)
```
{% endraw %}
