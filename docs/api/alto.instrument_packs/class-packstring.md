---
title: PackString
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/class-packstring/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PackString(
    pitch: str,
    nut: Point,
    bridge: Point,
)
```

{% endraw %}{% include api-source.html name="PackString" line=27 %}{% raw %}

</div>

One open pitch with its nut and bridge locations in the original
image pixels.

## PackString.point

<div class="api-signature" markdown="1">

```python
def point(half_steps: int) -> Point
```

{% endraw %}{% include api-source.html name="PackString.point" line=37 %}{% raw %}

</div>

Locate the pitch along the photographed string.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of float` | Image coordinates measured from the top left. |
{% endraw %}
