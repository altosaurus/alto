---
title: ExerciseSettingsPanel
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/class-exercisesettingspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class ExerciseSettingsPanel(QWidget)
```

{% endraw %}{% include api-source.html name="ExerciseSettingsPanel" line=1540 %}{% raw %}

</div>

What every exercise's settings pane has in common: it says when a
setting has been edited.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `changed` | `Signal` | Emitted after any setting is edited that changes what is asked, so the exercise asks a new question. |
| `restyled` | `Signal` | Emitted after a setting is edited that changes only how the exercise looks, so the question stays and the picture is drawn again. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = ExerciseSettingsPanel()
>>> got = []
>>> _ = panel.changed.connect(
...     lambda: got.append(1)
... )
>>> panel.changed.emit()
True
>>> got
[1]
```

## ExerciseSettingsPanel.refresh_limits

<div class="api-signature" markdown="1">

```python
def refresh_limits(
    mode: str,
    *,
    self_grading: bool = False,
) -> None
```

{% endraw %}{% include api-source.html name="ExerciseSettingsPanel.refresh_limits" line=1603 %}{% raw %}

</div>

Update scheduling controls for the active scheduler and profile.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `mode` | `str` | Selected question scheduler. |
| `self_grading` | `bool` | Disable Next Question when a passing grade advances the exercise. |

**Examples**

```text
Switching to ASRS hides the row and leaves its submenu.
```
{% endraw %}
