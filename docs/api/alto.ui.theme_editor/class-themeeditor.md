---
title: ThemeEditor
parent: alto.ui.theme_editor
api_module: alto.ui.theme_editor
package: alto.ui
permalink: /api/alto.ui.theme_editor/class-themeeditor/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ThemeEditor(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="ThemeEditor" line=58 %}{% raw %}

</div>

Bases: `QWidget`

A form to make a theme, or change one: its name, and the colors of
its light and dark versions.

A small picture of each version follows the colors as they are
chosen. Choosing a theme in the "Start from" list takes its
colors at once.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `name_edit` | `QLineEdit` | The theme's name. |
| `start_from` | `FieldComboBox` | The themes whose colors can be taken; choosing one takes them. |
| `colors` | `dict of str to dict of str to str` | The colors being made, by "light" or "dark", and then by part. |
| `buttons` | `dict of str to dict of str to QPushButton` | The button of each color, which opens the color picker, by version and part. |
| `pictures` | `dict of str to ThemeThumb` | The picture of each version. |
| `save_button` | `QPushButton` | Saves the theme. |
| `delete_button` | `QPushButton` | Deletes the theme; it is only there for a theme that has been saved. |
| `saved` | `Signal` | Emitted with the theme's key when it is saved. |
| `canceled` | `Signal` | Emitted when the editing is given up. |
| `deleted` | `Signal` | Emitted with the theme's key when it is deleted. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ThemeEditor().save_button.text()
'Save'
```

**Constructor**

Build the form, ready to make a new theme.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sorted(ThemeEditor().colors)
['dark', 'light']
```

## ThemeEditor.eventFilter

<div class="api-signature" markdown="1">

```python
def eventFilter(
    watched: QObject,
    event: QEvent,
) -> bool
```

{% endraw %}{% include api-source.html name="ThemeEditor.eventFilter" line=245 %}{% raw %}

</div>

Light up the code written beside a color while the pointer is
over the color.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `watched` | `QObject` | The object the event is for. |
| `event` | `QEvent` | The event. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | Always False: the color button still gets the event. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> editor = ThemeEditor()
>>> button = editor.buttons["light"]["accent"]
>>> _ = editor.eventFilter(
...     button, QEvent(QEvent.Type.Enter)
... )
>>> "bold" in editor._values["light"][
...     "accent"
... ].styleSheet()
True
>>> _ = editor.eventFilter(
...     button, QEvent(QEvent.Type.Leave)
... )
>>> "bold" in editor._values["light"][
...     "accent"
... ].styleSheet()
False
```

## ThemeEditor.load

<div class="api-signature" markdown="1">

```python
def load(record: ThemeRecord | None) -> None
```

{% endraw %}{% include api-source.html name="ThemeEditor.load" line=291 %}{% raw %}

</div>

Fill the form from a theme that was saved, or for a new one that
starts as Studio.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `record` | `ThemeRecord or None` | The theme to change; None for a new theme. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> editor = ThemeEditor()
>>> editor.load(None)
>>> (
...     editor.delete_button.isHidden(),
...     editor.name_edit.text(),
... )
(True, 'My theme')
```

## ThemeEditor.record

<div class="api-signature" markdown="1">

```python
def record() -> ThemeRecord
```

{% endraw %}{% include api-source.html name="ThemeEditor.record" line=340 %}{% raw %}

</div>

Give the theme as it is now in the form.

**Returns**

| Type | Description |
| --- | --- |
| `ThemeRecord` | The key, the name and the colors of both versions. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> editor = ThemeEditor()
>>> editor.record()["light"][
...     "window"
... ] == editor.colors["light"]["window"]
True
```
{% endraw %}
