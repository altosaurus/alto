---
title: FieldComboBox
parent: alto.ui.dropdown
api_module: alto.ui.dropdown
package: alto.ui
permalink: /api/alto.ui.dropdown/class-fieldcombobox/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
FieldComboBox(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="FieldComboBox" line=31 %}{% raw %}

</div>

Bases: `QComboBox`

A shared dropdown whose field and popup both use Alto's rounded
styling.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picker = FieldComboBox()
>>> picker.addItems(["m2", "M2", "m3"])
>>> picker.currentText()
'm2'
```

**Constructor**

Create a themed dropdown and prepare to clip its popup corners.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns the dropdown. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> FieldComboBox().maxVisibleItems()
12
```

## FieldComboBox.showPopup

<div class="api-signature" markdown="1">

```python
def showPopup() -> None
```

{% endraw %}{% include api-source.html name="FieldComboBox.showPopup" line=62 %}{% raw %}

</div>

Open the dropdown with a rounded outer window, including its
native container.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picker = FieldComboBox()
>>> picker.addItems(["P4", "P5"])
>>> picker.showPopup()
>>> picker.view().window().mask().isEmpty()
False
>>> picker.hidePopup()
```
{% endraw %}
