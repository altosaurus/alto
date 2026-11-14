---
title: alto.ui.lesson_nav
parent: api
package: alto.ui
order: 31
permalink: /api/alto.ui.lesson_nav/
---
{% raw %}
The list on the left in lesson mode: the lessons, and the steps of the one that is open.

It is the lessons' counterpart of the exercise list, and looks the same.

**Examples**

```pycon
>>> nav = LessonNav()
>>> nav.show_lesson("circle-of-fifths")
>>> nav.count() > len(LESSONS)
True
```

## section_item

```python
def section_item(
    text: str,
    *,
    palette: QPalette,
) -> QListWidgetItem
```

Make a section label for a list: small, grey capitals that cannot be selected.

**Parameters**

- `text` (*str*): The heading, which is shown in capitals.
- `palette` (*QPalette*): The palette to take the grey from. Keyword-only.

**Returns**

- *QListWidgetItem*: The row.

**Examples**

```pycon
>>> section_item("Scales & Keys", palette=QPalette()).text()
'SCALES & KEYS'
```

## LessonNav

```python
LessonNav(parent: QWidget | None = None)
```

Bases: `QListWidget`

A flat list of the lessons by category, with the steps of the open lesson listed under it.

**Attributes**

- `lesson_chosen` (*Signal*): Emitted with a lesson's key when its row is clicked.
- `step_chosen` (*Signal*): Emitted with a step's number, from 0, when its row is clicked.

**Examples**

```pycon
>>> nav = LessonNav()
>>> chosen = []
>>> _ = nav.step_chosen.connect(chosen.append)
>>> nav.show_lesson("circle-of-fifths")
>>> nav.itemClicked.emit(nav.step_items[2])
True
>>> chosen
[2]
```

**Constructor**

Build the list with no lesson open.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns it.

**Constructor examples**

```pycon
>>> LessonNav().objectName()
'nav'
```

### LessonNav.show_lesson

```python
def show_lesson(key: str | None) -> None
```

Fill the list, with the steps of one lesson under it.

**Parameters**

- `key` (*str or None*): The key of the lesson that is open; None for none.

**Examples**

```pycon
>>> nav = LessonNav()
>>> nav.show_lesson("circle-of-fifths")
>>> len(nav.step_items)
8
>>> nav.show_lesson(None)
>>> nav.step_items
[]
```

### LessonNav.select_step

```python
def select_step(number: int) -> None
```

Highlight the step that is showing.

**Parameters**

- `number` (*int*): The step, from 0.

**Examples**

```pycon
>>> nav = LessonNav()
>>> nav.show_lesson("circle-of-fifths")
>>> nav.select_step(3)
>>> nav.currentItem() is nav.step_items[3]
True
```
{% endraw %}
