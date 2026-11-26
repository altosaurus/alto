---
title: read_lessons
parent: alto.lessons.packs
api_module: alto.lessons.packs
package: alto.lessons
permalink: /api/alto.lessons.packs/function-read_lessons/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_lessons(
    value: object,
    *,
    pack_id: str,
    pack_name: str,
    instruments: Mapping[str, PackInstrument],
    exercises: Mapping[str, str],
    icons: Mapping[str, str] | None = None,
) -> tuple[Lesson, ...]
```

{% endraw %}{% include api-source.html name="read_lessons" line=114 %}{% raw %}

</div>

Validate the optional ``lessons`` list of a plugin manifest and
build its lessons.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The manifest's ``lessons`` entry, or None when the plugin has no lessons. |
| `pack_id` | `str` | The plugin's id, which qualifies each lesson's key. Keyword-only. |
| `pack_name` | `str` | The plugin's display name, used as a lesson's category when it names none. Keyword-only. |
| `instruments` | `mapping of str to PackInstrument` | The plugin's instruments by qualified key, which pictures and sounds refer to. Keyword-only. |
| `exercises` | `mapping of str to str` | The plugin's exercises, from the id the manifest uses to the key Alto registers it under. Keyword-only. |
| `icons` | `mapping of str to str or None, default None` | The plugin's icons by the file name the manifest uses, already read. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of Lesson` | The lessons, in the order the manifest lists them. |

**Raises**

- *ValueError*: If a lesson, step, picture, or question is malformed, or refers to something the plugin does not declare.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_lessons(
...     None,
...     pack_id="demo",
...     pack_name="Demo",
...     instruments={},
...     exercises={},
... )
()
```
{% endraw %}
