---
title: read_picture_file
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-read_picture_file/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_picture_file(
    files: PackFiles,
    *,
    name: object,
) -> tuple[Path, tuple[int, int]]
```

{% endraw %}{% include api-source.html name="read_picture_file" line=1160 %}{% raw %}

</div>

Find and check a picture in the pack.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `files` | `PackFiles` | The pack's files. |
| `name` | `object` | The manifest entry: a pack-relative path to a PNG, WebP, or JPEG picture. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of Path and tuple of int` | The picture file and its width and height in pixels. |

**Raises**

- *ValueError*: If the picture is missing, unreadable, or larger than 16 megapixels.
{% endraw %}
