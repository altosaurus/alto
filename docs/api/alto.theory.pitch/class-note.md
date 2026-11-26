---
title: Note
parent: alto.theory.pitch
api_module: alto.theory.pitch
package: alto.theory
permalink: /api/alto.theory.pitch/class-note/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Note(
    octave: int,
    *,
    letter: int,
    accidental: int = 0,
)
```

{% endraw %}{% include api-source.html name="Note" line=76 %}{% raw %}

</div>

A spelled pitch: a letter name, an accidental and an octave.

The spelling matters. C♯4 and D♭4 sound the same (they share a MIDI
number) but are different notes, because they sit on
different lines of the staff.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `octave` | `int` | The octave in scientific pitch notation, where middle C is C4. |
| `letter` | `int` | An index into `LETTERS`: 0 is C, 1 is D, 2 is E, 3 is F, 4 is G, 5 is A and 6 is B. Keyword-only. |
| `accidental` | `int, default 0` | -2 for a double flat, -1 for a flat, 0 for a natural, 1 for a sharp and 2 for a double sharp. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> middle_c = Note(4, letter=0)
>>> middle_c.midi
60
>>> str(Note(4, letter=3, accidental=1))
'F♯4'
>>> Note(4, letter=0) < Note(4, letter=1)
True
```

## Note.midi

<div class="api-signature" markdown="1">

```python
@property
def midi() -> int
```

{% endraw %}{% include api-source.html name="Note.midi" line=112 %}{% raw %}

</div>

Return the MIDI note number, where middle C (C4) is 60.

**Returns**

| Type | Description |
| --- | --- |
| `int` | The number of semitones above C-1. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Note(4, letter=0).midi
60
>>> Note(
...     4, letter=1, accidental=-1
... ).midi  # D♭4 sounds like C♯4
61
```

## Note.diatonic

<div class="api-signature" markdown="1">

```python
@property
def diatonic() -> int
```

{% endraw %}{% include api-source.html name="Note.diatonic" line=137 %}{% raw %}

</div>

Return the absolute staff-step index of the note, ignoring its
accidental.

Counting from C0 as 0, D0 as 1 and so on, each line or space of
the staff is one step. The distance between two notes in
staff steps is the difference of their indexes.

**Returns**

| Type | Description |
| --- | --- |
| `int` | `octave * 7 + letter`. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Note(4, letter=0).diatonic  # C4
28
>>> Note(
...     4, letter=2, accidental=1
... ).diatonic  # E♯4 is on the same step as E4
30
```

## Note.pitch_class

<div class="api-signature" markdown="1">

```python
@property
def pitch_class() -> int
```

{% endraw %}{% include api-source.html name="Note.pitch_class" line=163 %}{% raw %}

</div>

Return the pitch class: the note's MIDI number modulo 12.

**Returns**

| Type | Description |
| --- | --- |
| `int` | A number from 0 (C) to 11 (B), the same for every octave and for enharmonic spellings. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Note(
...     4, letter=0, accidental=1
... ).pitch_class  # C♯4
1
>>> Note(
...     3, letter=6, accidental=1
... ).pitch_class  # B♯3 sounds like C
0
```

## Note.name

<div class="api-signature" markdown="1">

```python
@property
def name() -> str
```

{% endraw %}{% include api-source.html name="Note.name" line=187 %}{% raw %}

</div>

Return the pitch-class name with Unicode accidentals, without
the octave.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The letter followed by ♭, ♯, 𝄫 or 𝄪 where the note has an accidental. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Note(4, letter=3, accidental=1).name
'F♯'
>>> Note(4, letter=3).name
'F'
```

## Note.from_diatonic

<div class="api-signature" markdown="1">

```python
@classmethod
def from_diatonic(
    diatonic: int,
    *,
    accidental: int = 0,
) -> Note
```

{% endraw %}{% include api-source.html name="Note.from_diatonic" line=224 %}{% raw %}

</div>

Build a note from an absolute staff-step index.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `diatonic` | `int` | The index, counting C0 as 0 (see `Note.diatonic`). |
| `accidental` | `int, default 0` | The accidental to give the note. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Note` | The note on that staff step with that accidental. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Note.from_diatonic(30)
Note(octave=4, letter=2, accidental=0)
>>> str(Note.from_diatonic(30, accidental=-1))
'E♭4'
```

## Note.parse

<div class="api-signature" markdown="1">

```python
@classmethod
def parse(text: str) -> Note
```

{% endraw %}{% include api-source.html name="Note.parse" line=255 %}{% raw %}

</div>

Parse a note with ASCII or musical accidentals, such as 'F#4',
'B♭3' or 'E𝄫2'.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | A letter A-G (either case), then an accidental ('#' for a sharp, 'b' for a flat, 'bb' for a double flat, 'x' for a double sharp, or nothing for a natural), then the octave number. |

**Returns**

| Type | Description |
| --- | --- |
| `Note` | The spelled note. |

**Raises**

- *ValueError*: If the letter is not A-G, or the octave is missing.
- *KeyError*: If the accidental is not one of '', '#', 'b', 'bb' or 'x'.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Note.parse("F#4")
Note(octave=4, letter=3, accidental=1)
>>> Note.parse("Bb3")
Note(octave=3, letter=6, accidental=-1)
>>> str(Note.parse("G𝄫4"))
'G𝄫4'
>>> Note.parse("H4")
Traceback (most recent call last):
    ...
ValueError: substring not found
```

## Note.transpose

<div class="api-signature" markdown="1">

```python
def transpose(
    interval: Interval,
    *,
    descending: bool = False,
) -> Note
```

{% endraw %}{% include api-source.html name="Note.transpose" line=300 %}{% raw %}

</div>

Move the note up or down by an interval, keeping the spelling
correct.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `interval` | `Interval` | How far to move. Its number decides the letter and its quality decides the accidental. |
| `descending` | `bool, default False` | Move down instead of up. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Note` | The new note. For example a major third above C is E, and a minor third above C is E♭, never D♯. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> str(
...     Note.parse("C4").transpose(
...         Interval.parse("M3")
...     )
... )
'E4'
>>> str(
...     Note.parse("C4").transpose(
...         Interval.parse("m3")
...     )
... )
'E♭4'
>>> str(
...     Note.parse("C4").transpose(
...         Interval.parse("P5"),
...         descending=True,
...     )
... )
'F3'
```
{% endraw %}
