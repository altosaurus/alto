"""
The scale teaching diagrams stay consistent with the exercise's musical
data.
"""

import pytest
from PySide6.QtWidgets import QApplication

from alto.audio import sounds
from alto.lessons.scale_identification import (
    SCALE_IDENTIFICATION,
    SCALE_PATTERNS,
)
from alto.ui.lesson import StepView
from alto.ui.reference import ScaleReferencePanel
from alto.ui.scale_explorer import ScaleExplorer


def test_transposition_preserves_patterns(app: QApplication) -> None:
    """
    Every supported tonic and mode has the expected gaps and closes at
    the octave.

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
            assert (
                " ".join(button.text() for button in explorer.steps) == pattern
            )
            assert explorer.notes[-1].midi - explorer.notes[0].midi == 12


def test_gap_selection_plays_and_highlights_the_same_pair(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A harmonic-minor augmented second highlights the exact notes sent to
    playback.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces playback dependencies for this test.
    """
    played = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(
        sounds,
        "play_notes",
        lambda columns, **kwargs: played.append(
            ([col[0].midi for col in columns], kwargs),
        ),
    )
    explorer = ScaleExplorer(scale="Harmonic minor", tonic="A4")
    explorer.steps[5].click()
    assert list(explorer.staff.column_colors) == [5, 6]
    midis, options = played[0]
    assert midis == [77, 80] and options["force"]
    options["on_step"](1)
    assert explorer.staff.column_colors[6] != explorer.staff.column_colors[5]
    explorer.mode.setCurrentText("Major (Ionian)")
    assert explorer.staff.column_colors == {}


def test_lesson_hear_uses_the_displayed_scale(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Play the transposed notes from the lesson's Hear button and
    highlight them in order.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Captures the rendered melody and its audio callbacks.
    """
    played = []
    monkeypatch.setattr(
        sounds,
        "play_notes",
        lambda columns, **options: played.append(
            ([col[0].midi for col in columns], options["on_step"]),
        ),
    )
    view = StepView(
        next(step for step in SCALE_IDENTIFICATION.steps if step.hear),
    )
    explorer = view.scale_explorer
    assert explorer is not None and view.hear_button is not None
    explorer.tonic.setCurrentText("D")
    view.hear_button.click()
    midis, highlight = played[0]
    assert (
        midis == [column[0].midi for column in explorer.staff.columns]
        and midis[0] == 62
    )
    for index in range(len(midis)):
        highlight(index)
        assert explorer.staff.column_colors[
            index
        ] == explorer.palette().highlight().color().lighter(160)
    highlight(None)
    assert all(
        color == explorer.palette().highlight().color()
        for color in explorer.staff.column_colors.values()
    )


def test_lesson_questions_have_fixed_visible_notation(
    app: QApplication,
) -> None:
    """
    Quiz diagrams provide notation without displaying the scale-type
    selector.

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
            assert not view.scale_explorer.mode.isVisibleTo(
                view.scale_explorer,
            )
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
