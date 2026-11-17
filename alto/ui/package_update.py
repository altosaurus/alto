"""
The window that updates a packaged copy of Alto: the download and its checks with their progress, then what happens next.

The work is in `alto.selfupdate`, which has no Qt, and runs on another thread here so that the window keeps moving. Until the
download has been checked nothing has been installed, and Cancel (or closing the window) throws it away. When it is ready the
window says that Alto will close, install the update and open again, and OK hands over; the caller starts the installer and quits.

Examples
--------
>>> from alto.updates import Release
>>> PackageUpdateDialog  # doctest: +ELLIPSIS
<class '...PackageUpdateDialog'>
"""

from __future__ import annotations

import platform
import shutil
import threading
from pathlib import Path

from PySide6.QtCore import (
    QObject,
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from alto import (
    selfupdate,
    updates,
)
from alto.selfupdate import (
    Prepared,
    Target,
    UpdateCanceled,
    UpdateError,
)
from alto.updates import Release

TITLE = "Update Alto"
READY = "The update is ready. Alto will close, install it and open again when you press OK."


class UpdatePreparer(QObject):
    """
    Download and check an update on another thread, and report how it goes through signals.

    Attributes
    ----------
    status : Signal
        Emitted with what is being done ("Checking the signature…").
    progress : Signal
        Emitted with the bytes received so far and the total (0 if it is not known), while the file downloads.
    done : Signal
        Emitted once at the end, with 0 if the update is ready (see `prepared`) or 1 if it failed, and the reason. Nothing is
        emitted if the person canceled.
    prepared : Prepared or None
        The checked update, once it is ready.

    Examples
    --------
    >>> UpdatePreparer().prepared is None
    True
    """

    status = Signal(str)
    progress = Signal(int, int)
    done = Signal(int, str)

    def __init__(self, parent: QObject | None = None) -> None:
        """
        Make a preparer that has not started.

        Parameters
        ----------
        parent : QObject or None, default None
            The object that owns it.
        """
        super().__init__(parent)
        self._canceled = False
        self.prepared: Prepared | None = None

    def start(
        self,
        *,
        release: Release,
        target: Target,
        work: Path,
        keys: tuple[str, ...],
    ) -> None:
        """
        Start downloading and checking.

        Parameters
        ----------
        release : Release
            The release to install.
        target : Target
            The copy that will be replaced.
        work : Path
            An empty folder to work in.
        keys : tuple of str
            The public keys (base64) a signature may be made with.
        """
        self._canceled = False
        arguments = {"release": release, "target": target, "work": work, "keys": keys}
        threading.Thread(target=self._work, kwargs=arguments, daemon=True).start()

    def cancel(self) -> None:
        """Stop, at the next chance, and say nothing more."""
        self._canceled = True

    def is_canceled(self) -> bool:
        """
        Say whether the person has canceled.

        Returns
        -------
        bool
            True once `cancel` has been called.

        Examples
        --------
        >>> UpdatePreparer().is_canceled()
        False
        """
        return self._canceled

    def _say(
        self,
        code: int,
        *,
        message: str,
    ) -> None:
        """
        Announce the end, unless the person canceled or the window is gone.

        Parameters
        ----------
        code : int
            0 for ready, 1 for failed.
        message : str
            The reason, if it failed. Keyword-only.
        """
        if self._canceled:
            return
        try:
            self.done.emit(code, message)
        except RuntimeError:  # the window was closed, and with it this object, while the thread worked
            return

    def _work(
        self,
        *,
        release: Release,
        target: Target,
        work: Path,
        keys: tuple[str, ...],
    ) -> None:
        """
        Do the work, on the thread.

        Parameters
        ----------
        release : Release
            The release to install. Keyword-only.
        target : Target
            The copy that will be replaced. Keyword-only.
        work : Path
            An empty folder to work in. Keyword-only.
        keys : tuple of str
            The public keys a signature may be made with. Keyword-only.
        """
        try:
            self.prepared = selfupdate.prepare_update(
                release,
                target=target,
                work=work,
                keys=keys,
                machine=platform.machine(),
                base=updates.DOWNLOAD_BASE,
                status=self._emit_status,
                progress=self._emit_progress,
                canceled=self.is_canceled,
            )
        except UpdateCanceled:
            shutil.rmtree(work, ignore_errors=True)  # the window removes it too, but this thread may still have been writing
        except UpdateError as error:
            shutil.rmtree(work, ignore_errors=True)
            self._say(1, message=str(error))
        except Exception as error:  # noqa: BLE001  (anything at all must end up in the window, not in a thread that nobody sees)
            shutil.rmtree(work, ignore_errors=True)
            self._say(1, message=f"The update could not be prepared: {error}")
        else:
            if self._canceled:
                shutil.rmtree(work, ignore_errors=True)
            self._say(0, message="")

    def _emit_status(self, text: str) -> None:
        """
        Pass on what is being done.

        Parameters
        ----------
        text : str
            What is being done.
        """
        if not self._canceled:
            try:
                self.status.emit(text)
            except RuntimeError:
                return

    def _emit_progress(  # noqa: PLR0917  (a progress callback, which is called with two numbers)
        self,
        done: int,
        total: int,
    ) -> None:
        """
        Pass on how much has been downloaded.

        Parameters
        ----------
        done : int
            The bytes received so far.
        total : int
            The total, or 0 if it is not known.
        """
        if not self._canceled:
            try:
                self.progress.emit(done, total)
            except RuntimeError:
                return


class PackageUpdateDialog(QDialog):
    """
    The window that downloads and checks an update for a packaged copy, and then says what happens next.

    Attributes
    ----------
    status : QLabel
        What is happening.
    bar : QProgressBar
        The progress of the download; a bar that keeps moving while the size is not known.
    button : QPushButton
        Cancel while the update is being prepared, then OK if it is ready or Close if it failed.
    ended : bool
        Whether the preparing has ended, ready, failed or canceled.
    ready : bool
        Whether the update is downloaded and checked.
    canceled : bool
        Whether the person canceled.
    error : str
        Why it failed, if it did.
    preparer : UpdatePreparer
        What does the work.
    """

    def __init__(
        self,
        parent: QWidget | None,
        *,
        release: Release,
        target: Target,
    ) -> None:
        """
        Build the window; nothing is downloaded until `run` is called.

        Parameters
        ----------
        parent : QWidget or None
            The window it belongs to.
        release : Release
            The release to install. Keyword-only.
        target : Target
            The copy that will be replaced. Keyword-only.
        """
        super().__init__(parent)
        self.setWindowTitle(TITLE)
        self.setModal(True)
        self._release, self._target = release, target
        self._work: Path | None = None
        self.ended = False
        self.ready = False
        self.canceled = False
        self.error = ""
        lay = QVBoxLayout(self)
        self.status = QLabel(f"Getting Alto {release.version}…")
        self.status.setWordWrap(True)
        self.status.setMinimumWidth(380)
        lay.addWidget(self.status)
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)
        self.bar.setTextVisible(False)
        lay.addWidget(self.bar)
        self.button = QPushButton("Cancel")
        self.button.clicked.connect(self._pressed)
        lay.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignRight)
        self.preparer = UpdatePreparer(self)
        self.preparer.status.connect(self.status.setText)
        self.preparer.progress.connect(self._progressed)
        self.preparer.done.connect(self._finished)

    def run(self) -> Prepared | None:
        """
        Download and check the update, showing the window until the person has read how it went.

        Returns
        -------
        Prepared or None
            The update, if it is ready and OK was pressed; None if it failed or was canceled, in which case nothing is left
            behind.

        Examples
        --------
        >>> here = Target("linux", folder=Path("/x"), prefix=None)
        >>> # noinspection PyTypeChecker
        >>> PackageUpdateDialog(None, release=Release("0.1.0", tag="v0.1.0", url=""), target=here).ready
        False
        """
        selfupdate.remove_leftovers()
        work = selfupdate.new_work_folder()
        self._work = work
        self.preparer.start(release=self._release, target=self._target, work=work, keys=updates.UPDATE_PUBLIC_KEYS)
        accepted = self.exec() == QDialog.DialogCode.Accepted
        if accepted and self.ready and self.preparer.prepared is not None:
            return self.preparer.prepared
        self._discard()
        return None

    def reject(self) -> None:
        """Close the window; before the update is ready that cancels it."""
        if not self.ended:
            self.canceled = True
            self.ended = True
            self.preparer.cancel()
        super().reject()

    def _discard(self) -> None:
        """Remove what was downloaded."""
        if self._work is not None:
            shutil.rmtree(self._work, ignore_errors=True)

    def _progressed(  # noqa: PLR0917  (a Qt slot: the signal passes positional arguments)
        self,
        done: int,
        total: int,
    ) -> None:
        """
        Show how much has been downloaded.

        Parameters
        ----------
        done : int
            The bytes received so far.
        total : int
            The total, or 0 if it is not known.
        """
        if total > 0:
            self.bar.setRange(0, total)
            self.bar.setValue(min(done, total))
            self.status.setText(f"Downloading… {done / 1_048_576:.0f} of {total / 1_048_576:.0f} MB")

    def _finished(  # noqa: PLR0917  (a Qt slot: the signal passes positional arguments)
        self,
        code: int,
        message: str,
    ) -> None:
        """
        Say how it went, and let the window be closed.

        Parameters
        ----------
        code : int
            0 if the update is ready, 1 if it failed.
        message : str
            Why it failed.
        """
        self.ended = True
        self.ready = code == 0
        self.bar.setRange(0, 1)
        self.bar.setValue(1 if self.ready else 0)
        if self.ready:
            self.status.setText(READY)
            self.button.setText("OK")
        else:
            self.error = message
            self.status.setText(f"{message}\n\nNothing was installed. You can try again from the menu.")
            self.button.setText("Close")
        self.button.setFocus()

    def _pressed(self) -> None:
        """Cancel the update while it is being prepared; once it is ready, close the window with OK meaning install it."""
        if self.ready:
            self.accept()
        else:
            self.reject()
