# Changelog

All notable changes to Alto are written here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
Alto uses [semantic versioning](https://semver.org/).

## [Unreleased]

### Added

- Every exercise with answer choices now offers Limited and All button layouts. Each exercise remembers its own selection.

- Interval Identification has per-clef pitch ranges, staff keys, display choices, an interval checklist, a Quality switch for number-only practice, and Limited or All answer buttons.

- Answer cards opened from Database or Statistics show graphs of response time and cumulative first-try accuracy for the question.
- Double-clicking a row in **Questions that need practice** opens the saved question and its answer.
- A beginner lesson on pitches and notes links to three note exercises, with reference hints and a return path to the lesson.
- Notation Identification lets learners name a highlighted marking or find a named component on the staff. Hovering
  previews a component before answering, and learners can choose which notation terms to practice.

- Keyboard Interval Identification with configurable keyboard and interval ranges, compound intervals, and Limited, All,
  or Compact answer buttons. Compact answers use a quality letter and an interval number.

- A searchable glossary in the top toolbar, with notation examples, playback, and related exercise and lesson tiles.
- An interactive Scale Identification reference and lesson, with scale comparisons and note highlighting.
- An optional octave answer in Note Identification, saved window geometry, and Restore defaults in Settings.

- Scale degrees as a note-name group for Note Identification, Keyboard Note Identification and Note Construction, with caret
  notation (1̂–7̂), function names (Tonic, Supertonic, and so on), altered degrees and explicit major-key context.
  Note-name previews have visible text labels.

### Changed

- Push buttons have a rounded hairline border, a tinted hover state, and a keyboard focus ring. In dark mode,
  exercise tile outlines are near black and other standard button outlines are graphite gray.

- The documentation homepage groups practice into six topic cards that switch between light- and dark-theme screenshots.
- Keyboard exercise icons use seven realistically proportioned white keys; the interval icon adds a span bracket.
- Exercise button-group labels appear above their buttons, and theme rebuilds preserve the exercise settings page.
- Code, documentation, and interface text use American English; saved color-scheme settings remain compatible.

- Appearance settings use a hierarchical sidebar and grouped overview. Data pages share the toolbar Back button,
  and active toolbar icons use the theme accent color.

- Scale Identification replaces Scale Spelling, keeping its icon. Identify an ascending scale on a staff, with selectable
  clefs, scale types, and independent staff and scale key signatures.

- Navigation is grouped on the left of the top bar, with Statistics and Browse database on the right. Exercises / Lessons
  changes the sidebar without leaving the active activity. Separate pane and grid buttons toggle the list or return to
  tiles while retaining the question, answer selection and lesson step. Search filters tiles and lists, and a back button
  resumes the active exercise or lesson. Before starting an activity, the workspace prompts you to select one.

### Fixed

- The documentation homepage shows dark app screenshots in dark mode, and its Keyboard Identification icon matches the other blue topic icons.
- Scale Identification plays with even rhythm on the first correct answer, highlights each note as it sounds, and waits
  for the scale to finish before advancing.

- Switching themes in Settings is faster, and Settings opens more quickly.

## [0.0.1] - 2026-11-15

### Added

- A new exercise, Clef Basics: a blank staff and the name of a clef. Choose the G, C or F clef symbol with three buttons, the mouse
  wheel or a right click, and put it where it makes that clef: the C clef on the second line is the mezzo-soprano clef. It can be tried
  on lines, spaces and three ledger lines each way. Its settings are Question Type, Clef Construction or Clef Identification (a clef is drawn on a staff and you press the
  button with its name), and Clefs, which chooses which clefs are asked for, including the French violin and subbass clefs. The baritone clef is accepted as the F clef on the middle line or the C clef on the top line.
- A Clef Basics lesson, in ten short steps with small exercises: what a clef does, the G, C and F clef, the line each puts its symbol
  on, and how to tell them apart. The Clef Basics exercise has a reference pane, opened with the book button, with a table of the clefs
  and a button that opens the lesson.
- The documentation has a version for each release and one for the development version, with a dropdown in the top bar to switch
  between them. A page of an older release says so and links to the latest.
- The documentation home page has a Download Alto button under the first paragraph, and a download section in place of "Get started". Its
  main button names the visitor's system and goes to the right file, with the other systems listed below it.
- The documentation has a Release notes page, made from this changelog, under About in the sidebar and linked from the home page.
- The circle of fifths has a Colors setting with fourteen color schemes, and a Create your own that saves schemes of your own. It
  applies to the exercise, the lessons and the reference.

### Changed

- The notation-font previews in Settings use the DSCH motif (D, E♭, C, B) in treble clef.
- Instrument previews play the same DSCH motif as the notation-font previews.
- Exercise and lesson icons use consistent musical glyphs and follow the theme color.

- In Key Signature Construction a number on the fork lights up as the mouse passes over it, the circle can be dragged along the fork, and
  the mouse wheel works over the staff and the Answer button too.
- The documentation sidebar sorts the pages under headings that open and close, with the developer guide and the API reference as single
  rows that open their pages, long pages have an "On this page" list that follows your reading, and every page ends with links to the
  previous and next pages. The home page leaves checking a download and updating to the Getting started page, which now explains both.
- The circle of fifths is colored from cyan through blue to indigo by key signature, instead of every color of the rainbow.
- The circle of fifths opens, and redraws when its window is resized, several times faster. Lessons that show it open faster too.

### Fixed

- Instrument previews keep an even rhythm on first playback by rendering the phrase as one audio clip.
- Changing the theme in the settings no longer sends you back to the exercises home page, or makes the window disappear and grow back
  from a dot. The window stays where it is, showing the exercise, lesson step or page you were on.

## [0.0.0] - 2026-11-15

The first release.

### Added

**Exercises**

- Eleven exercises in four categories:
  - Notation: Note Identification, Keyboard Note Identification and Note Construction.
  - Intervals: Interval identification.
  - Scales and keys: Key Signature Identification, Key Signature Construction, Scale spelling, Scale Construction and the Circle of Fifths.
  - Chords: Chord quality and Arpeggio identification.
- Seven clefs, in every exercise that has a clef setting: treble, bass, alto, tenor, soprano, mezzo-soprano and baritone.
- Every exercise can be answered from the keyboard alone.
- Settings for the exercises, remembered between sessions.

**Learning**

- Questions you miss, or take a long time over, come back more often; ones you answer quickly and correctly fade into the background.
- Profiles, each with its own history, kept in one local database file.
- Lessons: a beginner lesson on the circle of fifths in eight steps, with small unscored exercises, and an Exercises | Lessons switch on the home page.
- A book button opens an interactive circle of fifths in a pane beside the exercise.

**Statistics**

- Charts of accuracy, speed and volume, filterable by exercise and timeframe.
- A calendar heatmap of the last twelve months of practice.
- Click a bar, point, exercise or day to see the answers behind it.
- A database browser for everything stored.

**Look and sound**

- 26 color themes, including light, dark and following the desktop, and a form to make your own.
- 11 notation styles (music fonts), 12 keyboard looks, and 30 transitions between the exercise and lesson cards, including none.
- The Salamander Grand Piano as the default piano, and recordings of a marimba, vibraphone, flute, horn and viola, chosen in Settings.
  The recordings and fonts are used under their own licenses, listed in `THIRD_PARTY_NOTICES.md`.

**Your data**

- Export backup… and Import backup… in the menu. A backup is one `.altobackup` file holding every profile, every answer and every
  setting. Importing replaces everything, and a safety copy of what was there is saved first.

**Installing and updating**

- `scripts/alto-install.sh` installs Alto from GitHub into its own environment, adds it to the application menu, updates it and
  removes it. Uninstalling keeps your data unless `--purge` is given.
- Check for updates… in the menu: says whether a newer release is available, offers to install it with its progress shown, and
  restarts Alto when you press OK. A packaged copy (the Linux download installed with `install.sh`, or the Windows installer)
  downloads the release, checks its signature and checksum, and then closes, installs it and opens again. Releases are signed, and
  Alto installs nothing whose signature does not verify.
- Settings → Updates shows the version you have, and a choice to follow the main branch instead of releases, for the latest
  changes before they are released.
- A Linux download: a `.tar.gz` with its own Python and Qt, so nothing else needs to be installed. `sh install.sh install` installs it
  for you alone, with an entry in the application menu, and `sh install.sh uninstall` removes it and keeps your data unless
  `--purge` is given. Installing a newer download over it updates it.
- A Windows installer: Alto for one user with no administrator prompt, an entry in the Start menu and in Settings → Apps, and an
  uninstaller that asks whether to also remove your practice history and settings. Running a newer installer updates it. The
  installer is not signed, so Windows may warn about an unknown publisher the first time.
- Both downloads are built and tested on GitHub when a version is tagged, and published with checksums.
- `alto --version` prints the version.
- `ALTO_HOME` keeps a copy of Alto apart, with its own history and settings, and `scripts/dev.sh` runs a clone that way.

**Documentation**

- A documentation site, a developer guide, an API reference generated from the docstrings, and `ARCHITECTURE.md`.

[Unreleased]: https://github.com/altosaurus/alto/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/altosaurus/alto/compare/v0.0.0...v0.0.1
[0.0.0]: https://github.com/altosaurus/alto/releases/tag/v0.0.0
