---
title: KeyboardCard
parent: alto.ui.app_settings
api_module: alto.ui.app_settings
package: alto.ui
permalink: /api/alto.ui.app_settings/class-keyboardcard/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyboardCard(
    style: keyboard_styles.KeyboardStyle,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeyboardCard" line=543 %}{% raw %}

</div>

Bases: `PreviewCard`

A selectable tile that previews a keyboard style: a short stretch of
keys drawn in that style.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `style_key` | `str` | The key of the style the card stands for. |
| `keys` | `KeyboardWidget` | The preview. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = KeyboardCard(
...     keyboard_styles.BY_KEY["modern"]
... )
>>> card.style_key
'modern'
```

**Constructor**

Build the card for a keyboard style.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `style` | `KeyboardStyle` | The style to preview; its label and a few words about it are shown under the keys. |
| `parent` | `QWidget or None, default None` | The widget that owns the card. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> # noinspection PyUnresolvedReferences
>>> KeyboardCard(
...     keyboard_styles.BY_KEY["classic"]
... ).keys.style_override.key
'classic'
```

## KeyboardCard.show_style

<div class="api-signature" markdown="1">

```python
def show_style(style: keyboard_styles.KeyboardStyle) -> None
```

{% endraw %}{% include api-source.html name="KeyboardCard.show_style" line=622 %}{% raw %}

</div>

Redraw the preview in a style.

The custom card follows the colors being edited.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `style` | `KeyboardStyle` | The style to preview. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = KeyboardCard(
...     keyboard_styles.BY_KEY["classic"]
... )
>>> card.show_style(
...     keyboard_styles.BY_KEY["modern"]
... )
>>> # noinspection PyUnresolvedReferences
>>> card.keys.style_override.key
'modern'
```
{% endraw %}
