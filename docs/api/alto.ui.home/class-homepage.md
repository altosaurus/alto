---
title: HomePage
parent: alto.ui.home
api_module: alto.ui.home
package: alto.ui
permalink: /api/alto.ui.home/class-homepage/
---
{% raw %}
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

{% endraw %}{% include api-source.html name="HomePage" line=712 %}{% raw %}

</div>

Bases: `QWidget`

The start screen: a row of exercise buttons for each category.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `exercise_chosen` | `Signal` | Emitted with the `Exercise` class when a card is clicked. |
| `lesson_chosen` | `Signal` | Emitted with a lesson's key when its card is clicked. |
| `filters_changed` | `Signal` | Emitted after a change to the search, tile selection or displayed section. |
| `cards` | `list of ExerciseCard` | One per exercise, in registry order. |
| `lesson_cards` | `list of TileCard` | One per lesson, with how far through it you are. |
| `canvas` | `TransitionCanvas` | Where the transition between the exercises and the lessons is drawn. |
| `mode_control` | `SegmentedControl` | The switch between the exercises and the lessons. The main window puts it in its top bar. |
| `resume_button` | `QPushButton` | Returns to the retained activity. The main window places it beside search and shows it on tiles after an activity begins. |
| `category_filter` | `QToolButton` | Shows or hides the filter sidebar from the right end of the search row. |
| `no_results` | `QLabel` | Shown when no tiles match the search. |
| `mode` | `str` | "exercises" or "lessons": which cards are showing. |
| `scroll_area` | `QScrollArea` | Scrolls the rows when the window is shorter than all of them. |

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

| Parameter | Type | Description |
| --- | --- | --- |
| `registry` | `iterable of type of Exercise` | The exercises to show, in the order to show them. |
| `parent` | `QWidget or None, default None` | The widget that owns the page. Keyword-only. |
| `learner` | `Learner or None` | Profile supplying the exercise tile counts. |
| `filter_layout` | `QHBoxLayout or None` | Shared workspace layout for the filter sidebar. A standalone page places it beside its tiles. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> len(HomePage([NoteNames]).cards)
1
```

## HomePage.set_search

<div class="api-signature" markdown="1">

```python
def set_search(text: str) -> None
```

{% endraw %}{% include api-source.html name="HomePage.set_search" line=928 %}{% raw %}

</div>

Show only tiles matching a title, description or category
search.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | Case-insensitive search text. Empty text shows every tile in the selected category. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> page.set_search("keyboard")
>>> page._query
'keyboard'
```

## HomePage.matches_filter

<div class="api-signature" markdown="1">

```python
def matches_filter(
    card: TileCard,
    *,
    section: str,
) -> bool
```

{% endraw %}{% include api-source.html name="HomePage.matches_filter" line=968 %}{% raw %}

</div>

Check whether a tile matches the search text and the selection
for its section.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `card` | `TileCard` | Exercise or lesson tile to check. |
| `section` | `str` | Section containing the tile, either "exercises" or "lessons". |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if both filters include the tile. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> page = HomePage([NoteNames])
>>> page.matches_filter(
...     page.cards[0], section="exercises"
... )
True
```

## HomePage.eventFilter

<div class="api-signature" markdown="1">

```python
def eventFilter(
    watched: QObject,
    event: QEvent,
) -> bool
```

{% endraw %}{% include api-source.html name="HomePage.eventFilter" line=1072 %}{% raw %}

</div>

Fit the open filter sidebar when its workspace changes width.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `watched` | `QObject` | Widget containing the activity and sidebar. |
| `event` | `QEvent` | Event delivered to the widget. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | Whether the base widget consumes the event. |

**Examples**

```text
Dragging the navigation divider resizes the space available for
the filters.
```

## HomePage.set_filter_available

<div class="api-signature" markdown="1">

```python
def set_filter_available(available: bool) -> None
```

{% endraw %}{% include api-source.html name="HomePage.set_filter_available" line=1121 %}{% raw %}

</div>

Show the filter control on browsing and exercise pages,
remembering the sidebar's open state.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `available` | `bool` | Whether the current page supports filtering. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = HomePage([])
>>> page.set_filter_available(False)
>>> page.category_filter.isHidden()
True
```

## HomePage.restore_tile_filters

<div class="api-signature" markdown="1">

```python
def restore_tile_filters(
    selections: dict[str, frozenset[str]],
    *,
    expanded: bool | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="HomePage.restore_tile_filters" line=1225 %}{% raw %}

</div>

Restore exercise and lesson checkboxes after a theme change.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `selections` | `dict of str to frozenset of str` | Checked tile titles for each section with a saved filter. |
| `expanded` | `bool or None` | Restore the sidebar at its open or closed width immediately. None keeps its current state. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HomePage([]).restore_tile_filters({})
```

## HomePage.set_category

<div class="api-signature" markdown="1">

```python
def set_category(category: str | None) -> None
```

{% endraw %}{% include api-source.html name="HomePage.set_category" line=1255 %}{% raw %}

</div>

Select the tiles of one category, or all tiles when the category
is absent.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `category` | `str or None` | Case-folded category name, or None for all tiles. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HomePage([]).set_category(None)
```

## HomePage.set_mode

<div class="api-signature" markdown="1">

```python
def set_mode(
    mode: str,
    *,
    animate: bool = True,
) -> None
```

{% endraw %}{% include api-source.html name="HomePage.set_mode" line=1306 %}{% raw %}

</div>

Show the exercises or the lessons, and remember which.

The cards change with the transition that is chosen in the
settings. The new cards are in place at once, so nothing
waits on it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `mode` | `str` | "exercises" or "lessons". |
| `animate` | `bool, default True` | Play the chosen transition; if False the new cards simply appear. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> page.set_mode("lessons")
>>> page.mode, page.mode_control.current()
('lessons', 1)
>>> page.set_mode("exercises")
```

## HomePage.page_changed

<div class="api-signature" markdown="1">

```python
def page_changed() -> None
```

{% endraw %}{% include api-source.html name="HomePage.page_changed" line=1377 %}{% raw %}

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

## HomePage.refresh_counts

<div class="api-signature" markdown="1">

```python
def refresh_counts() -> None
```

{% endraw %}{% include api-source.html name="HomePage.refresh_counts" line=1477 %}{% raw %}

</div>

Refresh each exercise tile and the totals for the current
filters.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HomePage([]).refresh_counts()
```

## HomePage.showEvent

<div class="api-signature" markdown="1">

```python
def showEvent(event: QShowEvent) -> None
```

{% endraw %}{% include api-source.html name="HomePage.showEvent" line=1509 %}{% raw %}

</div>

Bring the lesson cards up to date each time the page is shown,
so they say where each lesson was left.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QShowEvent` | The show. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> page.show()
```

## HomePage.resizeEvent

<div class="api-signature" markdown="1">

```python
def resizeEvent(event: QResizeEvent) -> None
```

{% endraw %}{% include api-source.html name="HomePage.resizeEvent" line=1530 %}{% raw %}

</div>

Lay the cards out again when the page changes size.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QResizeEvent` | The resize that happened. |

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
