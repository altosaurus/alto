---
title: alto.theory.fifths
parent: api
package: alto.theory
order: 14
permalink: /api/alto.theory.fifths/
---
{% raw %}
The circle of fifths: the twelve keys in order, each major with its relative minor.

Going clockwise from C at the top, each key is a fifth above the one before, so it has one more sharp (or one fewer flat).
The relative minor of a major key has the same key signature and starts on its sixth note: A minor goes with C major.

A key has six chords that fit on the circle: the major triads I, IV and V on the outer ring, and the minor triads ii, iii and
vi on the inner ring. They are the key's own wedge and the wedge on each side of it, on both rings. (The seventh chord, vii°,
is diminished and has no wedge.)

**Examples**

```pycon
>>> MAJORS[3], MINORS[3], SIGNATURES[3]
(('A',), ('F♯m',), 3)
>>> relative_minor("A")
'F♯m'
>>> numeral_chords(1)
{'I': 'G', 'ii': 'Am', 'iii': 'Bm', 'IV': 'C', 'V': 'D', 'vi': 'Em'}
>>> accidentals_of(-2)
['B♭', 'E♭']
```

## place_of_major

```python
def place_of_major(name: str) -> int
```

Return where a major key is on the circle, by either of its names.

**Parameters**

- `name` (*str*): The key's name, such as "A", "B♭" or "C♭".

**Returns**

- *int*: The place, clockwise from C at 0.

**Raises**

- *ValueError*: If no key has that name.

**Examples**

```pycon
>>> place_of_major("A"), place_of_major("C♭"), place_of_major("G♭")
(3, 5, 6)
```

## relative_minor

```python
def relative_minor(name: str) -> str
```

Return the relative minor of a major key.

**Parameters**

- `name` (*str*): The major key's name.

**Returns**

- *str*: The first name of its relative minor, such as "F♯m" for A.

**Examples**

```pycon
>>> relative_minor("C"), relative_minor("E♭"), relative_minor("C♯")
('Am', 'Cm', 'B♭m')
```

## cells_of_key

```python
def cells_of_key(place: int) -> dict[tuple[str, int], str]
```

Return the six wedges that hold the chords of a major key, and the Roman numeral of each.

**Parameters**

- `place` (*int*): The key's own place on the circle, clockwise from C at 0.

**Returns**

- *dict of tuple of (str, int) to str*: For each of the six cells, its ring ("outer" or "inner") and place, the numeral of its chord.

**Examples**

```pycon
>>> cells = cells_of_key(0)
>>> cells[("outer", 11)], cells[("inner", 0)], cells[("inner", 1)]  # F is IV; Am is vi; Em is iii
('IV', 'vi', 'iii')
>>> cells[("outer", 1)]  # G is V
'V'
>>> len(cells_of_key(11)), cells_of_key(11)[("outer", 10)]  # in F major, B♭ is IV
(6, 'IV')
```

## numeral_chords

```python
def numeral_chords(place: int) -> dict[str, str]
```

Return the six chords of a major key that are on the circle, spelt as that key spells them.

A wedge with two names, such as D♭ and C♯, is the same chord, but the key decides which name is right: C♯ is the V of F♯.

**Parameters**

- `place` (*int*): The key's own place on the circle.

**Returns**

- *dict of str to str*: The chord's name for each numeral, in the order of `NUMERALS`: "G", "Am" and so on.

**Examples**

```pycon
>>> numeral_chords(0)
{'I': 'C', 'ii': 'Dm', 'iii': 'Em', 'IV': 'F', 'V': 'G', 'vi': 'Am'}
>>> numeral_chords(6)["V"], numeral_chords(7)["IV"]  # in F♯ major the V is C♯; in D♭ major the IV is G♭
('C♯', 'G♭')
```

## display_major

```python
def display_major(place: int) -> str
```

Return the major key of a place as it is written to ask about it: "A major", or "B major / C♭ major".

**Parameters**

- `place` (*int*): The place on the circle.

**Returns**

- *str*: The name, with both names when the wedge has two.

**Examples**

```pycon
>>> display_major(3), display_major(5)
('A major', 'B major / C♭ major')
```

## display_minor

```python
def display_minor(place: int) -> str
```

Return the minor key of a place as it is written to ask about it: "F♯ minor", or "G♯ minor / A♭ minor".

**Parameters**

- `place` (*int*): The place on the circle.

**Returns**

- *str*: The name, with both names when the wedge has two.

**Examples**

```pycon
>>> display_minor(3), display_minor(5)
('F♯ minor', 'G♯ minor / A♭ minor')
```

## accidentals_of

```python
def accidentals_of(signature: int) -> list[str]
```

Return the sharps or flats of a key signature, in the order they are written.

**Parameters**

- `signature` (*int*): The number of sharps (positive) or flats (negative).

**Returns**

- *list of str*: The notes that are altered: "F♯", "C♯" and so on, or "B♭", "E♭" and so on.

**Examples**

```pycon
>>> accidentals_of(3), accidentals_of(0)
(['F♯', 'C♯', 'G♯'], [])
```

## explain

```python
def explain(
    ring: str,
    *,
    place: int,
) -> str
```

Explain a cell of the circle: its key signature, where it comes from, its relative key and its chords.

**Parameters**

- `ring` (*str*): "outer" for the major key at the place, "inner" for its relative minor.
- `place` (*int*): The place on the circle, clockwise from C at 0. Keyword-only.

**Returns**

- *str*: Simple HTML, a few short paragraphs.

**Examples**

```pycon
>>> text = explain("outer", place=1)
>>> "<b>G major</b>" in text and "1 sharp: F♯" in text and "a fifth above C" in text
True
>>> "relative major, <b>C major</b>" in explain("inner", place=0)
True
>>> "<b>C♭ major</b>" in explain("outer", place=5) and "7 flats" in explain("outer", place=5)
True
```
{% endraw %}
