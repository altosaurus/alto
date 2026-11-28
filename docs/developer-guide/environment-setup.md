---
title: Development environment
parent: developer-guide
order: 0
permalink: /developer-guide/environment-setup/
---
Use uv to create a Python environment for your checkout of Alto. It installs Alto in editable mode, so the next time you run it, your Python changes take effect.

## Source checkout

You’ll need Git to clone the repository and uv to manage the Python environment. After installing them, open a new terminal and run `git --version` and `uv --version` to check that both are available. [Install Git](https://git-scm.com/install/) · [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

Clone Alto and enter the repository. If you already have a checkout, open a terminal in the folder that contains `pyproject.toml`.

```sh
git clone https://github.com/altosaurus/alto.git
cd alto
```

## Project environment

From the repository root, create `.venv` and install Alto with its development tools, including pytest, Ruff, and pre-commit.

```sh
uv sync --locked --extra dev --python 3.14
```

Alto requires Python 3.11 or newer. This command uses Python 3.14 and lets uv download it if needed. The `--locked` flag checks that `uv.lock` matches `pyproject.toml` and installs the recorded versions. Run the same command after pulling dependency changes.

## Shell activation

Activate the environment so that `python` and the developer tools in this terminal use Alto’s `.venv`. Repeat this step when you open a new terminal.

**Linux or macOS (Bash or Zsh)**

```sh
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
```

## Setup check

Print Alto’s version and run the music theory tests. The first command prints `Alto` followed by its version and exits. The second should report passing tests.

```sh
python -m alto --version
python -m pytest -q tests/test_theory.py
```

If you’ll be contributing changes, run `pre-commit install` once in this checkout to enable the repository’s Git hooks. Keep the environment active for the [Application launch walkthrough]({{ '/developer-guide/application-launch/' | relative_url }}).

## Dependencies

The `uv sync` command above installs the application libraries and the `dev` tools. Alto declares its direct Python dependencies and supported versions in `pyproject.toml`. The lockfile records the exact versions for each supported environment.

### Application libraries

| Package | Use in Alto |
| --- | --- |
| PySide6 | Provides the Qt windows and controls, draws notation, and plays exercise audio. |
| fsrs | Schedules the next review of a practice item based on the learner’s ratings. |
| genanki | Writes Anki decks so learners can export exercises as `.apkg` files. |
| certifi | Supplies trusted certificates for HTTPS connections to Alto’s update server. |
| PyNaCl | Verifies the digital signature on a release’s checksum list before Alto installs an update. |

### Development tools

| Package | Use in Alto |
| --- | --- |
| pytest | Runs the test suite, including executable examples in docstrings. |
| Hypothesis | Generates note selections and seeds for Beat Construction tests and reduces failures to reproducible examples. |
| pytest-xdist | Runs tests across multiple worker processes to shorten the suite’s runtime. |
| pytest-cov | Measures which lines of code the tests execute. |
| diff-cover | Checks test coverage on lines changed by a patch. |
| Ruff | Formats Python and flags lint issues. |
| Pylint | Detects duplicated code across application modules. |
| Pyright | Checks Python type annotations and reports type errors. |
| pre-commit | Runs repository checks through Git hooks. |
| asv | Benchmarks performance across revisions. |
| NumPy | Supports image and audio checks in tests and helps map notes to clickable regions in score excerpts. |

### Build tools

Setuptools builds Alto as a Python package, including the editable installation used during development. The `package` extra adds PyInstaller to bundle desktop releases. The Windows and macOS build scripts also use Pillow to convert Alto’s PNG icon to the platform’s icon format.

For documentation work, uv installs the locked `docs` dependency group. Sphinx builds the HTML and search index, MyST parses the Markdown guides, and AutoAPI reads Python signatures and docstrings. Python Liquid renders the shared figures and download links. [Building the docs]({{ '/development/' | relative_url }}#building-the-docs)
