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

## Adding an exercise

Subclass `Exercise` in `alto/exercises/library.py`, decorate it with `@register`, and implement `generate`, which returns a
`Question`:

```python
@register
class MyExercise(Exercise):
    name = "My exercise"
    category = "Intervals"
    description = "One line shown on the home screen."
    par_seconds = 5.0  # a good first-answer time; see How practice adapts

    def generate(self, rng):
        ...
        return Question("What is this?", choices, answer, staff=[[note]], clef="treble")
```

- `Question` describes everything the screen needs: a prompt, the answer buttons, the notes to draw, a key signature, a keyboard key to highlight, and so on.
- If your exercise reads user settings, override `settings_signature()` and return `signature(...)` of those settings. Stored questions are only replayed while the signature is unchanged.
- Give the exercise an icon in `alto/ui/home.py` so it appears properly on the home screen.
- Pick its `category` from the existing ones, or make a new one. `@register` places the exercise next to the others of its category, so the home screen and the exercise list show each category once, whatever order the classes are written in.

Everything else comes with it: the question is recorded in the database, scored for speed, drawn in the chosen
notation font and included in the statistics.

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
