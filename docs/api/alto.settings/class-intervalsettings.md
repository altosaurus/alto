---
title: IntervalSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-intervalsettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
IntervalSettings(
    *,
    staff_keys: set[int] = field(default_factory=lambda: {0}),
    displays: set[str] = field(default_factory=lambda: {'Harmonic'}),
    directions: set[str] = field(default_factory=lambda: {'ascending'}),
    button_mode: str = 'limited',
    button_count: int = 6,
    accidentals: set[int] = field(default_factory=lambda: set(DEFAULT_INTERVAL_ACCIDENTALS)),
    quality_mode: str = 'combined',
    inversions: bool = False,
    consonance: bool = False,
    intervals: set[str] = field(default_factory=lambda: {name for name, iv in WRITTEN_INTERVALS.items() if 2 <= iv.number <= 7 or name == 'P8'}),
)
```

{% endraw %}{% include api-source.html name="IntervalSettings" line=664 %}{% raw %}

</div>

Bases: `StaffRangeSettings`

Staff signatures, presentations, answer format and spelled intervals
for Interval Identification.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalSettings().quality_mode
'combined'
```

## IntervalSettings.staff_span

<div class="api-signature" markdown="1">

```python
def staff_span(clef: str) -> int
```

{% endraw %}{% include api-source.html name="IntervalSettings.staff_span" line=697 %}{% raw %}

</div>

Count the written staff positions in a clef's selected range,
including both endpoints.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `clef` | `str` | The clef whose range to measure. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | The largest diatonic interval number that fits. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> IntervalSettings(
...     ranges={"treble": (28, 30)}
... ).staff_span("treble")
3
```
{% endraw %}
