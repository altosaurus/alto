---
title: ToggleRow
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/class-togglerow/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ToggleRow(title: str)
```

{% endraw %}{% include api-source.html name="ToggleRow" line=1253 %}{% raw %}

</div>

Bases: `MenuRow`

A menu row with a switch that changes a setting in place instead of
opening a page.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `switched` | `Signal` | Emitted with the new state when the row is clicked. |
| `switch` | `Switch` | The switch. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row = ToggleRow("Accidentals")
>>> changes = []
>>> _ = row.switched.connect(changes.append)
>>> row.click()
>>> changes, row.isOn()
([True], True)
```

**Constructor**

Build the row with its switch off.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `title` | `str` | The row's title. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ToggleRow("Accidentals").isOn()
False
```

## ToggleRow.isOn

<div class="api-signature" markdown="1">

```python
def isOn() -> bool
```

{% endraw %}{% include api-source.html name="ToggleRow.isOn" line=1327 %}{% raw %}

</div>

Report whether the switch is on.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if on. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ToggleRow("Accidentals").isOn()
False
```

## ToggleRow.setOn

<div class="api-signature" markdown="1">

```python
def setOn(on: bool) -> None
```

{% endraw %}{% include api-source.html name="ToggleRow.setOn" line=1344 %}{% raw %}

</div>

Set the switch without announcing it, as when a setting is
loaded.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `on` | `bool` | The new state. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row = ToggleRow("Accidentals")
>>> row.setOn(True)
>>> row.isOn()
True
```
{% endraw %}
