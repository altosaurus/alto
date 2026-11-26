---
title: LessonNav
parent: alto.ui.lesson_nav
api_module: alto.ui.lesson_nav
package: alto.ui
permalink: /api/alto.ui.lesson_nav/class-lessonnav/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
LessonNav(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="LessonNav" line=85 %}{% raw %}

</div>

Bases: `QListWidget`

A flat list of the lessons by category, with the steps of the open
lesson listed under it.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `lesson_chosen` | `Signal` | Emitted with a lesson's key when its row is clicked. |
| `step_chosen` | `Signal` | Emitted with a step's number, from 0, when its row is clicked. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> LessonNav().objectName()
'nav'
```

## LessonNav.show_lesson

<div class="api-signature" markdown="1">

```python
def show_lesson(key: str | None) -> None
```

{% endraw %}{% include api-source.html name="LessonNav.show_lesson" line=139 %}{% raw %}

</div>

Fill the list, with the steps of one lesson under it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str or None` | The key of the lesson that is open; None for none. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> nav = LessonNav()
>>> nav.show_lesson("circle-of-fifths")
>>> len(nav.step_items)
8
>>> nav.show_lesson(None)
>>> nav.step_items
[]
```

## LessonNav.select_step

<div class="api-signature" markdown="1">

```python
def select_step(number: int) -> None
```

{% endraw %}{% include api-source.html name="LessonNav.select_step" line=190 %}{% raw %}

</div>

Highlight the step that is showing.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `number` | `int` | The step, from 0. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> nav = LessonNav()
>>> nav.show_lesson("circle-of-fifths")
>>> nav.select_step(3)
>>> nav.currentItem() is nav.step_items[3]
True
```
{% endraw %}
