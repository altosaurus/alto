---
title: read_picture
parent: alto.lessons.packs
api_module: alto.lessons.packs
package: alto.lessons
permalink: /api/alto.lessons.packs/function-read_picture/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_picture(
    spec: object,
    *,
    where: str,
    pack_id: str,
    instruments: Mapping[str, PackInstrument],
) -> PicturePosition | FingerboardPosition
```

{% endraw %}{% include api-source.html name="read_picture" line=480 %}{% raw %}

</div>

Build a step's instrument picture: a note on a string, or a marked
place on the picture.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `spec` | `object` | The picture's manifest object. Give ``string`` and ``note`` for a note on a string, or ``point`` for a place. |
| `where` | `str` | Which lesson and step this is, for messages. Keyword-only. |
| `pack_id` | `str` | The plugin's id. Keyword-only. |
| `instruments` | `mapping of str to PackInstrument` | The plugin's instruments by qualified key. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `PicturePosition or FingerboardPosition` | What the step's picture shows. |

**Raises**

- *ValueError*: If the picture is malformed or refers to something the plugin does not declare.
{% endraw %}
