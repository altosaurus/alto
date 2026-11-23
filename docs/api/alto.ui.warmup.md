---
title: alto.ui.warmup
parent: api
package: alto.ui
permalink: /api/alto.ui.warmup/
---
{% raw %}
Get ready, while Alto sits idle just after it opens, what a first visit to a page would otherwise pay for.

The music font of the notation style is loaded by drawing a small staff out of sight. And most of what makes a page slow to open
the first time is not the page. Labels such as "F♯" and "B♭" use signs that the interface font does not have, so Qt looks for a
font that does, and it does so again for every size and weight of text, about 40 ms each time on Linux. Pages show such labels in
several sizes, so a first visit could spend a tenth of a second looking for fonts. Laying out a line with those signs once in each
size the interface uses, a little at a time while nothing else is happening, makes the first visit to a page about as quick as the
second.

**Examples**

```pycon
>>> warmed = []
>>> owner = QObject()
>>> start(owner, steps=[lambda: warmed.append(1), lambda: warmed.append(2)], delay=0)
>>> import time
>>> deadline = time.monotonic() + 2
>>> while len(warmed) < 2 and time.monotonic() < deadline:
...     app.processEvents()
>>> warmed
[1, 2]
```

## warmup_steps

```python
def warmup_steps() -> list[Callable[[], None]]
```

List the steps of the warm-up: the application's own font size and each style sheet size, plain and bold, at the zoom.

**Returns**

- *list of callable*: The steps, each a few tens of milliseconds at most.

**Examples**

```pycon
>>> len(warmup_steps())  # a staff, then the application's size and the ten style sheet sizes, in two weights
23
```

## start

```python
def start(
    owner: QObject,
    *,
    steps: list[Callable[[], None]] | None = None,
    delay: int = START_DELAY_MS,
) -> None
```

Run the warm-up's steps one at a time, each when the event loop has nothing else to do, beginning after a short delay.

Input and painting are handled between the steps, so the window stays as responsive as it is without the warm-up. If the
owner is deleted first (the window closed), the rest of the steps are dropped.

**Parameters**

- `owner` (*QObject*): What the warm-up belongs to, usually the main window.
- `steps` (*list of callable or None, default None*): The steps; None for the usual ones (`warmup_steps()`). Keyword-only.
- `delay` (*int, default START_DELAY_MS*): How long to wait first, in milliseconds. Keyword-only.

**Examples**

```pycon
>>> start(QObject(), steps=[], delay=0)  # nothing to do
```
{% endraw %}
