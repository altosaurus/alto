---
title: Release notes
nav_order: 11.8
nav_group: About
permalink: /release-notes/
---
{% comment %}
  The release notes of Alto. Written by scripts/release_notes.py from CHANGELOG.md: change the changelog and run
  the script, not this file.
{% endcomment %}
{% raw %}
All notable changes to Alto, newest first. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and Alto uses [semantic versioning](https://semver.org/).
Each release's downloads are on its GitHub release.

## 0.0.3

Released 2026-11-25. [GitHub release](https://github.com/altosaurus/alto/releases/tag/v0.0.3)

### Added
{: .no-toc}

- Alto now has a signed and notarized disk image for Apple Silicon Macs. Open the disk image and drag Alto into Applications.
- On Linux, play answers in supported note, interval, and scale exercises with a USB MIDI keyboard or the Virtual MIDI Piano Keyboard.
- In Statistics, use the diagonal arrows beside the review heatmap to switch between a continuous calendar and one with gaps between months.
- Search the documentation from the header and press Enter for all results. Code examples have a copy button, and API signatures link to their source.

- A new **Duration** lesson under **Rhythm** introduces quarter, half, and whole notes and quarter rests with counted listening examples. Its icon shows an eighth note beamed to two sixteenth notes. Rhythm examples in lessons and the glossary show a time signature, upward stems, bar lines, and optional counts on staffless notation paper.

- Rythmic Equations lets you choose both the arithmetic signs and the number of operators (zero to three) independently on each side of the equals sign. Its **Answer Type** checkboxes let you practice missing symbols, missing numbers, or both. Turn on **Parentheses** to practice grouped calculations.

- Settings → Sound now has separate **Instruments** and **Metronome** pages. Hear four beats of High pip, Low pip, or Pencil click and watch a smooth spectrum curve rise and fall with each click. The Duration lesson and rhythm glossary examples use the selected click for note onsets and meter accents, with silence for rests. The tie example pairs the metronome with a sustained instrument note.

- Third-party instrument packs can supply artwork, recordings, correct-answer animations, and exercises in one ZIP. Tools → Plugins lists the installed plugins and installs one from a downloaded ZIP or uninstalls it while keeping practice history. Packs can also add their own lessons, extra views of an instrument such as its back, settings for a note exercise (a sound override, a range, accidentals, and the octave), tile icons, glossary entries, links between exercises and lessons, and knowledge checks answered by clicking the picture. The viola plugin tutorial includes a downloadable example with fingerboard and instrument anatomy exercises and two lessons. Instruments can also declare keyboards, which Alto draws in a look the plugin chooses, and a keyboard interval exercise highlights two keys on them, with a range selector, a choice of intervals, and a choice of manuals. A plugin exercise's sound setting opens a list of instruments to sound instead of switching the plugin's sound on or off. It lists the plugin's own instruments first, then other instruments of the same kind, then the rest. The harpsichord example pack, with a Flemish harpsichord sound, shows a double harpsichord, asks the interval between two highlighted keys, names its parts, and adds two lessons and glossary entries.

- Alto can zoom. <kbd>Ctrl</kbd>+<kbd>+</kbd>, <kbd>Ctrl</kbd>+<kbd>-</kbd> and <kbd>Ctrl</kbd> with the mouse wheel make the text, controls, notation, keyboard and icons larger or smaller together, from 50% to 300%, and <kbd>Ctrl</kbd>+<kbd>0</kbd> goes back to 100%. The zoom is remembered.

- The glossary explains intervals: interval, harmonic interval, melodic interval, unison, simple intervals, compound intervals, perfect, major and minor. A harmonic interval's example stacks its two notes and plays them together.

- Interval Identification has an **Inversions** switch for naming the inversion of a written interval. After a right answer, the staff shows and plays the inversion.

- Interval Identification has a **Consonance** switch for telling whether an interval is consonant or dissonant. Perfect unisons, fourths, fifths and octaves, and major and minor thirds and sixths, count as consonant, as do their compound forms. With **Inversions** on too, it asks about the inversion.

- Lesson keyboards highlight each note as it sounds and show chord tones together during playback.
- The Pitches and Notes lesson labels C and brackets its neighboring pair of black keys before asking learners to name the next white key.

### Changed
{: .no-toc}

- The Database page opens faster for long practice histories. It loads answers as you scroll and searches and sorts across the newest 10,000 answers.

- Windows release installers gain a timestamped publisher signature that can be checked in the file’s **Properties → Digital Signatures** tab.

- The Windows installer now uses the Microsoft Visual C++ Runtime installed on Windows. If Windows lacks it or has an older version, the installer downloads Microsoft's installer for it from Microsoft, checks Microsoft's signature, and runs it; Windows asks for administrator permission and Microsoft's window asks to accept Microsoft's license. This happens once, also when Alto updates itself. Alto now needs Windows 10 or later.
- On Windows, the installer asks once to accept the terms for the Microsoft code in Alto's program files, also when Alto updates itself: an update that has not been accepted yet asks before it changes anything, and canceling keeps the version already installed.
- The release builds have added checks that strengthen license compliance, and the downloads include the license notices of the third-party components they contain, in the `licenses` folder.
- Alto no longer depends on NumPy, which makes the installed program about 35–40 MB smaller on Linux and Windows. Sound previews are mixed as quickly as before, and the staff's click map is built about four times faster. Notes made by pitch shifting or synthesis are now kept and reused instead of being made again each time they play, and the current instrument's missing notes are made while Alto is idle after it opens, so even their first play is quick. Previews of plugin instruments are kept too, until the plugin's recordings change.

### Fixed
{: .no-toc}

- On small screens, tap **Contents** to expand the documentation menu below it. On desktop, the sidebar opens directly with the navigation links.

- Keyboard Note Identification now saves its own **Note names** choice. Switching to **Caret** in Note Identification leaves the keyboard exercise’s answers unchanged.

- The Exercises and Lessons toolbar buttons now open their respective catalogs from the Database, Statistics, and Glossary pages.
- Single-question lesson knowledge checks say **Try again** after a wrong answer. Checks with multiple questions keep **Try another**.
- Lesson tiles, search, navigation, menus, and exercise controls now update their icons and colors when the desktop switches between light and dark mode while Alto is set to System.
- Light mode uses a gray window with white tiles and a pale gray search bar, including when following a light desktop.

## 0.0.2

Released 2026-11-19. [GitHub release](https://github.com/altosaurus/alto/releases/tag/v0.0.2)

### Added
{: .no-toc}

- Profiles can use ASRS, ARTS, SM-2, or FSRS. With SM-2 and FSRS, set daily limits, see new, learning, and due counts,
  and optionally grade correct answers Hard, Good, or Easy. Switching between the two carries over the card schedule.
- Filter the exercise grid by category or turn on Shuffle to move between the selected exercises after an answer.
- The database browser shows when a question is due. Statistics can group question counts by hour, day, week, or month.
- The glossary covers enharmonic pitches, transposition, the circle of fifths, minor scales, and relative and parallel keys.
- The **Next Question** setting lets each exercise advance immediately, advance after playback and animation, or wait for **Next**.
- **Help → About** shows Alto’s version and alpha status. **Help → Report an issue** opens the GitHub issue tracker.

- Alto checks for new releases daily and offers upgrades from the main grid. Learners can update, defer the reminder for 24 hours, or skip a release. Automatic checks can be turned off in Settings → Updates.

- Interval Construction asks learners to place a second note above or below a given note on the staff.

- Automatic SM-2 and FSRS grades use each learner’s recent response times for the exercise. After calibration, each card shows the Hard, Good, and Easy review intervals before the learner answers. Practice settings include adjustable percentiles and a chart of the times used.

- The Anki Exporter in the Tools menu saves selected exercises as decks in one Anki package. You can preview cards,
  filter each deck, and include review schedules from an SM-2 or FSRS profile.

- Order of Keys asks learners to write a named key signature one sharp or flat at a time on a blank staff. Learners can choose clefs, scales, key signatures, and how many accidentals are already written.

- Every exercise with answer choices now offers Limited and All button layouts. Each exercise remembers its own selection.

- Interval Identification has per-clef pitch ranges, staff keys, display choices, an interval checklist, a Quality menu for practicing the interval number, quality, or both, and Limited or All answer buttons.

- A Key Signatures lesson teaches how to read and write major and minor key signatures and links to the key signature exercises.
- An Intervals lesson uses staff and keyboard examples to teach interval numbers and qualities, with links to staff and keyboard identification and staff construction.

- Answer cards opened from Database or Statistics show graphs of response time and cumulative first-try accuracy for the question.
- Double-clicking a row in **Questions that need practice** opens the saved question and its answer.
- A beginner lesson on pitches and notes links to three note exercises, with reference hints and a return path to the lesson.
- Notation Identification lets learners name a highlighted marking or find a named component on the staff. Hovering
  previews a component before answering, and learners can choose which notation terms to practice.
  Eight public-domain piano excerpts from Schubert and Schumann put 34 of those terms in musical context.

- Keyboard Interval Identification with configurable keyboard and interval ranges, compound intervals, and Limited, All,
  or Compact answer buttons. Compact answers use a quality letter and an interval number.

- A searchable glossary in the top toolbar, with notation examples, playback, and related exercise and lesson tiles.
- An interactive Scale Identification reference and lesson, with scale comparisons and note highlighting.
- An optional octave answer in Note Identification, saved window geometry, and Restore defaults in Settings.

- Scale degrees as a note-name group for Note Identification, Keyboard Note Identification and Note Construction, with caret
  notation (1̂–7̂), function names (Tonic, Supertonic, and so on), altered degrees and explicit major-key context.
  Note-name previews have visible text labels.

### Changed
{: .no-toc}

- Alto upgrades the practice database the first time you open this version. Before upgrading, close Alto and copy
  `alto.db` to a backup folder to keep a copy of your previous history.

- Push buttons have a rounded hairline border, a tinted hover state, and a keyboard focus ring. In dark mode,
  exercise tile outlines are near black and other standard button outlines are graphite gray.

- Lesson questions and their feedback appear together in a “Knowledge check” callout.

- Lesson samples and instrument previews play at the same volume as the corresponding exercise notes.
- Playable staff examples in lessons, the glossary, and saved answer cards highlight each note or chord as it sounds.

- Lesson staves keep clefs, signatures, and notes together as the pane widens. Longer examples wrap with their clef and signature.

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
{: .no-toc}

- The documentation homepage shows dark app screenshots in dark mode, and its Keyboard Identification icon matches the other blue topic icons.
- Scale Identification plays with even rhythm on the first correct answer, highlights each note as it sounds, and waits
  for the scale to finish before advancing.

- Switching themes in Settings is faster, and Settings opens more quickly.

## 0.0.1

Released 2026-11-15. [GitHub release](https://github.com/altosaurus/alto/releases/tag/v0.0.1)

### Added
{: .no-toc}

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
{: .no-toc}

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
{: .no-toc}

- Instrument previews keep an even rhythm on first playback by rendering the phrase as one audio clip.
- Changing the theme in the settings no longer sends you back to the exercises home page, or makes the window disappear and grow back
  from a dot. The window stays where it is, showing the exercise, lesson step or page you were on.

## 0.0.0

Released 2026-11-15. [GitHub release](https://github.com/altosaurus/alto/releases/tag/v0.0.0)

The first release.

### Added
{: .no-toc}

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
{% endraw %}
