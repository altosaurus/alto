"""Tests for the choice of tests by `scripts/changed_tests.py` and for the workflows that use it."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"


def load() -> ModuleType:
    """
    Load `scripts/changed_tests.py` as a module, without running it.

    Returns
    -------
    ModuleType
        The loaded module.
    """
    spec = importlib.util.spec_from_file_location("changed_tests", ROOT / "scripts" / "changed_tests.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_change_to_the_docs_alone_runs_the_tests_that_read_the_docs_and_no_others() -> None:
    """Check that docs and top-level Markdown files select the docs tests, and a nested Markdown file is not docs."""
    script = load()
    assert script.choose(["docs/index.md", "CHANGELOG.md"]) == list(script.DOCS_TESTS)
    assert script.choose(["docs/assets/img/home.png"]) == list(script.DOCS_TESTS)
    assert script.choose(["alto/README.md"]) == "all"  # not part of the docs, and unknown, so everything runs


def test_anything_the_script_does_not_know_runs_everything() -> None:
    """Check that scripts, workflows, packaging, settings and conftest files select the whole suite."""
    script = load()
    for path in [
        "scripts/docs_site.py",
        ".github/workflows/tests.yml",
        "pyproject.toml",
        "packaging/x.spec",
        "tests/conftest.py",
    ]:
        assert script.choose([path]) == "all", path
    assert script.choose(["docs/index.md", "pyproject.toml"]) == "all"
    assert script.choose([]) == []


def test_a_change_to_a_module_runs_the_tests_that_import_it_however_indirectly() -> None:
    """Check that the tests of a module and of the modules built on it are chosen, and the unrelated ones are not."""
    script = load()
    chosen = script.choose(["alto/theory/pitch.py"])
    assert "alto/theory/pitch.py" in chosen and "tests/test_theory.py" in chosen
    assert "tests/test_main_window.py" in chosen  # reaches the theory through the exercises and the screens
    for name in script.WHOLE_CODE_TESTS:
        assert name in chosen  # these read every module or page
    narrow = script.choose(["tests/test_stats.py"])
    assert "tests/test_stats.py" in narrow and "tests/test_theory.py" not in narrow


def test_the_helpers_a_test_imports_by_their_plain_name_count_as_imports() -> None:
    """Check that a change to `tests/keys.py`, imported as `from keys import`, selects the tests that use it."""
    script = load()
    users = [
        path.name
        for path in (ROOT / "tests").glob("test_*.py")
        if re.search(r"^from keys import", path.read_text(), re.MULTILINE)
    ]
    assert users
    chosen = script.choose(["tests/keys.py"])
    for name in users:
        assert f"tests/{name}" in chosen


def test_a_pull_request_runs_two_python_versions_and_a_docs_change_one_while_main_runs_all() -> None:
    """Check that the Tests workflow picks its versions in a scope job, from the kind of change and the event."""
    workflow = (WORKFLOWS / "tests.yml").read_text(encoding="utf-8")
    assert "fromJSON(needs.scope.outputs.versions)" in workflow and "changed_tests.py --kind" in workflow
    assert """versions='["3.11", "3.15"]'""" in workflow and """versions='["3.14"]'""" in workflow
    assert """ALL: '["3.11", "3.12", "3.13", "3.14", "3.15"]'""" in workflow
    assert "fetch-depth: 0" in workflow  # the diff needs the history


def test_every_workflow_that_runs_on_pull_requests_cancels_what_a_new_push_makes_stale_but_never_a_run_on_main() -> None:
    """Check the concurrency rule of the workflows that run on pull requests."""
    for name in ["tests", "pyright", "codecov", "ruff", "package", "docs-check"]:
        workflow = (WORKFLOWS / f"{name}.yml").read_text(encoding="utf-8")
        assert "cancel-in-progress:" in workflow and "github.event.pull_request.number" in workflow, name
        assert "cancel-in-progress: ${{ github.event_name == 'pull_request' }}" in workflow or name == "docs-check", name


def test_the_checks_of_the_code_skip_a_change_to_the_docs_alone() -> None:
    """Check that Pyright, Ruff and Coverage ignore the docs on a pull request, and still run on every push to main."""
    for name in ["pyright", "ruff", "codecov"]:
        workflow = (WORKFLOWS / f"{name}.yml").read_text(encoding="utf-8")
        assert 'paths-ignore:\n      - "docs/**"\n      - "*.md"' in workflow, name
        assert "push:\n    branches: [main]" in workflow, name


def test_the_docs_are_built_on_a_pull_request_that_changes_them_and_nothing_is_published() -> None:
    """Check the Docs check workflow: it builds with Jekyll for the docs paths and has no permission to write."""
    workflow = (WORKFLOWS / "docs-check.yml").read_text(encoding="utf-8")
    assert "pull_request:" in workflow and 'paths:\n      - "docs/**"' in workflow
    assert (
        "jekyll build" in workflow
        and "contents: read" in workflow
        and "gh-pages" not in workflow.replace("the Docs workflow", "")
    )


def test_the_pre_push_hook_runs_what_the_script_chooses_unless_told_to_run_everything() -> None:
    """Check that `scripts/run-tests.sh` asks the script, and that ALTO_TEST_ALL=1 skips the choice."""
    hook = (ROOT / "scripts" / "run-tests.sh").read_text(encoding="utf-8")
    assert "scripts/changed_tests.py" in hook and "ALTO_TEST_ALL" in hook
