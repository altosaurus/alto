"""ALSA keyboard input for answering a question with a played pitch."""

from __future__ import annotations

import re
import subprocess

from PySide6.QtCore import QProcess, Signal
from PySide6.QtGui import QHideEvent
from PySide6.QtWidgets import QMenu, QToolButton

_PORT = re.compile(r"\s*(\d+:\d+)\s+(.+)")
_NOTE_ON = re.compile(
    rb"\s*\d+:\d+\s+Note on\s+\d+, note (\d+), velocity (\d+)\s*",
)


class MidiInput(QToolButton):
    """
    Select one ALSA sequencer source and forward its key presses on the
    Qt event loop.
    """

    note_pressed = Signal(int)

    def __init__(self) -> None:
        """Create the source menu with input turned off."""
        super().__init__()
        self.setText("MIDI")
        self.setAccessibleName("MIDI input")
        self.setToolTip("Choose a MIDI keyboard")
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(self)
        self.setMenu(menu)
        self._sources = menu
        menu.aboutToShow.connect(self._refresh)
        self._port = ""
        self._message = ""
        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._read)
        self._process.errorOccurred.connect(self._ended)
        self._process.finished.connect(self._ended)

    def _refresh(self) -> None:
        """
        List current sources each time the menu opens so newly connected
        keyboards appear.
        """
        menu = self._sources
        menu.clear()
        off = menu.addAction("Off")
        off.setCheckable(True)
        off.setChecked(not self._port)
        off.triggered.connect(self.disconnect_port)
        if self._message:
            menu.addAction(self._message).setEnabled(False)
        try:
            result = subprocess.run(
                ["aseqdump", "-l"],
                capture_output=True,
                timeout=1,
                check=True,
            )
        except FileNotFoundError:
            menu.addAction("Install alsa-utils to enable MIDI").setEnabled(
                False,
            )
            return
        except (OSError, subprocess.SubprocessError):
            menu.addAction("Could not list ALSA MIDI inputs").setEnabled(False)
            return
        found = False
        for line in result.stdout.decode(errors="replace").splitlines():
            match = _PORT.fullmatch(line)
            if match is None or match[1].startswith(
                "0:",
            ):  # ALSA timer and announcement ports
                continue
            port, name = match.groups()
            action = menu.addAction(f"{' '.join(name.split())} ({port})")
            action.setCheckable(True)
            action.setChecked(port == self._port)
            action.triggered.connect(
                lambda checked=False, address=port: self._listen(address),
            )
            found = True
        if not found:
            menu.addAction("No MIDI inputs found").setEnabled(False)

    def _listen(self, port: str) -> None:
        """
        Subscribe to the chosen source.

        Parameters
        ----------
        port : str
            ALSA client and port address from the menu.
        """
        self.disconnect_port()
        self._port = port
        self.setText("MIDI on")
        self.setToolTip(f"Listening to MIDI input {port}")
        self._process.start("aseqdump", ["-p", port])

    def _read(self) -> None:
        """
        Deliver complete note-on messages and handle removal of the
        selected source.
        """
        while self._port and self._process.canReadLine():
            line = self._process.readLine().data()
            if b"Port unsubscribed" in line:
                self.disconnect_port()
                self._message = (
                    "Keyboard disconnected. Choose an input to reconnect."
                )
                self.setToolTip(self._message)
                return
            match = _NOTE_ON.fullmatch(line)
            if match and int(match[2]) > 0 and 0 <= int(match[1]) <= 127:
                self.note_pressed.emit(int(match[1]))

    def _ended(self) -> None:
        """
        Show an interrupted connection on the button and allow another
        selection.
        """
        if self._port:
            self._port = ""
            self._message = (
                "MIDI input unavailable. Choose an input to reconnect."
            )
            self.setText("MIDI")
            self.setToolTip(self._message)

    def disconnect_port(self) -> None:
        """
        Release the input when the learner turns it off or leaves the
        exercise.
        """
        self._port = ""
        self._message = ""
        self.setText("MIDI")
        self.setToolTip("Choose a MIDI keyboard")
        if self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()
            self._process.waitForFinished(1000)
        if self._process.isOpen():
            self._process.readAllStandardOutput()

    def hideEvent(self, event: QHideEvent) -> None:
        """
        Release the MIDI connection when its input control disappears.

        Parameters
        ----------
        event : QHideEvent
            Notification that the control is hidden.
        """
        self.disconnect_port()
        super().hideEvent(event)
