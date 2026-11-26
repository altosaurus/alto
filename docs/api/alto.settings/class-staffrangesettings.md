---
title: StaffRangeSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-staffrangesettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
StaffRangeSettings(
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    *,
    ranges: dict[str, tuple[int, int]] = field(default_factory=dict),
    note_values: set[str] = field(default_factory=lambda: {'whole'}),
)
```

{% endraw %}{% include api-source.html name="StaffRangeSettings" line=425 %}{% raw %}

</div>

Bases: `ClefChoice`

Selected clefs and inclusive pitch limits for each staff.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> StaffRangeSettings().active_clefs()
['treble', 'bass']
```

## StaffRangeSettings.active_values

<div class="api-signature" markdown="1">

```python
def active_values() -> list[str]
```

{% endraw %}{% include api-source.html name="StaffRangeSettings.active_values" line=447 %}{% raw %}

</div>

Return the note values to draw, from longest to shortest.

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | The chosen values in the order of `NOTE_VALUES`, or whole notes if none are chosen. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNameSettings(
...     note_values={"half", "whole"}
... ).active_values()
['whole', 'half']
```

## StaffRangeSettings.range_for

<div class="api-signature" markdown="1">

```python
def range_for(clef: str) -> tuple[int, int]
```

{% endraw %}{% include api-source.html name="StaffRangeSettings.range_for" line=466 %}{% raw %}

</div>

Return the range of notes that may be asked on a clef.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `clef` | `str` | A key of `DEFAULT_RANGES`. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (int, int)` | The lowest and highest staff step, inclusive; the user's override if there is one, otherwise the default. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNameSettings().range_for("treble")
(22, 52)
>>> NoteNameSettings(
...     ranges={"treble": (40, 30)}
... ).range_for(
...     "treble"
... )  # given in the wrong order
(30, 40)
```
{% endraw %}
