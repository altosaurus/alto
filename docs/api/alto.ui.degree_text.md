---
title: alto.ui.degree_text
parent: api
package: alto.ui
api_components: [{"title": "DegreeButton", "url": "/api/alto.ui.degree_text/class-degreebutton/"}, {"title": "DegreeCheckBox", "url": "/api/alto.ui.degree_text/class-degreecheckbox/"}, {"title": "DegreeLabel", "url": "/api/alto.ui.degree_text/class-degreelabel/"}, {"title": "degree_tooltip", "url": "/api/alto.ui.degree_text/function-degree_tooltip/"}, {"title": "draw_degree_text", "url": "/api/alto.ui.degree_text/function-draw_degree_text/"}]
permalink: /api/alto.ui.degree_text/
---
{% raw %}
Draw scale-degree carets above their digits without relying on
font-specific combining accents.

## Classes

- [`DegreeButton`](class-degreebutton/) — An answer button that draws scale-degree carets directly above the digits.
- [`DegreeCheckBox`](class-degreecheckbox/) — Draw the scale degree caret centered above the checkbox label's digit.
- [`DegreeLabel`](class-degreelabel/) — A plain-text label with explicitly positioned scale-degree carets.

## Functions

- [`draw_degree_text`](function-draw_degree_text/) — Draw text with each combining circumflex centered above its preceding digit.
- [`degree_tooltip`](function-degree_tooltip/) — Render caret examples as an inline image for Qt's rich-text tooltip.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> button = DegreeButton("♭3̂")
>>> button.text()
'♭3̂'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"draw_degree_text": "function-draw_degree_text/", "degree_tooltip": "function-degree_tooltip/", "degreebutton": "class-degreebutton/", "degreebuttonpaintevent": "class-degreebutton/#degreebuttonpaintevent", "degreecheckbox": "class-degreecheckbox/", "degreecheckboxpaintevent": "class-degreecheckbox/#degreecheckboxpaintevent", "degreelabel": "class-degreelabel/", "degreelabelpaintevent": "class-degreelabel/#degreelabelpaintevent"}</script>
{% include api-fragments.html %}
