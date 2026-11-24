"""
Setup for the doctests in alto/: a Qt application for examples that make
widgets, and settings kept away from the real ones.
"""

import atexit
import gc
import os
import shutil
import tempfile

# Examples that save a setting must not touch the real ones, even if
# only `pytest alto` runs and tests/conftest.py is not loaded.
_HOME = tempfile.mkdtemp(prefix="alto-doctests-")
os.environ["XDG_CONFIG_HOME"] = f"{_HOME}/config"
os.environ["XDG_DATA_HOME"] = f"{_HOME}/data"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
atexit.register(lambda: shutil.rmtree(_HOME, ignore_errors=True))

from collections.abc import Iterator  # noqa: E402

import pytest  # noqa: E402
from PySide6.QtCore import QEvent  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from alto.audio import sounds  # noqa: E402


@pytest.fixture(autouse=True)
def _qt_application_for_doctests(
    request: pytest.FixtureRequest,
    *,
    doctest_namespace: dict,
) -> Iterator[None]:
    """
    Give every doctest a Qt application and mute its example playback.

    Parameters
    ----------
    request : pytest.FixtureRequest
        The running test, used to tell doctests from ordinary tests.
    doctest_namespace : dict
        The names every doctest can use without importing them.
        Keyword-only.

    Yields
    ------
    None
        Control, while the doctest runs. Afterwards every window it left
        open is closed, so they do not pile up: Qt restyles
        every live widget when a theme is applied, and a thousand
        examples' worth made the theme examples take minutes.

    Examples
    --------
    >>> from PySide6.QtWidgets import QApplication
    >>> # the application `app` that every doctest can use
    >>> QApplication.instance() is not None
    True
    """
    if type(request.node).__name__ != "DoctestItem":
        yield
        return

    doctest_namespace["app"] = QApplication.instance() or QApplication([])
    was_enabled = sounds.enabled
    sounds.enabled = False
    try:
        yield
    finally:
        sounds.enabled = was_enabled
        _delete_every_widget()


def _delete_every_widget() -> None:
    """
    Close and delete every top-level widget, then let Qt carry out the
    deletions.
    """
    if QApplication.instance() is None:
        return
    for widget in QApplication.topLevelWidgets():
        widget.close()
        widget.deleteLater()
    QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def pytest_sessionfinish() -> None:
    """
    Delete every widget the run left behind, while Python and Qt are
    both still running.

    Examples make widgets they never close. Left to the interpreter's
    exit, PySide destroys them in an order that aborts the
    process after every test has passed, which fails the pre-push hook.

    Examples
    --------
    >>> callable(pytest_sessionfinish)
    True
    """
    _delete_every_widget()
    gc.collect()
