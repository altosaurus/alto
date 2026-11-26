---
title: StyleCard
parent: alto.ui.app_settings
api_module: alto.ui.app_settings
package: alto.ui
permalink: /api/alto.ui.app_settings/class-stylecard/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
StyleCard(
    style: notation.NotationStyle,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="StyleCard" line=465 %}{% raw %}

</div>

Bases: `PreviewCard`

A selectable tile that previews a notation style: a short phrase on
a staff, drawn in that style.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `style_key` | `str` | The key of the style the card stands for. |
| `staff` | `StaffWidget` | The preview. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = StyleCard(notation.BY_KEY["leland"])
>>> card.style_key, card.isCheckable()
('leland', True)
```

**Constructor**

Build the card for a notation style.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `style` | `NotationStyle` | The style to preview; its label and a few words about it are shown under the staff. |
| `parent` | `QWidget or None, default None` | The widget that owns the card. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> StyleCard(
...     notation.BY_KEY["bravura"]
... ).width()
232
```
{% endraw %}
