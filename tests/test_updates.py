"""
Tests for what decides whether an installed Alto can update itself, and for the commands that check and update.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from alto import updates
from alto.updates import (
    NOT_BY_SCRIPT,
    SOURCE_FOLDER,
    Source,
    check_command,
    find_program,
    installed_source,
    is_tool_install,
    parse_direct_url,
    parse_ls_remote,
    short,
    updatable,
    upgrade_command,
)

COMMIT = "b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe"
URL = "https://github.com/altosaurus/alto.git"
GIT_INSTALL = json.dumps({"url": URL, "vcs_info": {"vcs": "git", "commit_id": COMMIT}})


def test_a_commit_is_shortened_to_seven_characters() -> None:
    """Check that a full commit id is cut to the seven characters people use."""
    assert short(COMMIT) == "b6e2091"
    assert short("abc") == "abc"


def test_a_git_install_records_its_address_commit_and_ref() -> None:
    """Check that the file the installer leaves is read, with the default branch unless the install named one."""
    assert parse_direct_url(GIT_INSTALL) == Source(URL, commit=COMMIT, ref="HEAD")
    named = json.dumps({"url": URL, "vcs_info": {"vcs": "git", "commit_id": COMMIT, "requested_revision": "dev"}})
    found = parse_direct_url(named)
    assert found is not None and found.ref == "dev"


@pytest.mark.parametrize(
    "text",
    [
        json.dumps({"url": "file:///home/me/alto", "dir_info": {"editable": True}}),
        json.dumps({"url": URL, "vcs_info": {"vcs": "hg", "commit_id": COMMIT}}),
        json.dumps({"url": URL, "vcs_info": {"vcs": "git"}}),
        json.dumps({"vcs_info": {"vcs": "git", "commit_id": COMMIT}}),
        "[]",
        "null",
        "{}",
        "not json at all",
        "",
    ],
)
def test_anything_that_is_not_a_git_install_has_no_source(text: str) -> None:
    """
    Check that a source folder, another kind of repository and unreadable files are all read as having no git source.

    Parameters
    ----------
    text : str
        The contents of a `direct_url.json`.
    """
    assert parse_direct_url(text) is None


class FakeDistribution:
    """Stands in for the installed package's record, holding one `direct_url.json` or none."""

    def __init__(self, text: str | None) -> None:
        """
        Hold the file's text.

        Parameters
        ----------
        text : str or None
            The contents of the file, or None if the package has no such file.
        """
        self.text = text

    def read_text(self, filename: str) -> str | None:
        """
        Give the file's text.

        Parameters
        ----------
        filename : str
            The name asked for; only `direct_url.json` is kept.

        Returns
        -------
        str or None
            The text.
        """
        return self.text if filename == "direct_url.json" else None


def test_the_installed_package_is_asked_where_it_came_from(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that the running copy's source comes from its package record, and that a missing record means no source.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces the package lookup.
    """
    monkeypatch.setattr(updates.metadata, "distribution", lambda _name: FakeDistribution(GIT_INSTALL))
    assert installed_source() == Source(URL, commit=COMMIT)
    monkeypatch.setattr(updates.metadata, "distribution", lambda _name: FakeDistribution(None))
    assert installed_source() is None


def test_a_copy_installed_by_uv_has_its_receipt_in_its_environment(tmp_path: Path) -> None:
    """
    Check that an environment made by `uv tool` is told apart by the receipt it keeps.

    Parameters
    ----------
    tmp_path : Path
        A new folder standing in for the environment.
    """
    assert not is_tool_install(prefix=tmp_path)
    (tmp_path / "uv-receipt.toml").write_text("[tool]\n")
    assert is_tool_install(prefix=tmp_path)


def test_only_a_git_install_made_by_the_script_can_update_itself() -> None:
    """Check that a copy updates itself only with a git source and a `uv tool` environment, and is told why not otherwise."""
    here = Source(URL, commit=COMMIT)
    assert updatable(here, tool=True) is here
    assert updatable(None, tool=True) == SOURCE_FOLDER
    assert updatable(None, tool=False) == SOURCE_FOLDER
    assert updatable(here, tool=False) == NOT_BY_SCRIPT


def test_a_program_is_found_on_the_path_or_where_the_installers_put_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check that `find_program` uses the search path first and then the folders that the installers use.

    Parameters
    ----------
    tmp_path : Path
        A new folder, used as the home folder and as a folder on the path.
    monkeypatch : pytest.MonkeyPatch
        Sets the search path for the length of the test.
    """
    monkeypatch.setenv("PATH", "")
    assert find_program("uv", home=tmp_path) is None
    local = tmp_path / ".local" / "bin"
    local.mkdir(parents=True)
    (local / "uv").write_text("#!/bin/sh\n")
    assert find_program("uv", home=tmp_path) is None  # present but not something that can be run
    os.chmod(local / "uv", 0o755)
    assert find_program("uv", home=tmp_path) == str(local / "uv")
    on_path = tmp_path / "bin"
    on_path.mkdir()
    (on_path / "git").write_text("#!/bin/sh\n")
    os.chmod(on_path / "git", 0o755)
    monkeypatch.setenv("PATH", str(on_path))
    assert find_program("git", home=tmp_path) == str(on_path / "git")


def test_the_two_commands_name_the_address_and_the_tool() -> None:
    """Check that the check asks the install's own address and ref, and that the update upgrades the `alto` tool."""
    source = Source(URL, commit=COMMIT, ref="dev")
    assert check_command(source, git="/usr/bin/git") == ("/usr/bin/git", ["ls-remote", URL, "dev"])
    assert upgrade_command(uv="/usr/bin/uv") == ("/usr/bin/uv", ["tool", "upgrade", "alto"])


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (f"{COMMIT}\tHEAD\n", COMMIT),
        (f"{COMMIT}\trefs/heads/main\n{'a' * 40}\trefs/heads/other\n", COMMIT),
        ("", None),
        ("\n", None),
        ("fatal: repository 'https://example.org/' not found\n", None),
        ("b6e2091\tHEAD\n", None),
        (f"{'G' * 40}\tHEAD\n", None),
    ],
)
def test_the_commit_is_read_from_what_ls_remote_prints(text: str, expected: str | None) -> None:
    """
    Check that the first line's commit id is read, and that an error or an empty answer gives none.

    Parameters
    ----------
    text : str
        What `git ls-remote` printed.
    expected : str or None
        The commit id that should be read.
    """
    assert parse_ls_remote(text) == expected
