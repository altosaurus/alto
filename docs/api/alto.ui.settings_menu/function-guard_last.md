---
title: guard_last
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/function-guard_last/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def guard_last(
    boxes: Iterable[QAbstractButton],
    *,
    enabled: bool = True,
) -> None
```

{% endraw %}{% include api-source.html name="guard_last" line=110 %}{% raw %}

</div>

Disable the only checked box, so that at least one choice always
stays selected.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `boxes` | `iterable of QAbstractButton` | The checkboxes of one choice. |
| `enabled` | `bool, default True` | False disables them all (for when the whole choice is switched off). Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> first, second = QCheckBox(), QCheckBox()
>>> first.setChecked(True)
>>> guard_last([first, second])
>>> first.isEnabled(), second.isEnabled()
(False, True)
>>> second.setChecked(True)
>>> guard_last([first, second])
>>> first.isEnabled()
True
```
{% endraw %}
