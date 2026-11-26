---
title: arrow_button
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/function-arrow_button/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def arrow_button(
    kind: Qt.ArrowType,
    *,
    tip: str,
) -> QToolButton
```

{% endraw %}{% include api-source.html name="arrow_button" line=168 %}{% raw %}

</div>

Make a small arrow button that repeats while it is held.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `kind` | `Qt.ArrowType` | Which way the arrow points. |
| `tip` | `str` | The tooltip. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `QToolButton` | The button. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> button = arrow_button(
...     Qt.ArrowType.UpArrow,
...     tip="Raise the lowest note",
... )
>>> button.toolTip(), button.autoRepeat()
('Raise the lowest note', True)
```
{% endraw %}
