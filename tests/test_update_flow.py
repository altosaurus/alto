"""
Tests for the menu's "Check for updates…": what is asked, what is shown
while it works, and when Alto restarts.

No test goes online or runs `git` or `uv`: GitHub's answer is a canned
reply, and both programs are replaced by Python
one-liners that print what the real ones would.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
)

from alto import (
    selfupdate,
    updates,
)
from alto.exercises.library import NoteNames
from alto.selfupdate import (
    Prepared,
    Target,
)
from alto.ui import update_flow as flow
from alto.ui.main_window import MainWindow
from alto.ui.update_flow import (
    CheckDialog,
    CommandRunner,
    ReleaseDialog,
    UpdateDialog,
    brief,
    save_channel,
    saved_channel,
)
from alto.updates import Source

if TYPE_CHECKING:
    from collections.abc import Callable

INSTALLED = "b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe"
LATEST = "c0ffee0123456789abcdef0123456789abcdef01"
RELEASE_URL = "https://example.org/releases/v0.1.0"
RELEASE = json.dumps(
    {
        "tag_name": "v0.1.0",
        "html_url": RELEASE_URL,
        "draft": False,
        "prerelease": False,
    },
)
YES, NO = QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No
SLEEPS = "import time; time.sleep(30)"
SOURCE = Source("https://example.org/alto.git", commit=INSTALLED)


def says_commit(commit: str) -> str:
    """
    Give a Python program that prints what `git ls-remote` prints for a
    commit.

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
    Stands in for everything the update flow reaches outside itself: the
    copy that is running, GitHub, programs and dialogs.

    Attributes
    ----------
    installed : Source or None
        Where the running copy came from; None for a copy run from a
        source folder.
    tool : bool
        Whether the running copy is a `uv tool` install.
    frozen : bool
        Whether the running copy is a packaged build.
    version : str
        The version of the running copy.
    status : int
        The HTTP status GitHub answers with; 0 means it could not be
        reached.
    release_text : str
        What GitHub answers with.
    fetch_seconds : float
        How long GitHub takes to answer.
    programs : dict of str to str or None
        The path each program is found at, or None if it is missing.
    check_script : str
        The Python program that stands in for `git ls-remote`.
    install_script : str
        The Python program that stands in for `uv tool install`.
    answer : QMessageBox.StandardButton
        What the person answers when asked whether to update.
    shown : list of tuple
        Each message box that appeared, as (kind, text).
    ran : list of str
        Which programs were started, in order.
    checked : list of Source
        The source each check of the main branch was asked about.
    installs : list of str or None
        The tag each installation was asked for; None for the main
        branch.
    fetched : list of str
        Each address GitHub was asked at.
    opened : list of str
        Each page that was opened in the browser.
    seen : list of tuple
        What the update window said and showed when it had finished, as
        (status, button text, log), before OK was pressed.
    restarts : int
        How many times Alto was asked to restart.
    """

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        Replace the lookups, the commands, the network and the dialogs.

        Parameters
        ----------
        monkeypatch : pytest.MonkeyPatch
            Replaces them for the length of the test.
        """
        self.installed: Source | None = SOURCE
        self.tool = True
        self.frozen = False
        self.version = "0.0.0"
        self.status = 200
        self.release_text = RELEASE
        self.fetch_seconds = 0.0
        self.programs: dict[str, str | None] = {
            "git": sys.executable,
            "uv": sys.executable,
        }
        self.check_script = says_commit(LATEST)
        self.install_script = (
            "print('Resolved 2 packages'); print('Installed alto')"
        )
        self.answer = YES
        self.shown: list[tuple[str, str]] = []
        self.ran: list[str] = []
        self.checked: list[Source] = []
        self.installs: list[str | None] = []
        self.fetched: list[str] = []
        self.opened: list[str] = []
        self.seen: list[tuple[str, str, str]] = []
        self.restarts = 0
        monkeypatch.setattr(
            updates,
            "installed_source",
            lambda: self.installed,
        )
        monkeypatch.setattr(updates, "is_tool_install", lambda: self.tool)
        monkeypatch.setattr(updates, "is_frozen", lambda: self.frozen)
        monkeypatch.setattr(updates, "installed_version", lambda: self.version)
        monkeypatch.setattr(
            updates,
            "find_program",
            lambda name: self.programs.get(name),
        )
        monkeypatch.setattr(updates, "check_command", self._check)
        monkeypatch.setattr(updates, "install_command", self._install)
        monkeypatch.setattr(updates, "fetch_text", self._fetch)
        monkeypatch.setattr(
            QMessageBox,
            "warning",
            lambda _parent, _title, text: self.shown.append(("warning", text)),
        )
        monkeypatch.setattr(
            QMessageBox,
            "information",
            lambda _parent, _title, text: self.shown.append(
                ("information", text),
            ),
        )
        monkeypatch.setattr(
            QMessageBox,
            "exec",
            lambda box: self._release_prompt(box),
        )
        monkeypatch.setattr(
            QMessageBox,
            "question",
            lambda _parent, _title, text, _buttons, _default: self._ask(text),
        )
        monkeypatch.setattr(
            flow.QDesktopServices,
            "openUrl",
            lambda url: self.opened.append(url.toString()) or True,
        )
        monkeypatch.setattr(QDialog, "exec", lambda dialog: self._exec(dialog))
        self.package_target: Target | None = None
        self.prepared: Prepared | None = Prepared(
            Path("/nowhere/work"),
            installer=None,
            root=Path("/nowhere/work/unpacked/alto"),
        )
        self.package_runs: list[tuple[str, str]] = []
        self.handoffs: list[tuple[Prepared, Target]] = []
        self.handoff_error: Exception | None = None
        self.quits = 0
        monkeypatch.setattr(
            selfupdate,
            "self_update_target",
            lambda: self.package_target,
        )
        # noinspection PyUnresolvedReferences
        monkeypatch.setattr(flow, "PackageUpdateDialog", self._package_window)
        monkeypatch.setattr(selfupdate, "start_handoff", self._handoff)

    def _fetch(
        self,
        url: str,
        *,
        seconds: int,
    ) -> tuple[int, str]:
        """
        Give the canned answer from GitHub, after the time the test
        chose. This runs on the fetching thread.

        Parameters
        ----------
        url : str
            The address asked.
        seconds : int
            How long the real function would wait. Keyword-only.

        Returns
        -------
        tuple of int and str
            The HTTP status and the body.
        """
        del seconds
        self.fetched.append(url)
        time.sleep(self.fetch_seconds)
        return self.status, self.release_text

    def _check(
        self,
        source: Source,
        *,
        git: str,
    ) -> tuple[str, list[str]]:
        """
        Give the stand-in for the check of the main branch.

        Parameters
        ----------
        source : Source
            What the check is asked about.
        git : str
            The program found for `git`. Keyword-only.

        Returns
        -------
        tuple of str and list of str
            The program and its arguments.
        """
        self.ran.append("check")
        self.checked.append(source)
        return git, ["-c", self.check_script]

    def _install(
        self,
        _source: Source,
        *,
        uv: str,
        tag: str | None = None,
    ) -> tuple[str, list[str]]:
        """
        Give the stand-in for the installation.

        Parameters
        ----------
        _source : Source
            Where the running copy came from.
        uv : str
            The program found for `uv`. Keyword-only.
        tag : str or None, default None
            The release asked for. Keyword-only.

        Returns
        -------
        tuple of str and list of str
            The program and its arguments.
        """
        self.ran.append("install")
        self.installs.append(tag)
        return uv, ["-c", self.install_script]

    def _release_prompt(self, box: QMessageBox) -> int:
        """
        Click the configured answer in the release dialog's visible
        button row.

        Parameters
        ----------
        box : QMessageBox
            Release offer.

        Returns
        -------
        int
            The dialog result after selecting a button.
        """
        box.show()
        buttons = sorted(box.buttons(), key=lambda button: button.x())
        assert [button.text() for button in buttons] == [
            "Yes",
            "No",
            "Don't remind me again",
        ]
        index = [YES, NO, QMessageBox.StandardButton.Ignore].index(
            self._ask(box.text()),
        )
        buttons[index].click()
        return box.result()

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
        Stand in for showing a dialog until it is done: wait for the
        answer, then press OK as a person would.

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
            if (
                isinstance(dialog, CheckDialog | ReleaseDialog | UpdateDialog)
                and dialog.ended
            ):
                break
            QTest.qWait(20)
        if isinstance(dialog, UpdateDialog):
            self.seen.append(
                (
                    dialog.status.text(),
                    dialog.button.text(),
                    dialog.log.toPlainText(),
                ),
            )
            assert dialog.button.isEnabled()
            dialog.button.click()
        return int(dialog.result())

    def restart(self) -> None:
        """Note that Alto was asked to restart."""
        self.restarts += 1

    def quit(self) -> None:
        """
        Note that Alto was asked to close, as it is once an update has
        been handed to its installer.
        """
        self.quits += 1

    def _package_window(
        self,
        parent: object,
        *,
        release: updates.Release,
        target: Target,
    ) -> SimpleNamespace:
        """
        Stand in for the window that downloads and checks an update: it
        gives back what the test chose.

        Parameters
        ----------
        parent : object
            The window it belongs to, ignored.
        release : updates.Release
            The release to install. Keyword-only.
        target : Target
            The copy that will be replaced. Keyword-only.

        Returns
        -------
        SimpleNamespace
            Something with the `run` method of the window.
        """
        del parent
        self.package_runs.append((release.version, target.system))
        return SimpleNamespace(run=lambda: self.prepared)

    def _handoff(
        self,
        prepared: Prepared,
        *,
        target: Target,
    ) -> None:
        """
        Stand in for starting the program that installs the update.

        Parameters
        ----------
        prepared : Prepared
            The checked update.
        target : Target
            The copy that is replaced. Keyword-only.

        Raises
        ------
        OSError
            If the test says the program cannot be started.
        """
        if self.handoff_error is not None:
            raise self.handoff_error
        self.handoffs.append((prepared, target))


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
    flow.check_for_updates(
        MainWindow(None),
        restart=fakes.restart,
        quit_app=fakes.quit,
    )


# -- what the update check follows
# ----------------------------------------------------------------------


def test_updates_follow_releases_unless_the_main_branch_is_chosen(
    app: QApplication,
) -> None:
    """
    Check that releases are followed by default, that the choice is
    remembered, and that anything else means releases.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert saved_channel() == "releases"
    save_channel("main")
    assert saved_channel() == "main"
    save_channel("releases")
    assert saved_channel() == "releases"
    save_channel("nonsense")
    assert saved_channel() == "releases"


# -- a copy installed with the script, following releases (the default)
# ----------------------------------------------


@pytest.mark.parametrize("automatic", [False, True])
def test_newer_release_offered_and_agreeing_installs_tag_and(
    app: QApplication,
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
    automatic: bool,
) -> None:
    """
    Follow the manual and scheduled release checks through an accepted
    upgrade and restart.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    monkeypatch : pytest.MonkeyPatch
        Keep the exercise grid active and intercept the restart.
    automatic : bool
        Start the background timer or invoke the menu command.
    """
    if automatic:
        window = MainWindow()
        monkeypatch.setattr(window, "isActiveWindow", lambda: True)
        monkeypatch.setattr(window, "restart_app", fakes.restart)
        flow.DailyReleaseCheck(window)
        deadline = time.monotonic() + 5
        while not fakes.restarts and time.monotonic() < deadline:
            QTest.qWait(10)
        window.close()
    else:
        check(fakes)
    assert fakes.fetched == [updates.RELEASES_API] and "check" not in fakes.ran
    assert len(fakes.shown) == 1 and fakes.shown[0][0] == "question"
    assert "0.0.0 → 0.1.0" in fakes.shown[0][1] and fakes.shown[0][1].endswith(
        "Update now?",
    )
    assert fakes.installs == ["v0.1.0"]
    status, button, log = fakes.seen[0]
    assert (
        "Alto has been updated." in status
        and "restart when you press OK" in status
    )
    assert (
        button == "OK"
        and "Resolved 2 packages" in log
        and "Installed alto" in log
    )
    assert fakes.restarts == 1


def test_when_newest_release_one_running_says_so_and_offers(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that a copy at the newest release, or past it, is told it is
    up to date.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.version = "0.1.0"
    check(fakes)
    # ahead of the newest release, as a copy that follows the main
    # branch can be
    fakes.version = "0.2.0"
    check(fakes)
    assert fakes.shown == [
        ("information", "Alto is up to date (0.1.0)."),
        ("information", "Alto is up to date (0.2.0)."),
    ]
    assert fakes.installs == [] and fakes.restarts == 0


def test_declining_a_release_installs_nothing(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that answering No to the question installs nothing and does
    not restart.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.answer = NO
    check(fakes)
    assert (
        [kind for kind, _ in fakes.shown] == ["question"]
        and fakes.installs == []
        and fakes.restarts == 0
    )


def test_a_failed_installation_says_so_shows_why_and_does_not_restart(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that when the installing program fails the window says so,
    offers Close, keeps its output, and Alto stays running.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.install_script = (
        "import sys; print('error: could not fetch'); sys.exit(2)"
    )
    check(fakes)
    status, button, log = fakes.seen[0]
    assert "did not finish" in status and "will not restart" in status
    assert button == "Close" and "error: could not fetch" in log
    assert fakes.restarts == 0


def test_with_no_release_yet_the_person_is_told_so_without_a_warning(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that GitHub having no release is reported as information, not
    as something that went wrong.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.status, fakes.release_text = 404, '{"message": "Not Found"}'
    check(fakes)
    assert (
        fakes.shown == [("information", updates.NO_RELEASE)]
        and fakes.installs == []
    )


@pytest.mark.parametrize(
    ("status", "text", "expected"),
    [
        (
            0,
            "Network is unreachable",
            "could not reach GitHub: Network is unreachable",
        ),
        (403, "rate limit exceeded", "error (403): rate limit exceeded"),
        (200, "<html>not json</html>", "not understood"),
        (
            200,
            json.dumps(
                {
                    "tag_name": "v1.0.0rc1",
                    "html_url": RELEASE_URL,
                    "prerelease": True,
                },
            ),
            "not understood",
        ),
    ],
)
def test_a_failed_or_unusable_answer_from_github_is_reported_with_the_reason(
    app: QApplication,
    fakes: Fakes,
    status: int,
    text: str,
    expected: str,
) -> None:
    """
    Check that no connection, an error, an answer that is not JSON and a
    pre-release each give a warning that says why.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    status : int
        What GitHub answers with.
    text : str
        The body of its answer.
    expected : str
        What the warning should say.
    """
    fakes.status, fakes.release_text = status, text
    check(fakes)
    assert (
        len(fakes.shown) == 1
        and fakes.shown[0][0] == "warning"
        and expected in fakes.shown[0][1]
    )
    assert fakes.installs == [] and fakes.restarts == 0


def test_canceling_wait_for_github_shows_nothing_and_late_answer(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that canceling while GitHub is slow marks the check canceled,
    shows nothing, and ignores the answer that comes later.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins; GitHub takes a moment here.
    """
    fakes.fetch_seconds = 0.4
    dialog = ReleaseDialog(None)
    dialog.fetcher.start(seconds=5)
    dialog.reject()
    QTest.qWait(800)
    assert (
        dialog.canceled
        and dialog.ended
        and dialog.release is None
        and dialog.error == ""
    )
    assert fakes.shown == []


def test_without_uv_agreeing_to_an_update_is_reported_and_nothing_is_attempted(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that a missing `uv` is reported after the person agrees,
    instead of failing inside the update window.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.programs["uv"] = None
    check(fakes)
    assert (
        fakes.shown[-1] == ("warning", flow.NO_UV)
        and fakes.installs == []
        and fakes.restarts == 0
    )


# -- a copy installed with the script, following the main branch
# ----------------------------------------------------


def test_following_main_branch_compares_commits_and_never_asks(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that on the main channel an equal commit is up to date, and
    that no release is asked for.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    save_channel("main")
    fakes.check_script = says_commit(INSTALLED)
    check(fakes)
    assert fakes.shown == [("information", "Alto is up to date (b6e2091).")]
    assert (
        fakes.ran == ["check"] and fakes.fetched == [] and fakes.restarts == 0
    )


def test_newer_commit_on_main_branch_offered_and_installed_from(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that the question names both commits and the main branch, that
    agreeing installs no tag, and that Alto restarts.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    save_channel("main")
    check(fakes)
    assert len(fakes.shown) == 1 and "main branch" in fakes.shown[0][1]
    assert "b6e2091 → c0ffee0" in fakes.shown[0][1] and fakes.shown[0][
        1
    ].endswith("Update now?")
    assert fakes.installs == [None] and fakes.restarts == 1


def test_main_branch_asked_about_even_if_copy_installed_from(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that a copy pinned to a tag, which is how a release install is
    recorded, can follow the main branch again.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    save_channel("main")
    fakes.installed = Source(SOURCE.url, commit=INSTALLED, ref="v0.0.9")
    check(fakes)
    assert [(source.url, source.ref) for source in fakes.checked] == [
        (SOURCE.url, "HEAD"),
    ]


def test_declining_a_newer_commit_installs_nothing(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that answering No installs nothing and does not restart.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    save_channel("main")
    fakes.answer = NO
    check(fakes)
    assert fakes.installs == [] and fakes.restarts == 0


def test_a_check_of_the_main_branch_that_fails_says_why_and_offers_nothing(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that when the address cannot be asked, the person is told why
    in git's own words and nothing is offered.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    save_channel("main")
    fakes.check_script = (
        "import sys; print('fatal: unable to access the address'); "
        "sys.exit(128)"
    )
    check(fakes)
    assert len(fakes.shown) == 1 and fakes.shown[0][0] == "warning"
    assert (
        "could not find out" in fakes.shown[0][1]
        and "fatal: unable to access the address" in fakes.shown[0][1]
    )
    assert fakes.installs == [] and fakes.restarts == 0


def test_an_answer_with_no_commit_in_it_is_a_failure_too(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that an answer with no commit in it, such as an address with
    no such branch, is reported rather than taken as news.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    save_channel("main")
    fakes.check_script = "pass"
    check(fakes)
    assert [kind for kind, _ in fakes.shown] == [
        "warning",
    ] and "did not answer" in fakes.shown[0][1]


def test_check_of_main_branch_takes_too_long_stopped_and(
    app: QApplication,
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that a check that never answers is stopped after the time
    allowed, and the person is told there was no answer.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    monkeypatch : pytest.MonkeyPatch
        Shortens the time allowed.
    """
    save_channel("main")
    monkeypatch.setattr(flow, "CHECK_SECONDS", 1)
    fakes.check_script = SLEEPS
    check(fakes)
    assert (
        len(fakes.shown) == 1
        and "no answer after 1 seconds" in fakes.shown[0][1]
    )


def test_a_program_that_cannot_be_started_is_reported(
    app: QApplication,
    fakes: Fakes,
    tmp_path: Path,
) -> None:
    """
    Check that a program path that does not work gives a message that
    says which program could not be started.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    tmp_path : Path
        A new folder, used for a path that holds no program.
    """
    save_channel("main")
    missing = f"{tmp_path}/no-such-git"
    fakes.programs["git"] = missing
    check(fakes)
    assert (
        len(fakes.shown) == 1
        and f"Could not start {missing}" in fakes.shown[0][1]
    )


def test_without_git_main_branch_cannot_be_checked_but_releases(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that a missing `git` is reported on the main channel before
    anything is attempted, and does not matter for releases.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.programs["git"] = None
    fakes.answer = NO
    check(fakes)  # releases need only the network
    assert fakes.shown[0][0] == "question"
    fakes.shown.clear()
    save_channel("main")
    check(fakes)
    assert fakes.shown == [("warning", flow.NO_GIT)] and fakes.ran == []


# -- a packaged copy
# ----------------------------------------------------------------------


def test_packaged_copy_told_about_newer_release_and_offered_page(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that a packaged copy gets the download page of a newer
    release, and that nothing is installed or restarted.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.frozen, fakes.installed, fakes.tool = True, None, False
    check(fakes)
    assert (
        len(fakes.shown) == 1
        and "0.1.0 is available (you have 0.0.0)" in fakes.shown[0][1]
    )
    assert "page where it can be downloaded" in fakes.shown[0][1]
    assert fakes.opened == [RELEASE_URL]
    assert fakes.installs == [] and fakes.ran == [] and fakes.restarts == 0


def test_a_packaged_copy_that_declines_or_is_up_to_date_opens_nothing(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that No to the question, and an up-to-date copy, both leave
    the browser alone.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.frozen, fakes.installed, fakes.tool = True, None, False
    fakes.answer = NO
    check(fakes)
    fakes.version = "0.1.0"
    check(fakes)
    assert fakes.opened == [] and fakes.shown[-1] == (
        "information",
        "Alto is up to date (0.1.0).",
    )


def test_a_packaged_copy_follows_releases_whatever_the_setting_says(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that choosing the main branch changes nothing for a packaged
    copy, which cannot follow it, and needs no `git`.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    save_channel("main")
    fakes.frozen, fakes.installed, fakes.tool = True, None, False
    fakes.programs.update({"git": None, "uv": None})
    check(fakes)
    assert (
        fakes.fetched == [updates.RELEASES_API]
        and fakes.opened == [RELEASE_URL]
        and fakes.ran == []
    )


# -- a packaged copy that can replace itself
# ----------------------------------------------------------------------


def make_packaged(
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
    *,
    keys: tuple[str, ...] = ("a public key",),
    can_replace_itself: bool = True,
) -> Target:
    """
    Make the running copy a packaged one, with or without the key and
    the right place to replace itself.

    Parameters
    ----------
    fakes : Fakes
        The stand-ins.
    monkeypatch : pytest.MonkeyPatch
        Sets the keys in the code.
    keys : tuple of str
        The public keys the code holds. Keyword-only.
    can_replace_itself : bool, default True
        Whether the copy is in the place a copy that the install script
        or the installer made would be. Keyword-only.

    Returns
    -------
    Target
        Where the copy is.
    """
    fakes.frozen, fakes.installed, fakes.tool = True, None, False
    target = Target(
        "linux",
        folder=Path("/home/me/.local/opt/alto"),
        prefix=Path("/home/me/.local"),
    )
    fakes.package_target = target if can_replace_itself else None
    monkeypatch.setattr(updates, "UPDATE_PUBLIC_KEYS", keys)
    return target


def test_packaged_copy_can_replace_itself_asked_updated_handed(
    app: QApplication,
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check the whole path: the question names both versions, the update
    is downloaded, handed over once, and Alto closes.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    monkeypatch : pytest.MonkeyPatch
        Sets the keys in the code.
    """
    target = make_packaged(fakes, monkeypatch)
    check(fakes)
    assert len(fakes.shown) == 1 and fakes.shown[0][0] == "question"
    assert "0.0.0 \u2192 0.1.0" in fakes.shown[0][1] and fakes.shown[0][
        1
    ].endswith("Update now?")
    assert fakes.package_runs == [("0.1.0", "linux")]
    assert fakes.prepared is not None and fakes.handoffs == [
        (fakes.prepared, target),
    ]
    assert (
        fakes.quits == 1
        and fakes.opened == []
        and fakes.restarts == 0
        and fakes.installs == []
    )


def test_declining_the_update_of_a_packaged_copy_downloads_nothing(
    app: QApplication,
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that No to the question starts nothing and does not close
    Alto.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    monkeypatch : pytest.MonkeyPatch
        Sets the keys in the code.
    """
    make_packaged(fakes, monkeypatch)
    fakes.answer = NO
    check(fakes)
    assert (
        fakes.package_runs == [] and fakes.handoffs == [] and fakes.quits == 0
    )


def test_a_failed_or_canceled_download_hands_nothing_over_and_leaves_alto_open(
    app: QApplication,
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that when the window gives back no update, which is how a
    failure and a cancel end, nothing is installed or closed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    monkeypatch : pytest.MonkeyPatch
        Sets the keys in the code.
    """
    make_packaged(fakes, monkeypatch)
    fakes.prepared = None
    check(fakes)
    assert (
        len(fakes.package_runs) == 1
        and fakes.handoffs == []
        and fakes.quits == 0
    )
    assert [kind for kind, _ in fakes.shown] == [
        "question",
    ]  # the window itself told the person what went wrong


def test_installer_cannot_be_started_reported_and_removes(
    app: QApplication,
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Check that a hand-over that fails says so, deletes the downloaded
    update, and does not close Alto.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    monkeypatch : pytest.MonkeyPatch
        Sets the keys in the code.
    tmp_path : Path
        A new folder, standing in for the update's temporary folder.
    """
    make_packaged(fakes, monkeypatch)
    work = tmp_path / "alto-update-x"
    work.mkdir()
    (work / "file").write_text("x")
    fakes.prepared = Prepared(work, installer=None, root=work / "unpacked")
    fakes.handoff_error = OSError("Permission denied")
    check(fakes)
    assert (
        fakes.shown[-1][0] == "warning"
        and "could not be started" in fakes.shown[-1][1]
        and "Permission denied" in fakes.shown[-1][1]
    )
    assert (
        "Nothing was installed" in fakes.shown[-1][1]
        and not work.exists()
        and fakes.quits == 0
    )


def test_packaged_copy_cannot_replace_itself_or_no_key_offered(
    app: QApplication,
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that a copy that was only unpacked, and a build whose code
    holds no key, are each sent to the download page.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    monkeypatch : pytest.MonkeyPatch
        Sets the keys in the code.
    """
    make_packaged(fakes, monkeypatch, can_replace_itself=False)
    check(fakes)
    make_packaged(fakes, monkeypatch, keys=())
    check(fakes)
    assert (
        fakes.opened == [RELEASE_URL, RELEASE_URL]
        and fakes.package_runs == []
        and fakes.quits == 0
    )
    assert all(
        "page where it can be downloaded" in text for _, text in fakes.shown
    )


def test_a_packaged_copy_that_is_up_to_date_is_told_so_and_asked_nothing(
    app: QApplication,
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the update is only offered when the release is newer.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    monkeypatch : pytest.MonkeyPatch
        Sets the keys in the code.
    """
    make_packaged(fakes, monkeypatch)
    fakes.version = "0.1.0"
    check(fakes)
    assert (
        fakes.shown == [("information", "Alto is up to date (0.1.0).")]
        and fakes.package_runs == []
    )


def test_the_main_branch_setting_does_not_change_how_a_packaged_copy_updates(
    app: QApplication,
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that a packaged copy follows releases and replaces itself from
    one even when the main branch is chosen.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    monkeypatch : pytest.MonkeyPatch
        Sets the keys in the code.
    """
    make_packaged(fakes, monkeypatch)
    save_channel("main")
    check(fakes)
    assert (
        fakes.fetched == [updates.RELEASES_API]
        and fakes.ran == []
        and fakes.quits == 1
    )


def test_copy_installed_with_script_still_installs_from_uv_and(
    app: QApplication,
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the new way of updating a packaged copy does not touch a
    copy installed with the script.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    monkeypatch : pytest.MonkeyPatch
        Sets the keys in the code.
    """
    monkeypatch.setattr(updates, "UPDATE_PUBLIC_KEYS", ("a public key",))
    fakes.package_target = Target(
        "linux",
        folder=Path("/x"),
        prefix=Path("/y"),
    )  # would be taken, were it a packaged copy
    check(fakes)
    assert (
        fakes.installs == ["v0.1.0"]
        and fakes.restarts == 1
        and fakes.package_runs == []
        and fakes.quits == 0
    )


# -- copies that cannot update
# ----------------------------------------------------------------------


def test_a_copy_that_cannot_update_itself_is_told_why_and_nothing_runs(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that a copy run from a source folder, and one not made by the
    install script, get the reason on either channel.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    fakes.installed = None
    check(fakes)
    save_channel("main")
    fakes.installed, fakes.tool = SOURCE, False
    check(fakes)
    assert fakes.shown == [
        ("information", updates.SOURCE_FOLDER),
        ("information", updates.NOT_BY_SCRIPT),
    ]
    assert fakes.ran == [] and fakes.fetched == [] and fakes.restarts == 0


# -- the windows
# ----------------------------------------------------------------------


def test_the_update_window_cannot_be_closed_until_the_update_has_ended(
    app: QApplication,
) -> None:
    """
    Check that closing the window is refused while the update runs,
    because stopping it half way could break the install.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    command = (
        sys.executable,
        ["-c", "import time; time.sleep(0.6); print('done')"],
    )
    dialog = UpdateDialog(None, command=command)
    dialog.runner.start(command[0], arguments=command[1])
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
    assert (
        dialog.bar.maximum() == 1 and dialog.bar.value() == 1
    )  # no longer a bar that keeps moving
    dialog.reject()
    assert not dialog.isVisible()


def test_canceling_the_check_of_the_main_branch_stops_it_quietly(
    app: QApplication,
    fakes: Fakes,
) -> None:
    """
    Check that canceling stops the program, marks the check canceled,
    and shows no message.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    fakes : Fakes
        The stand-ins.
    """
    dialog = CheckDialog(None, source=SOURCE, git=sys.executable)
    dialog.runner.start(sys.executable, arguments=["-c", SLEEPS])
    assert dialog.runner.running
    dialog.reject()
    assert dialog.canceled and dialog.ended and not dialog.runner.running
    assert fakes.shown == [] and dialog.commit == ""


def test_the_runner_hands_on_output_as_it_comes_and_the_exit_code_once(
    app: QApplication,
) -> None:
    """
    Check that the runner announces each piece of output, then one end
    with the exit code and everything printed.

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
    runner.start(
        sys.executable,
        arguments=[
            "-c",
            (
                "import sys; print('one'); print('two', file=sys.stderr); "
                "sys.exit(3)"
            ),
        ],
    )
    for _ in range(300):
        if ends:
            break
        QTest.qWait(20)
    assert len(ends) == 1 and ends[0][0] == 3
    assert (
        "one" in ends[0][1]
        and "two" in ends[0][1]
        and "".join(pieces) == ends[0][1]
    )


def test_long_output_is_cut_to_its_end_for_a_message() -> None:
    """
    Check that `brief` keeps the end of what a program printed and drops
    the blank space around it.
    """
    assert brief("  one\ntwo  \n") == "one\ntwo"
    assert brief("x" * 1000 + "end", limit=10) == "xxxxxxxend"


def test_menu_offers_check_with_or_without_profile_and_hands(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the menu offers the update check even with no profile,
    and that it runs the flow with the window's restart.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces the flow, to see what it is given.
    """
    calls: list[tuple[object, Callable[[], None]]] = []
    monkeypatch.setattr(
        flow,
        "check_for_updates",
        lambda parent, *, restart: calls.append((parent, restart)),
    )
    window = MainWindow(None)
    assert (
        window.update_action.text() == "Check for updates…"
        and window.update_action.isVisible()
    )
    window.update_action.trigger()
    assert calls == [(window, window.restart_app)]


def test_daily_release_check(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    fakes: Fakes,
) -> None:
    """
    Throttle checks across launches and defer each upgrade offer until
    the grid is active.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Control the clock and network reply.
    fakes : Fakes
        Record prompts and upgrade actions.
    """
    now = 1800000000
    monkeypatch.setattr(flow.time, "time", lambda: now)
    window = MainWindow()
    monkeypatch.setattr(window, "isActiveWindow", lambda: True)
    fakes.answer = NO
    saved = flow.store()
    saved.setValue("updates/lastReleaseCheck", "invalid")
    fetches = []
    monkeypatch.setattr(
        flow.ReleaseFetcher,
        "start",
        lambda self, *, seconds: fetches.append(seconds),
    )
    clock = flow.DailyReleaseCheck(window)
    clock.stop()
    clock._check()
    assert fetches == [flow.RELEASE_SECONDS]
    reopened = flow.DailyReleaseCheck(window)
    reopened.stop()
    reopened._check()
    assert reopened.interval() == flow.DAY_SECONDS * 1000 and len(fetches) == 1
    reopened.stop()

    window.open_exercise(NoteNames)
    clock._received(200, RELEASE)
    assert not fakes.shown and clock.pending is not None
    window.show_home()
    clock._check()
    assert (
        len(fakes.shown) == 1
        and "0.1.0" in fakes.shown[0][1]
        and not fakes.installs
    )
    now += flow.DAY_SECONDS - 60
    reopened._received(200, RELEASE)
    assert reopened.interval() == 60_000 and len(fakes.shown) == 1
    now += 60
    fakes.answer = QMessageBox.StandardButton.Ignore
    reopened._check()
    assert len(fakes.shown) == 2 and not fakes.installs
    reopened.stop()
    for status, response in [
        (200, RELEASE),
        (200, RELEASE.replace("0.1.0", "0.0.0")),
        (404, ""),
        (0, "offline"),
        (200, RELEASE.replace('"prerelease": false', '"prerelease": true')),
    ]:
        now += flow.DAY_SECONDS
        clock._check()
        clock._received(status, response)
    assert len(fetches) == 6 and len(fakes.shown) == 2
    now += flow.DAY_SECONDS
    clock._check()
    clock._received(200, RELEASE.replace("0.1.0", "0.2.0"))
    assert len(fakes.shown) == 3 and "0.2.0" in fakes.shown[-1][1]
    clock.stop()
    window.close()


def test_daily_release_check_preferences(
    app: QApplication,
    fakes: Fakes,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Honor the opt-out, installation type, and channel even when a
    request is already in flight.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    fakes : Fakes
        Supply installation metadata and collect prompts.
    monkeypatch : pytest.MonkeyPatch
        Control window activation and network access.
    """
    window = MainWindow()
    monkeypatch.setattr(window, "isActiveWindow", lambda: True)
    monkeypatch.setattr(
        flow.ReleaseFetcher,
        "start",
        lambda self, *, seconds: fakes.fetched.append("releases"),
    )
    fakes.installed = None
    assert not flow.DailyReleaseCheck(window).isActive()
    fakes.installed = SOURCE
    clock = flow.DailyReleaseCheck(window)
    clock.stop()
    save_channel(updates.MAIN)
    clock._check()
    assert not fakes.fetched
    fakes.frozen = True
    packaged = flow.DailyReleaseCheck(window)
    packaged.stop()
    packaged._check()
    assert fakes.fetched == ["releases"]
    flow.store().setValue("updates/automatic", False)
    packaged._received(200, RELEASE)
    assert packaged.pending is None and not fakes.shown
    clock.stop()
    packaged.stop()
    window.close()
