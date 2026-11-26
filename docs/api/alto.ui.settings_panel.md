---
title: alto.ui.settings_panel
parent: api
package: alto.ui
api_components: [{"title": "ArpeggioSettingsPanel", "url": "/api/alto.ui.settings_panel/class-arpeggiosettingspanel/"}, {"title": "CircleSettingsPanel", "url": "/api/alto.ui.settings_panel/class-circlesettingspanel/"}, {"title": "ClefBasicsSettingsPanel", "url": "/api/alto.ui.settings_panel/class-clefbasicssettingspanel/"}, {"title": "IntervalSettingsPanel", "url": "/api/alto.ui.settings_panel/class-intervalsettingspanel/"}, {"title": "KeySignatureSettingsPanel", "url": "/api/alto.ui.settings_panel/class-keysignaturesettingspanel/"}, {"title": "KeyboardIntervalSettingsPanel", "url": "/api/alto.ui.settings_panel/class-keyboardintervalsettingspanel/"}, {"title": "KeyboardSettingsPanel", "url": "/api/alto.ui.settings_panel/class-keyboardsettingspanel/"}, {"title": "NotationSettingsPanel", "url": "/api/alto.ui.settings_panel/class-notationsettingspanel/"}, {"title": "NoteConstructionSettingsPanel", "url": "/api/alto.ui.settings_panel/class-noteconstructionsettingspanel/"}, {"title": "NoteNameSettingsPanel", "url": "/api/alto.ui.settings_panel/class-notenamesettingspanel/"}, {"title": "settings_inversion_names", "url": "/api/alto.ui.settings_panel/function-settings_inversion_names/"}, {"title": "settings_panel_for", "url": "/api/alto.ui.settings_panel/function-settings_panel_for/"}]
permalink: /api/alto.ui.settings_panel/
---
{% raw %}
The settings panels of the built-in exercises, and `settings_panel_for`,
which picks the panel for any exercise.

## Classes

- [`NoteNameSettingsPanel`](class-notenamesettingspanel/) — The settings of the note identification exercise: a menu leading to a page for each group of settings.
- [`KeyboardSettingsPanel`](class-keyboardsettingspanel/) — The settings of the keyboard exercise: a menu with a page for the range of keys.
- [`NoteConstructionSettingsPanel`](class-noteconstructionsettingspanel/) — The settings of the note construction exercise: a menu with a page for the staff and one for the keys.
- [`IntervalSettingsPanel`](class-intervalsettingspanel/) — Choose the notation and answer format for written intervals.
- [`KeyboardIntervalSettingsPanel`](class-keyboardintervalsettingspanel/) — Range and interval selection pages for keyboard interval identification.
- [`ArpeggioSettingsPanel`](class-arpeggiosettingspanel/) — The settings of the arpeggio exercise: a menu with a page for each group of settings.
- [`KeySignatureSettingsPanel`](class-keysignaturesettingspanel/) — The settings of a key signature exercise: a menu with a page for each group of settings.
- [`NotationSettingsPanel`](class-notationsettingspanel/) — Choose the question type and the notation terms to practice.
- [`ClefBasicsSettingsPanel`](class-clefbasicssettingspanel/) — The settings of the clef basics exercise: a menu with two pages, Question Type and Clefs.
- [`CircleSettingsPanel`](class-circlesettingspanel/) — The settings of the circle of fifths exercise: which kinds of question to ask, and the colors of the circle.

## Functions

- [`settings_inversion_names`](function-settings_inversion_names/) — Return the inversions as they are written in the settings.
- [`settings_panel_for`](function-settings_panel_for/) — Return the settings panel for an exercise.

<details markdown="1">
<summary>Module notes and examples</summary>

Each exercise with settings has a panel: a menu of rows (Clefs, Range,
Key signatures ...) that each lead to a page. Edits
are live: they change the shared settings object, are saved, and a
`changed` signal tells the exercise to ask a new
question. The widgets the panels are built from are in
`alto.ui.settings_menu`, plugin exercises' panels are in
`alto.ui.pack_settings_panel`, and loading and saving the settings is in
`alto.ui.exercise_settings`.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = settings_panel_for(ClefBasics())
>>> type(panel).__name__
'ClefBasicsSettingsPanel'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"notenamesettingspanel": "class-notenamesettingspanel/", "keyboardsettingspanel": "class-keyboardsettingspanel/", "noteconstructionsettingspanel": "class-noteconstructionsettingspanel/", "intervalsettingspanel": "class-intervalsettingspanel/", "keyboardintervalsettingspanel": "class-keyboardintervalsettingspanel/", "arpeggiosettingspanel": "class-arpeggiosettingspanel/", "keysignaturesettingspanel": "class-keysignaturesettingspanel/", "notationsettingspanel": "class-notationsettingspanel/", "clefbasicssettingspanel": "class-clefbasicssettingspanel/", "settings_inversion_names": "function-settings_inversion_names/", "circlesettingspanel": "class-circlesettingspanel/", "settings_panel_for": "function-settings_panel_for/"}</script>
{% include api-fragments.html %}
