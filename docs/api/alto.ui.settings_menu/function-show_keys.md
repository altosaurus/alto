---
title: show_keys
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/function-show_keys/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def show_keys(
    row: MenuRow,
    *,
    diagram: KeyDiagram,
    enabled: bool,
    keys: set[int],
) -> None
```

{% endraw %}{% include api-source.html name="show_keys" line=855 %}{% raw %}

</div>

Show the selected keys as a diagram in a menu row, or "Off" when key
signatures are switched off.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `row` | `MenuRow` | The menu row. |
| `diagram` | `KeyDiagram` | The diagram to update. Keyword-only. |
| `enabled` | `bool` | Whether key signatures are on. Keyword-only. |
| `keys` | `set of int` | The selected key signatures. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row_, diagram_ = (
...     MenuRow("Key signatures"),
...     KeyDiagram(),
... )
>>> show_keys(
...     row_,
...     diagram=diagram_,
...     enabled=False,
...     keys={0},
... )
>>> row_.value.text(), diagram_.isHidden()
('Off', True)
```
{% endraw %}
