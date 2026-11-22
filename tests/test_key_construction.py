"""
The key signature construction exercise.

Building the key signature of a named key with the fork: the question, the fork widget, the exercise screen and the settings.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import (
    QEvent,
    QPoint,
    QPointF,
    Qt,
)
from PySide6.QtGui import (
    QKeyEvent,
    QMouseEvent,
    QWheelEvent,
)
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QLabel

from alto import settings
from alto.exercises import REGISTRY
from alto.exercises.base import Question
from alto.exercises.library import (
    KeySignatureConstruction,
    KeySignatures,
)
from alto.learning import (
    Database,
    Learner,
)
from alto.theory.scales import format_key_signature
from alto.ui import exercise_settings as es
from alto.ui import settings_panel as sp
from alto.ui.exercise_view import ExerciseView
from alto.ui.home import (
    EXERCISE_ICONS,
    ExerciseCard,
)
from alto.ui.key_fork import (
    APEX_X,
    BOTTOM_Y,
    JOINT_X,
    MID_Y,
    STEM_X,
    TOP_Y,
    KeyFork,
    fork_path,
    node_position,
    path_between,
    route,
)
from alto.ui.question_preview import QuestionPreview
from alto.ui.store import store

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


def questions(
    n: int = 200,
    *,
    seed: int = 1,
    **choose: object,
) -> list[Question]:
    """
    `n` questions made with these settings (clefs, modes, keys).

    Parameters
    ----------
    n : int
        How many questions.
    seed : int
        The random seed.
    choose : object
        Key construction settings to change before asking.

    Returns
    -------
    list of Question
        The questions.
    """
    for name, value in choose.items():
        setattr(settings.key_construction, name, value)
    rng = random.Random(seed)
    return [KeySignatureConstruction().generate(rng) for _ in range(n)]


def press(
    fork: KeyFork,
    *,
    at: QPointF,
) -> None:
    """
    Click the fork with the left button.

    Parameters
    ----------
    fork : KeyFork
        The fork.
    at : QPointF
        Where to click, in the fork's coordinates.
    """
    fork.mousePressEvent(
        QMouseEvent(
            QEvent.Type.MouseButtonPress,
            at,
            at,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        ),
    )


def roll(
    fork: KeyFork,
    *,
    delta: int,
) -> None:
    """
    Turn the mouse wheel over the fork.

    Parameters
    ----------
    fork : KeyFork
        The fork.
    delta : int
        The wheel's angle delta: 120 is one notch up.
    """
    here = QPointF(100, 50)
    fork.wheelEvent(
        QWheelEvent(
            here,
            here,
            QPoint(0, 0),
            QPoint(0, delta),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            False,
        ),
    )


# -- the question -----------------------------------------------------------------------------------------------------


def test_the_exercise_is_registered_in_scales_and_keys_and_is_silent() -> None:
    """
    Check that the exercise is registered under Scales & keys with its name, and makes no sound.
    """
    assert KeySignatureConstruction in REGISTRY
    assert KeySignatureConstruction.name == "Key Signature Construction"
    assert KeySignatureConstruction.category == KeySignatures.category
    assert KeySignatureConstruction.has_sound is False
    assert "Key Signature Construction" in KeySignatureConstruction().instructions()


def test_a_question_names_the_key_under_a_blank_staff_and_the_answer_is_its_signature() -> None:
    """
    Check that a question names the key under a blank staff and that the answer is its signature.
    """
    for q in questions(
        100,
        modes={"Dorian"},
        clefs={"alto"},
        keys={2},
    ):
        assert q.build_key and q.show_staff and q.staff == [] and q.choices == []
        assert q.clef == "alto" and q.key == 2 and q.answer == "2 sharps"
        assert q.caption == "E Dorian" and q.prompt == "Build the key signature of E Dorian."
        assert q.explanation.endswith("E F♯ G A B C♯ D E")
        assert q.check_built(2) and not q.check_built(-2) and not q.check_built(0)


def test_by_default_major_and_minor_keys_come_in_the_treble_and_bass_clefs() -> None:
    """
    Check that by default major and minor keys come in the treble and bass clefs, across all fifteen signatures.
    """
    asked = questions(600)
    assert {q.clef for q in asked} == {"treble", "bass"}
    assert {q.key for q in asked} == set(range(-7, 8))
    assert {q.caption.split()[-1] for q in asked} == {"Major", "minor"}
    assert all(q.answer == format_key_signature(q.key) for q in asked)


def test_a_question_comes_back_as_a_question_to_build() -> None:
    """
    Check that a stored question is still one to build, and that an old stored question defaults to not building.
    """
    for q in questions(30):
        again = Question.from_dict(q.to_dict())
        assert again == q and again.build_key and again.item_key() == q.item_key()
    old = {k: v for k, v in questions(1)[0].to_dict().items() if k != "build_key"}
    assert not Question.from_dict(old).build_key


def test_the_two_key_exercises_keep_their_own_settings() -> None:
    """
    Check that key signature construction and identification keep separate settings.
    """
    before = KeySignatureConstruction().settings_signature()
    settings.key_signatures.modes = {"Dorian"}
    assert KeySignatureConstruction().settings_signature() == before
    settings.key_construction.modes = {"Dorian"}
    assert KeySignatureConstruction().settings_signature() != before


def test_the_preview_shows_the_signature_to_build(app: QApplication) -> None:
    """
    Check that the popup for a stored question shows the staff with its answer and the key's name.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    q = questions(1, keys={-3})[0]
    dialog = QuestionPreview("Key Signature Construction", question=q)
    text = " ".join(label.text() for label in dialog.findChildren(QLabel))
    assert dialog.grab().width() > 0 and "3 flats" in text
    assert q.caption and q.prompt not in text  # the key's name is on the staff, not above it


# -- the fork ---------------------------------------------------------------------------------------------------------


def test_the_fork_starts_at_the_natural_sign_and_keeps_to_seven_sharps_and_flats(app: QApplication) -> None:
    """
    Check that the fork starts at no sharps or flats and cannot go beyond seven of either.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    fork = KeyFork()
    assert fork.value == 0
    fork.set_value(12)
    assert fork.value == 7
    fork.set_value(-12)
    assert fork.value == -7


def test_sharps_are_on_the_top_tine_flats_on_the_bottom_and_the_natural_sign_on_the_stem(app: QApplication) -> None:
    """
    Check where the numbers sit on the fork.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert node_position(0).x() < min(node_position(v).x() for v in (-1, 1))  # the stem sticks out on the left
    assert node_position(0).y() == pytest.approx((node_position(1).y() + node_position(-1).y()) / 2)  # level with the fork
    assert all(node_position(v).y() < node_position(0).y() for v in range(1, 8))
    assert all(node_position(-v).y() > node_position(0).y() for v in range(1, 8))
    assert [node_position(v).x() for v in range(1, 8)] == sorted(node_position(v).x() for v in range(1, 8))  # 1 nearest the stem


def test_clicking_a_number_chooses_it(app: QApplication) -> None:
    """
    Check that clicking a number on either tine, or the natural sign, chooses it.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    fork = KeyFork()
    changes: list[int] = []
    fork.changed.connect(changes.append)
    for value in (5, -3, 0, 7, -7):
        press(fork, at=node_position(value))
        assert fork.value == value
    assert changes == [5, -3, 0, 7, -7]
    press(fork, at=QPointF(5, 135))  # nowhere near a number
    assert fork.value == -7


def test_the_mouse_wheel_moves_along_the_fork_through_the_natural_sign(app: QApplication) -> None:
    """
    Check that the wheel steps one number a notch, up for sharps and down for flats, passing through the natural sign.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    fork = KeyFork()
    seen: list[int] = []
    fork.changed.connect(seen.append)
    for _ in range(2):
        roll(fork, delta=120)
    for _ in range(4):
        roll(fork, delta=-120)
    assert seen == [1, 2, 1, 0, -1, -2]
    roll(fork, delta=60)  # half a notch is saved up, not lost
    assert fork.value == -2
    roll(fork, delta=60)
    assert fork.value == -1
    roll(fork, delta=120 * 30)
    assert fork.value == 7  # and it stops at the end of the tine


def mouse(
    kind: QEvent.Type,
    *,
    point: QPointF,
    button: Qt.MouseButton,
    held: Qt.MouseButton,
) -> QMouseEvent:
    """
    Make a mouse event at a point of the fork.

    Parameters
    ----------
    kind : QEvent.Type
        Press, move or release.
    point : QPointF
        Where the mouse is. Keyword-only.
    button : Qt.MouseButton
        The button that changed. Keyword-only.
    held : Qt.MouseButton
        The buttons held down. Keyword-only.

    Returns
    -------
    QMouseEvent
        The event.
    """
    return QMouseEvent(
        kind,
        point,
        point,
        button,
        held,
        Qt.KeyboardModifier.NoModifier,
    )


def test_the_circle_can_be_dragged_along_the_fork_and_settles_on_a_number(app: QApplication) -> None:
    """
    Check that holding the circle and moving the mouse carries it along the fork, and that letting go slides it to a number.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    fork = KeyFork()
    seen: list[int] = []
    fork.changed.connect(seen.append)
    start = node_position(0)
    left = Qt.MouseButton.LeftButton
    none = Qt.MouseButton.NoButton
    fork.mousePressEvent(mouse(QEvent.Type.MouseButtonPress, point=start, button=left, held=left))
    for target in (node_position(2) + QPointF(6, -4), node_position(-3) + QPointF(2, 5)):
        fork.mouseMoveEvent(mouse(QEvent.Type.MouseMove, point=target, button=none, held=left))
    assert fork.value == -3 and seen[-1] == -3 and 2 in seen
    assert fork._marker != node_position(-3)  # it follows the mouse, off the number, while held
    fork.mouseReleaseEvent(mouse(QEvent.Type.MouseButtonRelease, point=start, button=left, held=none))
    fork._slide.setCurrentTime(fork._slide.duration())
    assert fork._marker == node_position(-3)


def test_a_number_lights_up_under_the_mouse_and_a_locked_fork_does_not(app: QApplication) -> None:
    """
    Check that the number under the mouse is lit, that leaving puts it out, and that a locked fork lights nothing.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    fork = KeyFork()
    none = Qt.MouseButton.NoButton
    move = mouse(QEvent.Type.MouseMove, point=node_position(4), button=none, held=none)
    fork.mouseMoveEvent(move)
    assert fork._hover == 4
    fork.leaveEvent(QEvent(QEvent.Type.Leave))
    assert fork._hover is None
    fork.locked = True
    fork.mouseMoveEvent(move)
    assert fork._hover is None


def test_the_wheel_over_the_music_or_the_answer_button_moves_the_circle(app: QApplication) -> None:
    """
    Check that turning the wheel over the staff or the Answer button moves the fork, and that it does nothing without a fork.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(KeySignatureConstruction(), rng=random.Random(1))
    view.show()
    here = QPointF(5, 5)
    turn = QWheelEvent(
        here,
        here,
        QPoint(0, 0),
        QPoint(0, 120),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    assert view.eventFilter(view.staff, turn) and view.fork.value == 1
    assert view.eventFilter(view.answer_button, turn) and view.fork.value == 2
    view.fork.hide()
    assert not view.eventFilter(view.staff, turn) and view.fork.value == 2
    view.close()


def test_the_arrow_keys_move_the_circle_too(app: QApplication) -> None:
    """
    Check that up and right add a sharp, and down and left a flat.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    fork = KeyFork()
    for key in (Qt.Key.Key_Up, Qt.Key.Key_Right, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Left):
        fork.keyPressEvent(QKeyEvent(QEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier))
    assert fork.value == -1


def test_a_locked_fork_ignores_the_mouse_the_wheel_and_the_keys(app: QApplication) -> None:
    """
    Check that a locked fork does not change.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    fork = KeyFork()
    fork.locked = True
    press(fork, at=node_position(4))
    roll(fork, delta=120)
    fork.keyPressEvent(QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Up, Qt.KeyboardModifier.NoModifier))
    assert fork.value == 0


def test_the_circle_travels_along_the_fork_never_across_the_gap(app: QApplication) -> None:
    """
    Check that the circle's way from a sharp to a flat goes through the base of the fork, and that it slides there.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    way = path_between(2, b=-2)
    assert way[0] == node_position(2) and way[-1] == node_position(-2)
    xs = {p.x() for p in way}
    assert min(xs) == pytest.approx(APEX_X)  # it goes around the U, through its apex
    fork = KeyFork()
    fork.set_value(2)
    QTest.qWait(40)
    assert fork._marker != node_position(0)  # on its way
    QTest.qWait(300)
    assert fork._marker == node_position(2)


def test_the_bend_of_the_fork_is_curved_and_so_is_the_circles_way_round_it(app: QApplication) -> None:
    """
    Check that the circle goes around the U of the fork on a curve, in small steps, with no corner.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    way = route(7)
    bend = [p for p in way if p.x() < JOINT_X and p != node_position(0)]
    assert len(bend) > 8  # a curve is made of many short pieces, not one corner
    assert any(p.y() not in {MID_Y, TOP_Y} for p in bend)  # it leaves both the stem's row and the tine's
    steps = [(b - a).manhattanLength() for a, b in zip(bend, bend[1:], strict=False)]
    assert max(steps) < 10 and min(steps) > 0
    path = fork_path()
    start, end = path.pointAtPercent(0.0), path.pointAtPercent(1.0)
    assert (start.x(), start.y()) == (STEM_X, MID_Y)  # it starts at the end of the stem
    assert end.y() == pytest.approx(BOTTOM_Y)  # and ends on a tine


# -- the exercise screen ----------------------------------------------------------------------------------------------


def test_the_screen_shows_a_blank_staff_with_the_key_name_and_the_fork(app: QApplication) -> None:
    """
    Check that the screen shows a staff with no signature, the key's name on it, the fork and the answer button.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(KeySignatureConstruction(), rng=random.Random(4))
    view.resize(900, 700)
    view.show()
    q = view.question
    assert q is not None
    assert view.staff.isVisibleTo(view) and view.staff.key == 0 and view.staff.columns == []
    assert view.staff.caption == q.caption and view.prompt.isHidden()  # the name is in the music, not above it
    assert view.fork.isVisibleTo(view) and view.fork.value == 0 and view.answer_button.isVisibleTo(view)
    assert view.answer_button.text() == "Answer"
    assert view.buttons == [] and not view.input_staff.isVisibleTo(view)


def test_other_exercises_do_not_show_the_fork(app: QApplication) -> None:
    """
    Check that an exercise that is not about building a key signature has no fork or answer button.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(KeySignatures(), rng=random.Random(4))
    view.show()
    assert not view.fork.isVisibleTo(view) and not view.answer_button.isVisibleTo(view)


def test_the_staff_follows_the_fork(app: QApplication) -> None:
    """
    Check that the signature on the staff is the one picked on the fork.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(KeySignatureConstruction(), rng=random.Random(4))
    q = view.question
    assert q is not None
    for value in (3, -5, 0, 7):
        view.fork.set_value(value)
        assert view.staff.key == value and view.staff.caption == q.caption and view.staff.clef == q.clef


def test_the_staff_keeps_its_width_whatever_signature_is_picked(app: QApplication) -> None:
    """
    Check that the staff is as wide with seven flats as with none, and that other exercises keep their own widths.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(KeySignatureConstruction(), rng=random.Random(4))
    view.resize(1400, 800)
    view.show()
    widths = set()
    for value in (0, 3, -7, 7, 1, -1, 0):
        view.fork.set_value(value, slide=False)
        app.processEvents()
        widths.add((view.staff.maximumWidth(), view.staff.sizeHint().width(), view.staff.width()))
    assert len(widths) == 1
    other = ExerciseView(KeySignatures(), rng=random.Random(4))
    assert other.staff.key_room == 0


def test_a_right_signature_is_scored_and_moves_on_with_no_sound(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that a right signature scores once, plays no tone and moves on to the next question.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the test.
    """
    played = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr("alto.ui.exercise_view.sounds.play_notes", lambda notes: played.append(notes))
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr("alto.ui.exercise_view.sounds.play_correct", lambda streak: played.append(streak))
    view = ExerciseView(KeySignatureConstruction(), rng=random.Random(4))
    first = view.question
    assert first is not None
    view.fork.set_value(first.key)
    view.answer_button.click()
    assert view.answered and (view.correct, view.total, view.streak) == (1, 1, 1) and view.fork.locked
    view.answer_button.click()  # a second press does not score again
    assert view.total == 1
    view._advance.stop()
    view.next_question()
    assert view.question is not first and not view.fork.locked and view.fork.value == 0 and view.staff.key == 0
    assert played == []


def test_a_wrong_signature_counts_against_the_first_try_and_the_fork_resets_to_try_again(app: QApplication) -> None:
    """
    Check that a wrong signature fails the question, and then the fork goes back to the natural sign and can be tried again.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(KeySignatureConstruction(), rng=random.Random(4))
    q = view.question
    assert q is not None
    view.fork.set_value(q.key + 1 if q.key < 7 else q.key - 1)
    view.answer_button.click()
    assert view.missed and not view.answered and view.total == 1 and view.correct == 0 and view.streak == 0
    assert view.fork.locked
    QTest.qWait(1200)
    assert not view.fork.locked and view.fork.value == 0 and view.staff.key == 0
    view.fork.set_value(q.key)
    view.answer_button.click()
    assert view.answered and view.total == 1 and view.correct == 0  # only the first try counts toward the score
    view._advance.stop()


def test_every_try_is_recorded_with_the_signature_that_was_built(app: QApplication) -> None:
    """
    Check that the learner's history gets each attempt, naming the signature that was built.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    view = ExerciseView(KeySignatureConstruction(), rng=random.Random(4), learner=learner)
    q = view.question
    assert q is not None
    wrong = q.key + 1 if q.key < 7 else q.key - 1
    view.fork.set_value(wrong)
    view.answer_button.click()
    QTest.qWait(1200)
    view.fork.set_value(q.key)
    view.answer_button.click()
    view._advance.stop()
    rows = db.conn.execute("SELECT answer, correct FROM attempts ORDER BY id").fetchall()
    assert [(r[0], r[1]) for r in rows] == [(format_key_signature(wrong), 0), (format_key_signature(q.key), 1)]


def test_a_changed_setting_gives_a_fresh_blank_question(app: QApplication) -> None:
    """
    Check that changing a setting replaces the question and puts the fork back to the natural sign.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(KeySignatureConstruction(), rng=random.Random(4))
    view.fork.set_value(5)
    view.settings_panel.changed.emit()
    assert view.fork.value == 0 and view.staff.key == 0


# -- the home page and the settings -----------------------------------------------------------------------------------


def test_the_home_card_has_its_own_icon_and_its_name_fits(app: QApplication) -> None:
    """
    Check that the exercise has an icon of its own on the home page.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert EXERCISE_ICONS["KeySignatureConstruction"] != EXERCISE_ICONS["KeySignatures"]
    card = ExerciseCard(KeySignatureConstruction)
    assert card.toolTip() == KeySignatureConstruction.description


def test_the_settings_pane_saves_under_its_own_name(app: QApplication) -> None:
    """
    Check that the construction settings are edited, saved and loaded apart from the identification ones.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(KeySignatureConstruction(), rng=random.Random(4))
    pane = view.settings_panel
    assert isinstance(pane, sp.KeySignatureSettingsPanel) and pane.cfg is settings.key_construction
    pane.modes.boxes["Dorian"].setChecked(True)
    pane.key_list.boxes[-6].setChecked(False)
    assert "Dorian" in settings.key_construction.modes and -6 not in settings.key_construction.keys
    assert "Dorian" in str(store().value("keyConstruction/modes")).split("|")
    assert store().value("keySignatures/modes") is None and "Dorian" not in settings.key_signatures.modes
    settings.key_construction.modes, settings.key_construction.keys = {"Major (Ionian)"}, set(range(-7, 8))
    es.load_key_construction()
    assert "Dorian" in settings.key_construction.modes and -6 not in settings.key_construction.keys
    assert settings.key_signatures.keys == set(range(-7, 8))
