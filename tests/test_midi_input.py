"""MIDI source selection and pitch grading in Interval Construction."""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication

from alto.exercises.library import IntervalConstruction
from alto.theory.pitch import Note
from alto.ui.exercise_view import ExerciseView
from alto.ui.midi_input import MidiInput


@pytest.mark.skipif(sys.platform != "linux", reason="ALSA sequencer input")
def test_play_interval(app: QApplication, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """
    Deliver ALSA events through the source menu, grade a played note, and disconnect on navigation.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Override the device command for this exercise.
    tmp_path : Path
        Directory for the simulated ALSA sequencer.
    """
    program = tmp_path / "aseqdump"
    program.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = '-l' ]; then\n"
        "  echo '  0:0   System     Timer'\n"
        "  echo '128:0   VMPK       Output'\n"
        "else\n"
        "  exec cat\n"
        "fi\n",
    )
    program.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ["PATH"])
    view = ExerciseView(IntervalConstruction())
    view.settings_panel.next_question_mode = "Wait"
    view.show()
    app.processEvents()
    q = view.question
    q.construct, q.accept = Note.parse("D4"), ("G♭4",)
    midi = view.midi_input
    assert midi is not None
    view.hide()
    view._place_midi(66)
    assert view.total == 0
    view.show()
    view.question = None
    view._place_midi(66)
    assert view.total == 0
    view.question = q
    view._place_midi(54)
    assert view.correct == 0 and view.total == 1
    app.processEvents()
    view.next_question()
    q = view.question
    q.construct, q.accept = Note.parse("D4"), ("G♭4",)
    midi._refresh()
    off, source = midi.menu().actions()
    assert off.isChecked() and source.text() == "VMPK Output (128:0)"
    source.trigger()
    process = midi._process
    assert process.waitForStarted(1000)
    process.write(b"128:0 Note off 1, note 66\n128:0 Note on 1, note 66, velocity 0\n128:0 Control change 1, controller 2\n")
    process.write(b"128:0 Note on 1, note 66, ")
    assert process.waitForReadyRead(2000)
    assert view.total == 1
    process.write(b"velocity 100\n")
    assert process.waitForReadyRead(2000)
    assert view.answered and (view.correct, view.total) == (1, 2)
    assert q.placement_columns(Note.parse("Gb4")) == view.input_staff.columns
    process.write(b"  0:1 Port unsubscribed     128:0 -> 130:0\n")
    assert process.waitForReadyRead(2000)
    assert "disconnected" in midi.toolTip()
    midi._refresh()
    assert "disconnected" in midi.menu().actions()[1].text()
    midi.menu().actions()[-1].trigger()
    assert process.waitForStarted(1000)
    process.closeWriteChannel()
    assert process.waitForFinished(2000)
    assert "unavailable" in midi.toolTip()
    midi._refresh()
    midi.menu().actions()[-1].trigger()
    assert process.waitForStarted(1000)
    view.hide()
    assert not midi._port and process.processId() == 0


def test_unavailable_sources(app: QApplication) -> None:
    """
    Explain missing ALSA utilities, unavailable sequencers, and empty device lists in the menu.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    midi = MidiInput()
    for failure, label in (
        (FileNotFoundError(), "Install alsa-utils"),
        (subprocess.TimeoutExpired("aseqdump", 1), "Could not list"),
    ):
        with patch("alto.ui.midi_input.subprocess.run", side_effect=failure):
            midi._refresh()
            assert label in midi.menu().actions()[-1].text()
    with patch("alto.ui.midi_input.subprocess.run", return_value=subprocess.CompletedProcess([], 0, b" 0:0 System Timer\n")):
        midi._refresh()
        assert midi.menu().actions()[-1].text() == "No MIDI inputs found"
