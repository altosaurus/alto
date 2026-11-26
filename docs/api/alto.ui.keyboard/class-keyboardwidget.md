---
title: KeyboardWidget
parent: alto.ui.keyboard
api_module: alto.ui.keyboard
package: alto.ui
permalink: /api/alto.ui.keyboard/class-keyboardwidget/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyboardWidget(
    parent: QWidget | None = None,
    *,
    label_middle_c: bool = False,
)
```

{% endraw %}{% include api-source.html name="KeyboardWidget" line=137 %}{% raw %}

</div>

Bases: `QWidget`

A piano keyboard drawn to real proportions that can highlight one or
more keys.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `lo` | `int` | The lowest key shown, as a MIDI number. |
| `hi` | `int` | The highest key shown, as a MIDI number. |
| `highlight` | `int or None` | The key to highlight. |
| `additional_highlights` | `set of int` | Other keys highlighted together with `highlight`. |
| `style_override` | `KeyboardStyle or None` | A fixed style, for the preview cards in the settings; otherwise the style chosen in the settings is used. |
| `pad` | `float` | The frame padding, in pixels. |
| `max_key_width` | `float` | The widest a key may be, in pixels. Smaller when something else (the key signature) shares the page. |
| `highlight_color` | `QColor` | The color of the highlighted key. |
| `key_length` | `float` | How long a natural key is drawn, in key widths. A piano's is 6.2, and a harpsichord's keys can be shorter. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keyboard = KeyboardWidget()
>>> (
...     keyboard.lo,
...     keyboard.hi,
... )  # C3 to C5, until another range is shown
(48, 72)
```

**Constructor**

Create a keyboard showing the default range, with no key
highlighted.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns the keyboard. |
| `label_middle_c` | `bool, default False` | Mark middle C and its neighboring pair of black keys for an introductory lesson. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardWidget().highlight is None
True
```

## KeyboardWidget.style

<div class="api-signature" markdown="1">

```python
@property
def style() -> KeyboardStyle
```

{% endraw %}{% include api-source.html name="KeyboardWidget.style" line=231 %}{% raw %}

</div>

Return the style the keyboard is drawn in.

**Returns**

| Type | Description |
| --- | --- |
| `KeyboardStyle` | The fixed style if one is set, otherwise the style chosen in the settings. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keyboard = KeyboardWidget()
>>> keyboard.style_override = (
...     keyboard_styles.BY_KEY["modern"]
... )
>>> keyboard.style.label
'Modern piano'
```

## KeyboardWidget.refit

<div class="api-signature" markdown="1">

```python
def refit() -> None
```

{% endraw %}{% include api-source.html name="KeyboardWidget.refit" line=252 %}{% raw %}

</div>

Size and redraw the keyboard after the style changes.

Some styles have a taller strip above the keys.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keyboard = KeyboardWidget()
>>> keyboard.refit()
>>> keyboard.height() > 0
True
```

## KeyboardWidget.full_width

<div class="api-signature" markdown="1">

```python
def full_width() -> int
```

{% endraw %}{% include api-source.html name="KeyboardWidget.full_width" line=290 %}{% raw %}

</div>

Measure the keyboard case when its keys reach their maximum
width.

**Returns**

| Type | Description |
| --- | --- |
| `int` | Width of the case in pixels, including padding. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardWidget().full_width()
590
```

## KeyboardWidget.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyboardWidget.resizeEvent" line=375 %}{% raw %}

</div>

Change the height to match the new width, since keys are drawn
to real proportions.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QResizeEvent` | The resize that happened. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keyboard = KeyboardWidget()
>>> keyboard.show()
>>> keyboard.resize(300, 300)
>>> keyboard.height()  # narrower, so shorter
143
```

## KeyboardWidget.show_key

<div class="api-signature" markdown="1">

```python
def show_key(
    midi: int | None,
    *,
    span: tuple[int, int] | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="KeyboardWidget.show_key" line=396 %}{% raw %}

</div>

Highlight a key, and optionally choose the range of keys to
show.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `midi` | `int or None` | The key to highlight, or None for no highlight. |
| `span` | `tuple of (int, int) or None, default None` | The lowest and highest key to show; it is widened to whole white keys. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keyboard = KeyboardWidget()
>>> keyboard.show_key(
...     60, span=(49, 71)
... )  # C#3 is widened to C3
>>> (
...     keyboard.lo,
...     keyboard.hi,
...     keyboard.highlight,
... )
(48, 71, 60)
```

## KeyboardWidget.show_keys

<div class="api-signature" markdown="1">

```python
def show_keys(
    midis: list[int],
    *,
    span: tuple[int, int] | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="KeyboardWidget.show_keys" line=441 %}{% raw %}

</div>

Highlight several keys together, clearing highlights from the
previous question.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `midis` | `list of int` | The MIDI numbers to highlight; an empty list clears all highlights. |
| `span` | `tuple of (int, int) or None, default None` | The inclusive range to display, widened to white keys. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keyboard = KeyboardWidget()
>>> keyboard.show_keys([60, 66], span=(48, 72))
>>> (
...     keyboard.highlight,
...     keyboard.additional_highlights,
... )
(60, {66})
>>> keyboard.show_key(62)
>>> keyboard.additional_highlights
set()
```

## KeyboardWidget.set_highlight_color

<div class="api-signature" markdown="1">

```python
def set_highlight_color(color: QColor) -> None
```

{% endraw %}{% include api-source.html name="KeyboardWidget.set_highlight_color" line=477 %}{% raw %}

</div>

Choose the color of the highlighted key and redraw.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `color` | `QColor` | The color. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keyboard = KeyboardWidget()
>>> keyboard.set_highlight_color(
...     QColor("#2e7d32")
... )
>>> keyboard.highlight_color.name()
'#2e7d32'
```

## KeyboardWidget.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="KeyboardWidget.paintEvent" line=499 %}{% raw %}

</div>

Draw the case, the keys, the highlighted key and the style's
extras.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `_` | `QPaintEvent` | The paint request; the whole widget is always redrawn. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keyboard = KeyboardWidget()
>>> keyboard.show_key(60)
>>> keyboard.grab().isNull()
False
```
{% endraw %}
