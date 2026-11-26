---
title: alto.ui.interval_range
parent: api
package: alto.ui
api_components: [{"title": "IntervalRangeSlider", "url": "/api/alto.ui.interval_range/class-intervalrangeslider/"}]
permalink: /api/alto.ui.interval_range/
---
{% raw %}
A two-handle slider for selecting interval distances without changing
the keyboard range.

## Classes

- [`IntervalRangeSlider`](class-intervalrangeslider/) — A draggable interval range with keyboard controls for either endpoint.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> slider = IntervalRangeSlider()
>>> slider.set_range(3, high=12, maximum=24)
>>> slider.low, slider.high
(3, 12)
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"intervalrangeslider": "class-intervalrangeslider/", "intervalrangesliderset_range": "class-intervalrangeslider/#intervalrangesliderset_range", "intervalrangeslidermove_endpoint": "class-intervalrangeslider/#intervalrangeslidermove_endpoint", "intervalrangesliderpaintevent": "class-intervalrangeslider/#intervalrangesliderpaintevent", "intervalrangeslidermousepressevent": "class-intervalrangeslider/#intervalrangeslidermousepressevent", "intervalrangeslidermousemoveevent": "class-intervalrangeslider/#intervalrangeslidermousemoveevent", "intervalrangeslidermousereleaseevent": "class-intervalrangeslider/#intervalrangeslidermousereleaseevent", "intervalrangesliderkeypressevent": "class-intervalrangeslider/#intervalrangesliderkeypressevent"}</script>
{% include api-fragments.html %}
