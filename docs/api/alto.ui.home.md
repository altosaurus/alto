---
title: alto.ui.home
parent: api
package: alto.ui
order: 31
permalink: /api/alto.ui.home/
---
{% raw %}
The start screen: a card for every exercise, or for every lesson, in rows.

A switch at the top chooses between the exercises and the lessons.

**Examples**

```pycon
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> len(page.cards) == len(REGISTRY)
True
```

## TileCard

```python
TileCard(
    *,
    icon: str,
    category: str,
    name: str,
    about: str,
    status: str = '',
    parent: QWidget | None = None,
)
```

Bases: `QPushButton`

A big button: an icon on top, then a category, a name and a one-line description, and optionally a line of status.

**Examples**

```pycon
>>> card = TileCard(icon=icons.EXERCISE_CIRCLE, category="Scales & Keys", name="Circle of Fifths", about="Find keys.")
>>> (card.width(), card.height()) == (CARD_W, CARD_H)
True
>>> card.accessibleName()
'Circle of Fifths, Scales & Keys'
```

**Constructor**

Build a card.

**Parameters**

- `icon` (*str*): The inside of a 24 by 24 SVG, drawn in the text colour. Keyword-only.
- `category` (*str*): The small heading above the name. Keyword-only.
- `name` (*str*): The name. Keyword-only.
- `about` (*str*): A line of description, which is also the tooltip. Keyword-only.
- `status` (*str, default ""*): A line under the description, such as how far through a lesson you are; nothing if empty. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns the card. Keyword-only.

**Constructor examples**

```pycon
>>> TileCard(icon=icons.HELP, category="Help", name="Help", about="Get help.", status="Step 2 of 8").toolTip()
'Get help.'
```

## ExerciseCard

```python
ExerciseCard(
    cls: type[Exercise],
    *,
    parent: QWidget | None = None,
)
```

Bases: `TileCard`

The card of an exercise: its icon on top, then its category, name and a one-line description.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> card = ExerciseCard(NoteNames)
>>> card.toolTip() == NoteNames.description
True
>>> (card.width(), card.height()) == (CARD_W, CARD_H)
True
```

**Constructor**

Build the card for one exercise.

**Parameters**

- `cls` (*type of Exercise*): The exercise class; its name, category and description are shown, and its class name picks the icon.
- `parent` (*QWidget or None, default None*): The widget that owns the card. Keyword-only.

**Constructor examples**

```pycon
>>> from alto.exercises.library import IntervalNames
>>> ExerciseCard(IntervalNames).toolTip()
'Name the interval between two notes (up to an octave).'
```

## lesson_card

```python
def lesson_card(
    lesson: Lesson,
    *,
    parent: QWidget | None = None,
) -> TileCard
```

Make the card of a lesson: the icon of the exercise that practises the same topic, and how far through it you are.

**Parameters**

- `lesson` (*Lesson*): The lesson.
- `parent` (*QWidget or None, default None*): The widget that owns the card. Keyword-only.

**Returns**

- *TileCard*: The card, which says "Start" or "Continue at step N".

**Examples**

```pycon
>>> card = lesson_card(LESSONS[0])
>>> card.accessibleName()
'The Circle of Fifths, Scales & Keys'
```

## HomePage

```python
HomePage(
    registry: Iterable[type[Exercise]],
    *,
    parent: QWidget | None = None,
)
```

Bases: `QWidget`

The start screen: a row of exercise buttons for each category.

**Attributes**

- `exercise_chosen` (*Signal*): Emitted with the `Exercise` class when a card is clicked.
- `lesson_chosen` (*Signal*): Emitted with a lesson's key when its card is clicked.
- `cards` (*list of ExerciseCard*): One per exercise, in registry order.
- `lesson_cards` (*list of TileCard*): One per lesson, with how far through it you are.
- `canvas` (*TransitionCanvas*): Where the transition between the exercises and the lessons is drawn.
- `mode_control` (*SegmentedControl*): The switch between the exercises and the lessons. The main window puts it in its top bar.
- `resume_button` (*QPushButton*): Returns to the retained activity. The main window places it beside search and shows it on tiles after an activity begins.
- `no_results` (*QLabel*): Shown when no tiles match the search.
- `mode` (*str*): "exercises" or "lessons": which cards are showing.
- `scroll_area` (*QScrollArea*): Scrolls the rows when the window is shorter than all of them.

**Examples**

```pycon
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> chosen = []
>>> _ = page.exercise_chosen.connect(chosen.append)
>>> page.cards[0].click()
>>> chosen == [REGISTRY[0]]
True
```

**Constructor**

Build the page.

**Parameters**

- `registry` (*iterable of type of Exercise*): The exercises to show, in the order to show them.
- `parent` (*QWidget or None, default None*): The widget that owns the page. Keyword-only.

**Constructor examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> len(HomePage([NoteNames]).cards)
1
```

### HomePage.set_search

```python
def set_search(text: str) -> None
```

Show only tiles matching a title, description or category search.

**Parameters**

- `text` (*str*): Case-insensitive search text; empty text restores all tiles.

**Examples**

```pycon
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> page.set_search("keyboard")
>>> page._query
'keyboard'
```

### HomePage.set_mode

```python
def set_mode(
    mode: str,
    *,
    animate: bool = True,
) -> None
```

Show the exercises or the lessons, and remember which.

The cards change with the transition that is chosen in the settings. The new cards are in place at once, so nothing
waits on it.

**Parameters**

- `mode` (*str*): "exercises" or "lessons".
- `animate` (*bool, default True*): Play the chosen transition; if False the new cards simply appear. Keyword-only.

**Examples**

```pycon
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> page.set_mode("lessons")
>>> page.mode, page.mode_control.current()
('lessons', 1)
>>> page.set_mode("exercises")
```

### HomePage.showEvent

```python
def showEvent(event: QShowEvent) -> None
```

Bring the lesson cards up to date each time the page is shown, so they say where each lesson was left.

**Parameters**

- `event` (*QShowEvent*): The show.

**Examples**

```pycon
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> page.show()
```

### HomePage.resizeEvent

```python
def resizeEvent(event: QResizeEvent) -> None
```

Lay the cards out again when the page changes size.

**Parameters**

- `event` (*QResizeEvent*): The resize that happened.

**Examples**

```pycon
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> page.show()
>>> page.resize(1000, 600)
>>> page._columns >= 1
True
```
{% endraw %}
