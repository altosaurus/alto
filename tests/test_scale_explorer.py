"""The scale teaching diagrams stay consistent with the exercise's musical data."""

import pytest
from PySide6.QtWidgets import QApplication

from alto.audio import sounds
from alto.lessons.scale_identification import SCALE_IDENTIFICATION, SCALE_PATTERNS
from alto.ui.lesson import StepView
from alto.ui.reference import ScaleReferencePanel
from alto.ui.scale_explorer import ScaleExplorer


def test_transposition_preserves_patterns(app: QApplication) -> None:
    """
    Every supported tonic and mode has the expected gaps and closes at the octave.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    explorer = ScaleExplorer()
    for mode, pattern in SCALE_PATTERNS.items():
        explorer.mode.setCurrentText(mode)
        for index in range(explorer.tonic.count()):
            explorer.tonic.setCurrentIndex(index)
            assert " ".join(button.text() for button in explorer.steps) == pattern
            assert explorer.notes[-1].midi - explorer.notes[0].midi == 12


def test_gap_selection_plays_and_highlights_the_same_pair(app: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    A harmonic-minor augmented second highlights the exact notes sent to playback.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces playback dependencies for this test.
    """
    played = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(sounds, "preview", lambda key, **kwargs: played.append(kwargs["midis"]))
    explorer = ScaleExplorer(scale="Harmonic minor", tonic="A4")
    explorer.steps[5].click()
    assert list(explorer.staff.column_colors) == [5, 6]
    assert played == [(77, 80)]
    explorer.mode.setCurrentText("Major (Ionian)")
    assert explorer.staff.column_colors == {}


def test_lesson_questions_have_fixed_visible_notation(app: QApplication) -> None:
    """
    Quiz diagrams provide notation without displaying the scale-type selector.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for step in SCALE_IDENTIFICATION.steps:
        view = StepView(step)
        assert view.scale_explorer is not None
        assert len(view.scale_explorer.notes) == 8
        if step.make_task is not None:
            assert not view.scale_explorer.mode.isVisibleTo(view.scale_explorer)
            assert view.task is not None
            assert view.task.correct in view.task.choices


def test_reference_opens_the_corresponding_lesson(app: QApplication) -> None:
    """
    The reference lesson link selects the scale lesson.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    panel = ScaleReferencePanel()
    requested = []
    panel.lesson_requested.connect(requested.append)
    panel.lesson_button.click()
    assert requested == [SCALE_IDENTIFICATION.key]
