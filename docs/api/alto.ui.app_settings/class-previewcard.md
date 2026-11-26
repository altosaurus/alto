---
title: PreviewCard
parent: alto.ui.app_settings
api_module: alto.ui.app_settings
package: alto.ui
permalink: /api/alto.ui.app_settings/class-previewcard/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PreviewCard(
    preview: QWidget,
    *,
    key: str,
    title: str,
    blurb: str,
    height: int,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="PreviewCard" line=368 %}{% raw %}

</div>

Bases: `QPushButton`

A selectable tile that previews a style: a picture drawn in it, with
its name and a few words about it underneath.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `style_key` | `str` | The key of the style the card stands for. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = PreviewCard(
...     QLabel("♪"),
...     key="demo",
...     title="Demo",
...     blurb="A short note.",
...     height=120,
... )
>>> (
...     card.style_key,
...     card.isCheckable(),
...     card.height(),
... )
('demo', True, 120)
```

**Constructor**

Build the card around its preview.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `preview` | `QWidget` | The picture of the style. Clicks pass through it to the card. |
| `key` | `str` | The key of the style. Keyword-only. |
| `title` | `str` | The style's name, shown in bold. Keyword-only. |
| `blurb` | `str` | A few words about the style, shown in small gray type. Keyword-only. |
| `height` | `int` | The card's height before zooming; every card is 232 wide. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns the card. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> label = QLabel("♪")
>>> card = PreviewCard(
...     label,
...     key="demo",
...     title="Demo",
...     blurb="",
...     height=120,
... )
>>> label.testAttribute(
...     Qt.WidgetAttribute.WA_TransparentForMouseEvents
... )
True
```
{% endraw %}
