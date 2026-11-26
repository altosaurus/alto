---
title: alto.ui.style
parent: api
package: alto.ui
api_components: [{"title": "app_style", "url": "/api/alto.ui.style/function-app_style/"}, {"title": "navigation_heading_style", "url": "/api/alto.ui.style/function-navigation_heading_style/"}]
permalink: /api/alto.ui.style/
---
{% raw %}
Application-wide stylesheet: rounded corners on buttons, panes, lists
and scroll bars.

## Functions

- [`navigation_heading_style`](function-navigation_heading_style/) — Style category headings in the navigation pane and tile filters.
- [`app_style`](function-app_style/) — Build the stylesheet for a palette.

<details markdown="1">
<summary>Module notes and examples</summary>

Colors come from the palette so it follows the system light/dark theme.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RADIUS
10
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"navigation_heading_style": "function-navigation_heading_style/", "app_style": "function-app_style/"}</script>
{% include api-fragments.html %}
