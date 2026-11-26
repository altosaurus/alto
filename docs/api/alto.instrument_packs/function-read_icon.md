---
title: read_icon
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-read_icon/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_icon(
    files: PackFiles,
    *,
    name: object,
) -> str
```

{% endraw %}{% include api-source.html name="read_icon" line=1029 %}{% raw %}

</div>

Read a plugin's tile icon: a plain SVG of simple shapes, redrawn in
the theme's ink.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `files` | `PackFiles` | The pack's files. |
| `name` | `object` | The manifest entry: a pack-relative path to an SVG file with the viewBox ``0 0 24 24``. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The shapes, with COLOR wherever the theme's ink goes, ready for `alto.ui.icons.svg_icon`. |

**Raises**

- *ValueError*: If the file is missing, too large, not an SVG of the right box, or uses anything but simple shapes (no scripts, images, styles, or links).

**Examples**

```text
The viola's icon is its own silhouette traced from the museum
photograph.
```
{% endraw %}
