#!/usr/bin/env python
"""
Classify pull requests for CI and list pytest targets for a local change.

    python scripts/changed_tests.py                    # what the working tree changed since it left origin/main
    python scripts/changed_tests.py --kind             # "skip", "docs", or "code" for pull requests
    python scripts/changed_tests.py --base A --head B  # changes introduced by B since it diverged from A

It prints `all`, or the paths to give to pytest (nothing at all when nothing changed). The rules are meant to be safe, so that a
test is never skipped by mistake, and anything they do not know is a reason to run `all`:

- Repository housekeeping (.gitignore, .git-blame-ignore-revs, and local previews under work/) needs no tests.
- Only docs (anything under `docs/`, and the Markdown files at the top) run the tests that read the docs.
- A change to a module of `alto` or to a test runs the tests that import it, directly or through other modules, and the
  doctests of the modules that import it, plus the tests that read the whole code base or the docs.
- Anything else (a script, a workflow, `pyproject.toml`, a `conftest.py`, the packaging files, a sound or a picture) runs `all`,
  because several tests read those files, and not only through an import.

The script uses nothing but the standard library, so that a workflow can run it before anything is installed.
"""

from __future__ import annotations

import argparse
import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_TESTS = (
    "tests/test_api_docs.py",
    "tests/test_changelog.py",
    "tests/test_docs.py",
    "tests/test_docs_site.py",
    "tests/test_guide_docs.py",
)
WHOLE_CODE_TESTS = (
    *DOCS_TESTS,
    "tests/test_docstrings.py",
)  # these read every module or every page, so any code change reaches them


def paths_affecting_tests(files: list[str]) -> list[str]:
    """
    Remove repository housekeeping paths before selecting tests.

    Parameters
    ----------
    files : list of str
        Changed paths relative to the repository root.

    Returns
    -------
    list of str
        Paths that can affect the tests.

    Examples
    --------
    >>> paths_affecting_tests([".gitignore", "work/preview.html", "docs/index.md"])
    ['docs/index.md']
    """
    return [path for path in files if path not in {".gitignore", ".git-blame-ignore-revs"} and not path.startswith("work/")]


def is_docs(path: str) -> bool:
    """
    Say whether a file is part of the docs: under `docs/`, or a Markdown file at the top of the repository.

    Parameters
    ----------
    path : str
        The path from the top of the repository, with forward slashes.

    Returns
    -------
    bool
        True for a docs file.

    Examples
    --------
    >>> is_docs("docs/index.md"), is_docs("CHANGELOG.md"), is_docs("alto/ui/home.py"), is_docs("alto/README.md")
    (True, True, False, False)
    """
    return path.startswith("docs/") or ("/" not in path and path.endswith(".md"))


def module_name(path: str) -> str | None:
    """
    Name the module that a Python file under `alto/` or `tests/` is, as an import would write it.

    Parameters
    ----------
    path : str
        The path from the top of the repository, with forward slashes.

    Returns
    -------
    str or None
        The dotted name (`alto/ui/home.py` is `alto.ui.home`, and a package's `__init__.py` is the package), or None for a file
        that is neither under `alto/` nor `tests/`.

    Examples
    --------
    >>> module_name("alto/ui/home.py"), module_name("alto/exercises/__init__.py"), module_name("tests/keys.py")
    ('alto.ui.home', 'alto.exercises', 'tests.keys')
    >>> module_name("scripts/docs_site.py") is None
    True
    """
    if not path.endswith(".py") or path.split("/")[0] not in {"alto", "tests"}:
        return None
    parts = path[: -len(".py")].split("/")
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def imports_of(source: str, *, known: set[str]) -> set[str]:
    r"""
    List the modules of the project that a piece of code imports.

    A module also needs the packages above it, so those are listed too, and `from a import b` counts as an import of `a.b` when
    that is a module.

    Parameters
    ----------
    source : str
        The text of a Python file.
    known : set of str
        The names of the project's modules.

    Returns
    -------
    set of str
        The names, among `known`, that the code imports.

    Examples
    --------
    >>> modules = {"alto", "alto.ui", "alto.ui.home", "alto.theory"}
    >>> sorted(imports_of("from alto.ui import home\nimport alto.theory", known=modules))
    ['alto', 'alto.theory', 'alto.ui', 'alto.ui.home']
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names = [node.module, *(f"{node.module}.{alias.name}" for alias in node.names)]
        for name in names:
            parts = name.split(".")
            found.update(".".join(parts[:count]) for count in range(1, len(parts) + 1) if ".".join(parts[:count]) in known)
    return found


def dependents(changed: set[str], *, graph: dict[str, set[str]]) -> set[str]:
    """
    Find the modules that depend, directly or through others, on the changed ones, and the changed ones themselves.

    Parameters
    ----------
    changed : set of str
        The names of the modules that changed.
    graph : dict of str to set of str
        For each module, the modules it imports.

    Returns
    -------
    set of str
        The changed modules and every module that imports one of them, however indirectly.

    Examples
    --------
    >>> edges = {"c": {"b"}, "b": {"a"}, "a": set(), "d": set()}
    >>> sorted(dependents({"a"}, graph=edges))
    ['a', 'b', 'c']
    """
    reached = set(changed)
    grew = True
    while grew:
        grew = False
        for name, imported in graph.items():
            if name not in reached and imported & reached:
                reached.add(name)
                grew = True
    return reached


def choose(files: list[str], *, root: Path = ROOT) -> str | list[str]:
    """
    Choose what to run for a list of changed files.

    Parameters
    ----------
    files : list of str
        The changed paths from the top of the repository, with forward slashes.
    root : Path, default ROOT
        The repository.

    Returns
    -------
    str or list of str
        "all" when the whole suite should run, otherwise the paths to give to pytest, which may be none.

    Examples
    --------
    >>> choose([])
    []
    >>> choose(["docs/index.md"]) == list(DOCS_TESTS)
    True
    >>> choose(["pyproject.toml"])
    'all'
    """
    files = paths_affecting_tests(files)
    if not files:
        return []
    if all(is_docs(path) for path in files):
        return list(DOCS_TESTS)
    code = [path for path in files if not is_docs(path)]
    if any(module_name(path) is None or path.endswith("conftest.py") for path in code):
        return "all"
    paths: dict[str, Path] = {}
    for path in sorted(root.glob("alto/**/*.py")) + sorted(root.glob("tests/**/*.py")):
        name = module_name(path.relative_to(root).as_posix())
        if name:
            paths[name] = path
            if name.startswith("tests."):
                paths[name.removeprefix("tests.")] = (
                    path  # a test imports a helper next to it by its plain name, as `from keys import`
                )
    known = set(paths)
    graph = {name: imports_of(path.read_text(encoding="utf-8"), known=known) for name, path in paths.items()}
    seeds: set[str] = set()
    for path in code:
        name = module_name(path)
        if name:
            seeds.update({name, name.removeprefix("tests.")})  # a helper is imported by its plain name as well
    reached = dependents(seeds, graph=graph)
    chosen: set[str] = set(WHOLE_CODE_TESTS)
    for name in reached:
        path = paths.get(name)
        if path is None:
            continue
        relative = path.relative_to(root).as_posix()
        if relative.startswith("alto/") or Path(relative).name.startswith("test_"):
            chosen.add(relative)
    return sorted(chosen)


def changed_files(*, base: str | None, head: str | None) -> list[str]:
    """
    Ask Git which files changed.

    Parameters
    ----------
    base : str or None
        The commit to compare from; the point where the branch left `origin/main` if None.
    head : str or None
        The commit to compare to; the working tree (what is committed, staged and not yet staged) if None.

    Returns
    -------
    list of str
        The changed paths from the top of the repository, with forward slashes, and the files not yet tracked when `head` is None.

    Examples
    --------
    >>> changed_files(base="HEAD", head="HEAD")
    []
    """
    if base is None:
        base = (
            subprocess.run(
                ["git", "merge-base", "HEAD", "origin/main"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            ).stdout.strip()
            or "HEAD"
        )
    # A PR owns changes since its merge base. Inspect both sides of moves across scope boundaries.
    compare = f"{base}...{head}" if head else base
    command = ["git", "diff", "--no-renames", "--name-only", "-z", compare, "--"]
    files = set(os.fsdecode(subprocess.check_output(command, cwd=ROOT)).split("\0"))
    if head is None:
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        ).stdout
        files.update(os.fsdecode(untracked).split("\0"))
    files.discard("")
    return sorted(files)


def main(argv: list[str] | None = None) -> int:
    """
    Print what to run for the files that changed.

    Parameters
    ----------
    argv : list of str or None, default None
        The arguments after the program's name; those the program was started with if None.

    Returns
    -------
    int
        0.

    Examples
    --------
    >>> main(["--files", "docs/index.md", "--kind"])
    docs
    0
    >>> main(["--files", "alto/ui/home.py", "--kind"])
    code
    0
    """
    parser = argparse.ArgumentParser(description="Choose the tests that a change could affect.")
    parser.add_argument("--base", help="the commit to compare from (default: where the branch left origin/main)")
    parser.add_argument("--head", help="the commit to compare to (default: the working tree)")
    parser.add_argument("--files", nargs="*", help="the changed files, instead of asking Git")
    parser.add_argument(
        "--kind",
        action="store_true",
        help='print the pull request scope: "skip", "docs", or "code"',
    )
    arguments = parser.parse_args(argv)
    files = arguments.files if arguments.files is not None else changed_files(base=arguments.base, head=arguments.head)
    if arguments.kind:
        inputs = paths_affecting_tests(files)
        if not inputs:
            print("skip")
        else:
            print("docs" if all(is_docs(path) for path in inputs) else "code")
        return 0
    chosen = choose(files)
    print(chosen if isinstance(chosen, str) else " ".join(chosen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
