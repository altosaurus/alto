"""
Where Alto keeps its practice history and its settings, and how to keep
them somewhere else with `ALTO_HOME`.

Without `ALTO_HOME` they are in the usual places for the system. With
it, both are in that folder instead, so a copy of Alto
that is being worked on can have its own history and settings, apart
from the copy that is used for practicing.

Examples
--------
>>> database_path(
...     environ={"ALTO_HOME": "/tmp/alto-dev"}
... ).as_posix()
'/tmp/alto-dev/data/alto.db'
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

from PySide6.QtCore import QStandardPaths

HOME_VARIABLE = "ALTO_HOME"


def alto_home(*, environ: Mapping[str, str] = os.environ) -> Path | None:
    """
    Give the folder named by `ALTO_HOME`, if there is one.

    Parameters
    ----------
    environ : mapping of str to str
        The environment to read. Keyword-only.

    Returns
    -------
    Path or None
        The folder, with `~` expanded and made absolute, or None if
        `ALTO_HOME` is not set or is empty.

    Examples
    --------
    >>> alto_home(environ={}) is None
    True
    >>> alto_home(environ={"ALTO_HOME": ""}) is None
    True
    >>> str(
    ...     alto_home(
    ...         environ={
    ...             "ALTO_HOME": "/tmp/alto-dev"
    ...         }
    ...     )
    ... )
    '/tmp/alto-dev'
    >>> alto_home(
    ...     environ={"ALTO_HOME": "~/alto-dev"}
    ... ) == Path.home() / "alto-dev"
    True
    """
    named = environ.get(HOME_VARIABLE, "").strip()
    return Path(named).expanduser().absolute() if named else None


def database_path(*, environ: Mapping[str, str] = os.environ) -> Path:
    """
    Give the file that holds the practice history.

    Parameters
    ----------
    environ : mapping of str to str
        The environment to read. Keyword-only.

    Returns
    -------
    Path
        `data/alto.db` in the `ALTO_HOME` folder if there is one,
        otherwise `alto.db` in the system's data folder for Alto. The
        folder need not exist yet.

    Examples
    --------
    >>> database_path(
    ...     environ={"ALTO_HOME": "/tmp/alto-dev"}
    ... ).as_posix()
    '/tmp/alto-dev/data/alto.db'
    >>> database_path(environ={}).name
    'alto.db'
    """
    home = alto_home(environ=environ)
    if home is not None:
        return home / "data" / "alto.db"
    return (
        Path(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppDataLocation,
            ),
        )
        / "alto.db"
    )


def settings_folder(*, environ: Mapping[str, str] = os.environ) -> Path | None:
    """
    Give the folder that holds the settings when `ALTO_HOME` moves them.

    Parameters
    ----------
    environ : mapping of str to str
        The environment to read. Keyword-only.

    Returns
    -------
    Path or None
        `config` in the `ALTO_HOME` folder, or None if the settings are
        in the system's usual place.

    Examples
    --------
    >>> settings_folder(environ={}) is None
    True
    >>> str(
    ...     settings_folder(
    ...         environ={
    ...             "ALTO_HOME": "/tmp/alto-dev"
    ...         }
    ...     )
    ... )
    '/tmp/alto-dev/config'
    """
    home = alto_home(environ=environ)
    return None if home is None else home / "config"


def desktop_name(*, environ: Mapping[str, str] = os.environ) -> str:
    """
    Give the name the desktop uses to match Alto's window to its menu
    entry, and so to its icon in the dock.

    Parameters
    ----------
    environ : mapping of str to str
        The environment to read. Keyword-only.

    Returns
    -------
    str
        "alto", or "alto-dev" when `ALTO_HOME` keeps a second copy
        apart, so that the two copies are separate in the dock.

    Examples
    --------
    >>> (
    ...     desktop_name(environ={}),
    ...     desktop_name(
    ...         environ={
    ...             "ALTO_HOME": "/tmp/alto-dev"
    ...         }
    ...     ),
    ... )
    ('alto', 'alto-dev')
    """
    return "alto" if alto_home(environ=environ) is None else "alto-dev"
