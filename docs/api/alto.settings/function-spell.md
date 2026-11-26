---
title: spell
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/function-spell/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def spell(
    note: Note,
    *,
    naming: str = 'letters',
    key: int = 0,
    octave: bool = False,
    minor: bool = False,
) -> str
```

{% endraw %}{% include api-source.html name="spell" line=205 %}{% raw %}

</div>

Return a note name in the chosen naming system, optionally including
its octave.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `note` | `Note` | The note. |
| `naming` | `str, default "letters"` | "letters" for C D E, "solfege" for Do Re Mi, "degrees" for caret scale degrees, or "functions" for function names. Keyword-only. |
| `key` | `int, default 0` | The major key signature for scale degrees: sharps if positive, flats if negative. Zero means C major. Keyword-only. |
| `octave` | `bool, default False` | Include the note's octave, separated from a scale degree by " / ". Keyword-only. |
| `minor` | `bool, default False` | Use the relative natural minor as the scale degree reference. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The name and, if requested, octave. Carets use accidental prefixes; function names use Raised or Lowered prefixes. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> spell(Note.parse("F#4"))
'F♯'
>>> spell(Note.parse("F#4"), naming="solfege")
'Fa♯'
>>> spell(
...     Note.parse("F#4"),
...     naming="degrees",
...     key=1,
... )
'7̂'
>>> spell(
...     Note.parse("F4"),
...     naming="degrees",
...     key=1,
... )
'♭7̂'
>>> spell(Note.parse("Eb4"), naming="degrees")
'♭3̂'
>>> spell(
...     Note.parse("G4"),
...     naming="functions",
...     key=1,
... )
'Tonic'
>>> spell(
...     Note.parse("F4"),
...     naming="functions",
...     key=1,
... )
'Lowered Leading tone'
>>> spell(
...     Note.parse("G4"),
...     naming="degrees",
...     key=1,
...     octave=True,
... )
'1̂ / 4'
```
{% endraw %}
