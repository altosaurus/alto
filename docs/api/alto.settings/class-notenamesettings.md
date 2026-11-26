---
title: NoteNameSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-notenamesettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
NoteNameSettings(
    *,
    key_signatures: set[int] = field(default_factory=lambda: {0}),
    naming: str = 'letters',
    minor_degrees: bool = False,
    accidentals: bool = False,
    require_octave: bool = False,
)
```

{% endraw %}{% include api-source.html name="NoteNameSettings" line=497 %}{% raw %}

</div>

Bases: `StaffRangeSettings`

The settings of the note identification exercise.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `clefs` | `set of str` | The clefs to ask on, any of `RANGE_KEYS`, so "grand" is allowed. |
| `ranges` | `dict of str to tuple of (int, int)` | Overrides of `DEFAULT_RANGES`, as inclusive staff-step ranges. Keyword-only. |
| `key_signatures` | `set of int` | The keys to use, as sharps (positive) or flats (negative). Keyword-only. |
| `note_values` | `set of str` | The note values to draw, from `NOTE_VALUES`. Keyword-only. |
| `naming` | `str, default "letters"` | A key of `NAMINGS`. Keyword-only. |
| `accidentals` | `bool, default False` | Also ask notes with explicit sharps, flats and naturals. Keyword-only. |
| `require_octave` | `bool, default False` | Also require the written octave as part of the answer. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = NoteNameSettings(
...     clefs={"bass"}, key_signatures={2}
... )
>>> cfg.active_clefs(), cfg.active_keys()
(['bass'], [2])
```

## NoteNameSettings.active_keys

<div class="api-signature" markdown="1">

```python
def active_keys() -> list[int]
```

{% endraw %}{% include api-source.html name="NoteNameSettings.active_keys" line=546 %}{% raw %}

</div>

Return the key signatures to draw from, lowest first.

The field is named `key_signatures` rather than `keys`, as in
`KeyChoice`, because the name is part of the practice
signature that stored questions are matched by; renaming it
would orphan every learner's saved questions.

**Returns**

| Type | Description |
| --- | --- |
| `list of int` | Sharps (positive) or flats (negative); no sharps or flats if none are chosen. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNameSettings(
...     key_signatures={2, -1}
... ).active_keys()
[-1, 2]
```
{% endraw %}
