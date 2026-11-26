---
title: alto.ui.colors
parent: api
package: alto.ui
api_components: [{"title": "blend", "url": "/api/alto.ui.colors/function-blend/"}, {"title": "blend_name", "url": "/api/alto.ui.colors/function-blend_name/"}]
permalink: /api/alto.ui.colors/
---
{% raw %}
Mixing colors. The interface blends palette colors to get its soft tints
and highlights.

## Functions

- [`blend`](function-blend/) — Return the color a given fraction of the way from one color to another.
- [`blend_name`](function-blend_name/) — Return the hex name of a blended color, for use in a stylesheet.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> blend_name(
...     QColor("#000000"),
...     b=QColor("#ffffff"),
...     t=0.5,
... )
'#808080'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"blend": "function-blend/", "blend_name": "function-blend_name/"}</script>
{% include api-fragments.html %}
