---
title: alto.ui.main_window
parent: api
package: alto.ui
api_components: [{"title": "MainWindow", "url": "/api/alto.ui.main_window/class-mainwindow/"}, {"title": "default_size", "url": "/api/alto.ui.main_window/function-default_size/"}]
permalink: /api/alto.ui.main_window/
---
{% raw %}
The main window: tile browsing or a workspace with an independently
selected exercise or lesson list.

## Classes

- [`MainWindow`](class-mainwindow/) — The application window.

## Functions

- [`default_size`](function-default_size/) — Return the size a new window opens at.

<details markdown="1">
<summary>Module notes and examples</summary>

Navigation stays on the left of the top bar, with data tools on the
right. Browsing tiles retains the active activity.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> window = MainWindow()
>>> window.title_label.text()
'Alto - Music Theory'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"default_size": "function-default_size/", "mainwindow": "class-mainwindow/", "mainwindowcloseevent": "class-mainwindow/#mainwindowcloseevent", "mainwindoweventfilter": "class-mainwindow/#mainwindoweventfilter", "mainwindowsidebar_width": "class-mainwindow/#mainwindowsidebar_width", "mainwindowtoggle_sidebar": "class-mainwindow/#mainwindowtoggle_sidebar", "mainwindowopen_exercise": "class-mainwindow/#mainwindowopen_exercise", "mainwindowshow_about": "class-mainwindow/#mainwindowshow_about", "mainwindowopen_anki_exporter": "class-mainwindow/#mainwindowopen_anki_exporter", "mainwindowopen_settings": "class-mainwindow/#mainwindowopen_settings", "mainwindowrebuild": "class-mainwindow/#mainwindowrebuild", "mainwindowopen_glossary": "class-mainwindow/#mainwindowopen_glossary", "mainwindowopen_stats": "class-mainwindow/#mainwindowopen_stats", "mainwindowtoggle_navigation": "class-mainwindow/#mainwindowtoggle_navigation", "mainwindowshow_lessons": "class-mainwindow/#mainwindowshow_lessons", "mainwindowopen_lessons": "class-mainwindow/#mainwindowopen_lessons", "mainwindowopen_database": "class-mainwindow/#mainwindowopen_database", "mainwindowclose_overlay": "class-mainwindow/#mainwindowclose_overlay", "mainwindowswitch_profile": "class-mainwindow/#mainwindowswitch_profile", "mainwindowexport_backup": "class-mainwindow/#mainwindowexport_backup", "mainwindowcheck_for_updates": "class-mainwindow/#mainwindowcheck_for_updates", "mainwindowimport_backup": "class-mainwindow/#mainwindowimport_backup", "mainwindowshow_home": "class-mainwindow/#mainwindowshow_home", "mainwindowopen_plugins": "class-mainwindow/#mainwindowopen_plugins", "mainwindowinstall_plugin": "class-mainwindow/#mainwindowinstall_plugin", "mainwindowuninstall_plugin": "class-mainwindow/#mainwindowuninstall_plugin", "mainwindowrestart_app": "class-mainwindow/#mainwindowrestart_app"}</script>
{% include api-fragments.html %}
