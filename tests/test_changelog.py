"""
Tests for the changelog and the script that cuts a version's notes out
of it for a GitHub release.
"""

from __future__ import annotations

import importlib.util
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent
LOG = (
    "# Changelog\n\n## [Unreleased]\n\n"
    "## [0.1.0] - 2026-12-01\n\nNotes.\n\n- One.\n\n"
    "## [0.0.0] - 2026-11-15\n\nFirst.\n\n"
    "[0.1.0]: https://example.org/a\n"
)


@pytest.fixture(scope="module")
def changelog() -> ModuleType:
    """
    Load scripts/changelog_section.py as a module, without running it.

    Returns
    -------
    ModuleType
        The loaded module.
    """
    spec = importlib.util.spec_from_file_location(
        "changelog_section",
        ROOT / "scripts" / "changelog_section.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_section_runs_from_its_heading_to_the_next_one(
    changelog: ModuleType,
) -> None:
    """
    Check that a version's notes stop at the next version's heading, and
    leave out their own heading.

    Parameters
    ----------
    changelog : ModuleType
        The script under test.
    """
    assert changelog.section(LOG, version="0.1.0") == "Notes.\n\n- One."
    assert changelog.section(LOG, version="0.0.0") == "First."


def test_last_section_stops_before_link_definitions_close_file(
    changelog: ModuleType,
) -> None:
    """
    Check that link definitions at the end of the file are not taken as
    part of the last version's notes.

    Parameters
    ----------
    changelog : ModuleType
        The script under test.
    """
    log = (
        "## [0.0.0] - 2026-11-15\n\nFirst.\n\n[0.0.0]: https://example.org/a\n"
        "[Unreleased]: https://example.org/b\n"
    )
    assert changelog.section(log, version="0.0.0") == "First."


def test_a_missing_section_is_none_and_an_empty_one_is_an_empty_string(
    changelog: ModuleType,
) -> None:
    """
    Check that no heading and a heading with nothing under it are told
    apart.

    Parameters
    ----------
    changelog : ModuleType
        The script under test.
    """
    assert changelog.section(LOG, version="9.9.9") is None
    assert changelog.section(LOG, version="Unreleased") == ""
    assert changelog.section(LOG, version="0.1") is None  # not a prefix match


def test_the_script_prints_the_notes_and_refuses_a_missing_or_empty_section(
    changelog: ModuleType,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Check the exit codes: 0 with the notes printed for a tag such as
    v0.1.0, and 1 with nothing printed otherwise.

    Parameters
    ----------
    changelog : ModuleType
        The script under test.
    tmp_path : Path
        A scratch folder for a changelog.
    capsys : pytest.CaptureFixture
        Captures what is printed.
    """
    path = tmp_path / "CHANGELOG.md"
    path.write_text(LOG, encoding="utf-8")
    assert changelog.main(["--file", str(path), "v0.1.0"]) == 0
    printed = capsys.readouterr()
    assert printed.out == "Notes.\n\n- One.\n" and printed.err == ""
    for version in ("9.9.9", "Unreleased"):
        assert changelog.main(["--file", str(path), version]) == 1
        refused = capsys.readouterr()
        assert refused.out == "" and version in refused.err
    assert (
        changelog.main(["--file", str(tmp_path / "missing.md"), "0.1.0"]) == 1
    )
    assert "Could not read" in capsys.readouterr().err


def test_the_changelog_has_notes_for_the_version_in_pyproject() -> None:
    """
    Check that the version the package declares has notes in
    CHANGELOG.md, so a release cannot go out without them.
    """
    declared = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
    )["project"]["version"]
    spec = importlib.util.spec_from_file_location(
        "changelog_section",
        ROOT / "scripts" / "changelog_section.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    notes = module.section(
        (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"),
        version=declared,
    )
    assert notes, f"CHANGELOG.md has no notes for {declared}"


def test_the_changelog_keeps_an_unreleased_section_above_the_versions() -> (
    None
):
    """
    Check that the Unreleased heading is there, and comes before the
    first version, ready for the next change.
    """
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert text.index("## [Unreleased]") < text.index("## [0.0.0]")
