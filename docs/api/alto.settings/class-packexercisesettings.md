---
title: PackExerciseSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-packexercisesettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PackExerciseSettings(
    *,
    sound: str | None = None,
    accidentals: bool = False,
    require_octave: bool = False,
    keys: tuple[int, int] | None = None,
    intervals: frozenset[str] | None = None,
    manuals: frozenset[str] | None = None,
)
```

{% endraw %}{% include api-source.html name="PackExerciseSettings" line=575 %}{% raw %}

</div>

Bases: `StaffRangeSettings`

The options a plugin's exercise offers the learner, such as its
range and whether to ask accidentals.

Only the options the plugin declares for the exercise are shown and
used; the rest keep their defaults.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `clefs` | `set of str` | The one clef the exercise's range is drawn on. |
| `ranges` | `dict of str to tuple of (int, int)` | The range of notes asked, as staff steps, under the clef. |
| `sound` | `str or None, default None` | The key of the instrument that sounds in this exercise instead of the plugin's own, or None for the plugin's own. Keyword-only. |
| `accidentals` | `bool, default False` | Also ask the notes between the listed ones, written with sharps or flats. Keyword-only. |
| `require_octave` | `bool, default False` | The answer also includes the note's written octave. Keyword-only. |
| `keys` | `tuple of int or None, default None` | For a keyboard interval exercise, the lowest and highest key asked, as MIDI numbers. None asks the plugin's own default range. Keyword-only. |
| `intervals` | `frozenset of str or None, default None` | For a keyboard interval exercise, the names of the intervals asked. None asks every interval the plugin lists. Keyword-only. |
| `manuals` | `frozenset of str or None, default None` | For a keyboard interval exercise, the names of the keyboards the highlighted keys may sit on. None uses them all. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> PackExerciseSettings(
...     clefs={"alto"}
... ).sound is None
True
>>> PackExerciseSettings(
...     clefs={"alto"}
... ).keys is None
True
```
{% endraw %}
