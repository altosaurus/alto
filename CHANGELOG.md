# Changelog

All notable changes to Alto are written here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
Alto uses [semantic versioning](https://semver.org/).

## [Unreleased]

## [0.0.0] - 2026-11-15

The first release.

### Added

**Exercises**

- Eleven exercises in four categories:
  - Notation: Note Identification, Keyboard Identification and Note Construction.
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

- 26 colour themes, including light, dark and following the desktop, and a form to make your own.
- 11 notation styles (music fonts), 12 keyboard looks, and 30 transitions between the exercise and lesson cards, including none.
- The Salamander Grand Piano as the default piano, and recordings of a marimba, vibraphone, flute, horn and viola, chosen in Settings.
  The recordings and fonts are used under their own licences, listed in `THIRD_PARTY_NOTICES.md`.

**Your data**

- Export backup… and Import backup… in the menu. A backup is one `.altobackup` file holding every profile, every answer and every
  setting. Importing replaces everything, and a safety copy of what was there is saved first.

**Installing and updating**

- `scripts/alto-install.sh` installs Alto from GitHub into its own environment, adds it to the application menu, updates it and
  removes it. Uninstalling keeps your data unless `--purge` is given.
- Check for updates… in the menu: says whether a newer release is available, offers to install it with its progress shown, and
  restarts Alto when you press OK. A packaged copy is offered the release's download page instead, as it cannot replace itself.
- Settings → Updates shows the version you have, and a choice to follow the main branch instead of releases, for the latest
  changes before they are released.
- A Linux download: a `.tar.gz` with its own Python and Qt, so nothing else needs installing. `sh install.sh install` installs it
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

[Unreleased]: https://github.com/altosaurus/alto/compare/v0.0.0...HEAD
[0.0.0]: https://github.com/altosaurus/alto/releases/tag/v0.0.0
