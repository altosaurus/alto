---
title: SchemeEditor
parent: alto.ui.circle_colors
api_module: alto.ui.circle_colors
package: alto.ui
permalink: /api/alto.ui.circle_colors/class-schemeeditor/
---
{% raw %}
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

| Attribute | Type | Description |
| --- | --- | --- |
| `saved` | `Signal` | Emitted with the record when Save is clicked. |
| `deleted` | `Signal` | Emitted with the scheme's key when Delete is clicked (only an existing scheme can be deleted). |
| `canceled` | `Signal` | Emitted when Cancel is clicked. |
| `name` | `QLineEdit` | The name. |
| `mode` | `QComboBox` | How the colors are made: a key of `MODES` is each item's data. |
| `wedges` | `QComboBox` | Whether the wedges are dark, with light names, or light, with dark names. |
| `swatches` | `list of QPushButton` | One button for each color the mode takes; the others are hidden. |
| `preview` | `SchemeThumb` | The picture of the scheme as it is. |

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

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(SchemeEditor().swatches)
3
```

## SchemeEditor.load

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

| Parameter | Type | Description |
| --- | --- | --- |
| `record` | `CustomRecord or None` | The scheme to edit, or None to start a new one. |
| `taken` | `list of CustomRecord` | The user's schemes, so that a new one gets a key none of them has. Keyword-only. |

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

## SchemeEditor.record

<div class="api-signature" markdown="1">

```python
def record() -> CustomRecord
```

{% endraw %}{% include api-source.html name="SchemeEditor.record" line=551 %}{% raw %}

</div>

Return the scheme as it is being edited.

**Returns**

| Type | Description |
| --- | --- |
| `CustomRecord` | Its key, name, mode, colors and whether its wedges are light. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> editor = SchemeEditor()
>>> editor.load(None, taken=[])
>>> editor.record()["colors"]
['#1fa7c9', '#2f6bd0', '#6a4fe0']
```

## SchemeEditor.set_color

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

| Parameter | Type | Description |
| --- | --- | --- |
| `index` | `int` | Which color of the mode: 0, 1 or 2. |
| `color` | `str` | The color, "#rrggbb". Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> editor = SchemeEditor()
>>> editor.load(None, taken=[])
>>> editor.set_color(0, color="#ff0000")
>>> editor.record()["colors"][0]
'#ff0000'
```
{% endraw %}
