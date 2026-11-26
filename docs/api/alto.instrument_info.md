---
title: alto.instrument_info
parent: api
package: alto
api_components: [{"title": "Coverage", "url": "/api/alto.instrument_info/class-coverage/"}, {"title": "InstrumentInfo", "url": "/api/alto.instrument_info/class-instrumentinfo/"}, {"title": "coverage", "url": "/api/alto.instrument_info/function-coverage/"}]
permalink: /api/alto.instrument_info/
---
{% raw %}
What is known about each instrument's recordings, for the summary shown
in the instrument settings.

## Classes

- [`InstrumentInfo`](class-instrumentinfo/) — The facts about where an instrument's recordings came from.
- [`Coverage`](class-coverage/) — Which notes an instrument has recordings for.

## Functions

- [`coverage`](function-coverage/) — Summarize the notes that have a recording.

<details markdown="1">
<summary>Module notes and examples</summary>

The facts here come from the sources' own pages (the University of Iowa
Musical Instrument Samples, and the Salamander
Grand Piano). What is on disk
(how many notes, their range, their size) is worked out when the page is
shown, not stored here. Pure Python, no Qt.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> coverage(range(60, 73)).describe()
'13 notes, C4 to C5, every semitone'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"instrumentinfo": "class-instrumentinfo/", "coverage": "class-coverage/", "coverageinstalled": "class-coverage/#coverageinstalled", "coveragedescribe": "class-coverage/#coveragedescribe", "coverage-1": "function-coverage/"}</script>
{% include api-fragments.html %}
