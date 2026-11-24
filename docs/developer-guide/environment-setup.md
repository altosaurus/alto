---
title: Development environment
parent: developer-guide
order: 0
permalink: /developer-guide/environment-setup/
---
Use uv to create a Python environment for your checkout of Alto. It installs Alto in editable mode, so the next time you run it, your Python changes take effect.

## Source checkout

You’ll need Git and uv. If you’re installing uv for the first time, follow the instructions for your operating system, then open a new terminal and run `uv --version`. [uv installation instructions](https://docs.astral.sh/uv/getting-started/installation/)

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
