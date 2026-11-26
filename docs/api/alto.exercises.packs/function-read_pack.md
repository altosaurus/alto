---
title: read_pack
parent: alto.exercises.packs
api_module: alto.exercises.packs
package: alto.exercises
permalink: /api/alto.exercises.packs/function-read_pack/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_pack(path: Path) -> list[type[PackExercise]]
```

{% endraw %}{% include api-source.html name="read_pack" line=1425 %}{% raw %}

</div>

Read and validate every exercise before making any of them
available.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `path` | `Path` | A pack.json file or a ZIP containing it at the root. |

**Returns**

| Type | Description |
| --- | --- |
| `list of type` | Exercise classes with stable identifiers. |

**Raises**

- *ValueError*: If the file or one of its exercises has an invalid format.

**Examples**

```text
The viola example contributes note identification and instrument
anatomy exercises.
```
{% endraw %}
