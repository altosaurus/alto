# <img src="docs/assets/img/icon.png" alt="" width="44" height="44" align="absmiddle"> Alto

[![Tests](https://github.com/altosaurus/alto/actions/workflows/tests.yml/badge.svg)](https://github.com/altosaurus/alto/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/altosaurus/alto/graph/badge.svg)](https://codecov.io/gh/altosaurus/alto)
[![Pyright](https://github.com/altosaurus/alto/actions/workflows/pyright.yml/badge.svg)](https://github.com/altosaurus/alto/actions/workflows/pyright.yml)
[![License: MIT](https://img.shields.io/github/license/altosaurus/alto)](LICENSE)
[![Docs](https://img.shields.io/github/actions/workflow/status/altosaurus/alto/docs.yml?branch=main&label=docs)](https://altosaurus.github.io/alto/)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14%20%7C%203.15-blue)](https://github.com/altosaurus/alto/blob/main/.github/workflows/tests.yml)

**Music theory practice for the Linux desktop that remembers what you get wrong.**

Alto is a free music theory trainer. Read notes on any clef, name intervals, chords and arpeggios, spell scales, learn key
signatures, find keys on a keyboard. It uses spaced repetition to optimize the learning process by feeding you problems that you find more challenging, and skipping over ones that are already easy.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/img/circle-of-fifths-dark.png">
    <img src="docs/assets/img/circle-of-fifths.png" alt="Alto's Circle of Fifths exercise, with the list of exercises open on the left" width="760">
  </picture>
</p>

## Make it yours

Almost everything is adjustable.

- **Notation in the font you like.** Eleven music fonts, from the polished look of Finale Maestro, Leland and Bravura to
  handwritten jazz styles. Every staff in the app follows your choice.
- **Light, dark or follow your desktop.** The theme switches instantly.
- **Practise exactly what you need.** Choose the clefs (the grand staff, treble, bass, alto, tenor, soprano, mezzo-soprano or baritone), the range of
  notes, the key signatures, the note values from the breve to the thirty-second note, letter or solfège names, and
  whether sharps, flats and naturals appear.
- **Choose the sound.** Pick the instrument that plays your answers.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/img/settings-dark.png">
    <img src="docs/assets/img/settings.png" alt="Alto's settings, with a preview of each notation font" width="760">
  </picture>
</p>

## It remembers what you get wrong

Every answer goes into a local database under your profile. Alto scores each question by how hard you find it:

- **Wrong answers count against it.** Every extra attempt pushes the question higher, so it returns more often.
- **Speed counts too.** A slow answer is held against a question, even when it is right. A very quick one earns it a
  rest.
- **Your progress is visible.** Charts show your accuracy, speed and volume over time, a calendar heatmap shows a year of
  practice at a glance, all filtered by exercise, and a read-only browser lets you look at everything stored.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/img/stats-dark.png">
    <img src="docs/assets/img/stats.png" alt="Alto's statistics page with accuracy, speed and volume charts" width="760">
  </picture>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/img/stats-heatmap-dark.png">
    <img src="docs/assets/img/stats-heatmap.png" alt="Alto's review heatmap: a year of practice, a square per day" width="760">
  </picture>
</p>

## Free and open source

Alto is released under the [MIT License](LICENSE). There are no accounts and no tracking.
Your history is one SQLite file on your computer that you can back up, move or open with any SQLite tool. The bundled
music fonts and recordings all come with their licences, listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Built for Linux

Linux is Alto's main platform. It is developed and tested there, follows your desktop's light or dark setting, and keeps
its files in the usual places (`~/.local/share/Alto` and `~/.config/alto`). It is a native Qt application, not a web
page in a wrapper. There is also a Windows installer, which is built and checked automatically but has had much less testing than
the Linux version. Alto may run on macOS too, but there is no package for it and it is not tested.

## Download

Each release on the [Releases page](https://github.com/altosaurus/alto/releases) has a Linux download and a Windows installer. They
carry their own Python and Qt, so nothing else needs installing. See
[Getting started](https://altosaurus.github.io/alto/latest/getting-started/) for how to install, update and uninstall them.

## Get started from the source

You need Python 3.11 or newer.

```bash
git clone https://github.com/altosaurus/alto.git
cd alto
python -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m alto
```

The first time it opens, Alto asks you to create a profile. There is no password.

## Documentation

Guides for every exercise, how the practice scheduling works, the statistics, settings and shortcuts are in
[`docs/`](docs/) and published at https://altosaurus.github.io/alto/, with a version for each release and one for the development docs.

## Development

```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/pre-commit install     # whitespace and Ruff checks on commit, tests on push
.venv/bin/pytest
.venv/bin/ruff check alto tests
```

The theory, exercises and learning code have no Qt dependency, so they can be tested without a display. See the
[developer guide](docs/guide/index.md) for how the program works, and [For developers](docs/development.md) for commands and
recipes such as adding an exercise or a notation font.

## License

[MIT](LICENSE). The bundled fonts and recordings keep their authors' licences; see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
