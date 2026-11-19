---
title: API reference
nav_order: 11
nav_group: For developers
children: api
permalink: /api/
---

Every public module, class and function in Alto, with its signature and docstring. Names that begin with an underscore are internal and are left out. The pages are written from the docstrings by `scripts/api_docs.py`, so they match the code.


## alto

Alto: a music theory trainer that learns what you find hard and asks it more often.

| Module | What it is |
|---|---|
| [alto.audio](alto.audio/) | Note playback: recorded instrument samples (University of Iowa), with pitch-shifting for missing notes. |
| [alto.circle_schemes](alto.circle_schemes/) | The color schemes of the circle of fifths: the presets, and the schemes a user makes. |
| [alto.instrument_info](alto.instrument_info/) | What is known about each instrument's recordings, for the summary shown in the instrument settings. |
| [alto.location](alto.location/) | Where Alto keeps its practice history and its settings, and how to keep them somewhere else with `ALTO_HOME`. |
| [alto.notation_excerpts](alto.notation_excerpts/) | Public-domain piano excerpts available for offline notation practice. |
| [alto.notation_terms](alto.notation_terms/) | Notation Identification terms, grouped by subject with their score placement and SMuFL code points. |
| [alto.selfupdate](alto.selfupdate/) | Replacing a packaged copy of Alto with a newer release: whether it can, getting the update, checking it, and handing over. |
| [alto.settings](alto.settings/) | User settings. Pure Python (no Qt); persistence lives in ui/settings_panel.py. |
| [alto.updates](alto.updates/) | What kind of copy of Alto is running, how it can be updated, and the commands and answers that checking involves. |

## alto.exercises

The exercises and the framework they are built on.

| Module | What it is |
|---|---|
| [alto.exercises.base](alto.exercises.base/) | Exercise framework. Register a ChoiceExercise for button answers or an Exercise for construction tasks. |
| [alto.exercises.library](alto.exercises.library/) | The exercises: note names, intervals, key signatures, scales, chords, arpeggios, keyboard keys and note construction. |

## alto.learning

Spaced repetition: who is learning (profiles), what they answered (a database) and what to ask next.

| Module | What it is |
|---|---|
| [alto.learning.backup](alto.learning.backup/) | Backup files: everything Alto keeps, in one file that can be read back into a clean install. Pure Python (no Qt). |
| [alto.learning.calendar](alto.learning.calendar/) | Daily exercise queues for SM-2 and FSRS. |
| [alto.learning.database](alto.learning.database/) | The SQLite store: profiles, every answer given, and what is known about each question. Pure Python (no Qt). |
| [alto.learning.learner](alto.learning.learner/) | Ties the profile, the database and the scheduler together for the exercise screen. |
| [alto.learning.scheduler](alto.learning.scheduler/) | How a question's history turns into how soon it comes back. Pure Python, no database and no Qt. |
| [alto.learning.stats](alto.learning.stats/) | Numbers and series for the statistics screen, worked out from the answers in the database. Pure Python, no Qt. |

## alto.lessons

The lessons: guided walks through a topic, with small exercises along the way.

| Module | What it is |
|---|---|
| [alto.lessons.base](alto.lessons.base/) | What a lesson is made of: steps, and the small tasks inside them. |
| [alto.lessons.circle_of_fifths](alto.lessons.circle_of_fifths/) | The lesson on the circle of fifths, taught from nothing. |
| [alto.lessons.clef_basics](alto.lessons.clef_basics/) | The lesson on clefs, taught from nothing. |
| [alto.lessons.intervals](alto.lessons.intervals/) | A guided introduction to naming intervals on the staff and keyboard. |
| [alto.lessons.key_signatures](alto.lessons.key_signatures/) | A guided lesson on reading and writing key signatures. |
| [alto.lessons.pitches_and_notes](alto.lessons.pitches_and_notes/) | A first lesson connecting a sound, a piano key, and a written note. |
| [alto.lessons.scale_identification](alto.lessons.scale_identification/) | Reading scales and recognizing their interval patterns. |

## alto.theory

Music theory, with no user interface.

| Module | What it is |
|---|---|
| [alto.theory.fifths](alto.theory.fifths/) | The circle of fifths: the twelve keys in order, each major with its relative minor. |
| [alto.theory.key_signatures](alto.theory.key_signatures/) | Staff positions for written key signatures. |
| [alto.theory.pitch](alto.theory.pitch/) | Pitches and intervals, spelled correctly (C# is not Db). |
| [alto.theory.scales](alto.theory.scales/) | Scales, modes, key signatures and chords, built from spelled intervals. |

## alto.ui

The windows, widgets and drawing code. Everything that needs Qt is in here.

| Module | What it is |
|---|---|
| [alto.ui.answer_bank](alto.ui.answer_bank/) | A responsive, scrollable grid for large banks of answer buttons. |
| [alto.ui.app_settings](alto.ui.app_settings/) | The application-wide settings dialog. |
| [alto.ui.backup_flow](alto.ui.backup_flow/) | Exporting a backup and importing one: the file dialogs, the questions asked, and the safety copy made before anything is replaced. |
| [alto.ui.charts](alto.ui.charts/) | Small charts drawn with QPainter, in the application's theme colors. |
| [alto.ui.circle](alto.ui.circle/) | The circle of fifths: twelve wedges, the major keys on the outside and their relative minors on the inside. |
| [alto.ui.circle_colors](alto.ui.circle_colors/) | The pages of the circle of fifths settings that choose its colors: a grid of schemes to pick from, and an editor to make one. |
| [alto.ui.colors](alto.ui.colors/) | Mixing colors. The interface blends palette colors to get its soft tints and highlights. |
| [alto.ui.database_page](alto.ui.database_page/) | A read-only look at what is stored: every answer, every question's record, and the profiles. |
| [alto.ui.degree_text](alto.ui.degree_text/) | Draw scale-degree carets above their digits without relying on font-specific combining accents. |
| [alto.ui.dropdown](alto.ui.dropdown/) | Shared dropdown fields with rounded popup windows. |
| [alto.ui.engraving](alto.ui.engraving/) | Drawing notation with SMuFL music fonts (Bravura, Leland, Petaluma, MuseJazz and others). |
| [alto.ui.exercise_view](alto.ui.exercise_view/) | The exercise screen: a question, its answer buttons, the score, and a pane of settings that slides in from the right. |
| [alto.ui.glossary](alto.ui.glossary/) | A searchable glossary of the notation terms used in Alto. |
| [alto.ui.home](alto.ui.home/) | The start screen: a card for every exercise, or for every lesson, in rows. |
| [alto.ui.icons](alto.ui.icons/) | Small monochrome icons drawn from SVG, tinted with the current theme's text color. |
| [alto.ui.instrument_picker](alto.ui.instrument_picker/) | Choosing the instrument that plays notes, with a summary of what each one is made from. |
| [alto.ui.interval_range](alto.ui.interval_range/) | A two-handle slider for selecting interval distances without changing the keyboard range. |
| [alto.ui.key_fork](alto.ui.key_fork/) | The fork: a picker for a key signature, shaped like a tuning fork lying on its side. |
| [alto.ui.keyboard](alto.ui.keyboard/) | The on-screen piano keyboard, drawn to real proportions, and a miniature of the whole piano for choosing a span of keys. |
| [alto.ui.keyboard_styles](alto.ui.keyboard_styles/) | Keyboard styles: the colors and materials the on-screen piano keys are drawn in. |
| [alto.ui.lesson](alto.ui.lesson/) | The lesson pages: a page that walks through one lesson step by step. |
| [alto.ui.lesson_nav](alto.ui.lesson_nav/) | The list on the left in lesson mode: the lessons, and the steps of the one that is open. |
| [alto.ui.main_window](alto.ui.main_window/) | The main window: tile browsing or a workspace with an independently selected exercise or lesson list. |
| [alto.ui.notation](alto.ui.notation/) | Notation styles: which music font the staff, clefs, notes and accidentals are engraved in. |
| [alto.ui.notes](alto.ui.notes/) | Engraved notes built from the Noto Music font's glyphs, the way notation software draws them. |
| [alto.ui.package_update](alto.ui.package_update/) | The window that updates a packaged copy of Alto: the download and its checks with their progress, then what happens next. |
| [alto.ui.pictures](alto.ui.pictures/) | Small pictures of musical things (clefs, note values, key signatures, note ranges ...) for the settings panes. |
| [alto.ui.practice_limits](alto.ui.practice_limits/) | Daily card allowances in profile and exercise settings. |
| [alto.ui.profile_dialog](alto.ui.profile_dialog/) | Choosing who is practicing. There is no password: a profile is just a name that keeps its own history. |
| [alto.ui.question_preview](alto.ui.question_preview/) | A popup showing a stored question the way the exercise showed it, with its answer. |
| [alto.ui.reference](alto.ui.reference/) | The reference pane: an interactive circle of fifths to look things up on, with an explanation under it. |
| [alto.ui.scale_explorer](alto.ui.scale_explorer/) | Interactive notation and step patterns for learning scales. |
| [alto.ui.score_excerpt](alto.ui.score_excerpt/) | Paint the engraved score and locate symbols from a pixel map made from the same SVG. |
| [alto.ui.settings_panel](alto.ui.settings_panel/) | The settings panels that slide in beside an exercise, and the small widgets they are built from. |
| [alto.ui.staff](alto.ui.staff/) | The staff: lines, clefs, key signatures and notes, drawn on a rounded white "paper". |
| [alto.ui.staff_input](alto.ui.staff_input/) | The staffs you click to place notes or a clef. |
| [alto.ui.staff_playback](alto.ui.staff_playback/) | Connect a displayed music sample to the notes sounding on its staff. |
| [alto.ui.stats_dialog](alto.ui.stats_dialog/) | The statistics screen: a few numbers and charts about how practice is going. |
| [alto.ui.store](alto.ui.store/) | The application's saved settings (a thin layer over `QSettings`). |
| [alto.ui.style](alto.ui.style/) | Application-wide stylesheet: rounded corners on buttons, panes, lists and scroll bars. |
| [alto.ui.theme](alto.ui.theme/) | The color theme: follow the system, force light or dark, or use a theme with colors of its own. |
| [alto.ui.theme_cards](alto.ui.theme_cards/) | The card of a theme in the settings. |
| [alto.ui.theme_editor](alto.ui.theme_editor/) | The editor for a theme of the user's own: a name, and a color for every part of its light and dark versions. |
| [alto.ui.transition_preview](alto.ui.transition_preview/) | A preview of a transition for the settings. |
| [alto.ui.transitions](alto.ui.transitions/) | The transitions between the exercises and the lessons on the home page. |
| [alto.ui.update_flow](alto.ui.update_flow/) | Checking for a newer Alto and installing it: the questions asked, the progress shown, and the restart afterwards. |
| [alto.ui.widgets](alto.ui.widgets/) | Small widgets shared by several screens: the sidebar toggle, the help button and a segmented control. |
