---
title: label_with_picture
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/function-label_with_picture/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def label_with_picture(
    button: QAbstractButton,
    *,
    picture: _Picture,
    name: str,
) -> None
```

{% endraw %}{% include api-source.html name="label_with_picture" line=615 %}{% raw %}

</div>

Label a checkbox or radio button with a picture instead of text.

The name stays as the tooltip and the accessible name.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `button` | `QAbstractButton` | The button to label. |
| `picture` | `_Picture` | The picture (a clef, a note value ...). Keyword-only. |
| `name` | `str` | What it is called. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> box = QCheckBox()
>>> label_with_picture(
...     box,
...     picture=ClefPictures(["treble"]),
...     name="Treble",
... )
>>> box.toolTip(), box.accessibleName()
('Treble', 'Treble')
```
{% endraw %}
