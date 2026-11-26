---
title: PackFiles
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/class-packfiles/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PackFiles(
    manifest: Path,
    *,
    archive: ZipFile | None,
)
```

{% endraw %}{% include api-source.html name="PackFiles" line=529 %}{% raw %}

</div>

Resolve only manifest-declared assets, from a folder or the root of
a ZIP.

**Constructor**

Keep folder assets in place and give ZIP assets private,
generated filenames.

**Raises**

- *ValueError*: If the ZIP lacks a root manifest or repeats an entry name.

## PackFiles.asset

<div class="api-signature" markdown="1">

```python
def asset(
    name: object,
    *,
    extensions: tuple[str, ...],
) -> Path
```

{% endraw %}{% include api-source.html name="PackFiles.asset" line=564 %}{% raw %}

</div>

Resolve a regular asset from this pack.

**Returns**

| Type | Description |
| --- | --- |
| `Path` | A local file usable by the image and audio readers. |

**Raises**

- *ValueError*: If the path is missing, outside the pack, or has an unsupported type or size.

## PackFiles.manifest

<div class="api-signature" markdown="1">

```python
def manifest() -> dict
```

{% endraw %}{% include api-source.html name="PackFiles.manifest" line=628 %}{% raw %}

</div>

Read the API version and top-level pack object.

**Returns**

| Type | Description |
| --- | --- |
| `dict` | Version two manifest. |

**Raises**

- *ValueError*: If the format is unsupported or the pack lacks a display name.
{% endraw %}
