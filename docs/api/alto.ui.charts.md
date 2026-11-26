---
title: alto.ui.charts
parent: api
package: alto.ui
api_components: [{"title": "HBarChart", "url": "/api/alto.ui.charts/class-hbarchart/"}, {"title": "HeatmapChart", "url": "/api/alto.ui.charts/class-heatmapchart/"}, {"title": "LineChart", "url": "/api/alto.ui.charts/class-linechart/"}, {"title": "StackedBarChart", "url": "/api/alto.ui.charts/class-stackedbarchart/"}, {"title": "nice_ticks", "url": "/api/alto.ui.charts/function-nice_ticks/"}]
permalink: /api/alto.ui.charts/
---
{% raw %}
Small charts drawn with QPainter, in the application's theme colors.

## Classes

- [`StackedBarChart`](class-stackedbarchart/) — Questions per period, the first-try right ones in green with the missed ones stacked above in red.
- [`LineChart`](class-linechart/) — A value per period joined by a line.
- [`HBarChart`](class-hbarchart/) — One bar per name, on a fixed 0-100 scale, each with its value at the end.
- [`HeatmapChart`](class-heatmapchart/) — A calendar of reviews: a column per week (Monday to Sunday), a square per day, darker the more questions.

## Functions

- [`nice_ticks`](function-nice_ticks/) — Return round tick values from 0 up to just above a top value.

<details markdown="1">
<summary>Module notes and examples</summary>

Stacked bars, a line, horizontal bars and a calendar heatmap. Each has a
title, draws a message when there is nothing to
show, and explains the bar or square under the pointer in a tooltip.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> nice_ticks(13)
[0, 5, 10, 15]
>>> chart = StackedBarChart(
...     "Questions answered"
... )
>>> chart.set_data(
...     ["Mon", "Tue"],
...     right=[3, 1],
...     wrong=[1, 0],
... )
>>> chart.right, chart.wrong
([3, 1], [1, 0])
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"nice_ticks": "function-nice_ticks/", "stackedbarchart": "class-stackedbarchart/", "stackedbarchartset_data": "class-stackedbarchart/#stackedbarchartset_data", "stackedbarchartpaintevent": "class-stackedbarchart/#stackedbarchartpaintevent", "stackedbarchartmousemoveevent": "class-stackedbarchart/#stackedbarchartmousemoveevent", "linechart": "class-linechart/", "linechartset_data": "class-linechart/#linechartset_data", "linechartpaintevent": "class-linechart/#linechartpaintevent", "linechartmousemoveevent": "class-linechart/#linechartmousemoveevent", "hbarchart": "class-hbarchart/", "hbarchartset_data": "class-hbarchart/#hbarchartset_data", "hbarchartpaintevent": "class-hbarchart/#hbarchartpaintevent", "hbarchartmousemoveevent": "class-hbarchart/#hbarchartmousemoveevent", "heatmapchart": "class-heatmapchart/", "heatmapchartset_data": "class-heatmapchart/#heatmapchartset_data", "heatmapchartfirst_day": "class-heatmapchart/#heatmapchartfirst_day", "heatmapchartlevel": "class-heatmapchart/#heatmapchartlevel", "heatmapchartday_at": "class-heatmapchart/#heatmapchartday_at", "heatmapchartpaintevent": "class-heatmapchart/#heatmapchartpaintevent", "heatmapchartmousemoveevent": "class-heatmapchart/#heatmapchartmousemoveevent"}</script>
{% include api-fragments.html %}
