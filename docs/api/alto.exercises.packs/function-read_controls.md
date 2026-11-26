---
title: read_controls
parent: alto.exercises.packs
api_module: alto.exercises.packs
package: alto.exercises
permalink: /api/alto.exercises.packs/function-read_controls/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_controls(
    value: object,
    *,
    where: str,
    kinds: tuple[str, ...] = CONTROL_KINDS,
) -> dict[str, str | bool]
```

{% endraw %}{% include api-source.html name="read_controls" line=640 %}{% raw %}

</div>

Validate the settings a pack offers for one of its exercises.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The exercise's ``settings`` entry: an object that may hold ``sound`` (the label of a switch that plays the pack's own sound), ``range`` (a clef to draw a range selector on, or true for the keys of a keyboard exercise), ``accidentals`` and ``octave`` (true for a switch), ``intervals`` (true for a choice of intervals), ``manuals`` (true for a choice of keyboards), or None. |
| `where` | `str` | The exercise id, for diagnostics. Keyword-only. |
| `kinds` | `tuple of str, default CONTROL_KINDS` | The settings this kind of exercise can have. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to str or bool` | The declared settings by kind; empty when the pack declares none. |

**Raises**

- *ValueError*: If the entry has an unknown kind or a value of the wrong type.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_controls(
...     {"range": "alto", "octave": True},
...     where="pack.v.notes",
... )
{'range': 'alto', 'octave': True}
>>> read_controls(
...     {"range": True, "intervals": True},
...     where="pack.v.keys",
...     kinds=KEYBOARD_CONTROL_KINDS,
... )
{'range': True, 'intervals': True}
>>> read_controls(None, where="pack.v.notes")
{}
```
{% endraw %}
