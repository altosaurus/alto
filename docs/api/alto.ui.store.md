---
title: alto.ui.store
parent: api
package: alto.ui
api_components: [{"title": "bool_value", "url": "/api/alto.ui.store/function-bool_value/"}, {"title": "choices_value", "url": "/api/alto.ui.store/function-choices_value/"}, {"title": "export_settings", "url": "/api/alto.ui.store/function-export_settings/"}, {"title": "import_settings", "url": "/api/alto.ui.store/function-import_settings/"}, {"title": "int_value", "url": "/api/alto.ui.store/function-int_value/"}, {"title": "joined", "url": "/api/alto.ui.store/function-joined/"}, {"title": "keys_value", "url": "/api/alto.ui.store/function-keys_value/"}, {"title": "list_value", "url": "/api/alto.ui.store/function-list_value/"}, {"title": "save_bool", "url": "/api/alto.ui.store/function-save_bool/"}, {"title": "store", "url": "/api/alto.ui.store/function-store/"}, {"title": "text_value", "url": "/api/alto.ui.store/function-text_value/"}]
permalink: /api/alto.ui.store/
---
{% raw %}
The application's saved settings (a thin layer over `QSettings`).

## Functions

- [`store`](function-store/) — Return the app's saved settings.
- [`int_value`](function-int_value/) — Read an integer setting.
- [`text_value`](function-text_value/) — Read a saved setting as text.
- [`bool_value`](function-bool_value/) — Read a switch saved as the text "true" or "false".
- [`save_bool`](function-save_bool/) — Save a switch as the text "true" or "false", the form `bool_value` reads.
- [`list_value`](function-list_value/) — Read a saved list of words, such as "treble,bass".
- [`choices_value`](function-choices_value/) — Read a saved set of choices, keeping only the ones that are still offered.
- [`keys_value`](function-keys_value/) — Read a saved set of key signatures, each a number of sharps (positive) or flats (negative) up to seven.
- [`joined`](function-joined/) — Write values as the text that `list_value`, `choices_value` and `keys_value` read back.
- [`export_settings`](function-export_settings/) — Return every saved preference, by key, for a backup.
- [`import_settings`](function-import_settings/) — Replace every saved preference with the ones from a backup, so the preferences are exactly as they were.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings = store()
>>> settings.setValue("demo/count", 3)
>>> int_value(
...     settings, key="demo/count", default=0
... )
3
>>> settings.remove("demo")
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"store": "function-store/", "int_value": "function-int_value/", "text_value": "function-text_value/", "bool_value": "function-bool_value/", "save_bool": "function-save_bool/", "list_value": "function-list_value/", "choices_value": "function-choices_value/", "keys_value": "function-keys_value/", "joined": "function-joined/", "export_settings": "function-export_settings/", "import_settings": "function-import_settings/"}</script>
{% include api-fragments.html %}
