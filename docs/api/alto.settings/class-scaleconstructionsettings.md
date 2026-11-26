---
title: ScaleConstructionSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-scaleconstructionsettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ScaleConstructionSettings(
    *,
    minor_keys: set[int] | None = None,
    motion: str = 'ascending',
    steps: bool = False,
    octave: bool = False,
    staff_keys: set[int] = field(default_factory=lambda: {0}),
)
```

{% endraw %}{% include api-source.html name="ScaleConstructionSettings" line=1599 %}{% raw %}

</div>

Bases: `KeySignatureSettings`

The settings of the scale construction exercise: the same choices as
key signature identification.

Here "keys" chooses the scale by the signature it has: G major and E
minor both have one sharp. `staff_keys` is a
separate choice: the key signature drawn on the staff, which need
not be the scale's. On a staff with two flats a C
major scale has to be placed with naturals where the staff would
otherwise flatten the notes.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `clefs` | `set of str` | The clefs the scale is placed on, any of `CLEFS`. Keyword-only. |
| `modes` | `set of str` | The kinds of scale to ask for, from `KEY_MODES`. Keyword-only. |
| `keys` | `set of int` | The key signatures the scales have, as sharps (positive) or flats (negative). Keyword-only. |
| `steps` | `bool, default False` | Also mark the whole and half steps between the notes, once the notes are placed. Keyword-only. |
| `staff_keys` | `set of int` | The key signatures that may be drawn on the staff, as sharps (positive) or flats (negative); 0 is none. Keyword-only. |
| `octave` | `bool, default False` | Name the octave of the first note, such as "G2 Major", and require the scale to start there; any scale asked then fits on the staff and its ledger lines. Without it any octave is accepted. Keyword-only. |
| `motion` | `str, default "ascending"` | Direction of the scale, "ascending" or "descending". Keyword-only. |
| `minor_keys` | `set of int or None` | Signatures for natural minor. None uses the shared key selection. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = ScaleConstructionSettings(keys={3})
>>> (
...     cfg.active_keys(),
...     cfg.active_clefs(),
...     cfg.steps,
...     cfg.octave,
...     cfg.active_staff_keys(),
... )
([3], ['treble', 'bass'], False, False, [0])
```

## ScaleConstructionSettings.active_staff_keys

<div class="api-signature" markdown="1">

```python
def active_staff_keys() -> list[int]
```

{% endraw %}{% include api-source.html name="ScaleConstructionSettings.active_staff_keys" line=1665 %}{% raw %}

</div>

Return the key signatures that may be drawn on the staff, lowest
first.

**Returns**

| Type | Description |
| --- | --- |
| `list of int` | Sharps (positive) or flats (negative); no sharps or flats if none are chosen. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleConstructionSettings(
...     staff_keys={-2, 3}
... ).active_staff_keys()
[-2, 3]
>>> ScaleConstructionSettings(
...     staff_keys=set()
... ).active_staff_keys()
[0]
```
{% endraw %}
