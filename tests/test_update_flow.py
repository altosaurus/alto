"""
Tests for the menu's "Check for updates…": what is asked, what is shown while it works, and when Alto restarts.

No test goes online or runs `git` or `uv`: both are replaced by Python one-liners that print what the real ones would.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
)

from alto import updates
from alto.ui import update_flow as flow
from alto.ui.main_window import MainWindow
from alto.ui.update_flow import (
    CheckDialog,
    CommandRunner,
    UpdateDialog,
    brief,
)
from alto.updates import Source

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

INSTALLED = "b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe"
LATEST = "c0ffee0123456789abcdef0123456789abcdef01"
YES, NO = QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No
SLEEPS = "import time; time.sleep(30)"


def says_commit(commit: str) -> str:
    """
    Give a Python program that prints what `git ls-remote` prints for a commit.

    Parameters
    ----------
    commit : str
        The commit id.

    Returns
    -------
    str
        The program's source.
    """
    return f"print({commit!r} + chr(9) + 'HEAD')"


class Fakes:
    """
    Stands in for everything the update flow reaches outside itself: what is installed, what is online, programs and dialogs.

    Attributes
    ----------
    installed : Source or None
        Where the running copy came from; None for a copy run from a source folder.
    tool : bool
        Whether the running copy is a `uv tool` install.
    programs : dict of str to str or None
        The path each program is found at, or None if it is missing.
    check_script : str
        The Python program that stands in for `git ls-remote`.
    upgrade_script : str
        The Python program that stands in for `uv tool upgrade`.
    answer : QMessageBox.StandardButton
        What the person answers when asked whether to update.
    shown : list of tuple
        Each message box that appeared, as (kind, text).
    ran : list of str
        Which programs were started, in order.
    seen : list of tuple
        What the update window said and showed when it had finished, as (status, button text, log), before OK was pressed.
    restarts : int
        How many times Alto was asked to restart.
    """

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Replace the lookups, the commands and the dialogs.

        Parameters
        ----------
        monkeypatch : pytest.MonkeyPatch
            Replaces them for the length of the test.
        """
        self.installed: Source | None = Source("https://example.org/alto.git", commit=INSTALLED)
        self.tool = True
        self.programs: dict[str, str | None] = {"git": sys.executable, "uv": sys.executable}
        self.check_script = says_commit(LATEST)
        self.upgrade_script = "print('Resolved 2 packages'); print('Updated alto')"
        self.answer = YES
        self.shown: list[tuple[str, str]] = []
        self.ran: list[str] = []
        self.seen: list[tuple[str, str, str]] = []
        self.restarts = 0
        monkeypatch.setattr(updates, "installed_source", lambda: self.installed)
        monkeypatch.setattr(updates, "is_tool_install", lambda: self.tool)
        monkeypatch.setattr(updates, "find_program", lambda name: self.programs.get(name))
        monkeypatch.setattr(updates, "check_command", self._check)
        monkeypatch.setattr(updates, "upgrade_command", self._upgrade)
        monkeypatch.setattr(QMessageBox, "warning", lambda _parent, _title, text: self.shown.append(("warning", text)))
        monkeypatch.setattr(QMessageBox, "information", lambda _parent, _title, text: self.shown.append(("information", text)))
        monkeypatch.setattr(QMessageBox, "question", lambda _parent, _title, text, _buttons, _default: self._ask(text))
        monkeypatch.setattr(QDialog, "exec", lambda dialog: self._exec(dialog))

    def _check(
        self,
        _source: Source,
        *,
        git: str,
    ) -> tuple[str, list[str]]:
        """
        Give the stand-in for the check.

        Parameters
        ----------
        _source : Source
            Where the running copy came from.
        git : str
            The program found for `git`. Keyword-only.

        Returns
        -------
        tuple of str and list of str
            The program and its arguments.
        """
        self.ran.append("check")
        return git, ["-c", self.check_script]

    def _upgrade(self, *, uv: str) -> tuple[str, list[str]]:
        """
        Give the stand-in for the update.

        Parameters
        ----------
        uv : str
            The program found for `uv`. Keyword-only.

        Returns
        -------
        tuple of str and list of str
            The program and its arguments.
        """
        self.ran.append("upgrade")
        return uv, ["-c", self.upgrade_script]

    def _ask(self, text: str) -> QMessageBox.StandardButton:
        """
        Record a question and give the answer the test chose.

        Parameters
        ----------
        text : str
            The question.

        Returns
        -------
        QMessageBox.StandardButton
            The chosen answer.
        """
        self.shown.append(("question", text))
        return self.answer

    def _exec(self, dialog: QDialog) -> int:
        """
        Stand in for showing a dialog until it is done: wait for the program to end, then press OK as a person would.

        Parameters
        ----------
        dialog : QDialog
            The dialog.

        Returns
        -------
        int
            How the dialog ended.
        """
        for _ in range(500):
            if isinstance(dialog, CheckDialog | UpdateDialog) and dialog.ended:
                break
            QTest.qWait(20)
        if isinstance(dialog, UpdateDialog):
            self.seen.append((dialog.status.text(), dialog.button.text(), dialog.log.toPlainText()))
            assert dialog.button.isEnabled()
            dialog.button.click()
        return int(dialog.result())

    def restart(self) -> None:
        """Note that Alto was asked to restart."""
        self.restarts += 1


@pytest.fixture
def fakes(monkeypatch: pytest.MonkeyPatch) -> Fakes:
    """
    Provide the stand-ins.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Replaces what the flow reaches outside itself.

    Returns
    -------
    Fakes
        The stand-ins, to be told what to do.
    """
    return Fakes(monkeypatch)


def check(fakes: Fakes) -> None:
    """
    Run the whole flow as the menu does.

    Parameters
    ----------
    fakes : Fakes
        The stand-ins, which also say what a restart does.
    """
    flow.check_for_updates(MainWindow(None), restart=fakes.restart)


def test_when_the_installed_commit_is_the_newest_it_says_so_and_offers_nothing(app: QApplication, fakes: Fakes) -> None:
    """
    Check that an up-to-date copy is told so, with its short commit, and that nothing is installed or restarted.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.check_script = says_commit(INSTALLED)
    check(fakes)
    assert fakes.shown == [("information", "Alto is up to date (b6e2091).")]
    assert fakes.ran == ["check"] and fakes.restarts == 0


def test_a_newer_commit_is_offered_and_declining_changes_nothing(app: QApplication, fakes: Fakes) -> None:
    """
    Check that the question names both commits, and that answering No installs nothing and does not restart.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.answer = NO
    check(fakes)
    assert len(fakes.shown) == 1 and fakes.shown[0][0] == "question"
    assert "b6e2091 → c0ffee0" in fakes.shown[0][1] and fakes.shown[0][1].endswith("Update now?")
    assert fakes.ran == ["check"] and fakes.restarts == 0


def test_agreeing_shows_the_output_says_it_will_restart_and_restarts_once_ok_is_pressed(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check the whole successful path: the update's output is shown, the window says Alto will restart after OK, and it then does.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    check(fakes)
    assert fakes.ran == ["check", "upgrade"]
    assert len(fakes.seen) == 1
    status, button, log = fakes.seen[0]
    assert "Alto has been updated." in status and "restart when you press OK" in status
    assert button == "OK" and "Resolved 2 packages" in log and "Updated alto" in log
    assert fakes.restarts == 1


def test_a_failed_update_says_so_shows_why_and_does_not_restart(app: QApplication, fakes: Fakes) -> None:
    """
    Check that when the update program fails the window says so, offers Close, keeps its output, and Alto is left running.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.upgrade_script = "import sys; print('error: could not fetch'); sys.exit(2)"
    check(fakes)
    status, button, log = fakes.seen[0]
    assert "did not finish" in status and "will not restart" in status
    assert button == "Close" and "error: could not fetch" in log
    assert fakes.restarts == 0


def test_a_check_that_fails_says_why_and_offers_nothing(app: QApplication, fakes: Fakes) -> None:
    """
    Check that when the address cannot be asked, the person is told why in git's own words and nothing is offered.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.check_script = "import sys; print('fatal: unable to access the address'); sys.exit(128)"
    check(fakes)
    assert len(fakes.shown) == 1 and fakes.shown[0][0] == "warning"
    assert "could not find out" in fakes.shown[0][1] and "fatal: unable to access the address" in fakes.shown[0][1]
    assert fakes.ran == ["check"] and fakes.restarts == 0


def test_a_check_that_gets_no_commit_back_is_a_failure_too(app: QApplication, fakes: Fakes) -> None:
    """
    Check that an answer with no commit in it, such as an address with no such branch, is reported rather than taken as news.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.check_script = "pass"
    check(fakes)
    assert [kind for kind, _ in fakes.shown] == ["warning"] and "did not answer" in fakes.shown[0][1]


def test_a_check_that_takes_too_long_is_stopped_and_reported(
    app: QApplication,
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that a check that never answers is stopped after the time allowed, and the person is told there was no answer.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    monkeypatch : pytest.MonkeyPatch
        Shortens the time allowed.
    """
    monkeypatch.setattr(flow, "CHECK_SECONDS", 1)
    fakes.check_script = SLEEPS
    check(fakes)
    assert len(fakes.shown) == 1 and "no answer after 1 seconds" in fakes.shown[0][1]


def test_a_program_that_cannot_be_started_is_reported(app: QApplication, fakes: Fakes, tmp_path: Path) -> None:
    """
    Check that a program path that does not work gives a message that says which program could not be started.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    tmp_path : Path
        A new folder, used for a path that holds no program.
    """
    missing = f"{tmp_path}/no-such-git"
    fakes.programs["git"] = missing
    check(fakes)
    assert len(fakes.shown) == 1 and f"Could not start {missing}" in fakes.shown[0][1]


def test_a_copy_that_cannot_update_itself_is_told_why_and_nothing_runs(app: QApplication, fakes: Fakes) -> None:
    """
    Check that a copy run from a source folder, and one not made by the install script, get the reason and nothing is started.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.installed = None
    check(fakes)
    fakes.installed, fakes.tool = Source("https://example.org/alto.git", commit=INSTALLED), False
    check(fakes)
    assert fakes.shown == [("information", updates.SOURCE_FOLDER), ("information", updates.NOT_BY_SCRIPT)]
    assert fakes.ran == [] and fakes.restarts == 0


def test_missing_git_or_uv_is_reported_before_anything_is_attempted(app: QApplication, fakes: Fakes) -> None:
    """
    Check that without `git` the check is not attempted, and that without `uv` the update is not attempted after agreeing.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.programs["git"] = None
    check(fakes)
    assert fakes.shown == [("warning", flow.NO_GIT)] and fakes.ran == []
    fakes.shown.clear()
    fakes.programs.update({"git": sys.executable, "uv": None})
    check(fakes)
    assert fakes.shown[-1] == ("warning", flow.NO_UV) and "upgrade" not in fakes.ran and fakes.restarts == 0


def test_the_update_window_cannot_be_closed_until_the_update_has_ended(app: QApplication, fakes: Fakes) -> None:
    """
    Check that closing the window is refused while the update runs, because stopping it half way could break the install.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins; the update here takes a moment.
    """
    fakes.upgrade_script = "import time; time.sleep(0.6); print('done')"
    dialog = UpdateDialog(None, uv=sys.executable)
    dialog.runner.start(sys.executable, arguments=["-c", fakes.upgrade_script])
    dialog.show()
    assert not dialog.button.isEnabled()
    dialog.reject()
    dialog.close()
    assert dialog.isVisible()  # neither closed it
    for _ in range(300):
        if dialog.ended:
            break
        QTest.qWait(20)
    assert dialog.ended and dialog.succeeded and dialog.button.isEnabled()
    assert dialog.bar.maximum() == 1 and dialog.bar.value() == 1  # no longer a bar that keeps moving
    dialog.reject()
    assert not dialog.isVisible()


def test_cancelling_the_check_stops_it_quietly(app: QApplication, fakes: Fakes) -> None:
    """
    Check that cancelling stops the program, marks the check cancelled, and shows no message.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    dialog = CheckDialog(None, source=Source("https://example.org/alto.git", commit=INSTALLED), git=sys.executable)
    dialog.runner.start(sys.executable, arguments=["-c", SLEEPS])
    assert dialog.runner.running
    dialog.reject()
    assert dialog.cancelled and dialog.ended and not dialog.runner.running
    assert fakes.shown == [] and dialog.commit == ""


def test_the_runner_hands_on_output_as_it_comes_and_the_exit_code_once(app: QApplication) -> None:
    """
    Check that the runner announces each piece of output, then one end with the exit code and everything printed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    pieces: list[str] = []
    ends: list[tuple[int, str]] = []
    runner = CommandRunner()
    runner.output.connect(pieces.append)
    runner.done.connect(lambda code, text: ends.append((code, text)))
    runner.start(sys.executable, arguments=["-c", "import sys; print('one'); print('two', file=sys.stderr); sys.exit(3)"])
    for _ in range(300):
        if ends:
            break
        QTest.qWait(20)
    assert len(ends) == 1 and ends[0][0] == 3
    assert "one" in ends[0][1] and "two" in ends[0][1] and "".join(pieces) == ends[0][1]


def test_long_output_is_cut_to_its_end_for_a_message() -> None:
    """Check that `brief` keeps the end of what a program printed and drops the blank space around it."""
    assert brief("  one\ntwo  \n") == "one\ntwo"
    assert brief("x" * 1000 + "end", limit=10) == "xxxxxxxend"


def test_the_menu_offers_the_check_with_or_without_a_profile_and_hands_it_the_restart(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the menu offers the update check even with no profile, and that it runs the flow with the window's restart.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces the flow, to see what it is given.
    """
    calls: list[tuple[object, Callable[[], None]]] = []
    monkeypatch.setattr(flow, "check_for_updates", lambda parent, *, restart: calls.append((parent, restart)))
    window = MainWindow(None)
    assert window.update_action.text() == "Check for updates…" and window.update_action.isVisible()
    window.update_action.trigger()
    assert calls == [(window, window.restart_app)]
