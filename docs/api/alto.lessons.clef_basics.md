---
title: alto.lessons.clef_basics
parent: api
package: alto.lessons
permalink: /api/alto.lessons.clef_basics/
---
{% raw %}
The lesson on clefs, taught from nothing.

It covers what a clef does, the three symbols (the G, C and F clef) and the line each clef puts them on, the way every C clef
points at middle C, and the rarer clefs.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(CLEF_BASICS.steps)
10
>>> symbol_task(random.Random(1)).choices
('G clef', 'C clef', 'F clef')
```

## symbol_task

```python
def symbol_task(rng: random.Random) -> Task
```

Ask which of the three symbols a clef is made with.

**Parameters**

- `rng` (*random.Random*): Chooses the clef.

**Returns**

- *Task*: A clef drawn on a staff, and a button for each symbol.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> task = symbol_task(random.Random(2))
>>> task.correct == CLEF_SYMBOL_NAMES[SYMBOLS[task.clef]]
True
```

## identify_task

```python
def identify_task(rng: random.Random) -> Task
```

Ask which clef is drawn on a staff.

**Parameters**

- `rng` (*random.Random*): Chooses the clef.

**Returns**

- *Task*: A clef drawn on a staff, and a button for each of the four everyday clefs.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> task = identify_task(random.Random(3))
>>> task.correct in task.choices and task.clef != ""
True
```

## line_task

```python
def line_task(rng: random.Random) -> Task
```

Ask which line of a blank staff a named clef is written on.

**Parameters**

- `rng` (*random.Random*): Chooses the clef.

**Returns**

- *Task*: A blank staff, and a button for each line.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> task = line_task(random.Random(4))
>>> task.correct in LINES and task.clef == ""
True
```
{% endraw %}
