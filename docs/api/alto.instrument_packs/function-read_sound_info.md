---
title: read_sound_info
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-read_sound_info/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_sound_info(
    value: object,
    *,
    where: str,
    pack_name: str,
) -> InstrumentInfo | None
```

{% endraw %}{% include api-source.html name="read_sound_info" line=709 %}{% raw %}

</div>

Validate the optional facts a pack gives about where its recordings
came from.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The instrument's ``sound_info`` entry, or None when it has none. |
| `where` | `str` | The instrument's qualified key, used in error messages. Keyword-only. |
| `pack_name` | `str` | The pack's display name, shown as the source when the entry gives none. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `InstrumentInfo or None` | The facts for the Sound settings, or None when the instrument declared none. |

**Raises**

- *ValueError*: If an entry is not text, is too long, contains markup, or if the link is not an https address.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> info = read_sound_info(
...     {"summary": "A viola."},
...     where="pack.v.va",
...     pack_name="Viola",
... )
>>> info.source if info else None
'Viola'
>>> read_sound_info(
...     None,
...     where="pack.v.va",
...     pack_name="Viola",
... ) is None
True
```
{% endraw %}
