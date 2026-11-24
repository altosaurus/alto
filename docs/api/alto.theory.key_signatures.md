---
title: alto.theory.key_signatures
parent: api
package: alto.theory
permalink: /api/alto.theory.key_signatures/
---
{% raw %}
Staff positions for written key signatures.

## key_signature_positions

```python
def key_signature_positions(
    clef: str,
    *,
    sign: int,
) -> list[str]
```

Return the notes the sharps or flats of a key signature are written
on, in a clef.

Each accidental is a fourth up or a fifth down from the one before
(sharps: F C G D A E B, flats: B E A D G C F), and the
pattern is chosen so that all seven stay on the staff, or one step
above or below it. This gives the usual signatures for
the treble, bass, alto and tenor clefs, and works out the rest.

**Parameters**

- `clef` (*str*): A key of `BOTTOM_LINE`.
- `sign` (*int*): 1 for sharps, -1 for flats. Keyword-only.

**Returns**

- *list of str*: Seven note names with octaves, in the order the accidentals appear.

**Raises**

- *ValueError*: If no placement keeps all seven accidentals on the staff.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> key_signature_positions("treble", sign=1)
['F5', 'C5', 'G5', 'D5', 'A4', 'E5', 'B4']
>>> key_signature_positions("bass", sign=-1)
['B2', 'E3', 'A2', 'D3', 'G2', 'C3', 'F2']
```

## written_signature

```python
def written_signature(
    clef: str,
    *,
    key: int,
) -> list[Note]
```

Spell a key signature at its conventional staff positions, from left
to right.

**Parameters**

- `clef` (*str*): The clef the signature is written in.
- `key` (*int*): Signed count of sharps or flats.

**Returns**

- *list of Note*: Pitches of the printed accidentals, including their octaves and signs.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [
...     str(note)
...     for note in written_signature(
...         "bass", key=-2
...     )
... ]
['B♭2', 'E♭3']
```
{% endraw %}
