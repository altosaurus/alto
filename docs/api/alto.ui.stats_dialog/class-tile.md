---
title: Tile
parent: alto.ui.stats_dialog
api_module: alto.ui.stats_dialog
package: alto.ui
permalink: /api/alto.ui.stats_dialog/class-tile/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Tile(
    caption: str,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="Tile" line=229 %}{% raw %}

</div>

Bases: `QFrame`

One headline number with its caption.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `value` | `QLabel` | The big number. |
| `caption` | `QLabel` | What the number is. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> tile = Tile("Questions answered")
>>> tile.value.text()
'–'
>>> tile.show_value("12")
>>> tile.value.text()
'12'
```

**Constructor**

Create a tile showing a dash until it is given a value.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `caption` | `str` | What the number is, shown under it. |
| `parent` | `QWidget or None, default None` | The widget that owns the tile. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> tile = Tile("Days practiced")
>>> tile.caption.text()
'Days practiced'
```

## Tile.show_value

<div class="api-signature" markdown="1">

```python
def show_value(text: str) -> None
```

{% endraw %}{% include api-source.html name="Tile.show_value" line=285 %}{% raw %}

</div>

Show a number (or any text) in the tile.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | What to show. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> tile = Tile("Typical first answer")
>>> tile.show_value("7.6 s")
>>> tile.value.text()
'7.6 s'
```
{% endraw %}
