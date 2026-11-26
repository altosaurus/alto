---
title: ConstructionSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-constructionsettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ConstructionSettings(
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    *,
    accidentals: bool = False,
    key_signature: bool = False,
    question_type: str = 'scale',
    degrees: set[int] = field(default_factory=lambda: set(range(1, 8))),
    octave: bool = True,
    staff_keys: set[int] | None = None,
    major: bool = True,
    minor: bool = False,
    keys: set[int] = field(default_factory=lambda: {-3, -2, -1, 0, 1, 2, 3}),
    minor_keys: set[int] | None = None,
)
```

{% endraw %}{% include api-source.html name="ConstructionSettings" line=1133 %}{% raw %}

</div>

Bases: `ClefChoice, KeyChoice`

The settings of the note construction exercise.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `clefs` | `set of str` | The clefs to ask on, any of `RANGE_KEYS`, so "grand" is allowed. |
| `accidentals` | `bool, default False` | Also ask for sharps and flats, which the answer then has to include. Keyword-only. |
| `key_signature` | `bool, default False` | Draw a key signature; it applies to the note unless the note is given its own sign. Keyword-only. |
| `question_type` | `str, default "scale"` | Use the selected scale keys or ask for notes without a scale key. Keyword-only. |
| `degrees` | `set of int` | Scale degrees to ask for in Scale and Degree mode. Keyword-only. |
| `octave` | `bool, default True` | Require the note to be placed in a specific octave. Keyword-only. |
| `staff_keys` | `set of int or None` | Staff signatures chosen independently. None uses the question key. Keyword-only. |
| `major` | `bool, default True` | Use major keys. With key signatures off, use C major. Keyword-only. |
| `minor` | `bool, default False` | Use relative minor keys. With key signatures off, use A minor. Keyword-only. |
| `keys` | `set of int` | The key signatures to draw from, as sharps (positive) or flats (negative). Keyword-only. |
| `minor_keys` | `set of int or None` | Signatures selected for minor keys. None uses the original shared selection. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ConstructionSettings(
...     clefs={"grand"}
... ).active_clefs()
['grand']
```
{% endraw %}
