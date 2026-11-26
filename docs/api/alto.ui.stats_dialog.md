---
title: alto.ui.stats_dialog
parent: api
package: alto.ui
api_components: [{"title": "StatsPage", "url": "/api/alto.ui.stats_dialog/class-statspage/"}, {"title": "Tile", "url": "/api/alto.ui.stats_dialog/class-tile/"}, {"title": "format_duration", "url": "/api/alto.ui.stats_dialog/function-format_duration/"}, {"title": "period_title", "url": "/api/alto.ui.stats_dialog/function-period_title/"}, {"title": "since_for", "url": "/api/alto.ui.stats_dialog/function-since_for/"}]
permalink: /api/alto.ui.stats_dialog/
---
{% raw %}
The statistics screen: a few numbers and charts about how practice is
going.

## Classes

- [`Tile`](class-tile/) — One headline number with its caption.
- [`StatsPage`](class-statspage/) — The statistics, as a page of the main window.

## Functions

- [`since_for`](function-since_for/) — Return the timestamp a timeframe starts from.
- [`format_duration`](function-format_duration/) — Write a length of time the way the statistics show it.
- [`period_title`](function-period_title/) — Name a chart period in words, for the heading of its list of answers.

<details markdown="1">
<summary>Module notes and examples</summary>

It shows the active profile's own answers, filterable by exercise and by
timeframe.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> since_for(
...     None, now=1000.0
... ) is None  # all time: from the start
True
>>> format_duration(3600)
'1 h 00 min'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"since_for": "function-since_for/", "format_duration": "function-format_duration/", "period_title": "function-period_title/", "tile": "class-tile/", "tileshow_value": "class-tile/#tileshow_value", "statspage": "class-statspage/", "statspagerefresh": "class-statspage/#statspagerefresh"}</script>
{% include api-fragments.html %}
