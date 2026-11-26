---
title: alto.ui.pack_settings_panel
parent: api
package: alto.ui
api_components: [{"title": "PackKeyboardSettingsPanel", "url": "/api/alto.ui.pack_settings_panel/class-packkeyboardsettingspanel/"}, {"title": "PackSettingsPanel", "url": "/api/alto.ui.pack_settings_panel/class-packsettingspanel/"}]
permalink: /api/alto.ui.pack_settings_panel/
---
{% raw %}
The settings panels of exercises that plugins add.

## Classes

- [`PackSettingsPanel`](class-packsettingspanel/) — The settings a plugin declared for one of its note exercises, drawn from a fixed set of controls.
- [`PackKeyboardSettingsPanel`](class-packkeyboardsettingspanel/) — The settings a plugin declared for a keyboard interval exercise: its sound, the range of keys, and the intervals.

<details markdown="1">
<summary>Module notes and examples</summary>

A plugin exercise declares the controls it wants (a range, a sound,
accidentals ...) and gets a panel built from them, like
the built-in exercises' panels. Its options are saved under the
exercise's name.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> COMMIT_DELAY_MS
150
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"packsettingspanel": "class-packsettingspanel/", "packkeyboardsettingspanel": "class-packkeyboardsettingspanel/", "packkeyboardsettingspanelflush": "class-packkeyboardsettingspanel/#packkeyboardsettingspanelflush", "packkeyboardsettingspanelhideevent": "class-packkeyboardsettingspanel/#packkeyboardsettingspanelhideevent"}</script>
{% include api-fragments.html %}
