"""
Tests for where Alto keeps its history and settings, and for `ALTO_HOME`
moving them.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import QSettings

from alto.location import (
    alto_home,
    database_path,
    desktop_name,
    settings_folder,
)
from alto.ui.store import store

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """
    Set `ALTO_HOME` to a new folder for one test, and put the settings
    folder back afterwards.

    Parameters
    ----------
    tmp_path : Path
        A new folder.
    monkeypatch : pytest.MonkeyPatch
        Sets the variable for the length of the test.

    Yields
    ------
    Path
        The folder.
    """
    monkeypatch.setenv("ALTO_HOME", str(tmp_path / "dev"))
    yield tmp_path / "dev"
    QSettings.setPath(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        os.environ["XDG_CONFIG_HOME"],
    )


def test_without_alto_home_everything_is_in_the_usual_places(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that with no `ALTO_HOME` there is no folder of its own and the
    database is the system's `alto.db`.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Removes the variable for the length of the test.
    """
    monkeypatch.delenv("ALTO_HOME", raising=False)
    assert alto_home() is None and settings_folder() is None
    assert database_path().name == "alto.db"


def test_alto_home_holds_the_database_and_the_settings(home: Path) -> None:
    """
    Check that `ALTO_HOME` gives a `data` folder for the database and a
    `config` folder for the settings.

    Parameters
    ----------
    home : Path
        The folder `ALTO_HOME` names.
    """
    assert alto_home() == home
    assert database_path() == home / "data" / "alto.db"
    assert settings_folder() == home / "config"


def test_a_home_with_a_tilde_is_expanded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that `~` in `ALTO_HOME` means the user's home folder.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Sets the variable for the length of the test.
    """
    monkeypatch.setenv("ALTO_HOME", "~/alto-dev")
    assert alto_home() == Path.home() / "alto-dev"


def test_settings_saved_with_alto_home_go_there_and_not_to_the_usual_place(
    home: Path,
) -> None:
    """
    Check that a setting saved while `ALTO_HOME` is set lands in its
    folder, and that the usual settings do not see it.

    Parameters
    ----------
    home : Path
        The folder `ALTO_HOME` names.
    """
    settings = store()
    settings.setValue("demo/where", "dev")
    settings.sync()
    assert (
        Path(settings.fileName()).is_relative_to(home / "config")
        and Path(settings.fileName()).is_file()
    )
    assert QSettings("alto", "alto").value("demo/where") is None


def test_a_copy_kept_apart_has_its_own_name_for_the_desktop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the desktop name, which decides the icon and the grouping
    in the dock, differs when `ALTO_HOME` is set.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Sets and removes the variable for the length of the test.
    """
    monkeypatch.delenv("ALTO_HOME", raising=False)
    assert desktop_name() == "alto"
    monkeypatch.setenv("ALTO_HOME", "/tmp/alto-dev")
    assert desktop_name() == "alto-dev"
