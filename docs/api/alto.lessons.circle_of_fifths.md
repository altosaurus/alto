---
title: alto.lessons.circle_of_fifths
parent: api
package: alto.lessons
order: 18
permalink: /api/alto.lessons.circle_of_fifths/
---
{% raw %}
The lesson on the circle of fifths, taught from nothing.

It covers what a key is, what a fifth is, how the circle counts sharps and flats, and what the inner ring and the neighbors of a
key mean.

**Examples**

```pycon
>>> len(CIRCLE_OF_FIFTHS.steps)
8
>>> summary("outer", place=2)
'<b>D major</b>: 2 sharps (F♯, C♯)'
```

## key_name

```python
def key_name(
    ring: str,
    *,
    place: int,
) -> str
```

Return the first name of the key in a cell, written out.

**Parameters**

- `ring` (*str*): "outer" for the major key, "inner" for the minor.
- `place` (*int*): The place on the circle, clockwise from the top. Keyword-only.

**Returns**

- *str*: "G major" or "E minor".

**Examples**

```pycon
>>> key_name("outer", place=1), key_name("inner", place=1)
('G major', 'E minor')
```

## summary

```python
def summary(
    ring: str,
    *,
    place: int,
) -> str
```

Say a key and its key signature in one line.

**Parameters**

- `ring` (*str*): "outer" or "inner".
- `place` (*int*): The place on the circle. Keyword-only.

**Returns**

- *str*: Simple HTML such as "<b>A major</b>: 3 sharps (F♯, C♯, G♯)".

**Examples**

```pycon
>>> summary("outer", place=0), summary("inner", place=11)
('<b>C major</b>: no sharps or flats', '<b>D minor</b>: 1 flat (B♭)')
```

## fifth_task

```python
def fifth_task(rng: random.Random) -> Task
```

Ask for the letter a fifth above a random letter, answered with buttons.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Task*: The question.

**Examples**

```pycon
>>> task = fifth_task(random.Random(1))
>>> task.correct in LETTERS and len(task.choices) == 4 and task.correct in task.choices
True
```

## sharps_task

```python
def sharps_task(rng: random.Random) -> Task
```

Ask for the major key with a given number of sharps, answered on the circle.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Task*: The question.

**Examples**

```pycon
>>> task = sharps_task(random.Random(2))
>>> ring, at = next(iter(task.cells))
>>> ring, SIGNATURES[at] == int(task.prompt.split("<b>")[1].split()[0])
('outer', True)
```

## flats_task

```python
def flats_task(rng: random.Random) -> Task
```

Ask for the major key with a given number of flats, answered on the circle.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Task*: The question.

**Examples**

```pycon
>>> task = flats_task(random.Random(3))
>>> ring, at = next(iter(task.cells))
>>> ring, -SIGNATURES[at] == int(task.prompt.split("<b>")[1].split()[0])
('outer', True)
```

## relative_task

```python
def relative_task(rng: random.Random) -> Task
```

Ask for the relative minor of a major key, answered on the circle.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Task*: The question.

**Examples**

```pycon
>>> task = relative_task(random.Random(4))
>>> task.cells <= {("inner", at) for at in range(12)}
True
```

## neighbor_task

```python
def neighbor_task(rng: random.Random) -> Task
```

Ask for the key a fifth above or below a random key, answered on the circle.

**Parameters**

- `rng` (*random.Random*): The random number generator.

**Returns**

- *Task*: The question.

**Examples**

```pycon
>>> task = neighbor_task(random.Random(5))
>>> ring, at = next(iter(task.cells))
>>> ring, at in range(12)
('outer', True)
```
{% endraw %}
