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

Notes the current instrument has no recording of are made by shifting the nearest recording the first time they play, which
takes a few tens of milliseconds each. They are made here too, one per step, so that even a first play is quick.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> warmed = []
>>> owner = QObject()
>>> start(owner, steps=[lambda: warmed.append(1), lambda: warmed.append(2)], delay=0)
>>> import time
>>> deadline = time.monotonic() + 2
>>> while len(warmed) < 2 and time.monotonic() < deadline:
...     app.processEvents()
>>> warmed
[1, 2]
>>> while any(timer.isActive() for timer in owner.findChildren(QTimer)) and time.monotonic() < deadline:
...     app.processEvents()
>>> any(timer.isActive() for timer in owner.findChildren(QTimer))  # it stops once every step has run
False
```

## warmup_steps

```python
def warmup_steps() -> list[Callable[[], None]]
```

List the steps of the warm-up.

They draw a staff; lay out text in the application's own font size and each style sheet size, plain and bold, at the zoom;
and, while sound is on, make the notes the current instrument has no recording of.

**Returns**

- *list of callable*: The steps, each a few tens of milliseconds at most.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> notes = len(sounds.unrecorded()) if sounds.enabled else 0
>>> len(warmup_steps()) == 1 + 22 + notes  # the staff, eleven sizes in two weights, and the notes
True
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

```console?lang=python&prompt=%3E%3E%3E,...
>>> start(QObject(), steps=[], delay=0)  # nothing to do
```
{% endraw %}
