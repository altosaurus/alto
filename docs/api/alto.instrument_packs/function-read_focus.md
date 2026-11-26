---
title: read_focus
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-read_focus/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_focus(
    value: object,
    *,
    width: int,
    height: int,
) -> tuple[float, float, float, float]
```

{% endraw %}{% include api-source.html name="read_focus" line=885 %}{% raw %}

</div>

Validate a picture question's region to show.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The manifest entry: a list of left, top, width and height in picture pixels. |
| `width` | `int` | The picture's width in pixels. Keyword-only. |
| `height` | `int` | The picture's height in pixels. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of float` | Left, top, width and height. |

**Raises**

- *ValueError*: If the entry is not four numbers describing a region of at least 40 pixels inside the picture.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_focus(
...     [0, 10, 200, 100], width=400, height=300
... )
(0.0, 10.0, 200.0, 100.0)
```
{% endraw %}
