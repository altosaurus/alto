---
title: alto.ui
parent: api
package: alto.ui
api_package: true
permalink: /api/alto.ui/
---

The windows, widgets and drawing code. Everything that needs Qt is in here.

## Modules

| Module | What it is |
|---|---|
| [alto.ui.anki_exporter](../alto.ui.anki_exporter/) | Modeless Anki deck exporter using Alto's exercise controls and music engraving. |
| [alto.ui.answer_bank](../alto.ui.answer_bank/) | A responsive, scrollable grid for large banks of answer buttons. |
| [alto.ui.app_settings](../alto.ui.app_settings/) | The application-wide settings dialog. |
| [alto.ui.background](../alto.ui.background/) | Run slow work, such as a download, on another thread, and hear how it went on the window's thread. |
| [alto.ui.backup_flow](../alto.ui.backup_flow/) | Exporting a backup and importing one: the file dialogs, the questions asked, and the safety copy made before anything is replaced. |
| [alto.ui.charts](../alto.ui.charts/) | Small charts drawn with QPainter, in the application's theme colors. |
| [alto.ui.circle](../alto.ui.circle/) | The circle of fifths: twelve wedges, the major keys on the outside and their relative minors on the inside. |
| [alto.ui.circle_colors](../alto.ui.circle_colors/) | The pages of the circle of fifths settings that choose its colors: a grid of schemes to pick from, and an editor to make one. |
| [alto.ui.colors](../alto.ui.colors/) | Mixing colors. The interface blends palette colors to get its soft tints and highlights. |
| [alto.ui.database_page](../alto.ui.database_page/) | A read-only look at what is stored: every answer, every question's record, and the profiles. |
| [alto.ui.degree_text](../alto.ui.degree_text/) | Draw scale-degree carets above their digits without relying on font-specific combining accents. |
| [alto.ui.dropdown](../alto.ui.dropdown/) | Shared dropdown fields with rounded popup windows. |
| [alto.ui.engraving](../alto.ui.engraving/) | Drawing notation with SMuFL music fonts (Bravura, Leland, Petaluma, MuseJazz and others). |
| [alto.ui.exercise_settings](../alto.ui.exercise_settings/) | Load and save each exercise's settings. |
| [alto.ui.exercise_view](../alto.ui.exercise_view/) | The exercise screen: a question, its answer buttons, the score, and a pane of settings that slides in from the right. |
| [alto.ui.fingerboard](../alto.ui.fingerboard/) | Render a pack's instrument portrait using its calibrated string endpoints. |
| [alto.ui.glossary](../alto.ui.glossary/) | A searchable glossary of the notation terms used in Alto. |
| [alto.ui.home](../alto.ui.home/) | The start screen: a card for every exercise, or for every lesson, in rows. |
| [alto.ui.icons](../alto.ui.icons/) | Small monochrome icons drawn from SVG, tinted with the current theme's text color. |
| [alto.ui.instrument_picker](../alto.ui.instrument_picker/) | Choosing the instrument that plays notes, with a summary of what each one is made from. |
| [alto.ui.interval_range](../alto.ui.interval_range/) | A two-handle slider for selecting interval distances without changing the keyboard range. |
| [alto.ui.key_fork](../alto.ui.key_fork/) | The fork: a picker for a key signature, shaped like a tuning fork lying on its side. |
| [alto.ui.keyboard](../alto.ui.keyboard/) | The on-screen piano keyboard, drawn to real proportions, and a miniature of the whole piano for choosing a span of keys. |
| [alto.ui.keyboard_styles](../alto.ui.keyboard_styles/) | Keyboard styles: the colors and materials the on-screen piano keys are drawn in. |
| [alto.ui.lesson](../alto.ui.lesson/) | The lesson pages: a page that walks through one lesson step by step. |
| [alto.ui.lesson_nav](../alto.ui.lesson_nav/) | The list on the left in lesson mode: the lessons, and the steps of the one that is open. |
| [alto.ui.main_window](../alto.ui.main_window/) | The main window: tile browsing or a workspace with an independently selected exercise or lesson list. |
| [alto.ui.meter_staff](../alto.ui.meter_staff/) | Staffless rhythm notation for lesson and glossary examples. |
| [alto.ui.metronome_spectrum](../alto.ui.metronome_spectrum/) | A bouncing spectrum display for the metronome preview. |
| [alto.ui.midi_input](../alto.ui.midi_input/) | ALSA keyboard input for answering a question with a played pitch. |
| [alto.ui.motion](../alto.ui.motion/) | Animations and feedback delays, run in one place so that tests decide when they happen. |
| [alto.ui.notation](../alto.ui.notation/) | Notation styles: which music font the staff, clefs, notes and accidentals are engraved in. |
| [alto.ui.notes](../alto.ui.notes/) | Engraved notes built from the Noto Music font's glyphs, the way notation software draws them. |
| [alto.ui.pack_settings_panel](../alto.ui.pack_settings_panel/) | The settings panels of exercises that plugins add. |
| [alto.ui.package_update](../alto.ui.package_update/) | The window that updates a packaged copy of Alto: the download and its checks with their progress, then what happens next. |
| [alto.ui.pictures](../alto.ui.pictures/) | Small pictures of musical things (clefs, note values, key signatures, note ranges ...) for the settings panes. |
| [alto.ui.plugins_dialog](../alto.ui.plugins_dialog/) | The Plugins dialog: the installed plugins on the left, and the buttons that add or remove one on the right. |
| [alto.ui.practice_limits](../alto.ui.practice_limits/) | Daily card allowances in profile and exercise settings. |
| [alto.ui.profile_dialog](../alto.ui.profile_dialog/) | Choosing who is practicing. There is no password: a profile is just a name that keeps its own history. |
| [alto.ui.question_preview](../alto.ui.question_preview/) | A popup showing a stored question the way the exercise showed it, with its answer. |
| [alto.ui.reference](../alto.ui.reference/) | The reference pane: an interactive circle of fifths to look things up on, with an explanation under it. |
| [alto.ui.response_times](../alto.ui.response_times/) | Profile speed-grading settings and the rolling distribution for each exercise. |
| [alto.ui.scale_explorer](../alto.ui.scale_explorer/) | Interactive notation and step patterns for learning scales. |
| [alto.ui.score_excerpt](../alto.ui.score_excerpt/) | Paint the engraved score and locate symbols from a pixel map made from the same SVG. |
| [alto.ui.settings_menu](../alto.ui.settings_menu/) | The building blocks of the settings panels that slide in beside an exercise. |
| [alto.ui.settings_panel](../alto.ui.settings_panel/) | The settings panels of the built-in exercises, and `settings_panel_for`, which picks the panel for any exercise. |
| [alto.ui.staff](../alto.ui.staff/) | The staff: lines, clefs, key signatures and notes, drawn on a rounded white "paper". |
| [alto.ui.staff_input](../alto.ui.staff_input/) | The staffs you click to place notes or a clef. |
| [alto.ui.staff_playback](../alto.ui.staff_playback/) | Connect a displayed music sample to the notes sounding on its staff. |
| [alto.ui.stats_dialog](../alto.ui.stats_dialog/) | The statistics screen: a few numbers and charts about how practice is going. |
| [alto.ui.store](../alto.ui.store/) | The application's saved settings (a thin layer over `QSettings`). |
| [alto.ui.style](../alto.ui.style/) | Application-wide stylesheet: rounded corners on buttons, panes, lists and scroll bars. |
| [alto.ui.theme](../alto.ui.theme/) | The color theme: follow the system, force light or dark, or use a theme with colors of its own. |
| [alto.ui.theme_cards](../alto.ui.theme_cards/) | The card of a theme in the settings. |
| [alto.ui.theme_editor](../alto.ui.theme_editor/) | The editor for a theme of the user's own: a name, and a color for every part of its light and dark versions. |
| [alto.ui.transition_preview](../alto.ui.transition_preview/) | A preview of a transition for the settings. |
| [alto.ui.transitions](../alto.ui.transitions/) | The transitions between the exercises and the lessons on the home page. |
| [alto.ui.update_flow](../alto.ui.update_flow/) | Checking for a newer Alto and installing it: the questions asked, the progress shown, and the restart afterwards. |
| [alto.ui.warmup](../alto.ui.warmup/) | Get ready, while Alto sits idle just after it opens, what a first visit to a page would otherwise pay for. |
| [alto.ui.widgets](../alto.ui.widgets/) | Small widgets shared by several screens: the sidebar toggle, the help button and a segmented control. |
| [alto.ui.zoom](../alto.ui.zoom/) | Zoom: make everything in Alto larger or smaller together. |
