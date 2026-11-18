---
title: For developers
nav_order: 9
nav_group: For developers
permalink: /development/
---
Alto is a Python application using PySide6. The source is at [github.com/altosaurus/alto](https://github.com/altosaurus/alto).

This page is the quick reference: commands, tooling and the short recipes. The [developer guide]({{ '/guide/' | relative_url }}) explains how
the program works and the ideas underneath it (audio, notation, spaced repetition, styling, animation), with reading lists.

## Layout

| Folder | What is in it |
|---|---|
| `alto/theory/` | The music theory engine: spelled notes, intervals, scales and chords. Pure Python, no Qt. |
| `alto/exercises/` | The exercises and the `Question` and `Exercise` base classes. No Qt. |
| `alto/learning/` | Profiles, the SQLite database, the scheduler and the statistics calculations. No Qt. |
| `alto/ui/` | The Qt widgets: main window, staff drawing, exercise screen, charts, settings and the database page. |
| `alto/assets/` | Bundled music fonts and instrument recordings. |
| `tests/` | The test suite. |

Keeping the theory, exercises and learning code free of Qt means they can be tested without a display.

## Running the tests

```bash
pip install -e ".[dev]"
pytest
```

The tests that touch widgets run with Qt's offscreen platform, so no display is needed.

The tests never read or change your own settings, profile or history. `tests/conftest.py` points them at a throwaway
folder, closes every window and database a test leaves open, and turns the sound off. Coverage measures executable statements under `alto/`. The pre-push hook and the GitHub Coverage job require tests
to execute every added or modified statement in that package. The Codecov project percentage tracks historical gaps.

GitHub Actions runs the tests on every pull request (`.github/workflows/tests.yml`) and reports coverage to Codecov
(`.github/workflows/codecov.yml`). To measure coverage yourself:

```bash
sh scripts/run-tests.sh --patch-coverage
```

### Which checks run for which change

The pre-push hook runs the full pytest suite once and checks the resulting coverage against the branch diff from
`origin/main`. Fetch the target branch first and set `ALTO_COVERAGE_BASE` when targeting another branch.
GitHub uses the pull request’s base commit, or the previous commit on a push to main. The GitHub workflows select their checks by change type:

- **Only docs** (`docs/**` and the Markdown files at the top): the tests that read the docs. A pull request also builds the docs
  with Jekyll (the Docs check workflow), and runs no Pyright, Ruff or coverage.
- **A change to `alto/` or to a test:** the full test suite, including doctests and documentation checks.
- **Anything else** (a script, a workflow, `pyproject.toml`, a `conftest.py`, the packaging files, a picture): everything.

In the workflows, a pull request runs the tests on the oldest and the newest Python version (a change to the docs alone, on one),
and a push to `main` runs every supported version. A new push to a pull request cancels the runs still going for the old one.
The Coverage job also reports a successful check for documentation-only pull requests, so it can be required on
`main` without leaving those pull requests waiting for a status.

## Keeping Alto fast

Three things watch how fast Alto is, each for a different kind of slowdown. The operations they time are in
`benchmarks/operations.py`: opening every page (and going between a lesson and an exercise), asking and answering a question,
painting each screen, drawing the circle of fifths at new sizes, and reading and writing the data of a profile with a year of practice
behind it.

- **Budgets, on every pull request.** `tests/test_performance.py` fails when an operation takes longer than its budget in
  `benchmarks/budgets.py`. A budget is four or five times what the operation takes on a development machine, so that a slow build
  machine does not fail a test but a change that makes something many times slower does. The first use of something in a new process
  (starting the app, the first look at a page, the circle at sizes not used before) is measured in a process of its own, because Qt
  makes fonts and layouts on first use and later runs hide that cost.
- **A history, from release to release.** `benchmarks/suite.py` is an [ASV](https://asv.readthedocs.io/) suite, and the Performance
  workflow (`.github/workflows/performance.yml`) runs it when a version is tagged and once a week, and keeps the results on the
  branch `asv-results`. A change of more than 30% against the previous release is written in the run's summary. That is advice and not a
  failure, because a shared build machine is too noisy for a strict gate; it is there to show a slow creep that no single budget
  would catch.
- **By hand, before a release.** The run takes a minute or two, and the feel of animations on a real screen is not something a test
  can judge, so look at the lesson, the circle of fifths and the statistics page on a real display as well.

```bash
python -m benchmarks.survey        # every operation once, slowest first, in milliseconds
python -m benchmarks.operations page:lesson --profile   # where the time goes in one operation, the first time
pytest tests/test_performance.py   # the budgets
asv run -E existing:$(which python) --set-commit-hash $(git rev-parse HEAD)   # record this commit
asv compare v0.0.0 HEAD            # what changed since a release, once both have been recorded
```

When an operation is made faster or slower on purpose, change its budget in the same commit. A new page or exercise needs a line in
`benchmarks/budgets.py` (a prefix such as `page:` covers it) and, if it is a new kind of operation, an entry in
`benchmarks/operations.py`; the tests fail until it has a budget, so nothing goes unwatched. The first release to be measured is the
one that has `benchmarks/`; to measure an earlier one, run the Performance workflow by hand with `ref` set to its tag.

## Type checking

[Pyright](https://github.com/microsoft/pyright) checks the types of `alto`, `tests` and `scripts`, in basic mode, as if
for Python 3.11:

```bash
sh scripts/typecheck.sh
```

It must report no errors. It runs on every pull request (`.github/workflows/pyright.yml`) and before each push. Two things
to know when writing Qt code:

- **Write Qt enums in their full form**, such as `Qt.AlignmentFlag.AlignLeft`, not the short `Qt.AlignLeft`. The short form
  works when the program runs, but Pyright cannot see it.
- Qt functions that may return nothing (`layout()`, `widget()`, `QApplication.instance()`) have to be checked for `None`
  before use, with an `if` or an `assert`.

If Pyright is wrong about one line, silence just that line with `# pyright: ignore[ruleName]` and a short reason.

## Running your copy apart from the installed one

Alto's history and settings are kept by name, so a clone run with `python -m alto` shares them with an installed Alto. To
keep them apart, run the clone with `sh scripts/dev.sh`. It sets `ALTO_HOME` to `~/.alto-dev` (or to a folder you choose),
where the clone has its own database and settings. The first run also adds "Alto (dev)" to the application menu, with the
clone's icon, so the dock shows the development copy on its own and not grouped with the installed one. See [Your data]({{ '/data/' | relative_url }}).

## Pre-commit

A [pre-commit](https://pre-commit.com/) configuration runs the checks automatically before each commit. Set it up once:

```bash
pip install -e ".[dev]"
pre-commit install
```

It then trims trailing whitespace, makes sure files end with a newline, checks YAML and TOML files, refuses very large
files (the bundled recordings and fonts are exempt) and runs Ruff, applying its safe fixes. If a hook changes a file,
the commit stops so you can review the change, then commit again.

The test suite and Pyright run when you **push**, not on every commit, so commits stay quick. A failing test or a type
error stops the push. Run the commit checks by hand with `pre-commit run --all-files`, the push checks with
`pre-commit run --all-files --hook-stage pre-push`, and update the pinned hook versions with `pre-commit autoupdate`.

## Linting

Alto uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting. It is installed with the `dev` extra and
configured in `pyproject.toml` (pycodestyle, pyflakes, import sorting, pyupgrade, bugbear and a few more rules, with a
130-character line limit).

```bash
ruff format alto tests scripts        # format the code
ruff check --fix alto tests scripts   # report problems and apply the safe fixes
```

Run them in that order. Anything that does not fit on a line, whether a list, a dictionary, a call or a signature, is put
one element per line with a trailing comma, and a trailing comma you write yourself keeps a short one exploded. The
`ruff-format` pre-commit hook does this on every commit. Ruff warns that the trailing-comma rule can conflict with the
formatter. Run in this order, it does not: the formatter leaves out a comma after a lone long argument, the check adds it,
and the formatter keeps it.

Imports follow these rules:

- **Absolute only.** `from alto.ui.store import store`, never `from .store import store` (`TID252`).
- **At the top of the file.** None inside a function (`PLC0415`), except in the `>>>` examples of a docstring, which have to
  import what they use. Two modules that need each other do not import each other: `notation.py` and `keyboard_styles.py`
  call hooks that `staff.py` and `keyboard.py` register with `on_redraw`. The `conftest.py` files set the settings folders
  before importing anything from Alto, so their imports are marked `# noqa: E402`.
- **One name per line** when a `from` import has two or more names, in parentheses with a trailing comma. Ruff cannot
  enforce this, but it keeps an import you have already written that way.
- **Sorted like isort** (`I`): the standard library, then third-party packages (PySide6, numpy, pytest), then `alto` as
  its own section (`known-first-party`), each section sorted alphabetically.

## PyCharm

The code is kept free of PyCharm warnings as well as Ruff and Pyright errors. PyCharm's settings live in `.idea/`, which
is not in the repository, so a fresh clone needs the three changes below. Without them PyCharm shows many warnings that
are not real problems.

**1. Use a project inspection profile that ignores the `alto` imports.** PyCharm analyses the `>>>` examples in
docstrings, which is useful, but it resolves `alto.exercises` and the like only when the file itself imports them, so
every example that imports from another package gets a false "Cannot find reference" warning.

- *Settings, Editor, Inspections*: choose the **Project Default** profile (the one saved in the project, not the IDE
  one).
- Under *Python, Unresolved references*, add these to *Ignore references*: `alto.exercises.*`, `alto.learning.*`,
  `alto.theory.*`, `alto.ui.*`, `alto.audio.*` and `alto.__main__`.

The result is this in `.idea/inspectionProfiles/Project_Default.xml`, with `USE_PROJECT_PROFILE` set to `true` in
`profiles_settings.xml` next to it:

```xml
<inspection_tool class="PyUnresolvedReferencesInspection" enabled="true" level="WARNING" enabled_by_default="true">
  <option name="ignoredIdentifiers">
    <list>
      <option value="alto.exercises.*" />
      <option value="alto.learning.*" />
      <option value="alto.theory.*" />
      <option value="alto.ui.*" />
      <option value="alto.audio.*" />
      <option value="alto.__main__" />
    </list>
  </option>
</inspection_tool>
```

Names that really are unresolved are still reported, in code and in examples.

**2. Add a database connection, so the SQL in `alto/learning/database.py` is checked.** Without one, PyCharm warns about
every SQL string.

1. Make a file with the real schema, which `Database` creates when it opens a new file:

   ```bash
   python -c "from alto.learning import Database; Database('.idea/alto-schema.db').close()"
   ```

   Delete the file and run this again whenever the schema in `database.py` changes.
2. In the *Database* tool window, add a **SQLite** data source named `alto (schema)` for that file
   (`jdbc:sqlite:<path to the clone>/.idea/alto-schema.db`).
3. In *Settings, Languages & Frameworks, SQL Dialects*, set the **Project SQL Dialect** to **SQLite**
   (`.idea/sqldialects.xml`).

**3. Leave "Analyze Python code in docstrings" switched on.** The examples are real code, so PyCharm should keep checking
them. A few habits keep them quiet:

- Name example variables so they do not shadow a parameter or a module-level name; a trailing underscore is fine
  (`database_`, `cfg_`).
- Where PyCharm cannot tell a value is not `None`, or the example deliberately uses a private member, put a comment line
  before that statement: `>>> # noinspection PyUnresolvedReferences` or `>>> # noinspection PyProtectedMember`. It covers
  only the next statement.

In code, suppress a false positive narrowly, with `# noinspection <Inspection>` on the line above the statement or the
function, and say why when it is not obvious. A few things that are not obvious:

- `PyUnusedLocal` is not honored for the parameters of a fake that has to match what it replaces; delete them explicitly
  (`del volume, kwargs`) instead.
- Read saved text with `text_value` in `alto/ui/store.py`, not `str(settings.value(...))`, which PyCharm flags and Pyright
  needs.
- Declare every attribute in `__init__`, not in the method that first sets it.

## Designing lessons and exercises

A **lesson** teaches a musical idea that a learner can apply in several situations. An **exercise** gives repeated
practice in one specific technique. In an identification exercise, the learner reads or hears an example and names
what it is. In a construction exercise, the learner starts with a specification and supplies the notes or symbols
that satisfy it.

Plan the relationship by learning goal. One lesson can prepare a learner for several exercises, and an exercise can
reinforce ideas introduced in several lessons. Reuse an existing lesson when it already explains the idea a new
exercise depends on.

Order the lesson tiles by prerequisite in `alto.lessons.LESSONS`. Start with a lesson that assumes no music theory
knowledge. When adding a lesson, place it after the ideas it uses and before lessons that build on it.

1. **Choose the lesson outcome.** Write one sentence describing what a first-time learner should understand by the
   end. Use that sentence to decide which examples belong and where the lesson should stop.
2. **Map the practice.** For each related exercise, describe what the learner is given, what they do, and what makes
   the answer correct. Check the exercise catalog for a match before proposing a new drill.
3. **Check the vocabulary in teaching order.** Read the lesson as a learner who has completed only the preceding
   lessons. For each musical term, find where its meaning was taught. If it is new, give a plain-language definition
   where the learner first needs it, before a diagram or question asks them to use it. A mention in a title or a
   glossary entry alone does not teach the term. For example, introduce the tonic as the note that feels like home,
   then ask the learner to find it. Repeat this check when reordering lessons.
4. **Build a short guided sequence.** Introduce the idea with an example the learner can read or hear. Change one
   feature and ask the learner to predict or explain the result. Give feedback that points back to the example.
   Use the closing step to name the skills the learner can practice next. Choose the primary practice target with `Lesson.exercise` and list
   additional practice targets in `Lesson.related_exercises`.
5. **Time a first pass.** Aim for **20 minutes or less**, including reading, listening, guided questions, and time
   to use a hint. Count independent exercise practice separately. If the lesson runs long, move repeated trials
   into an exercise or split off a concept that has its own learning outcome.

### Engraving lesson examples

Let the music determine the width of a lesson example. Measure spacing in **staff spaces**, where one space is the
distance between the centers of adjacent staff lines. The values below are starting points for Alto. Measure
horizontal gaps between the visible edges of the symbols, except where the table specifies notehead centers.

| Where | Starting spacing |
| --- | --- |
| Clef to key signature | Leave 1 staff space before the first sharp or flat and ¼ space between successive signature marks. |
| Key signature to first note | Leave 1½ spaces before the notehead or its local accidental. With an empty signature, measure directly from the clef. |
| Local accidental to notehead | Leave ¼ space so the sign reads with its note. Stagger accidentals in a chord as needed to clear other signs, notes, and ledger lines. |
| Notes in a phrase | Start equal quarter notes 3½ spaces apart, measured from center to center. Give longer values more room and shorter values less. Allow clearance for flags, dots, and accidentals. Keep simultaneous pitches at the same rhythmic position. |
| End of a short staff | End the lines about 2 spaces past the last symbol, including when the example shows only a key signature. |

Anchor short examples at the left. When the pane widens, let the extra room fall beyond the staff. When a longer
phrase needs another line, wrap at a musical boundary and repeat the clef and key signature. For paired examples,
align the left edges and clefs, keep the staff size consistent, and align corresponding beats when comparing phrases.
Size the white box to the wider of the music and its caption, with a small margin around both. Once the example
fits on one line, keep the box at that width as the pane grows. Let long captions wrap below the staff in a narrow
pane. Allow enough height for the clef, accidentals, ledger lines, and every line of the caption.

Group related staves and their playback button in one bordered panel. Arrange the staves in reading order across
the panel, with a vertical divider between neighbors on the same row. Use continuous white notation paper all
the way to the panel border, including between staves and behind the playback button beneath the music. Use the
theme’s light button colors on that paper. At a
lesson content width of 760 pixels or more, align the top of the panel with the top of the explanation. Below
that width, place the panel after the opening paragraph and before the remaining text and question. Keep paired
staves together whenever both fit and wrap them when necessary.

Put each guided question in the **Check your understanding** callout. Keep its prompt, choices, hints, explanation,
and retry control together. Let answer buttons wrap in reading order when space is tight.

Use `StaffPlayback` for a playable staff example. Its callback identifies each onset by position, so repeated notes
light in reading order and a chord lights together. When two diagrams show the same sounding note, highlight both.
Clear the playback highlight at the end and when changing examples.

Lesson diagrams use `StaffWidget(lesson_layout=True)` in `alto/ui/lesson.py` and the lesson's scale explorer.
The renderer measures the selected notation font and keeps each chord together when wrapping. In the scale explorer,
a step label followed by an arrow leads to the first pitch on the next line.

To check a layout change, view an F natural in G major, a three-flat bass-clef signature on its own, and a short
run of quarter notes in both narrow and wide panes. The natural should read with the F, the flats should read as
one group, and widening the pane should preserve the distance between the quarter notes. Also try a single note
with a caption wider than its staff. Narrow the pane until the caption wraps, then widen it again. The last word
should stay visible throughout, and the white box should stop growing once the caption fits on one line.

### Reviewing the lesson sequence for gaps

Review the affected stretch whenever a lesson is added, moved, or substantially revised. Every few lesson changes,
walk the full sequence in the order given by `alto.lessons.LESSONS`. Start with an absolute beginner and carry
forward what each lesson actually teaches. An optional exercise or glossary lookup can reinforce a skill, but a
learner can reach the next tile without doing either.

1. Work through the next lesson's examples and questions. For each, finish the sentence “To do this, I already need
   to be able to …” Include reading the diagram, hearing a difference, and interpreting the answer choices.
2. For each prerequisite, record the earlier lesson and step that teaches it, or the worked example in the current
   lesson before its first use. Distinguish seeing a definition, following a demonstration, and using the idea on a
   fresh example. Match the evidence to what the question actually asks the learner to do.
3. Try one fresh example with the same demands. For instance, after a learner reads a note just above a known line,
   ask them to read one just below it. When possible, watch a first-time learner try it before giving a hint.
   Record where their reasoning stops. A walkthrough by the author and an observed learner result are different evidence.
4. Flag a **blocking gap** when an essential action requires knowledge the sequence has yet to teach. Flag a
   **practice gap** when the explanation exists but the jump to independent use needs a smaller example.
   Record one row per finding. Keep a row open until someone retries the original task using the revised sequence.

| First lesson and step that needs the skill | What the learner must do | Where it was taught | Finding and smallest repair | Recheck |
| --- | --- | --- | --- | --- |
| Scale Identification · Count the steps | Locate middle C on a treble staff to follow the C-major example | Intervals · Lower the upper note traces E4 on the bottom line through D4 to C4 on its ledger line. The staff shows C4 and E♭4. | The worked example now connects the bottom line to middle C before scales. | Open. Ask a first-time learner to locate C4 on a fresh treble staff and explain how they found it. |

Prefer a short bridge at first use when it serves one lesson. Move a prerequisite earlier when several lessons rely
on it. Add a separate lesson when the missing skill needs its own guided sequence to keep a first pass within
about 20 minutes.

### Example lesson plan for scales

A lesson on **Scales** could ask, “How can the same major-scale pattern start on two different notes?” Have the
learner play C major, locate the half steps, then start on G and decide whether F or F♯ preserves the pattern.
Close by playing the G scale they predicted. An illustrative first pass allows four minutes for C major, six for
the guided G major example, and three for the comparison and recap.

| Related exercise | What the learner practices |
| --- | --- |
| Scale Identification | Given a written scale, identify its tonic or mode from the notes and their spacing. |
| Scale Construction | Given a tonic and a scale type, place the notes on the staff with the correct spelling. |

## Adding an exercise

For an exercise with answer choices, subclass `ChoiceExercise` in `alto/exercises/library.py` and implement `make_question`. Supply the full set of eligible answers. Alto adds the **Buttons** submenu and applies **Limited** or **All**. A construction exercise whose buttons edit or submit an answer uses `Exercise.generate`.

```python
@register
class MyExercise(ChoiceExercise):
    name = "My exercise"
    category = "Intervals"
    description = "One line shown on the home screen."
    par_seconds = 5.0  # a good first-answer time; see How practice adapts

    def make_question(self, rng):
        ...
        return Question("What is this?", choices=choices, answer=answer, staff=[[note]], clef="treble")
```

- `Question` describes everything the screen needs: a prompt, the answer buttons, the notes to draw, a key signature, a keyboard key to highlight, and so on.
- If your exercise reads user settings, override `practice_signature()` for a `ChoiceExercise` or `settings_signature()` for other exercises and return `signature(...)` of those settings. Stored questions are only replayed while the signature is unchanged.
- Give the exercise an icon in `alto/ui/home.py` so it appears properly on the home screen.
- Pick its `category` from the existing ones, or make a new one. `@register` places the exercise next to the others of its category, so the home screen and the exercise list show each category once, whatever order the classes are written in.

Everything else comes with it: the question is recorded in the database, scored for speed, drawn in the chosen
notation font and included in the statistics.

### Adding an exercise option

#### Requesting exercise options

Use the option names below when asking an agent to design or implement exercise settings. An **option** is a row in
the exercise’s settings menu. A **choice** is a value inside that row, such as **Descending** under **Motion**.
**Answer buttons** are the controls the learner presses during practice. The **Buttons** option configures them.

| What to ask | What to expect |
| --- | --- |
| “Propose options for Interval Identification.” | A short table of options that fit the exercise. For each, give its menu label, what changes for the learner, the template exercise, the choices and default, and any behavior that would need new work. |
| “Add standard Clefs to Interval Identification.” | A working Clefs row modeled on Note Identification, with the shared picker and selected-clef preview. The exercise generates questions using the checked clefs. |
| “Use Range from Keyboard Note Identification. Default to C4–C5.” | The named exercise supplies the keyboard range editor, preview, and interactions. The requested range sets the initial endpoints. |

**Standard** means to reuse the option in the table below. **From [exercise]** selects a specific variant. An explicit
override takes precedence. For example, “default to treble and bass” sets the boxes checked on first use. “Offer only
treble and bass” limits which boxes appear. If the request leaves the default open, preserve the target exercise’s
current behavior where possible. Reusing a picker gives the target exercise its own saved selection unless the
request calls for a shared preference or the exercises already share it.

#### Exercise option vocabulary

The template exercise gives you a place to try the option in Alto. Its panel and the named helpers are in
`alto/ui/settings_panel.py`. Start with the option’s effect on the question or answer to choose among variants.

| Option to request | What the learner gets | Template to reuse |
| --- | --- | --- |
| **Clefs** (also “Clef”) | A row showing the selected clef symbols. Its submenu has grouped, illustrated checkboxes. At least one stays checked. Offer the grand staff when the exercise supports questions on both staves. | **Note Identification** uses `ClefPictures` with `_clefs_page`. **Scale Construction** shows the single-staff variant of the same picker. |
| **Range** | Low and high pitches. Staff exercises can keep a range per clef. Keyboard exercises select a span on a piano and show a miniature keyboard in the row. | **Note Identification** uses `RangeEditor` with `RangePictures`. **Keyboard Note Identification** uses `KeyboardSpan` and endpoint arrows. |
| **Staff Key** | Check which signatures can be drawn at the start of the staff, including the blank signature. The row previews the selection. | **Scale Identification** uses `KeyChecklist` and `KeyDiagram`. |
| **Scale Key** | Choose the musical keys used in questions. Underlined Major and Minor tabs each offer 15 signatures. Either tab may be empty if the other has a selection. The row counts selections by mode. | **Scale Identification** uses `_ScaleKeyPicker`. When both key options apply, place **Staff Key** above **Scale Key**. |
| **Key signatures** | A single checklist of signature counts. Some exercises also let the learner turn signatures on or off. | **Note Identification** uses `KeyChecklist`. For the version with a switch inside the submenu, follow **Keyboard Note Identification** and `KeySignaturePage`. |
| **Scales** | Check the scale types or modes that can appear, such as major, Dorian, and natural minor. | **Scale Construction** uses `ChoiceChecklist` and shows the selected count in the row. |
| **Motion** | Choose **Ascending** or **Descending** with radio buttons. | **Scale Identification** and **Scale Construction** share this page in `KeySignatureSettingsPanel`. |
| **Display** | Choose how the notes appear on the staff. Checked presentations can be mixed. | **Interval Identification** offers Melodic and Harmonic checkboxes. |
| **Quality** | An inline switch requires the interval quality as part of the answer. Turning it off asks for the number alone. | **Interval Identification** uses `_ToggleRow`. |
| **Question Type** | Choose what the learner is asked to do. Use radios for one format, or checkboxes when the question can combine parts. | **Notation Identification** has **Click on Staff** and **Answer Button** radios. **Scale Identification** has independent **Key** and **Mode** boxes. **Note Construction** shows its keys and degrees when **Scale and Degree** is selected. |
| **Buttons** | One submenu for answer layouts. **Limited** caps the number offered, with **Button count** directly below it. **All** shows the full answer set. | **Scale Identification** and **Interval Identification** share the Limited and All submenu. **Keyboard Interval Identification** adds **Compact**, where the learner picks a quality and an interval number in either order. |
| **Octave** | An inline switch that makes the octave part of the required answer. | **Note Construction** uses `_ToggleRow`. **Keyboard Note Identification** labels its variant **Octave number**. |
| **Note names**, **Note values**, **Accidentals** | Choose a naming system, check the durations that can appear, or switch on questions with written accidentals. These are separate options. | **Note Identification** has the naming and value previews and the Accidentals switch. |
| **Terms**, **Degrees**, **Arpeggio types**, **Inversions** | Check the items eligible for practice. **Terms** also restricts the distractors. **Degrees** is a section within **Scale and Degree**. | All use `ChoiceChecklist`. **Notation Identification** groups terms, **Note Construction** lists degrees, and **Arpeggio Identification** has separate pages for types and inversions. |
| **Intervals** | Choose interval sizes individually or by endpoints. The available sizes depend on the keyboard range. | **Keyboard Interval Identification** combines `ChoiceChecklist` and `IntervalRangeSlider`. **Interval Identification** uses the slider for interval numbers and the checklist for written spellings, so A4 and d5 can be selected separately. |

For exercise-specific options, use the existing exercise as the reference. Examples include **Black keys** in
Keyboard Note Identification, **Steps** in Scale Construction, and **Questions** and **Colors** in Circle of Fifths.

#### Implementing the request

Start by opening the template’s settings row and tracing its panel, saved settings, and question or answer behavior.
Reuse the shared picker, preview, and selection rules where they fit. If two exercises need the same behavior and
it currently lives inside one panel, share that implementation while preserving the original exercise’s behavior.
When a new option needs a distinct interaction, describe the difference from its closest template. Add a vocabulary
entry when introducing a reusable option or variant so it can be requested by name next time.

1. Give the option a row on the exercise settings menu. Use the shared `_Row` in `alto/ui/settings_panel.py` with
   the option name, a short summary of the current selection, and the chevron. For a standalone on/off setting,
   such as **Octave**, an inline `Switch` in a row without a chevron is appropriate. Two named modes, such as
   **Click on Staff** and **Answer Button**, belong together in a submenu.
2. Open the option with the panel’s `SlideStack`. Build its page with `_subpage` so the title matches the row and
   Back returns to the settings menu. Use radio buttons when exactly one choice applies and checkboxes when
   several can apply. Keep long lists scrollable.
3. Load the saved value when building the panel, using a default for first use. When a choice changes, save it,
   update the row summary, and apply it to the exercise. Opening the submenu or pressing Back should keep the
   current question. Include settings that affect question selection in the exercise’s review signature.
4. Test the path from the exercise gear through the row and back. Verify the first-use default, the effect on
   questions and answers, the updated summary, and the restored choice when reopening the app. For example, select
   only bass under **Clefs**, generate questions, and check that the row preview and each staff show bass. If the
   implementation touched a shared picker, run the original exercise’s settings tests too.

## Adding an instrument

1. Put its recordings in `alto/assets/samples/<key>/`, one mono WAV per note, named by MIDI note number (for example
   `60.wav` for middle C). Every semitone is best. Where a note has no recording, Alto shifts the nearest one.
2. Add an `Instrument` to `INSTRUMENTS` in `alto/audio.py`. Mark it `sustained=True` if it is bowed or blown, so each
   note ends as the next begins. If it is another way of playing an instrument already listed, give both the same
   `family` and each its own `variant` (the viola's "Arco" and "Pizzicato"), and they appear as one entry with a choice.
3. Add an entry for the same key to `INFO` in `alto/instrument_info.py`: what it is, the source, who played it, and
   the terms. This is what the summary in the Sound settings shows.
4. Credit the recordings in `THIRD_PARTY_NOTICES.md` and the folder's `SOURCE.txt`.

Only add recordings whose license allows redistribution.

## Adding a notation font

Alto draws notes with fonts that follow the [SMuFL](https://www.smufl.org/) standard.

1. Put the font file and its license in `alto/assets/fonts/`.
2. Add its stem anchors and engraving defaults to `engraving.json`, read from the font's SMuFL metadata file.
3. Register the file name in `_FILES` in `alto/ui/engraving.py`.
4. Add a `NotationStyle` to `STYLES` in `alto/ui/notation.py`.
5. Record the font in `THIRD_PARTY_NOTICES.md`.

Only add fonts whose license allows redistribution, such as the SIL Open Font License.

## Adding a keyboard style

Add a `KeyboardStyle` to `STYLES` in `alto/ui/keyboard_styles.py`: the colors of the naturals and sharps, and any extras such as
a case, felt, bone caps or stop knobs. The settings page, the keyboard and the range picker all read from that list, so nothing
else needs to be changed. Add a row to the table in `docs/settings.md`. The colors named after materials in the builder are `MATERIALS` in the same file.

## Versions of the docs

The docs exist in one copy for each release and one for the development version, and a dropdown in the top bar switches between them.
A page of an old release says so in a banner, and links to the same page in the latest one.

```
/alto/dev/        the development version, rebuilt when a change to docs/ is merged into main
/alto/v0.1.0/     one folder for each release, built once when its tag is pushed and not changed after that
/alto/latest/     the newest release again, built with its own address so that its links and its sitemap say /latest/
/alto/            goes to latest (to dev until there is a release); also versions.json, version-switcher.js, 404.html, robots.txt
```

The Docs workflow (`.github/workflows/docs.yml`) builds them with Jekyll and keeps the result on the branch `gh-pages`, which
GitHub Pages serves. `scripts/docs_site.py` writes what sits around the versions: `versions.json`, the home page that goes to the
latest, and the sitemap. The files that belong to the whole site and not to one version are in `docs/site-root/`. One of them,
`version-switcher.js`, fills the dropdown from `versions.json` at run time, so a release made years ago still offers the newest
versions, and a fix to the dropdown reaches all of them.

Search engines are told to prefer the latest version: every page has a `canonical` address under `/latest/`, `dev` is `noindex`, and
only `latest` is in the sitemap. A page that existed at the root before the docs had versions is sent to `/latest/` by `404.html`.

To add a docs-only fix to an old release, there is nothing to do but publish a new release: a version is built once from its tag.
To build a release that was tagged before it had a dropdown, run the Docs workflow by hand with `ref` set to its tag. It puts the
current layout over that tag's docs, and the words stay as they were.

**Switching a copy of the repository to this**, once: after the first run has created the `gh-pages` branch, set Settings, Pages,
Source to "Deploy from a branch", `gh-pages`, `/ (root)`. Until then GitHub builds a single copy from `main:/docs` as before. Do this
soon after merging, because the one copy no longer has `robots.txt`, `llms.txt` or the Search Console file, which now live in
`docs/site-root/`.

### Pages in the sidebar

The sidebar and the "On this page" list are built from the pages themselves. A page is listed by what its front matter says:

| Key | Meaning |
|---|---|
| `nav_order` | Where it goes, lowest first. A page without one is not in the sidebar. |
| `nav_group` | The heading it goes under (Using Alto, For developers, About). The headings open and close, and the pages of one heading must be next to each other in `nav_order`. Home has none. |
| `children`, `parent` | A page with `children: name` is one row that links to it and opens the pages that say `parent: name`, in their `order`. Those pages can also say `package:` to be grouped under a small heading that opens and closes (the API reference). |

A heading that is also the title of a page (For developers) is that page's link, and the page is not listed again under it. Whatever holds
the page you are on is open. Which headings you closed is remembered in the browser.

On a wide screen a page with two or more `##` or `###` headings gets an "On this page" list beside it, made in the browser from those
headings, and on a narrower one a box above the text. Nothing needs to be written for it. A page that should not have one, such as the
home page, says `toc: false` in its front matter. `docs/api/index.md` is written by
`scripts/api_docs.py`, so change its front matter there.

Every page in the sidebar ends with a link to the previous page at the bottom left and to the next at the bottom right, in the sidebar's
own order: the pages by `nav_order`, each followed by its `children` in their `order`. Nothing needs to be written for them. The first page has
no previous link and the last no next one.

### Building the docs

You need Ruby and Bundler. In `docs/`, `bundle install` once, then build one version the way the workflow does:

```bash
cd docs
printf 'baseurl: /alto/dev\ndocs_version: dev\n' > /tmp/version.yml
bundle exec jekyll build --destination /tmp/site/dev --config _config.yml,/tmp/version.yml
python ../scripts/docs_site.py finish /tmp/site --root-files site-root --site-url https://altosaurus.github.io/alto
```

then serve `/tmp/site` under a folder called `alto` (for example `mkdir /tmp/www && ln -s /tmp/site /tmp/www/alto && python -m http.server -d /tmp/www`)
and open `http://127.0.0.1:8000/alto/`. `tests/test_docs_site.py` checks the script and the files without needing Ruby.

## Keeping the docs and screenshots current

Every picture in the docs comes as a light and a dark pair, and `scripts/screenshots.py` makes all of them:

```bash
.venv/bin/python scripts/screenshots.py                    # every picture, both themes
.venv/bin/python scripts/screenshots.py --only home stats  # just these
.venv/bin/python scripts/screenshots.py --out /tmp/shots   # somewhere else, to look before replacing
```

It runs against a made-up profile and a temporary settings folder, so it never touches your own history or settings. It
needs a display or `QT_QPA_PLATFORM=offscreen`. Fonts render slightly differently on each machine, so regenerate on the
machine you normally use and look at the pictures before committing them. To add a picture, include it in a docs page
with `shot.html`, and add its name to `SHOTS` in the script. `tests/test_docs.py` checks that both match and that both themes
exist.

The pre-push hook runs `scripts/check-docs.sh`, which warns when the interface (`alto/ui`) has changed since the pictures
were last updated. It only warns; set `ALTO_DOCS_STRICT=1` to make it fail.

## The API reference

The pages under [API reference](../api/) (`docs/api/`) are written from the docstrings by `scripts/api_docs.py`. Each module
has a page with its public classes, methods and functions: the signature, then the NumPy-style docstring as Markdown. Names
that begin with an underscore are left out. The script reads the source as text, so it needs neither Qt nor a display.

```bash
python scripts/api_docs.py          # rewrite docs/api
python scripts/api_docs.py --check  # list the pages that are out of date, and change nothing
```

GitHub Pages cannot run the script, so the generated pages are committed. When you change a docstring or a public signature,
run it and commit the pages with the change. `tests/test_api_docs.py` fails when they are out of date, so a forgotten run is
caught by the tests, the pre-push hook and the pull request.

## Changelog and releases

`CHANGELOG.md` lists what changed for the people who use Alto, newest first, in the
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) layout. A change a user would notice (a new exercise, a changed menu, a
fixed bug) adds a line under **Unreleased** in the same pull request. Internal tidying does not need one.

To make a release:

1. Choose the version. Alto uses [semantic versioning](https://semver.org/): a new feature raises the middle number, a fix
   raises the last.
2. In `CHANGELOG.md`, rename **Unreleased** to the version with today's date (`## [0.1.0] - 2026-12-01`), add a new empty
   **Unreleased** above it, and update the two links at the bottom. Then run `python scripts/release_notes.py`, which rewrites
   the Release notes page of the docs (`docs/release-notes.md`) from the changelog; `--check` says whether it is up to date, and a
   test fails when it is not, so a changelog line always arrives with its page.
3. Set the same version in `pyproject.toml`. `tests/test_changelog.py` fails if the changelog has no notes for it.
4. Merge that as a pull request, then tag the merge commit and push the tag: `git tag v0.1.0 && git push origin v0.1.0`. Pushing
   the tag starts the **Release** workflow (see below), which publishes the downloads.

Publish a release as a normal release, not a pre-release: the update check asks GitHub for the latest release, which leaves
pre-releases out, and compares version numbers (`0.10.0` is newer than `0.9.0`), so a tag must be plain numbers such as `v0.1.0`.

`python scripts/changelog_section.py 0.1.0` prints the notes of one version, which is what a GitHub release shows. `alto --version`
prints the version of the copy you run.

## Building the Linux download

```bash
sh scripts/build-linux.sh                       # dist/alto-<version>-linux-<architecture>.tar.gz, and its .sha256 file
PYTHON=/path/to/python3.13 sh scripts/build-linux.sh
```

The script makes a clean virtual environment under `.package-build/`, installs Alto and PyInstaller (the `package` extra in
`pyproject.toml`) in it, freezes Alto with `packaging/alto.spec`, and packs the result with `packaging/linux/install.sh`, a
README, the license and the third-party notices. Nothing is installed on your computer. Before it packs anything it checks that the
frozen program says `Alto <version>` and that it opens its window (under Qt's offscreen platform, with its own data folder, so a
real profile is never touched).

The download is the program folder, which carries its own Python and Qt, so users need no Python. `install.sh install` copies it to
`~/.local/opt/alto`, links `~/.local/bin/alto` and adds the menu entry; `uninstall` removes those and keeps the user's data, and
`uninstall --purge` deletes that too. `tests/test_linux_install.py` runs the real script in a scratch home.

Two things to know when building a release:

- **Build on an old Linux.** The frozen program needs at least the C library of the system it was built on, so the release
  workflow builds on Ubuntu 22.04, and a build made on a newer system will not start on older ones.
- **System libraries come from the build machine.** PyInstaller copies the libraries Qt needs from the system it runs on
  (including GTK, glib and `libstdc++`), apart from a short list it leaves out (graphics drivers, `libxcb` and `libwayland`).
  That includes the libraries of Qt's X11 plugin (`libxcb-cursor`, `libxkbcommon-x11` and a few more), so the build machine must have
  them installed: the workflow does, and the build script fails if the X11 plugin of the finished folder cannot find any of them.
  If a build misbehaves on another distribution, check which libraries it loads, and exclude the offender in `packaging/alto.spec`.

To try a build without touching your own install, extract it and run `./alto/alto`, or run `install.sh` with `ALTO_PREFIX`,
`XDG_DATA_HOME` and `XDG_CONFIG_HOME` pointing at scratch folders.

## Building the Windows installer, and the release workflow

`scripts\build-windows.ps1` builds `dist\alto-<version>-windows-x64-setup.exe`. It needs Windows, Python 3.13 and
[Inno Setup 6](https://jrsoftware.org/isinfo.php). Like the Linux script it freezes Alto with `packaging/alto.spec` and checks that the
program starts; then it compiles `packaging/windows/alto.iss` and tries the installer for real: a silent install, a run, a silent
uninstall that must keep the data, and an uninstall with `/PURGE=1` that must remove it. That test uses the real `%APPDATA%\Alto`, so
run it only on a computer where that folder may be touched, such as a CI runner. The installer is for one user (no administrator
prompt); its `AppId` in `alto.iss` must never change, because a newer installer finds the copy it updates by it. The uninstaller asks
whether to also remove the practice history (`%APPDATA%\Alto`) and the settings (`HKEY_CURRENT_USER\Software\alto`); a silent
uninstall keeps them unless it is given `/PURGE=1`. The installer is not signed, so Windows shows an "unknown publisher" warning.

### Signing releases, once

A packaged copy of Alto updates itself, and it installs only what is signed with a key that came with it. The key pair is made once:

1. Run `python scripts/make_signing_key.py`. It prints a **private** key and a **public** key and writes nothing.
2. Store the private key as the GitHub secret `ALTO_SIGNING_KEY` (the repository's Settings → Secrets and variables → Actions), and keep
   an offline copy of it, for example in a password manager. Whoever has it can sign an update that every copy of Alto will install,
   and if it is lost no copy can be updated by a release signed with a new key: people would install the next version by hand.
3. Put the public key in `UPDATE_PUBLIC_KEYS` in `alto/updates.py` and commit it. Until it is there a packaged copy does not replace
   itself; it is only told that a newer release exists, and the Release workflow refuses to publish.

The Release workflow signs `SHA256SUMS` with the secret (`scripts/sign_release.py`) and uploads `SHA256SUMS.sig` with it. Before it
builds anything it signs a probe file, and the script checks the signature against the public key in the code, so a secret that is
not that key's stops the release at once and not after the builds. `UPDATE_PUBLIC_KEYS` is a tuple so that a release can carry a
second key before the first is retired.

`alto --self-test` checks, with no network, that a packaged build has what an update needs (the certificate authorities, which the
bundled Python cannot count on the system for, and the signature check). Both build scripts run it. The Windows script also runs a
newer installer over a running Alto with the arguments Alto uses, and checks that the old one closed, the new one was installed and
Alto opened again. What cannot be tested before a release exists is a copy checking a real release, which first happens when a
release newer than the installed one is published; try the update on a real Linux and a real Windows machine then.

Three GitHub workflows do the building:

- **Build packages** (`build-packages.yml`) builds and tests both packages: the Linux download on Ubuntu 22.04 and the Windows
  installer on a Windows runner, both with Python 3.13. The other two call it.
- **Package** runs it on a pull request that changes `packaging/`, the build scripts, `pyproject.toml` or the assets, so a break
  shows before a release. It publishes nothing.
- **Release** runs when a tag such as `v0.1.0` is pushed. It first checks that the tag is `v` plus the version in `pyproject.toml` and
  that `CHANGELOG.md` has notes for it; then builds both packages; then creates the GitHub release with both files, a `SHA256SUMS`
  file and the changelog notes. Started by hand from the Actions tab, it only builds, to rehearse a release.

The release is a normal one and never a pre-release, because Alto's update check asks GitHub for the latest release.

## Reporting problems

Open an issue on [GitHub](https://github.com/altosaurus/alto/issues). Say which operating system and Python version you
use, and which exercise you were in.
