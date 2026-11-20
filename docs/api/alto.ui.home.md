---
title: alto.ui.home
parent: api
package: alto.ui
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

## category_tree

```python
def category_tree(name: str) -> QTreeWidget
```

Build a navigation tree with themed checkboxes and right-aligned expansion arrows.

**Parameters**

- `name` (*str*): Accessible name of the tree.

**Returns**

- *QTreeWidget*: Empty tree ready for categories and exercises.

**Examples**

```pycon
>>> category_tree("Decks").columnCount()
2
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

- `icon` (*str*): The inside of a 24 by 24 SVG, drawn in the text color. Keyword-only.
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
'Name the interval between two notes.'
```

### ExerciseCard.set_counts

```python
def set_counts(counts: tuple[int, int] | tuple[int, int, int] | None) -> None
```

Show due reviews, new cards, and outstanding incorrect cards in the upper right corner.

**Parameters**

- `counts` (*tuple of int or None*): Reviews due, new cards available, and optionally the outstanding incorrect count. None hides the counts.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> card = ExerciseCard(NoteNames)
>>> card.set_counts((2, 3, 1))
>>> print(card.counts.toolTip())
Blue — 3 new cards available
Red — 1 incorrect card awaiting a correct answer
Green — 2 reviews due
```

## lesson_card

```python
def lesson_card(
    lesson: Lesson,
    *,
    parent: QWidget | None = None,
) -> TileCard
```

Make the card of a lesson: the icon of the exercise that practices the same topic, and how far through it you are.

**Parameters**

- `lesson` (*Lesson*): The lesson.
- `parent` (*QWidget or None, default None*): The widget that owns the card. Keyword-only.

**Returns**

- *TileCard*: The card, which says "Start" or "Continue at step N".

**Examples**

```pycon
>>> card = lesson_card(LESSONS[0])
>>> card.accessibleName()
'Pitches and Notes, Notation'
```

## HomePage

```python
HomePage(
    registry: Iterable[type[Exercise]],
    *,
    parent: QWidget | None = None,
    learner: Learner | None = None,
    filter_layout: QHBoxLayout | None = None,
)
```

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
- `learner` (*Learner or None*): Profile supplying the exercise tile counts.
- `filter_layout` (*QHBoxLayout or None*): Shared workspace layout for the filter sidebar. A standalone page places it beside its tiles.

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

- `text` (*str*): Case-insensitive search text. Empty text shows every tile in the selected category.

**Examples**

```pycon
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> page.set_search("keyboard")
>>> page._query
'keyboard'
```

### HomePage.matches_filter

```python
def matches_filter(
    card: TileCard,
    *,
    section: str,
) -> bool
```

Check whether a tile matches the search text and the selection for its section.

**Parameters**

- `card` (*TileCard*): Exercise or lesson tile to check.
- `section` (*str*): Section containing the tile, either "exercises" or "lessons".

**Returns**

- *bool*: True if both filters include the tile.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> page = HomePage([NoteNames])
>>> page.matches_filter(page.cards[0], section="exercises")
True
```

### HomePage.eventFilter

```python
def eventFilter(
    watched: QObject,
    event: QEvent,
) -> bool
```

Fit the open filter sidebar when its workspace changes width.

**Parameters**

- `watched` (*QObject*): Widget containing the activity and sidebar.
- `event` (*QEvent*): Event delivered to the widget.

**Returns**

- *bool*: Whether the base widget consumes the event.

**Examples**

```pycon
Dragging the navigation divider resizes the space available for the filters.
```

### HomePage.set_filter_available

```python
def set_filter_available(available: bool) -> None
```

Show the filter control on browsing and exercise pages, remembering the sidebar's open state.

**Parameters**

- `available` (*bool*): Whether the current page supports filtering.

**Examples**

```pycon
>>> page = HomePage([])
>>> page.set_filter_available(False)
>>> page.category_filter.isHidden()
True
```

### HomePage.restore_tile_filters

```python
def restore_tile_filters(
    selections: dict[str, frozenset[str]],
    *,
    expanded: bool | None = None,
) -> None
```

Restore exercise and lesson checkboxes after a theme change.

**Parameters**

- `selections` (*dict of str to frozenset of str*): Checked tile titles for each section with a saved filter.
- `expanded` (*bool or None*): Restore the sidebar at its open or closed width immediately. None keeps its current state.

**Examples**

```pycon
>>> HomePage([]).restore_tile_filters({})
```

### HomePage.set_category

```python
def set_category(category: str | None) -> None
```

Select the tiles of one category, or all tiles when the category is absent.

**Parameters**

- `category` (*str or None*): Case-folded category name, or None for all tiles.

**Examples**

```pycon
>>> HomePage([]).set_category(None)
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

### HomePage.page_changed

```python
def page_changed() -> None
```

Animate the tiles from an empty grid on return, or stop the animation when leaving.

**Examples**

```pycon
>>> page = HomePage([])
>>> page.page_changed()
>>> page.canvas.running
False
```

### HomePage.refresh_counts

```python
def refresh_counts() -> None
```

Refresh each exercise tile and the totals for the current filters.

**Examples**

```pycon
>>> HomePage([]).refresh_counts()
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
