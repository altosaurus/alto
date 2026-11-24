---
title: alto.ui.dropdown
parent: api
package: alto.ui
permalink: /api/alto.ui.dropdown/
---
{% raw %}
Shared dropdown fields with rounded popup windows.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> FieldComboBox().property("field")
True
```

## FieldComboBox

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

- `parent` (*QWidget or None, default None*): The widget that owns the dropdown.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> FieldComboBox().maxVisibleItems()
12
```

### FieldComboBox.showPopup

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

## style_combo_popup

<div class="api-signature" markdown="1">

```python
def style_combo_popup(combo: QComboBox) -> None
```

{% endraw %}{% include api-source.html name="style_combo_popup" line=80 %}{% raw %}

</div>

Apply the shared field and popup styling to a dropdown, including
one created by Qt.

**Parameters**

- `combo` (*QComboBox*): Field whose item view and outer popup should follow the application theme.
{% endraw %}
