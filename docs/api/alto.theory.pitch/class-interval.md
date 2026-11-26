---
title: Interval
parent: alto.theory.pitch
api_module: alto.theory.pitch
package: alto.theory
permalink: /api/alto.theory.pitch/class-interval/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Interval(
    number: int,
    *,
    quality: str,
)
```

{% endraw %}{% include api-source.html name="Interval" line=356 %}{% raw %}

</div>

A simple or compound interval between two spelled notes.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `number` | `int` | The size counting both end notes: 1 is a unison, 3 a third, 8 an octave, 9 a ninth and so on. |
| `quality` | `str` | One of 'dd' (doubly diminished), 'd' (diminished), 'm' (minor), 'M' (major), 'P' (perfect), 'A' (augmented) and 'AA' (doubly augmented). Keyword-only. Unisons, fourths, fifths and octaves are perfect, the others major or minor. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Interval(3, quality="M").semitones
4
>>> str(Interval.parse("P5"))
'P5'
```

## Interval.inversion

<div class="api-signature" markdown="1">

```python
@property
def inversion() -> Interval
```

{% endraw %}{% include api-source.html name="Interval.inversion" line=403 %}{% raw %}

</div>

Invert the spelled interval within an octave.

**Returns**

| Type | Description |
| --- | --- |
| `Interval` | The complementary number and quality. Reduce compounds first, keeping octaves as octaves. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     Interval.parse("M3").inversion.short,
...     Interval.parse("A4").inversion.short,
... )
('m6', 'd5')
>>> (
...     Interval.parse("m10").inversion.short,
...     Interval.parse("P15").inversion.short,
... )
('M6', 'P1')
```

## Interval.is_perfect_type

<div class="api-signature" markdown="1">

```python
@property
def is_perfect_type() -> bool
```

{% endraw %}{% include api-source.html name="Interval.is_perfect_type" line=441 %}{% raw %}

</div>

Report whether this size of interval is "perfect type" (unison,
fourth, fifth, octave) rather than major or minor type.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True for unisons, fourths, fifths and octaves (and their compounds), False for seconds, thirds, sixths and sevenths. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Interval.parse("P5").is_perfect_type
True
>>> Interval.parse("M3").is_perfect_type
False
```

## Interval.semitones

<div class="api-signature" markdown="1">

```python
@property
def semitones() -> int
```

{% endraw %}{% include api-source.html name="Interval.semitones" line=462 %}{% raw %}

</div>

Return the size of the interval in semitones.

**Returns**

| Type | Description |
| --- | --- |
| `int` | The distance in half steps, including whole octaves for compound intervals. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Interval.parse("M3").semitones
4
>>> Interval.parse("d5").semitones
6
>>> Interval.parse(
...     "m9"
... # a minor ninth is an octave plus a minor second
... ).semitones
13
```

## Interval.short

<div class="api-signature" markdown="1">

```python
@property
def short() -> str
```

{% endraw %}{% include api-source.html name="Interval.short" line=506 %}{% raw %}

</div>

Return the interval in short form: its quality followed by its
number.

**Returns**

| Type | Description |
| --- | --- |
| `str` | For example 'M3', 'P5' or 'd7'. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Interval(7, quality="m").short
'm7'
```

## Interval.between

<div class="api-signature" markdown="1">

```python
@classmethod
def between(
    low: Note,
    *,
    high: Note,
) -> Interval
```

{% endraw %}{% include api-source.html name="Interval.between" line=540 %}{% raw %}

</div>

Work out the interval from one note up to a higher one.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `low` | `Note` | The lower note. |
| `high` | `Note` | The higher note. It must not be below `low`. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Interval` | The spelled interval, such as a major third (C4 up to E4) or an augmented fourth (C4 up to F♯4). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Interval.between(
...     Note.parse("C4"), high=Note.parse("E4")
... )
Interval(number=3, quality='M')
>>> Interval.between(
...     Note.parse("C4"), high=Note.parse("F#4")
... ).short
'A4'
```

## Interval.parse

<div class="api-signature" markdown="1">

```python
@classmethod
def parse(text: str) -> Interval
```

{% endraw %}{% include api-source.html name="Interval.parse" line=597 %}{% raw %}

</div>

Parse an interval written in short form, such as 'M3', 'P5' or
'd7'.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | The quality (one of dd, d, m, M, P, A, AA) followed by the number. |

**Returns**

| Type | Description |
| --- | --- |
| `Interval` | The interval. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Interval.parse("m7")
Interval(number=7, quality='m')
>>> Interval.parse("P8").semitones
12
```
{% endraw %}
