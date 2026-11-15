"""
Tests for the window that updates a packaged copy: progress, the word that Alto will restart, failures, and cancelling.

The real worker thread runs against a local web server that plays GitHub, with keys made for the test, so the download and the
checks are the real ones. Nothing here goes online or starts an installer.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
)

from alto import (
    selfupdate,
    updates,
)
from alto.selfupdate import Target
from alto.ui.package_update import (
    READY,
    PackageUpdateDialog,
    UpdatePreparer,
)
from alto.updates import Release
from releases import (
    VERSION,
    Keys,
    Server,
    linux_package,
    publish,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

NAME = f"alto-{VERSION}-linux-x86_64.tar.gz"


class Window:
    """
    Runs the window the way a test needs: waits for the worker, records what was shown, and then does what a person would.

    Attributes
    ----------
    keys : Keys
        The key pair the release is signed with, and trusted.
    server : Server
        The local server.
    seen : list of tuple
        What the window said and showed when the work had ended, as (status, button text, bar maximum, bar value).
    action : str
        What the person does: "press" the button once the work has ended, "close" the window instead, or "cancel" at once, before
        the work has ended.
    """

    def __init__(
        self,
        monkeypatch: pytest.MonkeyPatch,
        server: Server,
        keys: Keys,
    ) -> None:
        """
        Point the updater at the local server and trust the test's key.

        Parameters
        ----------
        monkeypatch : pytest.MonkeyPatch
            Replaces the address, the keys, the processor and `exec`.
        server : Server
            The local server.
        keys : Keys
            The test's key pair.
        """
        self.keys, self.server = keys, server
        self.seen: list[tuple[str, str, int, int]] = []
        self.action = "press"
        monkeypatch.setattr(updates, "DOWNLOAD_BASE", server.base)
        monkeypatch.setattr(updates, "UPDATE_PUBLIC_KEYS", (keys.public,))
        monkeypatch.setattr("platform.machine", lambda: "x86_64")
        monkeypatch.setattr(QDialog, "exec", lambda dialog: self._exec(dialog))

    def _exec(self, dialog: QDialog) -> int:
        """
        Stand in for showing the dialog until it is done.

        Parameters
        ----------
        dialog : QDialog
            The dialog.

        Returns
        -------
        int
            How it ended.
        """
        assert isinstance(dialog, PackageUpdateDialog)
        if self.action == "cancel":
            dialog.button.click()  # while the work is going on, so that the button is still Cancel
            return int(dialog.result())
        for _ in range(500):
            if dialog.ended:
                break
            QTest.qWait(20)
        self.seen.append((dialog.status.text(), dialog.button.text(), dialog.bar.maximum(), dialog.bar.value()))
        if self.action == "press":
            dialog.button.click()
        else:
            dialog.reject()
        return int(dialog.result())

    @staticmethod
    def run(
        release: Release,
        tmp_path: Path,
    ) -> tuple[PackageUpdateDialog, selfupdate.Prepared | None]:
        """
        Open the window for a release and run it.

        Parameters
        ----------
        release : Release
            The release.
        tmp_path : Path
            A new folder, where the program is said to be installed.

        Returns
        -------
        tuple of PackageUpdateDialog and Prepared or None
            The window, and what it gave back.
        """
        dialog = PackageUpdateDialog(None, release=release, target=Target("linux", folder=tmp_path, prefix=tmp_path))
        return dialog, dialog.run()


@pytest.fixture
def window(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Window]:
    """
    Provide a window runner with a local server and a key pair.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces the address, the keys and `exec`.

    Yields
    ------
    Window
        The runner.
    """
    with Server() as server:
        yield Window(monkeypatch, server, Keys())


def wait_until_gone(folder: Path) -> bool:
    """
    Wait, at most five seconds, for a folder to be removed, which the worker thread may still be doing.

    Parameters
    ----------
    folder : Path
        The folder.

    Returns
    -------
    bool
        True if it is gone.
    """
    for _ in range(100):
        if not folder.exists():
            return True
        time.sleep(0.05)
    return not folder.exists()


def test_a_good_release_is_checked_and_then_the_window_says_alto_will_restart(window: Window, tmp_path: Path) -> None:
    """
    Check the whole path through the real thread: the window ends ready, says so, offers OK, and gives back the unpacked update.

    Parameters
    ----------
    window : Window
        The runner.
    tmp_path : Path
        A new folder.
    """
    release = publish(window.server, keys=window.keys, package=linux_package(), name=NAME)
    dialog, prepared = window.run(release, tmp_path)
    status, button, maximum, value = window.seen[0]
    assert status == READY and "Alto will close, install it and open again when you press OK" in status
    assert button == "OK" and (maximum, value) == (1, 1)  # a bar that is full
    assert dialog.ready and dialog.error == "" and not dialog.cancelled
    assert prepared is not None and prepared.root is not None and (prepared.root / "install.sh").is_file()
    assert prepared.work.is_dir()  # kept for the hand-over, which removes it


def test_a_release_that_does_not_check_out_ends_in_the_reason_and_leaves_nothing_behind(window: Window, tmp_path: Path) -> None:
    """
    Check that a signature that does not verify is shown, with Close, that nothing is given back, and that the folder is gone.

    Parameters
    ----------
    window : Window
        The runner.
    tmp_path : Path
        A new folder.
    """
    release = publish(window.server, keys=window.keys, package=linux_package(), name=NAME, sign_with=Keys())
    dialog, prepared = window.run(release, tmp_path)
    status, button, _, value = window.seen[0]
    assert "signature of this update is not valid" in status and "Nothing was installed" in status
    assert button == "Close" and value == 0
    assert prepared is None and not dialog.ready and "not valid" in dialog.error
    assert dialog._work is not None and wait_until_gone(dialog._work)


def test_a_file_that_cannot_be_fetched_ends_in_the_reason(window: Window, tmp_path: Path) -> None:
    """
    Check that a release with a file missing from the server says so, and installs nothing.

    Parameters
    ----------
    window : Window
        The runner.
    tmp_path : Path
        A new folder.
    """
    release = publish(window.server, keys=window.keys, package=linux_package(), name=NAME)
    del window.server.files[f"/releases/download/v{VERSION}/{NAME}"]  # the signed list is there, the package is not
    dialog, prepared = window.run(release, tmp_path)
    assert prepared is None and "download failed" in dialog.error and window.seen[0][1] == "Close"


def test_cancelling_while_it_works_stops_the_update_and_removes_what_was_downloaded(window: Window, tmp_path: Path) -> None:
    """
    Check that pressing Cancel while the work goes on gives back nothing, marks the window cancelled, and clears the folder.

    Parameters
    ----------
    window : Window
        The runner.
    tmp_path : Path
        A new folder.
    """
    release = publish(window.server, keys=window.keys, package=linux_package(), name=NAME)
    window.action = "cancel"
    dialog, prepared = window.run(release, tmp_path)
    assert prepared is None and dialog.cancelled and dialog.ended and dialog.preparer.is_cancelled() and not dialog.ready
    assert dialog._work is not None and wait_until_gone(dialog._work)


def test_closing_the_window_after_it_is_ready_throws_the_update_away(window: Window, tmp_path: Path) -> None:
    """
    Check that closing the window, rather than pressing OK, installs nothing and removes the download.

    Parameters
    ----------
    window : Window
        The runner.
    tmp_path : Path
        A new folder.
    """
    release = publish(window.server, keys=window.keys, package=linux_package(), name=NAME)
    window.action = "close"
    dialog, prepared = window.run(release, tmp_path)
    assert dialog.ready and prepared is None
    assert dialog._work is not None and wait_until_gone(dialog._work)


def test_the_download_shows_how_much_has_arrived(app: QApplication) -> None:
    """
    Check that progress turns the bar into a measure and the text into megabytes, and that an unknown total changes nothing.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    here = Target("linux", folder=Path("/x"), prefix=None)
    dialog = PackageUpdateDialog(None, release=Release("0.1.0", tag="v0.1.0", url=""), target=here)
    megabyte = 1_048_576
    dialog._progressed(5 * megabyte, 10 * megabyte)
    assert dialog.status.text() == "Downloading… 5 of 10 MB"
    assert (dialog.bar.maximum(), dialog.bar.value()) == (10 * megabyte, 5 * megabyte)
    dialog._progressed(7, 0)  # the server did not say how large it is
    assert (dialog.bar.maximum(), dialog.bar.value()) == (10 * megabyte, 5 * megabyte)


def test_the_preparer_reports_through_signals_and_stays_quiet_when_cancelled(window: Window, tmp_path: Path) -> None:
    """
    Check the thread's signals: the steps and the end for a good release, and no end at all if it was cancelled first.

    Parameters
    ----------
    window : Window
        The runner.
    tmp_path : Path
        A new folder.
    """
    release = publish(window.server, keys=window.keys, package=linux_package(), name=NAME)
    preparer = UpdatePreparer()
    steps: list[str] = []
    ends: list[tuple[int, str]] = []
    preparer.status.connect(steps.append)
    preparer.done.connect(lambda code, message: ends.append((code, message)))
    work = tmp_path / "work"
    work.mkdir()
    preparer.start(
        release=release,
        target=Target("linux", folder=tmp_path, prefix=tmp_path),
        work=work,
        keys=(window.keys.public,),
    )
    for _ in range(500):
        if ends:
            break
        QTest.qWait(20)
    assert ends == [(0, "")] and steps[0] == "Checking the signature…" and steps[-1] == "Unpacking…"
    assert preparer.prepared is not None
    quiet = UpdatePreparer()
    quiet_ends: list[tuple[int, str]] = []
    quiet.done.connect(lambda code, message: quiet_ends.append((code, message)))
    quiet.cancel()
    quiet._say(0, message="")
    quiet._say(1, message="x")
    assert quiet_ends == [] and quiet.is_cancelled()
