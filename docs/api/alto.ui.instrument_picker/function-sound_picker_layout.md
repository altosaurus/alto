---
title: sound_picker_layout
parent: alto.ui.instrument_picker
api_module: alto.ui.instrument_picker
package: alto.ui
permalink: /api/alto.ui.instrument_picker/function-sound_picker_layout/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def sound_picker_layout(
    picker: QWidget,
    *,
    choices: QListWidget,
    card: QFrame,
) -> None
```

{% endraw %}{% include api-source.html name="sound_picker_layout" line=68 %}{% raw %}

</div>

Place sound choices beside their detail card in Settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `picker` | `QWidget` | The instrument or metronome picker. |
| `choices` | `QListWidget` | The list of sounds. |
| `card` | `QFrame` | The selected sound's details and preview. |

**Examples**

```text
Resizing the picker gives extra width to the detail card.
```
{% endraw %}
