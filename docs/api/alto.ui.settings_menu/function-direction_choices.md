---
title: direction_choices
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/function-direction_choices/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def direction_choices(
    cfg: settings.ScaleIdentificationSettings | settings.ScaleConstructionSettings,
    *,
    edited: Callable[[], None],
) -> QWidget
```

{% endraw %}{% include api-source.html name="direction_choices" line=2941 %}{% raw %}

</div>

Choose the direction of a scale.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `ScaleIdentificationSettings or ScaleConstructionSettings` | The exercise settings that store the selected motion. |
| `edited` | `callable` | Save the edit and refresh the exercise. |

**Returns**

| Type | Description |
| --- | --- |
| `QWidget` | A pair of mutually exclusive Ascending and Descending radio buttons. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = settings.ScaleIdentificationSettings()
>>> choices = direction_choices(
...     cfg, edited=lambda: None
... )
>>> next(
...     b
...     for b in choices.findChildren(
...         QRadioButton
...     )
...     if b.text() == "Descending"
... ).click()
>>> cfg.motion
'descending'
```
{% endraw %}
