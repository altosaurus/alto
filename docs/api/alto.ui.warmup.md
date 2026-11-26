---
title: alto.ui.warmup
parent: api
package: alto.ui
api_components: [{"title": "start", "url": "/api/alto.ui.warmup/function-start/"}, {"title": "warmup_steps", "url": "/api/alto.ui.warmup/function-warmup_steps/"}]
permalink: /api/alto.ui.warmup/
---
{% raw %}
Get ready, while Alto sits idle just after it opens, what a first visit
to a page would otherwise pay for.

## Functions

- [`warmup_steps`](function-warmup_steps/) — List the steps of the warm-up.
- [`start`](function-start/) — Run the warm-up's steps one at a time, each when the event loop has nothing else to do, beginning after a short delay.

<details markdown="1">
<summary>Module notes and examples</summary>

The music font of the notation style is loaded by drawing a small staff
out of sight. And most of what makes a page slow to open
the first time is not the page. Labels such as "F♯" and "B♭" use signs
that the interface font does not have, so Qt looks for a
font that does, and it does so again for every size and weight of text,
about 40 ms each time on Linux. Pages show such labels in
several sizes, so a first visit could spend a tenth of a second looking
for fonts. Laying out a line with those signs once in each
size the interface uses, a little at a time while nothing else is
happening, makes the first visit to a page about as quick as the
second.

Notes the current instrument has no recording of are made by shifting
the nearest recording the first time they play, which
takes a few tens of milliseconds each. They are made here too, one per
step, so that even a first play is quick.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> warmed = []
>>> owner = QObject()
>>> start(
...     owner,
...     steps=[
...         lambda: warmed.append(1),
...         lambda: warmed.append(2),
...     ],
...     delay=0,
... )
>>> import time
>>> deadline = time.monotonic() + 2
>>> while (
...     len(warmed) < 2
...     and time.monotonic() < deadline
... ):
...     app.processEvents()
>>> warmed
[1, 2]
>>> while (
...     any(
...         timer.isActive()
...         for timer in owner.findChildren(
...             QTimer
...         )
...     )
...     and time.monotonic() < deadline
... ):
...     app.processEvents()
>>> any(
...     timer.isActive()
...     for timer in owner.findChildren(QTimer)
... )  # it stops once every step has run
False
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"warmup_steps": "function-warmup_steps/", "start": "function-start/"}</script>
{% include api-fragments.html %}
