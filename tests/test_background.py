"""Check work run in the background reports back on the window's thread, and not at all once its owner is gone."""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject

from alto.ui.background import run_in_background

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


def test_the_outcome_arrives_on_the_thread_that_asked(app: QApplication) -> None:
    """
    Call `done` on the thread that started the work, not on the worker.

    Parameters
    ----------
    app : QApplication
        Runs the events that deliver the outcome.
    """
    owner = QObject()
    threads: list[threading.Thread] = []
    run_in_background(lambda: 1, owner=owner, done=lambda _: threads.append(threading.current_thread()), failed=print)
    deadline = time.monotonic() + 5
    while not threads and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)
    assert threads == [threading.main_thread()]


def test_nothing_is_reported_once_the_owner_is_deleted(app: QApplication) -> None:
    """
    Drop the outcome of work whose owner, such as a closed dialog, was deleted while it ran.

    Parameters
    ----------
    app : QApplication
        Runs any events that would deliver the outcome.
    """
    owner = QObject()
    release = threading.Event()
    heard: list[object] = []
    thread = run_in_background(release.wait, owner=owner, done=heard.append, failed=heard.append)
    del owner  # the owner, and the relay it owns, are deleted with their last reference
    release.set()
    thread.join(timeout=5)
    app.processEvents()
    assert not thread.is_alive()
    assert heard == []
