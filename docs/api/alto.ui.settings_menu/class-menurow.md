---
title: MenuRow
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/class-menurow/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
MenuRow(
    title: str,
    *,
    chevron: bool = True,
    tall: bool = False,
)
```

{% endraw %}{% include api-source.html name="MenuRow" line=948 %}{% raw %}

</div>

Bases: `QPushButton`

A menu row: title on the left, current value and a chevron on the
right.

A `tall` row puts a picture on a second line of its own, using the
full width, for summaries that need room to be
readable.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `tall` | `bool` | Whether the row has a second line. |
| `title` | `QLabel` | The title. |
| `value` | `QLabel` | The current value, shown on the right. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row = MenuRow("Range", tall=True)
>>> row.tall, row.title.text()
(True, '<b>Range</b>')
```

**Constructor**

Build the row.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `title` | `str` | The row's title. |
| `chevron` | `bool, default True` | Show a chevron on the right, to say it opens a page. Keyword-only. |
| `tall` | `bool, default False` | Give the row a second line for a picture. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MenuRow("Clefs").minimumHeight()
48
```

## MenuRow.attach

<div class="api-signature" markdown="1">

```python
def attach(widget: QWidget) -> None
```

{% endraw %}{% include api-source.html name="MenuRow.attach" line=1049 %}{% raw %}

</div>

Put a widget in the row.

Just after the value text, or (in a tall row) centered on its
own line below.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `widget` | `QWidget` | The widget, usually a small picture of the current choice. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row = MenuRow("Clefs")
>>> picture = ClefPictures(["treble"])
>>> row.attach(picture)
>>> # noinspection PyUnresolvedReferences
>>> row.layout().indexOf(picture)
2
```

## MenuRow.fit

<div class="api-signature" markdown="1">

```python
def fit() -> None
```

{% endraw %}{% include api-source.html name="MenuRow.fit" line=1078 %}{% raw %}

</div>

Make a tall row as high as its contents need.

A button does not size itself to a layout inside it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row = MenuRow("Range", tall=True)
>>> row.attach(QLabel("a picture"))
>>> row.minimumHeight() > 0
True
```
{% endraw %}
