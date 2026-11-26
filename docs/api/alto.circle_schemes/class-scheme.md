---
title: Scheme
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/class-scheme/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Scheme(
    key: str,
    name: str,
    description: str,
    light: bool,
    cells: dict[str, tuple[Cell, ...]],
)
```

{% endraw %}{% include api-source.html name="Scheme" line=130 %}{% raw %}

</div>

A color scheme for the circle.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `key` | `str` | Its identifier, used to save the choice. |
| `name` | `str` | Its name, as the settings show it. |
| `description` | `str` | A sentence about it. |
| `light` | `bool` | Whether the wedges are light, with dark names, instead of dark with white names. |
| `cells` | `dict of str to tuple of (tuple of float, tuple of float)` | For each ring ("outer" and "inner"), the 12 cells' quiet and lit colors, clockwise from the top. |

## Scheme.color

<div class="api-signature" markdown="1">

```python
def color(
    ring: str,
    *,
    place: int,
    lift: float,
) -> tuple[float, float, float]
```

{% endraw %}{% include api-source.html name="Scheme.color" line=156 %}{% raw %}

</div>

Return the color of a cell as it is lit.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `ring` | `str` | "outer" or "inner". |
| `place` | `int` | The cell's place, clockwise from the top. Keyword-only. |
| `lift` | `float` | How lit it is, from 0 (quiet) to 1 (fully lit). Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of float` | Its red, green and blue, each from 0 to 1. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> red, green, blue = preset("spectrum").color(
...     "outer", place=0, lift=1.0
... )
>>> red > green and red > blue
True
>>> preset("spectrum").color(
...     "outer", place=6, lift=0.0
... )[0] < 0.2
True
```

## Scheme.names

<div class="api-signature" markdown="1">

```python
def names() -> dict[str, str]
```

{% endraw %}{% include api-source.html name="Scheme.names" line=201 %}{% raw %}

</div>

Return the colors of the names written on the wedges.

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to str` | "ink" (a key's name) and "muted" (its other name and its numeral), as "#rrggbb". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     preset("paper").names()["ink"],
...     preset("spectrum").names()["ink"],
... )
('#1b2030', '#f5f5f5')
```
{% endraw %}
