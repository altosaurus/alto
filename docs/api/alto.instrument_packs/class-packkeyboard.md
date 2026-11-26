---
title: PackKeyboard
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/class-packkeyboard/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PackKeyboard(
    name: str,
    lowest: str,
    highest: str,
)
```

{% endraw %}{% include api-source.html name="PackKeyboard" line=103 %}{% raw %}

</div>

One keyboard of an instrument, drawn by Alto from the range of keys
the plugin gives it.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `name` | `str` | What the plugin calls this keyboard, such as "Lower manual". |
| `lowest` | `str` | The pitch of the lowest key, a natural such as "E1". |
| `highest` | `str` | The pitch of the highest key, a natural such as "F6". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keys = PackKeyboard("Manual", "C4", "E4")
>>> keys.naturals
3
>>> keys.has("C#4"), keys.has("E#4")
(True, False)
```

## PackKeyboard.naturals

<div class="api-signature" markdown="1">

```python
@property
def naturals() -> int
```

{% endraw %}{% include api-source.html name="PackKeyboard.naturals" line=131 %}{% raw %}

</div>

Count the natural keys.

**Returns**

| Type | Description |
| --- | --- |
| `int` | The number of natural keys from the lowest to the highest, both included. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> PackKeyboard("M", "C4", "C5").naturals
8
```

## PackKeyboard.has

<div class="api-signature" markdown="1">

```python
def has(name: str) -> bool
```

{% endraw %}{% include api-source.html name="PackKeyboard.has" line=152 %}{% raw %}

</div>

Report whether a pitch is a key on this keyboard.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `name` | `str` | A pitch such as "F#3". |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True when the keyboard has that key, natural or sharp. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> board = PackKeyboard("M", "C4", "E4")
>>> (
...     board.has("C#4"),
...     board.has("E#4"),
...     board.has("F4"),
...     board.has("Db4"),
... )
(True, False, False, False)
```
{% endraw %}
