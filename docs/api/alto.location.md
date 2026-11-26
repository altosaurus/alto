---
title: alto.location
parent: api
package: alto
api_components: [{"title": "alto_home", "url": "/api/alto.location/function-alto_home/"}, {"title": "database_path", "url": "/api/alto.location/function-database_path/"}, {"title": "desktop_name", "url": "/api/alto.location/function-desktop_name/"}, {"title": "settings_folder", "url": "/api/alto.location/function-settings_folder/"}]
permalink: /api/alto.location/
---
{% raw %}
Where Alto keeps its practice history and its settings, and how to keep
them somewhere else with `ALTO_HOME`.

## Functions

- [`alto_home`](function-alto_home/) — Give the folder named by `ALTO_HOME`, if there is one.
- [`database_path`](function-database_path/) — Give the file that holds the practice history.
- [`settings_folder`](function-settings_folder/) — Give the folder that holds the settings when `ALTO_HOME` moves them.
- [`desktop_name`](function-desktop_name/) — Give the name the desktop uses to match Alto's window to its menu entry, and so to its icon in the dock.

<details markdown="1">
<summary>Module notes and examples</summary>

Without `ALTO_HOME` they are in the usual places for the system. With
it, both are in that folder instead, so a copy of Alto
that is being worked on can have its own history and settings, apart
from the copy that is used for practicing.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> database_path(
...     environ={"ALTO_HOME": "/tmp/alto-dev"}
... ).as_posix()
'/tmp/alto-dev/data/alto.db'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"alto_home": "function-alto_home/", "database_path": "function-database_path/", "settings_folder": "function-settings_folder/", "desktop_name": "function-desktop_name/"}</script>
{% include api-fragments.html %}
