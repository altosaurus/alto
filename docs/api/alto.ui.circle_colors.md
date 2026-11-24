---
title: alto.ui.circle_colors
parent: api
package: alto.ui
permalink: /api/alto.ui.circle_colors/
---
{% raw %}
The pages of the circle of fifths settings that choose its colors: a
grid of schemes to pick from, and an editor to make one.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.circle_schemes import preset
>>> SchemeThumb(preset("midnight")).scheme.name
'Midnight'
```

## blank

<div class="api-signature" markdown="1">

```python
def blank(key: str) -> CustomRecord
```

{% endraw %}{% include api-source.html name="blank" line=66 %}{% raw %}

</div>

Make the scheme a new one starts as: colors by key signature, from
cyan through blue to indigo, on dark wedges.

**Parameters**

- `key` (*str*): The key the new scheme gets.

**Returns**

- *CustomRecord*: The scheme.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     blank("custom-3")["id"],
...     blank("custom-3")["mode"],
... )
('custom-3', 'signature')
```

## SchemeThumb

<div class="api-signature" markdown="1">

```python
SchemeThumb(
    scheme: Scheme,
    *,
    size: int = THUMB,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="SchemeThumb" line=98 %}{% raw %}

</div>

Bases: `QPushButton`

A small picture of the circle in a color scheme, to click to choose
the scheme.

**Attributes**

- `scheme` (*Scheme*): The scheme it shows and chooses.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.circle_schemes import preset
>>> thumb = SchemeThumb(preset("paper"))
>>> thumb.isCheckable(), thumb.toolTip()
(True, 'Pastel wedges of every hue with dark names, which deepen
when lit.')
```

**Constructor**

Build the picture.

**Parameters**

- `scheme` (*Scheme*): The color scheme to draw.
- `size` (*int, default 112*): Its width and height in pixels. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns it. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.circle_schemes import preset
>>> SchemeThumb(
...     preset("paper"), size=80
... ).width()
80
```

### SchemeThumb.sizeHint

<div class="api-signature" markdown="1">

```python
def sizeHint() -> QSize
```

{% endraw %}{% include api-source.html name="SchemeThumb.sizeHint" line=153 %}{% raw %}

</div>

Return the size it asks for.

**Returns**

- *QSize*: The size it was built with.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.circle_schemes import preset
>>> SchemeThumb(
...     preset("paper"), size=90
... ).sizeHint().width()
90
```

### SchemeThumb.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="SchemeThumb.paintEvent" line=172 %}{% raw %}

</div>

Draw the circle, with one cell asked and its relative lit, and a
ring around it when it is the chosen scheme.

**Parameters**

- `_` (*QPaintEvent*): The paint request.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.circle_schemes import preset
>>> SchemeThumb(
...     preset("midnight")
... ).grab().isNull()
False
```

## SchemePage

<div class="api-signature" markdown="1">

```python
SchemePage(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="SchemePage" line=228 %}{% raw %}

</div>

Bases: `QWidget`

The page that lists the color schemes: the presets, the user's own,
and a button to make another.

**Attributes**

- `chosen` (*Signal*): Emitted with the key of the scheme that was clicked.
- `new` (*Signal*): Emitted when "Create your own" is clicked.
- `edit_asked` (*Signal*): Emitted with the key of one of the user's schemes when its Edit button is clicked.
- `thumbs` (*dict of str to SchemeThumb*): The picture of each scheme, by its key.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = SchemePage()
>>> page.load(current="midnight", customs=[])
>>> (
...     page.thumbs["midnight"].isChecked(),
...     len(page.thumbs),
... )
(True, 14)
```

**Constructor**

Build the page, empty until `load` is called.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> SchemePage().thumbs
{}
```

### SchemePage.load

<div class="api-signature" markdown="1">

```python
def load(
    *,
    current: str,
    customs: list[CustomRecord],
) -> None
```

{% endraw %}{% include api-source.html name="SchemePage.load" line=279 %}{% raw %}

</div>

Fill the page: a picture and a name for each scheme, with the
current one marked.

**Parameters**

- `current` (*str*): The key of the chosen scheme. Keyword-only.
- `customs` (*list of CustomRecord*): The user's own schemes. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = SchemePage()
>>> from alto.circle_schemes import record_of
>>> mine = record_of(
...     "custom-1",
...     name="Mine",
...     mode="single",
...     colors=["#2f6bd0"],
... )
>>> page.load(
...     current="custom-1", customs=[mine]
... )
>>> (
...     page.thumbs["custom-1"].isChecked(),
...     page.thumbs["midnight"].isChecked(),
... )
(True, False)
```

## SchemeEditor

<div class="api-signature" markdown="1">

```python
SchemeEditor(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="SchemeEditor" line=404 %}{% raw %}

</div>

Bases: `QWidget`

The editor for a color scheme of the user's own: a name, how its
colors are made, and the colors.

The colors are what a cell looks like when lit; the quiet cells are
made from them. A picture shows the result as it is
edited.

**Attributes**

- `saved` (*Signal*): Emitted with the record when Save is clicked.
- `deleted` (*Signal*): Emitted with the scheme's key when Delete is clicked (only an existing scheme can be deleted).
- `canceled` (*Signal*): Emitted when Cancel is clicked.
- `name` (*QLineEdit*): The name.
- `mode` (*QComboBox*): How the colors are made: a key of `MODES` is each item's data.
- `wedges` (*QComboBox*): Whether the wedges are dark, with light names, or light, with dark names.
- `swatches` (*list of QPushButton*): One button for each color the mode takes; the others are hidden.
- `preview` (*SchemeThumb*): The picture of the scheme as it is.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> editor = SchemeEditor()
>>> editor.load(None, taken=[])
>>> (
...     editor.record()["mode"],
...     editor.record()["id"],
... )
('signature', 'custom-1')
```

**Constructor**

Build the editor.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(SchemeEditor().swatches)
3
```

### SchemeEditor.load

<div class="api-signature" markdown="1">

```python
def load(
    record: CustomRecord | None,
    *,
    taken: list[CustomRecord],
) -> None
```

{% endraw %}{% include api-source.html name="SchemeEditor.load" line=515 %}{% raw %}

</div>

Start editing a scheme, or a new one.

**Parameters**

- `record` (*CustomRecord or None*): The scheme to edit, or None to start a new one.
- `taken` (*list of CustomRecord*): The user's schemes, so that a new one gets a key none of them has. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> editor = SchemeEditor()
>>> editor.load(None, taken=[])
>>> (
...     editor.name.text(),
...     editor.delete_button.isHidden(),
... )
('My colors', True)
```

### SchemeEditor.record

<div class="api-signature" markdown="1">

```python
def record() -> CustomRecord
```

{% endraw %}{% include api-source.html name="SchemeEditor.record" line=551 %}{% raw %}

</div>

Return the scheme as it is being edited.

**Returns**

- *CustomRecord*: Its key, name, mode, colors and whether its wedges are light.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> editor = SchemeEditor()
>>> editor.load(None, taken=[])
>>> editor.record()["colors"]
['#1fa7c9', '#2f6bd0', '#6a4fe0']
```

### SchemeEditor.set_color

<div class="api-signature" markdown="1">

```python
def set_color(
    index: int,
    *,
    color: str,
) -> None
```

{% endraw %}{% include api-source.html name="SchemeEditor.set_color" line=570 %}{% raw %}

</div>

Set one of the colors.

**Parameters**

- `index` (*int*): Which color of the mode: 0, 1 or 2.
- `color` (*str*): The color, "#rrggbb". Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> editor = SchemeEditor()
>>> editor.load(None, taken=[])
>>> editor.set_color(0, color="#ff0000")
>>> editor.record()["colors"][0]
'#ff0000'
```
{% endraw %}
