"""MIDI source selection and pitch grading in music exercises."""

import os
import random
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QApplication

from alto import settings
from alto.exercises.library import (
    IntervalConstruction,
    NoteNames,
    ScaleConstruction,
)
from alto.theory.pitch import Note
from alto.ui.exercise_view import ExerciseView
from alto.ui.midi_input import MidiInput


@pytest.mark.skipif(sys.platform != "linux", reason="ALSA sequencer input")
def test_play_interval(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    Deliver ALSA events through the source menu, grade a played note,
    and disconnect on navigation.

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
    assert view.session.total == 0
    view.show()
    view.question = None
    view._place_midi(66)
    assert view.session.total == 0
    view.question = q
    view._place_midi(54)
    assert view.session.correct == 0 and view.session.total == 1
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
    process.write(
        b"128:0 Note off 1, note 66\n"
        b"128:0 Note on 1, note 66, velocity 0\n"
        b"128:0 Control change 1, controller 2\n",
    )
    process.write(b"128:0 Note on 1, note 66, ")
    assert process.waitForReadyRead(2000)
    assert view.session.total == 1
    process.write(b"velocity 100\n")
    assert process.waitForReadyRead(2000)
    assert view.session.answered and (
        view.session.correct,
        view.session.total,
    ) == (1, 2)
    assert (
        q.placement_columns(Note.parse("Gb4"))
        == view.question_view.note_input.columns
    )
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
    Explain missing ALSA utilities, unavailable sequencers, and empty
    device lists in the menu.

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
    with patch(
        "alto.ui.midi_input.subprocess.run",
        return_value=subprocess.CompletedProcess(
            [],
            0,
            b" 0:0 System Timer\n",
        ),
    ):
        midi._refresh()
        assert midi.menu().actions()[-1].text() == "No MIDI inputs found"


@pytest.mark.skipif(sys.platform != "linux", reason="ALSA sequencer input")
@pytest.mark.parametrize(
    ("naming", "octave"),
    [("solfege", False), ("degrees", True)],
)
def test_identify_played_note(
    app: QApplication,
    naming: str,
    octave: bool,
) -> None:
    """
    Score a played note in the chosen naming system and respect the
    question's octave requirement.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    naming : str
        Naming system for the answer buttons.
    octave : bool
        Whether the written octave is required.
    """
    cfg = settings.note_names
    cfg.naming, cfg.require_octave = naming, octave
    cfg.key_signatures, cfg.minor_keys = set(), {0}
    view = ExerciseView(NoteNames(), rng=random.Random(5))
    view.settings_panel.next_question_mode = "Wait"
    view.show()
    midi, q = view.midi_input, view.question
    assert midi is not None and q is not None
    target = q.staff[0][0]
    if octave:
        view.answer_controls.buttons[
            -1
        ].click()  # MIDI replaces an unfinished mouse answer.
    midi.note_pressed.emit(target.midi + (12 if octave else 1))
    assert (
        view.session.total == 1
        and view.session.missed
        and "Try again" in view.prompt.text()
    )
    midi.note_pressed.emit(target.midi + (0 if octave else 12))
    midi.note_pressed.emit(target.midi)
    assert (
        view.session.answered
        and view.session.attempts == 2
        and (view.session.correct, view.session.total) == (0, 1)
    )
    if octave:
        assert view._pending["octave"][0] == str(target.octave)
    view.close()


@pytest.mark.skipif(sys.platform != "linux", reason="ALSA sequencer input")
@pytest.mark.parametrize("steps", [True, False])
def test_play_scale(app: QApplication, steps: bool) -> None:
    """
    Place and undo played notes, then grade the scale with the
    configured octave and step rules.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    steps : bool
        Ask for manual whole and half steps after the notes.
    """
    cfg = settings.scale_construction
    cfg.motion, cfg.keys, cfg.modes = "descending", {-6}, {"Major (Ionian)"}
    cfg.steps, cfg.octave = steps, steps
    view = ExerciseView(ScaleConstruction(), rng=random.Random(5))
    view.settings_panel.next_question_mode = "Wait"
    view.show()
    midi, q = view.midi_input, view.question
    assert midi is not None and q is not None and q.construct_scale
    scale = q.construct_scale
    foreign = next(
        n
        for n in range(60, 72)
        if all(note.pitch_class != n % 12 for note in scale)
    )
    midi.note_pressed.emit(foreign)
    assert view.question_view.scale_input.notes[-1].midi == foreign
    view.answer_controls.placement.undo_button.click()
    assert not view.question_view.scale_input.notes
    for note in scale:
        midi.note_pressed.emit(note.midi + (0 if steps else 12))
    assert [n.name for n in view.question_view.scale_input.notes] == [
        n.name for n in scale
    ]
    if steps:
        assert not view.session.answered and q.construct_steps
        midi.note_pressed.emit(60)
        assert not view.question_view.scale_input.steps
        for step in q.construct_steps:
            view.step_buttons[step].click()
            view.answer_controls.placement.place_button.click()
        view.answer_controls.placement.answer_button.click()
    assert (
        view.session.answered
        and view.session.total == view.session.correct == 1
    )
    view.close()
