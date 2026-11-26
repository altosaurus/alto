---
title: Coverage
parent: alto.instrument_info
api_module: alto.instrument_info
package: alto
permalink: /api/alto.instrument_info/class-coverage/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Coverage(
    count: int,
    *,
    lowest: int | None = None,
    highest: int | None = None,
    gaps: int = 0,
)
```

{% endraw %}{% include api-source.html name="Coverage" line=192 %}{% raw %}

</div>

Which notes an instrument has recordings for.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `count` | `int` | How many notes have a recording. |
| `lowest` | `int or None` | The lowest recorded note, as a MIDI number. Keyword-only. |
| `highest` | `int or None` | The highest recorded note, as a MIDI number. Keyword-only. |
| `gaps` | `int, default 0` | How many semitones inside the range have no recording. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Coverage(0).describe()
'None installed'
```

## Coverage.installed

<div class="api-signature" markdown="1">

```python
@property
def installed() -> bool
```

{% endraw %}{% include api-source.html name="Coverage.installed" line=221 %}{% raw %}

</div>

Report whether any recordings are on disk.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if at least one note has a recording. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     Coverage(0).installed,
...     coverage([60]).installed,
... )
(False, True)
```

## Coverage.describe

<div class="api-signature" markdown="1">

```python
def describe() -> str
```

{% endraw %}{% include api-source.html name="Coverage.describe" line=240 %}{% raw %}

</div>

Describe the coverage in a sentence for the instrument settings.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The number of notes, the range, and how complete it is (the spacing, when the notes are well apart). Missing notes are shifted from a neighbor. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> coverage(range(60, 73)).describe()
'13 notes, C4 to C5, every semitone'
>>> coverage([60, 62, 64, 65]).describe()
'4 notes, C4 to F4, almost every semitone. The few missing notes
are shifted from a neighbor.'
>>> coverage(range(48, 73, 2)).describe()
'13 notes, C3 to C5, about every second semitone. The other
notes are shifted from a neighbor.'
>>> coverage(range(21, 109, 3)).describe()
'30 notes, A0 to C8, about every third semitone. The other notes
are shifted from a neighbor.'
```
{% endraw %}
