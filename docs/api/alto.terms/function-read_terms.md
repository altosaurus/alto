---
title: read_terms
parent: alto.terms
api_module: alto.terms
package: alto
permalink: /api/alto.terms/function-read_terms/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_terms(
    value: object,
    *,
    pack_id: str,
    pack_name: str,
    instruments: Mapping[str, PackInstrument],
    exercises: Mapping[str, str],
    lessons: Mapping[str, str],
) -> tuple[PluginTerm, ...]
```

{% endraw %}{% include api-source.html name="read_terms" line=152 %}{% raw %}

</div>

Validate the optional ``glossary`` list of a plugin manifest.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The manifest's ``glossary`` entry: a list of objects with a ``term`` and a ``definition``, and optionally a ``guide``, a ``picture`` with a ``caption``, and the ids of related ``exercises`` and ``lessons``. None when there is none. |
| `pack_id` | `str` | The plugin's id. Keyword-only. |
| `pack_name` | `str` | The plugin's display name. Keyword-only. |
| `instruments` | `mapping of str to PackInstrument` | The plugin's instruments by qualified key. Keyword-only. |
| `exercises` | `mapping of str to str` | The plugin's exercises, from the id the manifest uses to the key Alto registers it under. Keyword-only. |
| `lessons` | `mapping of str to str` | The plugin's lessons, from the id the manifest uses to the key Alto registers it under. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of PluginTerm` | The entries, in the order the manifest lists them. |

**Raises**

- *ValueError*: If an entry is malformed, repeats a term, or links to an exercise or lesson the plugin does not declare.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_terms(
...     None,
...     pack_id="demo",
...     pack_name="Demo",
...     instruments={},
...     exercises={},
...     lessons={},
... )
()
>>> read_terms(
...     [
...         {
...             "term": "nut",
...             "definition": "It holds the strings.",
...         }
...     ],
...     pack_id="demo",
...     pack_name="Demo",
...     instruments={},
...     exercises={},
...     lessons={},
... )[0].name
'nut'
```
{% endraw %}
