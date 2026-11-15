---
title: alto.ui.theme_editor
parent: api
package: alto.ui
order: 53
permalink: /api/alto.ui.theme_editor/
---
{% raw %}
The editor for a theme of the user's own: a name, and a colour for every part of its light and dark versions.

**Examples**

```pycon
>>> editor = ThemeEditor()
>>> editor.load(None)
>>> editor.record()["name"]
'My theme'
```

## theme_of

```python
def theme_of(
    colours: dict[str, str],
    *,
    dark: bool,
) -> CustomTheme
```

Make a theme from a set of colours, to draw a picture of it.

**Parameters**

- `colours` (*dict of str to str*): A colour for every part, as "#rrggbb".
- `dark` (*bool*): True if it is the dark version. Keyword-only.

**Returns**

- *CustomTheme*: The theme, without a key or a name of its own.

**Examples**

```pycon
>>> theme_of({part: "#102030" for part in PARTS}, dark=True).window
'#102030'
```

## ThemeEditor

```python
ThemeEditor(parent: QWidget | None = None)
```

Bases: `QWidget`

A form to make a theme, or change one: its name, and the colours of its light and dark versions.

A small picture of each version follows the colours as they are chosen. Choosing a theme in the "Start from" list takes its
colours at once.

**Attributes**

- `name_edit` (*QLineEdit*): The theme's name.
- `start_from` (*QComboBox*): The themes whose colours can be taken; choosing one takes them.
- `colours` (*dict of str to dict of str to str*): The colours being made, by "light" or "dark", and then by part.
- `buttons` (*dict of str to dict of str to QPushButton*): The button of each colour, which opens the colour picker, by version and part.
- `pictures` (*dict of str to ThemeThumb*): The picture of each version.
- `save_button` (*QPushButton*): Saves the theme.
- `delete_button` (*QPushButton*): Deletes the theme; it is only there for a theme that has been saved.
- `saved` (*Signal*): Emitted with the theme's key when it is saved.
- `cancelled` (*Signal*): Emitted when the editing is given up.
- `deleted` (*Signal*): Emitted with the theme's key when it is deleted.

**Examples**

```pycon
>>> ThemeEditor().save_button.text()
'Save'
```

**Constructor**

Build the form, ready to make a new theme.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```pycon
>>> sorted(ThemeEditor().colours)
['dark', 'light']
```

### ThemeEditor.eventFilter

```python
def eventFilter(
    watched: QObject,
    event: QEvent,
) -> bool
```

Light up the code written beside a colour while the pointer is over the colour.

**Parameters**

- `watched` (*QObject*): The object the event is for.
- `event` (*QEvent*): The event.

**Returns**

- *bool*: Always False: the colour button still gets the event.

**Examples**

```pycon
>>> editor = ThemeEditor()
>>> button = editor.buttons["light"]["accent"]
>>> _ = editor.eventFilter(button, QEvent(QEvent.Type.Enter))
>>> "bold" in editor._values["light"]["accent"].styleSheet()
True
>>> _ = editor.eventFilter(button, QEvent(QEvent.Type.Leave))
>>> "bold" in editor._values["light"]["accent"].styleSheet()
False
```

### ThemeEditor.load

```python
def load(record: ThemeRecord | None) -> None
```

Fill the form from a theme that was saved, or for a new one that starts as Studio.

**Parameters**

- `record` (*ThemeRecord or None*): The theme to change; None for a new theme.

**Examples**

```pycon
>>> editor = ThemeEditor()
>>> editor.load(None)
>>> editor.delete_button.isHidden(), editor.name_edit.text()
(True, 'My theme')
```

### ThemeEditor.record

```python
def record() -> ThemeRecord
```

Give the theme as it is now in the form.

**Returns**

- *ThemeRecord*: The key, the name and the colours of both versions.

**Examples**

```pycon
>>> editor = ThemeEditor()
>>> editor.record()["light"]["window"] == editor.colours["light"]["window"]
True
```
{% endraw %}
