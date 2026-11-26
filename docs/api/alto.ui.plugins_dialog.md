---
title: alto.ui.plugins_dialog
parent: api
package: alto.ui
api_components: [{"title": "PluginsDialog", "url": "/api/alto.ui.plugins_dialog/class-pluginsdialog/"}]
permalink: /api/alto.ui.plugins_dialog/
---
{% raw %}
The Plugins dialog: the installed plugins on the left, and the buttons
that add or remove one on the right.

## Classes

- [`PluginsDialog`](class-pluginsdialog/) — List the installed plugins and offer to install one from a file or uninstall the selected one.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> PluginsDialog(
...     Path("no-such-plugins-folder")
... ).windowTitle()
'Plugins'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"pluginsdialog": "class-pluginsdialog/", "pluginsdialogselected": "class-pluginsdialog/#pluginsdialogselected", "pluginsdialogrefresh": "class-pluginsdialog/#pluginsdialogrefresh", "pluginsdialogdone": "class-pluginsdialog/#pluginsdialogdone"}</script>
{% include api-fragments.html %}
