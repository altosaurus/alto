---
title: image_point
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-image_point/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def image_point(
    value: object,
    *,
    width: int,
    height: int,
) -> Point
```

{% endraw %}{% include api-source.html name="image_point" line=668 %}{% raw %}

</div>

Validate a marker or string endpoint against the image dimensions.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of float` | Coordinates in original image pixels. |

**Raises**

- *ValueError*: If either coordinate is missing or outside the picture.
{% endraw %}
