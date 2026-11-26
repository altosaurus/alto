---
title: alto.ui.app_settings
parent: api
package: alto.ui
api_components: [{"title": "AppSettingsDialog", "url": "/api/alto.ui.app_settings/class-appsettingsdialog/"}, {"title": "KeyboardBuilder", "url": "/api/alto.ui.app_settings/class-keyboardbuilder/"}, {"title": "KeyboardCard", "url": "/api/alto.ui.app_settings/class-keyboardcard/"}, {"title": "PreviewCard", "url": "/api/alto.ui.app_settings/class-previewcard/"}, {"title": "StyleCard", "url": "/api/alto.ui.app_settings/class-stylecard/"}, {"title": "load_metronome_click", "url": "/api/alto.ui.app_settings/function-load_metronome_click/"}]
permalink: /api/alto.ui.app_settings/
---
{% raw %}
The application-wide settings dialog.

## Classes

- [`PreviewCard`](class-previewcard/) — A selectable tile that previews a style: a picture drawn in it, with its name and a few words about it underneath.
- [`StyleCard`](class-stylecard/) — A selectable tile that previews a notation style: a short phrase on a staff, drawn in that style.
- [`KeyboardCard`](class-keyboardcard/) — A selectable tile that previews a keyboard style: a short stretch of keys drawn in that style.
- [`KeyboardBuilder`](class-keyboardbuilder/) — Rows for coloring each part of a keyboard.
- [`AppSettingsDialog`](class-appsettingsdialog/) — Application-wide settings. Changes apply immediately, and the main window can be used while the dialog is open.

## Functions

- [`load_metronome_click`](function-load_metronome_click/) — Apply the saved click or use High pip as the default.

<details markdown="1">
<summary>Module notes and examples</summary>

It holds the color theme, the notation font, the keyboard style, the
transitions, instruments, metronome clicks and what updates follow.

Changes apply as soon as they are made. Each style is a card that
previews it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> dialog = AppSettingsDialog()
>>> dialog.windowTitle()
'Settings'
>>> dialog.pages.count()  # Appearance, Sound and Updates
3
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"load_metronome_click": "function-load_metronome_click/", "previewcard": "class-previewcard/", "stylecard": "class-stylecard/", "keyboardcard": "class-keyboardcard/", "keyboardcardshow_style": "class-keyboardcard/#keyboardcardshow_style", "keyboardbuilder": "class-keyboardbuilder/", "keyboardbuilderrefresh": "class-keyboardbuilder/#keyboardbuilderrefresh", "appsettingsdialog": "class-appsettingsdialog/", "appsettingsdialogcard": "class-appsettingsdialog/#appsettingsdialogcard", "appsettingsdialogcard_page": "class-appsettingsdialog/#appsettingsdialogcard_page", "appsettingsdialogthumb": "class-appsettingsdialog/#appsettingsdialogthumb", "appsettingsdialogchoose_theme": "class-appsettingsdialog/#appsettingsdialogchoose_theme"}</script>
{% include api-fragments.html %}
