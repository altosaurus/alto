---
title: alto.ui.dropdown
parent: api
package: alto.ui
permalink: /api/alto.ui.dropdown/
---
{% raw %}
Shared dropdown fields with rounded popup windows.

**Examples**

```pycon
>>> FieldComboBox().property("field")
True
```

## FieldComboBox

```python
FieldComboBox(parent: QWidget | None = None)
```

Bases: `QComboBox`

A shared dropdown whose field and popup both use Alto's rounded styling.

**Examples**

```pycon
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

```pycon
>>> FieldComboBox().maxVisibleItems()
12
```

### FieldComboBox.showPopup

```python
def showPopup() -> None
```

Open the dropdown with a rounded outer window, including its native container.

**Examples**

```pycon
>>> picker = FieldComboBox()
>>> picker.addItems(["P4", "P5"])
>>> picker.showPopup()
>>> picker.view().window().mask().isEmpty()
False
>>> picker.hidePopup()
```

## style_combo_popup

```python
def style_combo_popup(combo: QComboBox) -> None
```

Apply the shared field and popup styling to a dropdown, including one created by Qt.

**Parameters**

- `combo` (*QComboBox*): Field whose item view and outer popup should follow the application theme.
{% endraw %}
