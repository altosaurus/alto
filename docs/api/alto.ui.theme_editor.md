---
title: alto.ui.theme_editor
parent: api
package: alto.ui
api_components: [{"title": "ThemeEditor", "url": "/api/alto.ui.theme_editor/class-themeeditor/"}]
permalink: /api/alto.ui.theme_editor/
---
{% raw %}
The editor for a theme of the user's own: a name, and a color for every
part of its light and dark versions.

## Classes

- [`ThemeEditor`](class-themeeditor/) — A form to make a theme, or change one: its name, and the colors of its light and dark versions.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> editor = ThemeEditor()
>>> editor.load(None)
>>> editor.record()["name"]
'My theme'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"themeeditor": "class-themeeditor/", "themeeditoreventfilter": "class-themeeditor/#themeeditoreventfilter", "themeeditorload": "class-themeeditor/#themeeditorload", "themeeditorrecord": "class-themeeditor/#themeeditorrecord"}</script>
{% include api-fragments.html %}
