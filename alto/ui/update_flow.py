r"""
Checking for a newer Alto and installing it: the questions asked, the progress shown, and the restart afterwards.

The menu's "Check for updates…" follows one of two channels, chosen in Settings: the newest release (the default), or the
newest commit on the main branch. A copy installed with `scripts/alto-install.sh` can replace itself, from either, with
`uv tool install`, showing its output, and restarts when OK is pressed. A packaged copy cannot replace itself, so it is told
that a newer release exists and offered the page where it can be downloaded; it always follows releases. A copy run from a
source folder is told to update with git.

Examples
--------
>>> brief("fatal: unable to access 'https://example.org/': Could not resolve host\n")
"fatal: unable to access 'https://example.org/': Could not resolve host"
"""

from __future__ import annotations

import shutil
import threading
import time
from typing import TYPE_CHECKING

from PySide6.QtCore import (
    QObject,
    QProcess,
    QProcessEnvironment,
    Qt,
    QTimer,
    QUrl,
    Signal,
)
from PySide6.QtGui import (
    QCloseEvent,
    QDesktopServices,
    QFontDatabase,
    QTextCursor,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from alto import (
    selfupdate,
    updates,
)
from alto.ui.package_update import PackageUpdateDialog
from alto.ui.store import (
    int_value,
    store,
    text_value,
)
from alto.ui.zoom import px
from alto.updates import (
    InstallKind,
    Release,
    Source,
    parse_ls_remote,
    short,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from alto.ui.main_window import MainWindow

CHECK_TITLE, UPDATE_TITLE = "Check for updates", "Update Alto"
CHECK_SECONDS = 20
RELEASE_SECONDS = 15
DAY_SECONDS = 24 * 60 * 60
QUIET = {
    "UV_NO_PROGRESS": "1",  # plain lines of text, not a progress bar drawn with control characters
    "NO_COLOR": "1",
    "GIT_TERMINAL_PROMPT": "0",  # never wait for a password that nobody can type
}
NO_GIT = "Git is needed to check for updates, and it was not found. Install it, then try again."
NO_UV = "uv is needed to install the update, and it was not found. Install it (https://docs.astral.sh/uv/), then try again."


def brief(
    text: str,
    *,
    limit: int = 400,
) -> str:
    r"""
    Cut what a program printed down to what is worth showing in a message: the end of it, without the blank space around it.

    Parameters
    ----------
    text : str
        What the program printed.
    limit : int, default 400
        The most characters to keep. Keyword-only.

    Returns
    -------
    str
        The end of the text, at most `limit` characters long.

    Examples
    --------
    >>> brief("  one\ntwo  \n")
    'one\ntwo'
    >>> brief("x" * 10, limit=4)
    'xxxx'
    """
    kept = text.strip()
    return kept[-limit:]


class CommandRunner(QObject):
    """
    Run one program without freezing the window, handing on what it prints as it prints it, and how it ended.

    Attributes
    ----------
    output : Signal
        Emitted with each piece of text the program prints, as it arrives. Its errors are mixed in with it.
    done : Signal
        Emitted once, with the exit code and everything the program printed. The exit code is -1 if the program could not be
        started, was stopped for taking too long, or crashed.

    Examples
    --------
    >>> runner = CommandRunner()
    >>> runner.running
    False
    """

    output = Signal(str)
    done = Signal(int, str)

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Make a runner that has not started anything.

        Parameters
        ----------
        parent : QObject or None, default None
            The object that owns it.
        """
        super().__init__(parent)
        self._text = ""
        self._ended = False
        self._program = ""
        self._seconds = 0
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        environment = QProcessEnvironment.systemEnvironment()
        for name, value in QUIET.items():
            environment.insert(name, value)
        self._process.setProcessEnvironment(environment)
        self._process.readyReadStandardOutput.connect(self._read)
        self._process.finished.connect(self._finished)
        self._process.errorOccurred.connect(self._failed)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._timed_out)

    @property
    def running(self) -> bool:
        """
        Say whether a program has been started and has not yet ended.

        Returns
        -------
        bool
            True while it runs.
        """
        return self._process.state() != QProcess.ProcessState.NotRunning

    def start(
        self,
        program: str,
        *,
        arguments: list[str],
        seconds: int = 0,
    ) -> None:
        """
        Start a program.

        Parameters
        ----------
        program : str
            The program's path.
        arguments : list of str
            What to give it. Keyword-only.
        seconds : int, default 0
            Stop it if it has not ended by then; 0 lets it take as long as it takes. Keyword-only.

        Examples
        --------
        >>> import sys
        >>> runner = CommandRunner()
        >>> runner.start(sys.executable, arguments=["-c", "import time; time.sleep(30)"])
        >>> runner.stop()
        >>> runner.running
        False
        """
        self._program, self._text, self._ended, self._seconds = program, "", False, seconds
        self._process.start(program, arguments)
        if seconds and not self._ended:
            self._timer.start(seconds * 1000)

    def stop(self) -> None:
        """
        Stop the program, if it is running, without announcing that it has ended.

        Examples
        --------
        >>> CommandRunner().stop()
        """
        self._ended = True
        self._timer.stop()
        if self.running:
            self._process.kill()
            self._process.waitForFinished(2000)

    def _read(self) -> None:
        """Pass on what the program has printed since the last time."""
        chunk = bytes(self._process.readAllStandardOutput().data()).decode(errors="replace")
        if chunk and not self._ended:
            self._text += chunk
            self.output.emit(chunk)

    def _finished(  # noqa: PLR0917  (a Qt slot: the signal passes positional arguments)
        self,
        code: int,
        status: QProcess.ExitStatus,
    ) -> None:
        """
        Note that the program has ended.

        Parameters
        ----------
        code : int
            Its exit code.
        status : QProcess.ExitStatus
            Whether it ended by itself or crashed.
        """
        self._read()
        self._end(code if status == QProcess.ExitStatus.NormalExit else -1)

    def _failed(self, error: QProcess.ProcessError) -> None:
        """
        Note that the program could not be started.

        Parameters
        ----------
        error : QProcess.ProcessError
            What went wrong. Only a program that does not start is dealt with here; one that crashes ends through `_finished`.
        """
        if error == QProcess.ProcessError.FailedToStart:
            self._say(f"Could not start {self._program}.")
            self._end(-1)

    def _timed_out(self) -> None:
        """Stop a program that has taken too long, and say so."""
        if self._ended:
            return
        self._process.kill()
        self._say(f"There was no answer after {self._seconds} seconds.")
        self._end(-1)

    def _say(self, message: str) -> None:
        """
        Add a line of our own to what the program printed.

        Parameters
        ----------
        message : str
            The line.
        """
        if not self._ended:
            self._text += message + "\n"
            self.output.emit(message + "\n")

    def _end(self, code: int) -> None:
        """
        Announce the end, once.

        Parameters
        ----------
        code : int
            The exit code to announce.
        """
        if self._ended:
            return
        self._ended = True
        self._timer.stop()
        self.done.emit(code, self._text)


def saved_channel() -> str:
    """
    Return what the update check follows, as chosen in Settings.

    Returns
    -------
    str
        "releases" for the newest release, or "main" for the newest commit on the main branch; "releases" if nothing valid is
        saved.

    Examples
    --------
    >>> saved_channel()
    'releases'
    >>> save_channel("main")
    >>> saved_channel()
    'main'
    >>> save_channel("releases")
    """
    channel = text_value(store(), key="updates/channel", default=updates.RELEASES)
    return channel if channel in {updates.RELEASES, updates.MAIN} else updates.RELEASES


def save_channel(channel: str) -> None:
    """
    Remember what the update check follows.

    Parameters
    ----------
    channel : str
        "releases" or "main". Anything else is saved as "releases".

    Examples
    --------
    >>> save_channel("nonsense")
    >>> saved_channel()
    'releases'
    """
    store().setValue("updates/channel", channel if channel in {updates.RELEASES, updates.MAIN} else updates.RELEASES)


class WaitDialog(QDialog):
    """
    A small window with a bar that keeps moving and a Cancel button, shown while something is asked for.

    Attributes
    ----------
    ended : bool
        Whether the asking has ended, by an answer, a failure or a cancel.
    canceled : bool
        Whether the person canceled it.
    """

    def __init__(
        self,
        parent: QWidget | None,
        *,
        text: str,
    ) -> None:
        """
        Build the window.

        Parameters
        ----------
        parent : QWidget or None
            The window it belongs to.
        text : str
            What is being asked for. Keyword-only.
        """
        super().__init__(parent)
        self.setWindowTitle(CHECK_TITLE)
        self.setModal(True)
        self.ended = False
        self.canceled = False
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(text))
        bar = QProgressBar()
        bar.setRange(0, 0)
        bar.setTextVisible(False)
        bar.setMinimumWidth(px(320))
        lay.addWidget(bar)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        lay.addWidget(cancel, alignment=Qt.AlignmentFlag.AlignRight)

    def reject(self) -> None:
        """Cancel the asking."""
        if not self.ended:
            self.canceled = True
            self.ended = True
            self._stop()
        super().reject()

    def _stop(self) -> None:
        """Stop what is being asked for. A window that asks for something overrides this."""


class CheckDialog(WaitDialog):
    """
    A waiting window while the address Alto came from is asked for the newest commit of its main branch.

    Attributes
    ----------
    commit : str
        The newest commit, once it is known; empty if it could not be found out.
    error : str
        What went wrong, if there is no commit.
    runner : CommandRunner
        The program that does the asking.
    """

    def __init__(
        self,
        parent: QWidget | None,
        *,
        source: Source,
        git: str,
    ) -> None:
        """
        Build the window; it asks nothing until `run` is called.

        Parameters
        ----------
        parent : QWidget or None
            The window it belongs to.
        source : Source
            Where the running copy of Alto came from. Keyword-only.
        git : str
            The path of the `git` program. Keyword-only.
        """
        super().__init__(parent, text="Asking for the newest version…")
        self.commit = ""
        self.error = ""
        self._command = updates.check_command(source, git=git)
        self.runner = CommandRunner(self)
        self.runner.done.connect(self._answered)

    def run(self) -> None:
        """
        Ask, showing the window until there is an answer.

        Examples
        --------
        >>> # noinspection PyTypeChecker
        >>> CheckDialog(None, source=Source("https://example.org/a.git", commit="abc1234"), git="git").canceled
        False
        """
        program, arguments = self._command
        self.runner.start(program, arguments=arguments, seconds=CHECK_SECONDS)
        if not self.ended:
            self.exec()

    def _stop(self) -> None:
        """Stop the program that is asking."""
        self.runner.stop()

    def _answered(  # noqa: PLR0917  (a Qt slot: the signal passes positional arguments)
        self,
        code: int,
        text: str,
    ) -> None:
        """
        Take the answer and close the window.

        Parameters
        ----------
        code : int
            The program's exit code.
        text : str
            What it printed.
        """
        self.ended = True
        self.commit = (parse_ls_remote(text) if code == 0 else None) or ""
        if not self.commit:
            self.error = brief(text) or "The address did not answer."
        self.accept()


class ReleaseFetcher(QObject):
    """
    Ask GitHub for the latest release on another thread, so that the window never freezes while it waits.

    Attributes
    ----------
    done : Signal
        Emitted once, with the HTTP status (0 if GitHub was not reached) and the answer or the reason there was none.

    Examples
    --------
    >>> ReleaseFetcher().cancel()
    """

    done = Signal(int, str)

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Make a fetcher that has not asked anything.

        Parameters
        ----------
        parent : QObject or None, default None
            The object that owns it.
        """
        super().__init__(parent)
        self._canceled = False

    def start(self, *, seconds: int) -> None:
        """
        Start asking.

        Parameters
        ----------
        seconds : int
            How long to wait for GitHub. Keyword-only.
        """
        self._canceled = False
        threading.Thread(target=self._work, args=(seconds,), daemon=True).start()

    def cancel(self) -> None:
        """Stop caring about the answer; the thread ends by itself when GitHub answers or the time is up."""
        self._canceled = True

    def _work(self, seconds: int) -> None:
        """
        Ask, on the thread, and hand the answer back to the window's thread through the signal.

        Parameters
        ----------
        seconds : int
            How long to wait for GitHub.
        """
        status, text = updates.fetch_text(updates.RELEASES_API, seconds=seconds)
        if not self._canceled:
            try:
                self.done.emit(status, text)
            except RuntimeError:  # the window was closed, and with it this object, while the thread waited
                return


class DailyReleaseCheck(QTimer):
    """
    Check for published releases in the background and honor the learner’s reminder choice at the exercise grid.

    Examples
    --------
    Reopening Alto on the same afternoon reuses the previous check time.
    """

    def __init__(self, window: MainWindow) -> None:
        """
        Schedule the first check after the startup window has opened.

        Parameters
        ----------
        window : MainWindow
            The window that owns the timer and presents upgrade offers.

        Examples
        --------
        Source checkouts continue to use Git for updates.
        """
        super().__init__(window)
        self.window = window
        self.source = updates.installed_source()
        self.kind = updates.install_kind(self.source, tool=updates.is_tool_install(), frozen=updates.is_frozen())
        self.pending: Release | None = None
        self.fetcher = ReleaseFetcher(self)
        self.fetcher.done.connect(self._received)
        self.setSingleShot(True)
        self.timeout.connect(self._check)
        if updates.cannot_update(self.kind) is None:
            self.start(0)

    def _check(self) -> None:
        """Wait until a check is due or a pending release can be offered."""
        saved = store()
        if not saved.value("updates/automatic", True, type=bool) or (
            self.kind is InstallKind.SCRIPT and saved_channel() == updates.MAIN
        ):
            self.pending = None
            self.start(60_000)
            return
        now = int(time.time())
        try:
            elapsed = now - int_value(saved, key="updates/lastReleaseCheck", default=0)
        except (ValueError, OverflowError):
            elapsed = DAY_SECONDS
        remaining = DAY_SECONDS - elapsed if 0 <= elapsed < DAY_SECONDS else 0
        if self.pending is None and remaining:
            self.start(remaining * 1000)
            return
        if (
            self.window.stack.currentWidget() is not self.window.home
            or not self.window.isActiveWindow()
            or QApplication.activeModalWidget()
        ):
            self.start(15_000)
            return
        if self.pending is not None:
            release = self.pending
            reminder = text_value(saved, key=f"updates/releaseReminder/{release.version}", default="")
            if reminder.isascii() and reminder.isdecimal() and len(reminder) <= 12:
                delay = int(reminder) - now
                if 0 < delay <= DAY_SECONDS:
                    self.start(delay * 1000)
                    return
            self.pending = None
            if reminder != "skip":
                offer_release(
                    self.window,
                    release=release,
                    kind=self.kind,
                    source=self.source,
                    installed=updates.installed_version(),
                    restart=self.window.restart_app,
                    quit_app=QApplication.quit,
                )
            self.start(max(1, remaining) * 1000)
            return
        saved.setValue("updates/lastReleaseCheck", now)
        self.fetcher.start(seconds=RELEASE_SECONDS)

    def _received(self, status: int, text: str) -> None:  # noqa: PLR0917 (Qt signal arguments)
        """
        Queue a newer release for the next safe opportunity to present it.

        Parameters
        ----------
        status : int
            HTTP status from the background fetch.
        text : str
            GitHub response or network error message.
        """
        answer = updates.release_answer(status, text=text)
        if isinstance(answer, Release) and updates.is_newer(answer.version, installed=updates.installed_version()):
            self.pending = answer
        self._check()


class ReleaseDialog(WaitDialog):
    """
    A waiting window while GitHub is asked for the latest release.

    Attributes
    ----------
    release : Release or None
        The latest release, once it is known; None if it could not be found out.
    error : str
        What went wrong, if there is no release.
    fetcher : ReleaseFetcher
        What does the asking.
    """

    def __init__(self, parent: QWidget | None) -> None:
        """
        Build the window; it asks nothing until `run` is called.

        Parameters
        ----------
        parent : QWidget or None
            The window it belongs to.
        """
        super().__init__(parent, text="Asking GitHub for the latest release…")
        self.release: Release | None = None
        self.error = ""
        self.fetcher = ReleaseFetcher(self)
        self.fetcher.done.connect(self._answered)

    def run(self) -> None:
        """
        Ask, showing the window until there is an answer.

        Examples
        --------
        >>> # noinspection PyTypeChecker
        >>> ReleaseDialog(None).canceled
        False
        """
        self.fetcher.start(seconds=RELEASE_SECONDS)
        if not self.ended:
            self.exec()

    def _stop(self) -> None:
        """Stop caring about the answer."""
        self.fetcher.cancel()

    def _answered(  # noqa: PLR0917  (a Qt slot: the signal passes positional arguments)
        self,
        status: int,
        text: str,
    ) -> None:
        """
        Take the answer and close the window.

        Parameters
        ----------
        status : int
            The HTTP status, or 0 if GitHub was not reached.
        text : str
            The answer, or the reason there was none.
        """
        self.ended = True
        answer = updates.release_answer(status, text=text)
        if isinstance(answer, Release):
            self.release = answer
        else:
            self.error = answer
        self.accept()


class UpdateDialog(QDialog):
    """
    The window that shows an update being installed: a bar that keeps moving, what `uv` prints, and then what comes next.

    It cannot be closed while the update runs, because stopping it half way could leave the installed copy broken. When it has
    finished it says so, and its one button closes it. After a successful update the caller restarts Alto.

    Attributes
    ----------
    status : QLabel
        What is happening.
    bar : QProgressBar
        A bar that keeps moving while the update runs, and fills when it has succeeded.
    log : QPlainTextEdit
        What `uv` prints, as it prints it.
    button : QPushButton
        Enabled when the update has ended.
    ended : bool
        Whether the update has ended.
    succeeded : bool
        Whether it ended well.
    runner : CommandRunner
        The program that does the update.
    """

    def __init__(
        self,
        parent: QWidget | None,
        *,
        command: tuple[str, list[str]],
    ) -> None:
        """
        Build the window; the update does not start until `run` is called.

        Parameters
        ----------
        parent : QWidget or None
            The window it belongs to.
        command : tuple of str and list of str
            The program that installs the update and its arguments. Keyword-only.
        """
        super().__init__(parent)
        self.setWindowTitle(UPDATE_TITLE)
        self.setModal(True)
        self.ended = False
        self.succeeded = False
        self._command = command
        lay = QVBoxLayout(self)
        self.status = QLabel("Updating Alto. This can take a minute.")
        self.status.setWordWrap(True)
        lay.addWidget(self.status)
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)
        self.bar.setTextVisible(False)
        lay.addWidget(self.bar)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(500)
        self.log.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.log.setAccessibleName("Update details")
        self.log.setMinimumSize(px(520), px(180))
        lay.addWidget(self.log, 1)
        self.button = QPushButton("OK")
        self.button.setEnabled(False)
        self.button.clicked.connect(self._pressed)
        lay.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignRight)
        self.runner = CommandRunner(self)
        self.runner.output.connect(self._show)
        self.runner.done.connect(self._ended)

    def run(self) -> bool:
        """
        Install the update, showing the window until the person has read how it went.

        Returns
        -------
        bool
            True if it succeeded and OK was pressed, so Alto should restart.

        Examples
        --------
        >>> # noinspection PyTypeChecker
        >>> UpdateDialog(None, command=("uv", ["tool", "install", "alto"])).succeeded
        False
        """
        program, arguments = self._command
        self.runner.start(program, arguments=arguments)
        return self.exec() == QDialog.DialogCode.Accepted and self.succeeded

    def reject(self) -> None:
        """Close the window, but not while the update is running."""
        if self.ended:
            super().reject()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Refuse to close while the update is running.

        Parameters
        ----------
        event : QCloseEvent
            The request to close.
        """
        if self.ended:
            super().closeEvent(event)
        else:
            event.ignore()

    def _show(self, chunk: str) -> None:
        """
        Add what `uv` printed to the log.

        Parameters
        ----------
        chunk : str
            The text.
        """
        self.log.moveCursor(QTextCursor.MoveOperation.End)
        self.log.insertPlainText(chunk)
        self.log.ensureCursorVisible()

    def _ended(self, code: int) -> None:
        """
        Say how the update went, and let the window be closed.

        Parameters
        ----------
        code : int
            The exit code of `uv`. What it printed is already in the log.
        """
        self.ended = True
        self.succeeded = code == 0
        self.bar.setRange(0, 1)
        self.bar.setValue(1 if self.succeeded else 0)
        if self.succeeded:
            self.status.setText("Alto has been updated.\n\nIt will restart when you press OK.")
        else:
            self.status.setText(
                "The update did not finish, and Alto will not restart. The details are below. "
                "You can try again from the menu, or run: sh scripts/alto-install.sh update",
            )
            self.button.setText("Close")
        self.button.setEnabled(True)
        self.button.setFocus()

    def _pressed(self) -> None:
        """Close the window: with success if the update worked, so that Alto restarts."""
        if self.succeeded:
            self.accept()
        else:
            self.reject()


def check_for_updates(
    parent: QWidget,
    *,
    restart: Callable[[], None],
    quit_app: Callable[[], None] = QApplication.quit,
) -> None:
    """
    Ask whether a newer Alto is available and, if the person agrees, install it and restart.

    What is asked depends on the copy: one run from a source folder is told how it is updated; a packaged copy asks for the
    latest release and is offered its download page; one installed with the script follows what Settings says, the latest release
    or the main branch, and can install it.

    Parameters
    ----------
    parent : QWidget
        The window the questions are asked over.
    restart : Callable
        What to do after a successful update to start the new version in place of this one. Keyword-only.
    quit_app : Callable, default QApplication.quit
        What to do to close Alto once an update has been handed to the program that installs it, which is how a packaged copy is
        replaced. Keyword-only.

    Examples
    --------
    >>> check_for_updates  # doctest: +SKIP
    """
    source = updates.installed_source()
    kind = updates.install_kind(source, tool=updates.is_tool_install(), frozen=updates.is_frozen())
    reason = updates.cannot_update(kind)
    if reason is not None:
        QMessageBox.information(parent, CHECK_TITLE, reason)
        return
    if kind is InstallKind.PACKAGE or source is None or saved_channel() == updates.RELEASES:
        check_release(parent, kind=kind, source=source, restart=restart, quit_app=quit_app)
    else:
        check_main(parent, source=source, restart=restart)


def check_release(
    parent: QWidget,
    *,
    kind: InstallKind,
    source: Source | None,
    restart: Callable[[], None],
    quit_app: Callable[[], None],
) -> None:
    """
    Ask GitHub for the latest release and compare it with the version that is running.

    Parameters
    ----------
    parent : QWidget
        The window the questions are asked over.
    kind : InstallKind
        What kind of copy is running: a packaged one is offered a download page, and one installed with the script is offered
        the update. Keyword-only.
    source : Source or None
        Where the running copy came from; None for a packaged copy. Keyword-only.
    restart : Callable
        What to do after a successful update. Keyword-only.
    quit_app : Callable
        What to do to close Alto once an update has been handed to the program that installs it. Keyword-only.

    Examples
    --------
    >>> check_release  # doctest: +SKIP
    """
    asking = ReleaseDialog(parent)
    asking.run()
    if asking.canceled:
        return
    release = asking.release
    if release is None:
        show = QMessageBox.information if asking.error == updates.NO_RELEASE else QMessageBox.warning
        show(parent, CHECK_TITLE, asking.error)
        return
    installed = updates.installed_version()
    if not updates.is_newer(release.version, installed=installed):
        QMessageBox.information(parent, CHECK_TITLE, f"Alto is up to date ({installed}).")
        return
    offer_release(parent, release=release, kind=kind, source=source, installed=installed, restart=restart, quit_app=quit_app)


def offer_release(
    parent: QWidget,
    *,
    release: Release,
    kind: InstallKind,
    source: Source | None,
    installed: str,
    restart: Callable[[], None],
    quit_app: Callable[[], None],
) -> None:
    """
    Ask whether to upgrade using the installation's supported update path.

    Parameters
    ----------
    parent : QWidget
        Window that owns the upgrade prompt.
    release : Release
        Published release to offer.
    kind : InstallKind
        Installation type.
    source : Source or None
        Repository used by a script installation.
    installed : str
        Current version.
    restart : Callable
        Restart a script installation after upgrading.
    quit_app : Callable
        Close a packaged copy after handing off to its installer.

    Examples
    --------
    A manual check can offer a version the learner previously declined.
    """
    packaged = kind is InstallKind.PACKAGE or source is None
    target = selfupdate.self_update_target() if packaged and updates.UPDATE_PUBLIC_KEYS else None
    download_page = packaged and target is None
    question = (
        f"Alto {release.version} is available (you have {installed}).\n\nOpen the page where it can be downloaded?"
        if download_page
        else f"An update is available ({installed} → {release.version}).\n\nUpdate now?"
    )
    box = QMessageBox(QMessageBox.Icon.Question, CHECK_TITLE, question, parent=parent)
    box.setOption(QMessageBox.Option.DontUseNativeDialog)
    # A single role keeps these choices in reading order across Qt platform layouts.
    role = QMessageBox.ButtonRole.ActionRole
    yes = box.addButton("Yes", role)
    no = box.addButton("No", role)
    skip = box.addButton("Don't remind me again", role)
    box.setDefaultButton(yes)
    box.setEscapeButton(no)
    box.exec()
    choice = box.clickedButton()
    reminder_key = f"updates/releaseReminder/{release.version}"
    if choice is skip:
        store().setValue(reminder_key, "skip")
        return
    store().setValue(reminder_key, str(int(time.time()) + DAY_SECONDS))
    if choice is not yes:
        return
    if target is not None:
        update_package(parent, release=release, target=target, quit_app=quit_app)
    elif download_page:
        QDesktopServices.openUrl(QUrl(release.url))
    else:
        assert source is not None
        install(parent, source=source, tag=release.tag, restart=restart)


def check_main(
    parent: QWidget,
    *,
    source: Source,
    restart: Callable[[], None],
) -> None:
    """
    Ask the address Alto came from for the newest commit on its main branch and compare it with the one that is running.

    Parameters
    ----------
    parent : QWidget
        The window the questions are asked over.
    source : Source
        Where the running copy came from. Keyword-only.
    restart : Callable
        What to do after a successful update. Keyword-only.

    Examples
    --------
    >>> check_main  # doctest: +SKIP
    """
    git = updates.find_program("git")
    if git is None:
        QMessageBox.warning(parent, CHECK_TITLE, NO_GIT)
        return
    check = CheckDialog(parent, source=Source(source.url, commit=source.commit), git=git)  # the default branch, not a tag
    check.run()
    if check.canceled:
        return
    latest = check.commit
    if not latest:
        QMessageBox.warning(parent, CHECK_TITLE, f"Alto could not find out whether there is a newer version.\n\n{check.error}")
        return
    if latest == source.commit:
        QMessageBox.information(parent, CHECK_TITLE, f"Alto is up to date ({short(source.commit)}).")
        return
    asked = QMessageBox.question(
        parent,
        CHECK_TITLE,
        f"An update is available on the main branch ({short(source.commit)} \u2192 {short(latest)}).\n\nUpdate now?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes,
    )
    if asked == QMessageBox.StandardButton.Yes:
        install(parent, source=source, tag=None, restart=restart)


def install(
    parent: QWidget,
    *,
    source: Source,
    tag: str | None,
    restart: Callable[[], None],
) -> None:
    """
    Install a release, or the newest commit of the main branch, showing the progress, and restart if it worked.

    Parameters
    ----------
    parent : QWidget
        The window the progress is shown over.
    source : Source
        Where the running copy came from. Keyword-only.
    tag : str or None
        The release to install, such as "v0.1.0"; None for the newest commit of the main branch. Keyword-only.
    restart : Callable
        What to do after a successful update. Keyword-only.

    Examples
    --------
    >>> install  # doctest: +SKIP
    """
    uv = updates.find_program("uv")
    if uv is None:
        QMessageBox.warning(parent, UPDATE_TITLE, NO_UV)
        return
    if UpdateDialog(parent, command=updates.install_command(source, uv=uv, tag=tag)).run():
        restart()


def update_package(
    parent: QWidget,
    *,
    release: updates.Release,
    target: selfupdate.Target,
    quit_app: Callable[[], None],
) -> None:
    """
    Replace a packaged copy after the user agrees: download and check it, say that Alto will restart, and hand over.

    Parameters
    ----------
    parent : QWidget
        The window the questions are asked over.
    release : updates.Release
        The newer release. Keyword-only.
    target : selfupdate.Target
        The copy that will be replaced. Keyword-only.
    quit_app : Callable
        What to do to close Alto once the update has been handed to the program that installs it. Keyword-only.

    Examples
    --------
    >>> update_package  # doctest: +SKIP
    """
    prepared = PackageUpdateDialog(parent, release=release, target=target).run()
    if prepared is None:
        return
    try:
        selfupdate.start_handoff(prepared, target=target)
    except (selfupdate.UpdateError, OSError) as error:
        shutil.rmtree(prepared.work, ignore_errors=True)
        QMessageBox.warning(parent, UPDATE_TITLE, f"The update could not be started: {error}\n\nNothing was installed.")
        return
    quit_app()
