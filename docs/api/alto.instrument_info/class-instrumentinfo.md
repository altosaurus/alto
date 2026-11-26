---
title: InstrumentInfo
parent: alto.instrument_info
api_module: alto.instrument_info
package: alto
permalink: /api/alto.instrument_info/class-instrumentinfo/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
InstrumentInfo(
    summary: str,
    *,
    source: str,
    source_url: str,
    performer: str = '',
    recorded: str = '',
    includes: str = '',
    terms: str = IOWA_TERMS,
    note: str = '',
)
```

{% endraw %}{% include api-source.html name="InstrumentInfo" line=43 %}{% raw %}

</div>

The facts about where an instrument's recordings came from.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `summary` | `str` | One sentence on what the sound is. |
| `source` | `str` | Who made the recordings. Keyword-only. |
| `source_url` | `str` | Where the source describes them. Keyword-only. |
| `performer` | `str, default ""` | Who played. Keyword-only. |
| `recorded` | `str, default ""` | When and where it was recorded. Keyword-only. |
| `includes` | `str, default ""` | The articulation and dynamic that were used. Keyword-only. |
| `terms` | `str` | The terms the recordings may be used under. Keyword-only. |
| `note` | `str, default ""` | Anything a user should know about how Alto prepared the recordings. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> info = InstrumentInfo(
...     "A flute.",
...     source=IOWA,
...     source_url="https://example.org/flute",
... )
>>> info.terms == IOWA_TERMS
True
```
{% endraw %}
