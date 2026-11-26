---
title: KeyboardBuilder
parent: alto.ui.app_settings
api_module: alto.ui.app_settings
package: alto.ui
permalink: /api/alto.ui.app_settings/class-keyboardbuilder/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyboardBuilder(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="KeyboardBuilder" line=649 %}{% raw %}

</div>

Bases: `QFrame`

Rows for coloring each part of a keyboard.

Each has a swatch that opens the color picker, and chips for colors
named after materials. Changing anything selects
the Custom style.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `changed` | `Signal` | Emitted after a part is recolored. |
| `swatches` | `dict of str to QPushButton` | The swatch of each part ("naturals", "sharps", "case", "felt" and "caps"). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> builder = KeyboardBuilder()
>>> sorted(builder.swatches)
['caps', 'case', 'felt', 'naturals', 'sharps']
```

**Constructor**

Build the rows and show each part's current color.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns the builder. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardBuilder().swatches[
...     "naturals"
... ].width()
46
```

## KeyboardBuilder.refresh

<div class="api-signature" markdown="1">

```python
def refresh() -> None
```

{% endraw %}{% include api-source.html name="KeyboardBuilder.refresh" line=795 %}{% raw %}

</div>

Show each part's current color on its swatch.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> builder = KeyboardBuilder()
>>> builder.refresh()
>>> builder.swatches[
...     "naturals"
... # a color is set, so the swatch shows it, not "none"
... ].text()
''
```
{% endraw %}
