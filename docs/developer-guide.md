---
title: Developer guide
nav_order: 9.5
nav_group: For developers
children: developer-guide
permalink: /developer-guide/
---
## Application launch

For a code walkthrough, start with [Application launch]({{ '/developer-guide/application-launch/' | relative_url }}). It follows `alto/__main__.py` from the terminal command to the first click on an exercise tile.

Run `python -m alto` from the repository with the project environment active. The installed `alto` command and the packaged desktop launcher also call `main()` in `alto/__main__.py`.

On a normal launch, `main()` creates the Qt `QApplication`, applies the saved theme, and opens Alto’s SQLite database. The next window depends on the profiles in that database. Select a numbered region in any screenshot, or use the links beneath it, to open the API reference for the class that owns or draws that component.

### First launch

An empty database opens the welcome dialog. **Create profile** passes the name to `Database.add_profile()`. A valid name closes the dialog with the new profile selected. Closing this dialog without creating a profile exits Alto before it opens the main window. [Database API]({{ '/api/alto.learning.database/#database' | relative_url }})

{% include component-shot.html screen="profile-create" width=380 height=234 alt="Welcome to Alto with a name field and a Create profile button." %}

### Returning profiles

`startup_profile()` first looks for the last-used profile. If it finds one, Alto opens it directly. If there is no remembered match, Alto uses the only profile in the database or, when there are several, opens the chooser shown below. Both the welcome screen and the chooser come from `ProfileDialog`. [Profile selection code]({{ '/api/alto.ui.profile_dialog/#startup_profile' | relative_url }})

{% include component-shot.html screen="profile-picker" width=380 height=407 alt="The profile chooser lists Ada and Sam and offers a field for a new profile." %}

### The main window

Once a profile is selected, `main()` constructs a `Learner` for it, passes the learner to `MainWindow`, calls `window.show()`, and enters Qt’s event loop with `app.exec()`. From here a click on a tile or toolbar button determines what code runs next. [Learner API]({{ '/api/alto.learning.learner/#learner' | relative_url }})

On the first launch, the main window opens to the exercise tiles. The toolbar and search field belong to `MainWindow`. The catalog beneath them is a `HomePage`, which lays out the tiles and emits `exercise_chosen` when a learner picks one. Alto remembers whether the catalog last showed exercises or lessons.

{% include component-shot.html screen="home" width=1100 height=720 alt="Alto’s main window with the navigation toolbar, search field, and exercise tiles." %}

## Screens reached from the main window

### Exercise workspace

Choosing **Note Identification** calls `MainWindow.open_exercise()`. It opens an `ExerciseView` for the exercise and connects it to the active learner. The staff is a separate widget. When tracing a misplaced note, start with `StaffWidget`. For a click on an answer button, start with `ExerciseView`.

{% include component-shot.html screen="note-identification" width=1100 height=720 alt="Note Identification with the exercise list on the left, a treble staff, and letter answers." %}

### Lesson catalog and reader

The graduation-cap button switches the catalog to lessons. `HomePage` uses a `TileCard` for each lesson and emits the lesson’s key when the learner selects it.

{% include component-shot.html screen="lesson-tiles" width=1100 height=768 alt="The lesson catalog with Pitches and Notes, Clef Basics, Intervals, and other lesson tiles." %}

Opening **Pitches and Notes** puts the lesson outline on the left. On the right, `LessonsPage` supplies **Leave lesson** and **Start over**. Inside it, `LessonView` tracks the current step and `StepView` displays that step’s text, example, and question.

{% include component-shot.html screen="lesson-workspace" width=1100 height=768 alt="Pitches and Notes open to its first step, with the outline, sound example, and knowledge check." %}

### Glossary

The glossary button opens a searchable term list. Selecting **harmonic minor scale** updates the definition, the example on the staff, and the links to related practice. The example uses the same staff class as Note Identification.

{% include component-shot.html screen="glossary" width=1100 height=720 alt="The harmonic minor scale glossary entry with a term list, a staff example, and related exercise tiles." %}

### Statistics

The chart button opens `StatsPage` for the active learner. Changing the exercise or date filter updates both the totals and the graphs. Each chart paints its own data. For example, the stacked bars group questions by the period selected under **Granularity**, while the line beside them shows daily accuracy.

{% include component-shot.html screen="stats" width=1100 height=720 alt="Statistics with filters, six summary tiles, and charts for question volume, accuracy, and speed." %}

### Database and answer details

The database button opens the history browser. `DatabasePage` handles the table choice and search field. To trace where a displayed cell gets its value, follow `RowsModel`, the model behind the table.

The [Database chapter]({{ '/developer-guide/database/' | relative_url }}) diagrams the relationships between profiles, submitted answers, and question summaries, and documents every stored column.

{% include component-shot.html screen="database" width=1100 height=720 alt="The database browser with Answers selected, a search field, and rows of recorded attempts." %}

Double-clicking an answer opens a separate `QuestionPreview` dialog. It recreates the question from the saved record. This chord example has a `StaffWidget` above the answer and timing details.

{% include component-shot.html screen="question-preview" width=560 height=518 alt="A saved Chord Quality question with its staff, correct answer, and recorded response time." %}

### Application settings

**Menu → Settings** opens `AppSettingsDialog`. Under **Appearance → Notation style**, each font sample is a `StyleCard`. The dialog manages the selection, and each card contains its own staff preview.

{% include component-shot.html screen="settings" width=1000 height=640 alt="Application settings showing the category list and the notation font cards." %}
