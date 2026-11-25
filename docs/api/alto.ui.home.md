---
title: alto.ui.home
parent: api
package: alto.ui
permalink: /api/alto.ui.home/
---
{% raw %}
The start screen: a card for every exercise, or for every lesson, in
rows.

A switch at the top chooses between the exercises and the lessons.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> len(page.cards) == len(REGISTRY)
True
```

## category_tree

<div class="api-signature" markdown="1">

```python
def category_tree(name: str) -> QTreeWidget
```

{% endraw %}{% include api-source.html name="category_tree" line=166 %}{% raw %}

</div>

Build a navigation tree with themed checkboxes and right-aligned
expansion arrows.

**Parameters**

- `name` (*str*): Accessible name of the tree.

**Returns**

- *QTreeWidget*: Empty tree ready for categories and exercises.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> category_tree("Decks").columnCount()
2
```

## TileCard

<div class="api-signature" markdown="1">

```python
TileCard(
    *,
    icon: str,
    category: str,
    name: str,
    about: str,
    progress: tuple[int, int] | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="TileCard" line=312 %}{% raw %}

</div>

Bases: `QPushButton`

A big button: an icon on top, then a category, a name and a short
description, and optionally a lesson's progress.

Progress takes no room in the layout: a strip along the bottom edge
shows it, and "Step N/M" sits in the top-right
corner, both only once the lesson has been begun. A card with or
without progress therefore has the same size and the
same icon.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = TileCard(
...     icon=icons.EXERCISE_CIRCLE,
...     category="Scales & Keys",
...     name="Circle of Fifths",
...     about="Find keys.",
... )
>>> (card.width(), card.height()) == (
...     CARD_W,
...     CARD_H,
... )
True
>>> card.accessibleName()
'Circle of Fifths, Scales & Keys'
```

**Constructor**

Build a card.

**Parameters**

- `icon` (*str*): The inside of a 24 by 24 SVG, drawn in the text color. Keyword-only.
- `category` (*str*): The small heading above the name. Keyword-only.
- `name` (*str*): The name. Keyword-only.
- `about` (*str*): A line of description, which is also the tooltip. Keyword-only.
- `progress` (*tuple of int or None, default None*): The step you are on, counting from 0, and how many steps there are. The bar and "Step N/M" appear only once the first step has been passed; nothing is drawn if None or at step 0. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns the card. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = TileCard(
...     icon=icons.HELP,
...     category="Help",
...     name="Help",
...     about="Get help.",
...     progress=(1, 8),
... )
>>> card.toolTip(), card.accessibleDescription()
('Get help.', 'Get help. Continue at step 2 of 8.')
```

### TileCard.changeEvent

<div class="api-signature" markdown="1">

```python
def changeEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="TileCard.changeEvent" line=494 %}{% raw %}

</div>

Recolor the icon when the tile receives a new palette.

**Parameters**

- `event` (*QEvent*): The widget change delivered by Qt.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = lesson_card(LESSONS[0])
>>> card.changeEvent(
...     QEvent(QEvent.Type.PaletteChange)
... )
```

## exercise_icon

<div class="api-signature" markdown="1">

```python
def exercise_icon(name: str) -> str
```

{% endraw %}{% include api-source.html name="exercise_icon" line=515 %}{% raw %}

</div>

Find the icon for an exercise: the one its plugin supplies, or
Alto's own.

**Parameters**

- `name` (*str*): The exercise's class name.

**Returns**

- *str*: SVG shapes with COLOR where the theme's ink goes.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> exercise_icon(
...     "NoteNames"
... ) == icons.EXERCISE_NOTE_NAMES
True
>>> exercise_icon(
...     "pack.nothing.here"
... ) == icons.EXERCISE_NOTE_NAMES
True
```

## lesson_icon

<div class="api-signature" markdown="1">

```python
def lesson_icon(lesson: Lesson) -> str
```

{% endraw %}{% include api-source.html name="lesson_icon" line=548 %}{% raw %}

</div>

Use the lesson's own icon when present, falling back to its primary
exercise's icon.

**Parameters**

- `lesson` (*Lesson*): The lesson.

**Returns**

- *str*: SVG shapes with COLOR where the theme's ink goes.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> lesson_icon(LESSONS[0]) == exercise_icon(
...     LESSONS[0].exercise
... )
True
```

## ExerciseCard

<div class="api-signature" markdown="1">

```python
ExerciseCard(
    cls: type[Exercise],
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ExerciseCard" line=573 %}{% raw %}

</div>

Bases: `TileCard`

The card of an exercise: its icon on top, then its category, name
and a one-line description.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> card = ExerciseCard(NoteNames)
>>> card.toolTip() == NoteNames.description
True
>>> (card.width(), card.height()) == (
...     CARD_W,
...     CARD_H,
... )
True
```

**Constructor**

Build the card for one exercise.

**Parameters**

- `cls` (*type of Exercise*): The exercise class; its name, category and description are shown, and its class name picks the icon.
- `parent` (*QWidget or None, default None*): The widget that owns the card. Keyword-only.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import (
...     IntervalNames,
... )
>>> ExerciseCard(IntervalNames).toolTip()
'Name the interval between two notes.'
```

### ExerciseCard.set_counts

<div class="api-signature" markdown="1">

```python
def set_counts(counts: tuple[int, int] | tuple[int, int, int] | None) -> None
```

{% endraw %}{% include api-source.html name="ExerciseCard.set_counts" line=631 %}{% raw %}

</div>

Show due reviews, new cards, and outstanding incorrect cards in
the upper right corner.

**Parameters**

- `counts` (*tuple of int or None*): Reviews due, new cards available, and optionally the outstanding incorrect count. None hides the counts.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> card = ExerciseCard(NoteNames)
>>> card.set_counts((2, 3, 1))
>>> print(card.counts.toolTip())
Blue — 3 new cards available
Red — 1 incorrect card awaiting a correct answer
Green — 2 reviews due
```

## lesson_card

<div class="api-signature" markdown="1">

```python
def lesson_card(
    lesson: Lesson,
    *,
    parent: QWidget | None = None,
) -> TileCard
```

{% endraw %}{% include api-source.html name="lesson_card" line=672 %}{% raw %}

</div>

Make the card of a lesson: the icon of the exercise that practices
the same topic, and a bar for how far through it you are.

**Parameters**

- `lesson` (*Lesson*): The lesson.
- `parent` (*QWidget or None, default None*): The widget that owns the card. Keyword-only.

**Returns**

- *TileCard*: The card, with a progress bar and "Step N/M" in its corner once the lesson has been begun.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = lesson_card(LESSONS[0])
>>> card.accessibleName()
'Pitches and Notes, Notation'
```

## HomePage

<div class="api-signature" markdown="1">

```python
HomePage(
    registry: Iterable[type[Exercise]],
    *,
    parent: QWidget | None = None,
    learner: Learner | None = None,
    filter_layout: QHBoxLayout | None = None,
)
```

{% endraw %}{% include api-source.html name="HomePage" line=710 %}{% raw %}

</div>

Bases: `QWidget`

The start screen: a row of exercise buttons for each category.

**Attributes**

- `exercise_chosen` (*Signal*): Emitted with the `Exercise` class when a card is clicked.
- `lesson_chosen` (*Signal*): Emitted with a lesson's key when its card is clicked.
- `filters_changed` (*Signal*): Emitted after a change to the search, tile selection or displayed section.
- `cards` (*list of ExerciseCard*): One per exercise, in registry order.
- `lesson_cards` (*list of TileCard*): One per lesson, with how far through it you are.
- `canvas` (*TransitionCanvas*): Where the transition between the exercises and the lessons is drawn.
- `mode_control` (*SegmentedControl*): The switch between the exercises and the lessons. The main window puts it in its top bar.
- `resume_button` (*QPushButton*): Returns to the retained activity. The main window places it beside search and shows it on tiles after an activity begins.
- `category_filter` (*QToolButton*): Shows or hides the filter sidebar from the right end of the search row.
- `no_results` (*QLabel*): Shown when no tiles match the search.
- `mode` (*str*): "exercises" or "lessons": which cards are showing.
- `scroll_area` (*QScrollArea*): Scrolls the rows when the window is shorter than all of them.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> chosen = []
>>> _ = page.exercise_chosen.connect(
...     chosen.append
... )
>>> page.cards[0].click()
>>> chosen == [REGISTRY[0]]
True
```

**Constructor**

Build the page.

**Parameters**

- `registry` (*iterable of type of Exercise*): The exercises to show, in the order to show them.
- `parent` (*QWidget or None, default None*): The widget that owns the page. Keyword-only.
- `learner` (*Learner or None*): Profile supplying the exercise tile counts.
- `filter_layout` (*QHBoxLayout or None*): Shared workspace layout for the filter sidebar. A standalone page places it beside its tiles.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> len(HomePage([NoteNames]).cards)
1
```

### HomePage.set_search

<div class="api-signature" markdown="1">

```python
def set_search(text: str) -> None
```

{% endraw %}{% include api-source.html name="HomePage.set_search" line=926 %}{% raw %}

</div>

Show only tiles matching a title, description or category
search.

**Parameters**

- `text` (*str*): Case-insensitive search text. Empty text shows every tile in the selected category.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> page.set_search("keyboard")
>>> page._query
'keyboard'
```

### HomePage.matches_filter

<div class="api-signature" markdown="1">

```python
def matches_filter(
    card: TileCard,
    *,
    section: str,
) -> bool
```

{% endraw %}{% include api-source.html name="HomePage.matches_filter" line=966 %}{% raw %}

</div>

Check whether a tile matches the search text and the selection
for its section.

**Parameters**

- `card` (*TileCard*): Exercise or lesson tile to check.
- `section` (*str*): Section containing the tile, either "exercises" or "lessons".

**Returns**

- *bool*: True if both filters include the tile.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> page = HomePage([NoteNames])
>>> page.matches_filter(
...     page.cards[0], section="exercises"
... )
True
```

### HomePage.eventFilter

<div class="api-signature" markdown="1">

```python
def eventFilter(
    watched: QObject,
    event: QEvent,
) -> bool
```

{% endraw %}{% include api-source.html name="HomePage.eventFilter" line=1070 %}{% raw %}

</div>

Fit the open filter sidebar when its workspace changes width.

**Parameters**

- `watched` (*QObject*): Widget containing the activity and sidebar.
- `event` (*QEvent*): Event delivered to the widget.

**Returns**

- *bool*: Whether the base widget consumes the event.

**Examples**

```text
Dragging the navigation divider resizes the space available for
the filters.
```

### HomePage.set_filter_available

<div class="api-signature" markdown="1">

```python
def set_filter_available(available: bool) -> None
```

{% endraw %}{% include api-source.html name="HomePage.set_filter_available" line=1119 %}{% raw %}

</div>

Show the filter control on browsing and exercise pages,
remembering the sidebar's open state.

**Parameters**

- `available` (*bool*): Whether the current page supports filtering.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = HomePage([])
>>> page.set_filter_available(False)
>>> page.category_filter.isHidden()
True
```

### HomePage.restore_tile_filters

<div class="api-signature" markdown="1">

```python
def restore_tile_filters(
    selections: dict[str, frozenset[str]],
    *,
    expanded: bool | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="HomePage.restore_tile_filters" line=1223 %}{% raw %}

</div>

Restore exercise and lesson checkboxes after a theme change.

**Parameters**

- `selections` (*dict of str to frozenset of str*): Checked tile titles for each section with a saved filter.
- `expanded` (*bool or None*): Restore the sidebar at its open or closed width immediately. None keeps its current state.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HomePage([]).restore_tile_filters({})
```

### HomePage.set_category

<div class="api-signature" markdown="1">

```python
def set_category(category: str | None) -> None
```

{% endraw %}{% include api-source.html name="HomePage.set_category" line=1253 %}{% raw %}

</div>

Select the tiles of one category, or all tiles when the category
is absent.

**Parameters**

- `category` (*str or None*): Case-folded category name, or None for all tiles.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HomePage([]).set_category(None)
```

### HomePage.set_mode

<div class="api-signature" markdown="1">

```python
def set_mode(
    mode: str,
    *,
    animate: bool = True,
) -> None
```

{% endraw %}{% include api-source.html name="HomePage.set_mode" line=1304 %}{% raw %}

</div>

Show the exercises or the lessons, and remember which.

The cards change with the transition that is chosen in the
settings. The new cards are in place at once, so nothing
waits on it.

**Parameters**

- `mode` (*str*): "exercises" or "lessons".
- `animate` (*bool, default True*): Play the chosen transition; if False the new cards simply appear. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> page.set_mode("lessons")
>>> page.mode, page.mode_control.current()
('lessons', 1)
>>> page.set_mode("exercises")
```

### HomePage.page_changed

<div class="api-signature" markdown="1">

```python
def page_changed() -> None
```

{% endraw %}{% include api-source.html name="HomePage.page_changed" line=1375 %}{% raw %}

</div>

Animate the tiles from an empty grid on return, or stop the
animation when leaving.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = HomePage([])
>>> page.page_changed()
>>> page.canvas.running
False
```

### HomePage.refresh_counts

<div class="api-signature" markdown="1">

```python
def refresh_counts() -> None
```

{% endraw %}{% include api-source.html name="HomePage.refresh_counts" line=1475 %}{% raw %}

</div>

Refresh each exercise tile and the totals for the current
filters.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HomePage([]).refresh_counts()
```

### HomePage.showEvent

<div class="api-signature" markdown="1">

```python
def showEvent(event: QShowEvent) -> None
```

{% endraw %}{% include api-source.html name="HomePage.showEvent" line=1507 %}{% raw %}

</div>

Bring the lesson cards up to date each time the page is shown,
so they say where each lesson was left.

**Parameters**

- `event` (*QShowEvent*): The show.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> page.show()
```

### HomePage.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="HomePage.resizeEvent" line=1528 %}{% raw %}

</div>

Lay the cards out again when the page changes size.

**Parameters**

- `event` (*QResizeEvent*): The resize that happened.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> page.show()
>>> page.resize(1000, 600)
>>> page._columns >= 1
True
```
{% endraw %}
