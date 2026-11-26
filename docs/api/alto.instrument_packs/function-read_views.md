---
title: read_views
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-read_views/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_views(
    value: object,
    *,
    files: PackFiles,
    where: str,
) -> tuple[PackView, ...]
```

{% endraw %}{% include api-source.html name="read_views" line=1205 %}{% raw %}

</div>

Validate the optional extra pictures of an instrument, such as a
view of its back.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The instrument's ``views`` entry, an object from a view name to a pack-relative picture path, or None. |
| `files` | `PackFiles` | The pack's files. Keyword-only. |
| `where` | `str` | The instrument's qualified key, used in error messages. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of PackView` | The views, in the order the manifest lists them. Empty when none were declared. |

**Raises**

- *ValueError*: If the entry is not a short object of valid names and readable pictures.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> # noinspection PyTypeChecker
>>> read_views(
...     None, files=None, where="pack.v.va"
... )
()
```
{% endraw %}
