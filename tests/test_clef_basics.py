"""Clef Basics: the settings, the questions, the staff a clef is put on, and the exercise on screen."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from PySide6.QtCore import (
    QEvent,
    QPoint,
    QPointF,
    Qt,
)
from PySide6.QtGui import (
    QMouseEvent,
    QWheelEvent,
)

from alto import settings
from alto.exercises import REGISTRY
from alto.exercises.base import Question
from alto.exercises.library import ClefBasics
from alto.ui import exercise_settings as es
from alto.ui import settings_panel as sp
from alto.ui.exercise_view import ExerciseView
from alto.ui.staff import (
    StaffWidget,
    clef_targets,
)
from alto.ui.staff_input import ClefInput
from alto.ui.store import store

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


def click(
    staff: ClefInput,
    *,
    step: int,
    button: Qt.MouseButton = Qt.MouseButton.LeftButton,
) -> None:
    """
    Click a line or space of the clef staff.

    Parameters
    ----------
    staff : ClefInput
        The staff, already sized.
    step : int
        The place to click: 0 for the bottom line, 1 for the space above it, up to 8 for the top line.
    button : Qt.MouseButton, default left
        The button to press.
    """
    point = QPointF(60, staff.staff_bottoms()["treble"] - step * staff.GAP / 2)
    staff.mousePressEvent(
        QMouseEvent(
            QEvent.Type.MouseButtonPress,
            point,
            point,
            button,
            button,
            Qt.KeyboardModifier.NoModifier,
        ),
    )


def turn(delta: int) -> QWheelEvent:
    """
    Make a turn of the mouse wheel.

    Parameters
    ----------
    delta : int
        The wheel's angle delta: 120 is one notch up.

    Returns
    -------
    QWheelEvent
        The event.
    """
    here = QPointF(50, 50)
    return QWheelEvent(
        here,
        here,
        QPoint(0, 0),
        QPoint(0, delta),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )


def sized(options: list[str]) -> ClefInput:
    """
    Make a clef staff with some symbols to choose from, big enough to click.

    Parameters
    ----------
    options : list of str
        The symbols to choose from, any of "G", "C" and "F".

    Returns
    -------
    ClefInput
        The staff.
    """
    staff = ClefInput()
    staff.reset(options)
    staff.resize(500, 300)
    return staff


# -- the settings -----------------------------------------------------------------------------------------------------


def test_the_clefs_asked_for_include_the_french_violin_and_subbass_clefs(app: QApplication) -> None:
    """
    Check that the clef exercise can ask for nine clefs, the last two being the French violin and subbass clefs.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert settings.CLEF_BASICS_CLEFS == (*settings.CLEFS, "french", "subbass")
    assert settings.CLEFS[-1] == "baritone"  # the other exercises do not have the two extra clefs
    cfg = settings.ClefBasicsSettings(clefs={"subbass", "mezzo", "french"})
    assert cfg.active_clefs() == ["mezzo", "french", "subbass"]
    assert settings.ClefBasicsSettings(clefs=set()).active_clefs() == ["treble"]  # something is always asked
    assert settings.CLEF_NAMES["french"] == "French violin" and settings.CLEF_NAMES["subbass"] == "Subbass"


def test_every_clef_can_be_asked_for_and_is_made_from_a_symbol(app: QApplication) -> None:
    """
    Check that each clef that can be asked for has a question and a place to put its symbol.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.clef_basics.clefs = set(settings.CLEF_BASICS_CLEFS)
    rng = random.Random(4)
    asked = set()
    for _ in range(300):
        q = ClefBasics().generate(rng)
        asked.add(q.place_clef)
        assert q.place_clef == q.answer and q.show_staff and not q.choices
        assert all(symbol in settings.CLEF_SYMBOLS and -1 < step < 9 for symbol, step in clef_targets(q.place_clef))
    assert asked == set(settings.CLEF_BASICS_CLEFS)


def test_the_question_is_written_under_the_staff(app: QApplication) -> None:
    """
    Check that the question is the staff's caption, so it shows in the white area and not above the music.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    q = ClefBasics().generate(random.Random(1))
    assert q.caption == q.prompt == f"Place the {settings.CLEF_NAMES[q.place_clef].lower()} clef."


def test_the_exercise_is_registered_and_its_questions_can_be_stored(app: QApplication) -> None:
    """
    Check that the exercise is on the home screen and that its question survives being stored.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert ClefBasics in REGISTRY
    q = ClefBasics().generate(random.Random(1))
    assert Question.from_dict(q.to_dict()) == q
    before = ClefBasics().settings_signature()
    settings.clef_basics.clefs = {"treble", "alto"}
    assert ClefBasics().settings_signature() != before  # stored questions are not replayed under other settings


# -- the staff --------------------------------------------------------------------------------------------------------


def test_each_clef_is_a_symbol_on_a_line(app: QApplication) -> None:
    """
    Check the symbol and the line each clef is written with: mezzo-soprano is the C clef on the second line.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert {c: clef_targets(c) for c in ("treble", "bass", "alto", "tenor", "soprano", "mezzo", "french", "subbass")} == {
        "treble": {("G", 2)},
        "bass": {("F", 6)},
        "alto": {("C", 4)},
        "tenor": {("C", 6)},
        "soprano": {("C", 0)},
        "mezzo": {("C", 2)},
        "french": {("G", 0)},  # the G clef on the bottom line
        "subbass": {("F", 8)},  # the F clef on the top line
    }


def test_the_baritone_clef_is_either_the_f_clef_on_the_middle_line_or_the_c_clef_on_the_top_line(app: QApplication) -> None:
    """
    Check that both ways of writing the baritone clef are right, whichever is chosen for drawing it in the settings.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert clef_targets("baritone") == {("F", 4), ("C", 8)}
    settings.clef_basics.clefs = {"baritone"}
    for symbol, step in sorted(clef_targets("baritone")):
        view = clef_view()
        choose(view, symbol)
        click(view.clef_input, step=step)
        assert view.answered and view.correct == 1, (symbol, step)
        view._advance.stop()
    view = clef_view()
    choose(view, "C")
    click(view.clef_input, step=4)  # the C clef on the middle line is the alto clef, not the baritone
    assert not view.answered
    view.clef_input.locked, view._busy = False, False
    view.clef_input.clear_placed()
    choose(view, "F")
    click(view.clef_input, step=8)  # nor is the F clef on the top line: that is the subbass clef
    assert not view.answered


def test_the_wheel_and_a_right_click_choose_the_symbol(app: QApplication) -> None:
    """
    Check that the wheel goes through the symbols both ways, going around, and that a right click goes on to the next.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = sized(["G", "C", "F"])
    assert staff.selected == "G" and staff.toolTip() == "G clef chosen"
    staff.wheelEvent(turn(120))
    assert staff.selected == "C"
    staff.wheelEvent(turn(-240))
    assert staff.selected == "F"  # back past the first, around to the last
    staff.wheelEvent(turn(60))
    staff.wheelEvent(turn(60))  # half a notch is saved up, not lost
    assert staff.selected == "G"
    click(staff, step=0, button=Qt.MouseButton.RightButton)
    assert staff.selected == "C" and staff.toolTip() == "C clef chosen" and staff.placed_symbol is None
    staff.select("F")
    staff.select("X")  # not one of the options
    assert staff.selected == "F"


def test_a_click_puts_the_symbol_on_the_nearest_line_or_space_or_ledger_line(app: QApplication) -> None:
    """
    Check that a click picks the nearest line or space, up to the third ledger line each side, and nothing is placed while locked.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = sized(["C"])
    got: list[tuple[str, int]] = []
    staff.placed.connect(lambda symbol, where: got.append((symbol, where)))
    for step in (0, 1, 5, 8, -2, 10, -6, 14, 13):
        click(staff, step=step)
    assert got == [("C", step) for step in (0, 1, 5, 8, -2, 10, -6, 14, 13)]
    assert staff.step_at(0) == 14 and staff.step_at(10_000) == -6  # far off the staff it stops at the third ledger lines
    staff.locked = True
    click(staff, step=3)
    staff.wheelEvent(turn(120))
    assert len(got) == 9


def test_the_keyboard_moves_and_places_the_symbol(app: QApplication) -> None:
    """
    Check that the caret starts on the middle line, goes by lines and spaces, stops at the ends and places the symbol.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = sized(["G", "F"])
    staff.move_caret(1)
    assert staff.caret == 5
    staff.move_caret(-20)
    assert staff.caret == -6
    staff.step_symbol(1)
    staff.place_caret()
    assert (staff.placed_symbol, staff.placed_step) == ("F", -6)
    staff.reset(["G"])
    assert staff.placed_symbol is None and staff.caret is None


def test_the_symbol_is_drawn_where_the_pointer_is_and_where_it_was_placed(app: QApplication) -> None:
    """
    Check that the symbol appears on the staff once it is placed or followed by the pointer, and not before.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    staff = sized(["G"])
    blank = staff.grab().toImage()
    staff.place(2)
    assert staff.grab().toImage() != blank
    staff.clear_placed()
    assert staff.grab().toImage() == blank
    staff.move_caret(0)
    assert staff.grab().toImage() != blank  # the one that would be placed, in a lighter color
    staff.clear_placed()
    staff.caret = 14  # on the third ledger line above: the lines it sits on are drawn too
    ledger = staff.grab().toImage()
    staff.caret = 8
    assert staff.grab().toImage() != ledger
    staff.caret = -6
    assert staff.grab().toImage() != ledger


# -- the exercise on screen -------------------------------------------------------------------------------------------


def clef_view(*, seed: int = 2) -> ExerciseView:
    """
    Make the exercise screen on a clef question.

    Parameters
    ----------
    seed : int, default 2
        The random seed.

    Returns
    -------
    ExerciseView
        The screen, with a question showing.
    """
    view = ExerciseView(ClefBasics(), rng=random.Random(seed))
    view.show()
    return view


def asked_of(view: ExerciseView) -> Question:
    """
    Return the question on the screen.

    Parameters
    ----------
    view : ExerciseView
        The screen.

    Returns
    -------
    Question
        The question showing.
    """
    assert view.question is not None
    return view.question


def choose(view: ExerciseView, symbol: str) -> None:
    """
    Choose a symbol on the screen's clef staff by turning the wheel.

    Parameters
    ----------
    view : ExerciseView
        The screen.
    symbol : str
        "G", "C" or "F".
    """
    for _ in range(3):
        if view.clef_input.selected == symbol:
            return
        view.clef_input.step_symbol(1)


def test_the_screen_shows_the_clef_staff_the_buttons_and_the_question_under_the_staff(app: QApplication) -> None:
    """
    Check that a clef question shows the blank staff, three symbol buttons under it, the question under the staff and Answer.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = clef_view()
    name = settings.CLEF_NAMES[asked_of(view).place_clef].lower()
    assert view.clef_input.caption == f"Place the {name} clef."  # under the staff, in the white area
    assert not view.prompt.isVisible()  # and not above the music
    assert view.clef_input.isVisible() and view.clef_input.options == ["G", "C", "F"]  # always the three symbols
    assert not view.staff.isVisible() and not view.fork.isVisible() and not view.input_staff.isVisible()
    assert [b.accessibleName() for b in view.symbol_buttons.values()] == ["G clef", "C clef", "F clef"]
    assert all(not b.icon().isNull() and not b.text() for b in view.symbol_buttons.values())  # a picture of each, not words
    assert all(b.isVisible() for b in view.symbol_buttons.values()) and view.symbol_buttons["G"].isChecked()
    assert view.answer_button.isVisible() and view.answer_button.isEnabled()
    assert not view.place_button.isVisible() and not view.undo_button.isVisible()


def test_the_buttons_choose_the_symbol_and_follow_the_wheel(app: QApplication) -> None:
    """
    Check that a button chooses its symbol, and that the pressed button follows the wheel and the keys.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = clef_view()
    view.symbol_buttons["F"].click()
    assert view.clef_input.selected == "F" and view.symbol_buttons["F"].isChecked()
    view.clef_input.wheelEvent(turn(120))
    assert view.clef_input.selected == "G" and view.symbol_buttons["G"].isChecked() and not view.symbol_buttons["F"].isChecked()
    view._key_action("right")
    assert view.symbol_buttons["C"].isChecked()


def test_the_right_symbol_in_the_right_place_is_correct(app: QApplication) -> None:
    """
    Check that choosing the symbol and clicking the place that make the clef asked for scores a correct answer and moves on.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = clef_view()
    symbol, step = min(clef_targets(asked_of(view).place_clef))
    choose(view, symbol)
    click(view.clef_input, step=step)
    assert (view.answered, view.correct, view.total) == (True, 1, 1)
    assert view.clef_input.locked
    view._advance.stop()


def test_the_mezzo_soprano_clef_is_the_c_symbol_on_the_second_line(app: QApplication) -> None:
    """
    Check the example: for the mezzo-soprano clef the C symbol on the second line is right, and the C symbol elsewhere is not.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.clef_basics.clefs = {"mezzo"}
    view = clef_view()
    assert asked_of(view).place_clef == "mezzo"
    choose(view, "C")
    click(view.clef_input, step=4)  # the middle line is the alto clef
    assert not view.answered and view.missed
    view.clef_input.locked, view._busy = False, False
    view.clef_input.clear_placed()
    click(view.clef_input, step=3)  # a space is not the line
    assert not view.answered
    view.clef_input.locked, view._busy = False, False
    view.clef_input.clear_placed()
    click(view.clef_input, step=2)
    assert view.answered and view.total == 1  # only the first try counted
    view._advance.stop()


def test_a_wrong_place_or_a_wrong_symbol_is_wrong_and_can_be_tried_again(app: QApplication) -> None:
    """
    Check that the right symbol in a wrong place, and another symbol in any place, count as wrong and clear for another try.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = clef_view()
    symbol, step = min(clef_targets(asked_of(view).place_clef))
    choose(view, symbol)
    click(view.clef_input, step=step + 1)
    assert (view.answered, view.missed, view.correct, view.total) == (False, True, 0, 1)
    assert view.clef_input.locked and not view.answer_button.isEnabled()  # the retry has not cleared it yet
    view.clef_input.locked, view._busy = False, False
    view.clef_input.clear_placed()
    other = next(s for s in ("G", "C", "F") if s != symbol)
    choose(view, other)
    click(view.clef_input, step=step)  # another symbol in that place is not the clef asked for
    assert not view.answered and view.total == 1  # only the first try counts


def test_the_ledger_lines_are_allowed_but_never_right(app: QApplication) -> None:
    """
    Check that a symbol can be put on the ledger lines, and that it is counted wrong, since no clef is written there.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = clef_view()
    click(view.clef_input, step=12)
    assert view.clef_input.placed_step == 12 and not view.answered and view.missed


def test_the_arrow_keys_and_answer_work_without_the_mouse(app: QApplication) -> None:
    """
    Check that Left and Right choose the symbol, Up and Down move it, and Answer places it.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = clef_view()
    symbol, step = min(clef_targets(asked_of(view).place_clef))
    for _ in range(3):
        if view.clef_input.selected == symbol:
            break
        view._key_action("right")
    assert view.clef_input.selected == symbol
    view._key_action("up")
    assert view.clef_input.caret == 5
    for _ in range(abs(step - 5)):  # on from the place the Up key reached, to the place asked for
        view._key_action("up" if step > 5 else "down")
    assert view.clef_input.caret == step
    view._answer()
    assert view.answered
    view._advance.stop()


def test_the_wheel_over_answer_chooses_the_symbol(app: QApplication) -> None:
    """
    Check that turning the wheel over the Answer button chooses a symbol, as it does over the staff.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = clef_view()
    first = view.clef_input.selected
    assert view.eventFilter(view.answer_button, turn(120))
    assert view.clef_input.selected != first


def test_other_exercises_do_not_show_the_clef_staff(app: QApplication) -> None:
    """
    Check that the clef staff and its buttons are hidden for every other exercise.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for cls in REGISTRY:
        if cls is ClefBasics:
            continue
        view = ExerciseView(cls(), rng=random.Random(1))
        view.show()
        assert not view.clef_input.isVisible() and not view.symbol_row.isVisible(), cls.name
        view.close()


# -- Clef Identification ----------------------------------------------------------------------------------------------


def test_identification_draws_a_clef_and_asks_for_its_name(app: QApplication) -> None:
    """
    Check that an identification question has a clef to draw, the clefs asked for as answers, and the question under the staff.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.clef_basics.question_type = "identification"
    settings.clef_basics.clefs = {"treble", "mezzo", "french", "subbass"}
    rng = random.Random(5)
    seen = set()
    for _ in range(200):
        q = ClefBasics().generate(rng)
        seen.add(q.clef)
        assert q.choices == ["Treble", "Mezzo-soprano", "French violin", "Subbass"]
        assert q.answer == settings.CLEF_NAMES[q.clef] and q.check(q.answer)
        assert q.show_staff and not q.staff and not q.place_clef and q.caption == "Which clef is this?"
    assert seen == {"treble", "mezzo", "french", "subbass"}


def test_identification_always_has_a_choice_of_at_least_two_buttons(app: QApplication) -> None:
    """
    Check that asking for one clef still offers two buttons, and that the clef asked for is among them.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert settings.ClefBasicsSettings(clefs={"alto"}).answer_clefs() == ["treble", "alto"]
    assert settings.ClefBasicsSettings(clefs={"treble"}).answer_clefs() == ["treble", "bass"]
    assert settings.ClefBasicsSettings(clefs={"soprano", "baritone"}).answer_clefs() == ["soprano", "baritone"]
    settings.clef_basics.question_type = "identification"
    settings.clef_basics.clefs = {"tenor"}
    q = ClefBasics().generate(random.Random(1))
    assert q.answer == "Tenor" and q.answer in q.choices and len(q.choices) == 2


def test_the_identification_screen_draws_the_clef_and_buttons_name_the_clefs(app: QApplication) -> None:
    """
    Check that the screen shows the staff with the clef drawn, a button for each clef, and none of the construction widgets.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.clef_basics.question_type = "identification"
    settings.clef_basics.clefs = {"alto", "tenor", "french"}
    view = ExerciseView(ClefBasics(), rng=random.Random(2))
    view.show()
    q = asked_of(view)
    assert view.staff.isVisible() and view.staff.clef == q.clef and view.staff.caption == "Which clef is this?"
    assert not view.staff.clef_hidden and not view.prompt.isVisible()
    assert not view.clef_input.isVisible() and not view.symbol_row.isVisible() and not view.answer_row.isVisible()
    assert [b.text() for b in view.buttons] == ["Alto", "Tenor", "French violin"]


def test_the_answer_buttons_have_room_around_them_and_a_widest_area(app: QApplication) -> None:
    """
    Check that the buttons sit in an area that is never wider than the maximum, however wide the window, and wrap into rows.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.clef_basics.question_type = "identification"
    settings.clef_basics.clefs = set(settings.CLEF_BASICS_CLEFS)
    view = ExerciseView(ClefBasics(), rng=random.Random(2))
    view.resize(1800, 700)
    view.show()
    assert view.choice_area.width() <= ExerciseView.CHOICE_MAX_WIDTH
    margins = view.choice_box.contentsMargins()
    assert margins.left() > 0 and margins.top() > 0 and view.choice_box.spacing() > 0  # padding around them
    rows = {b.geometry().y() for b in view.buttons}
    assert len(view.buttons) == 9 and len(rows) == 2  # nine clefs in two rows of five and four, not one long row
    left = view.choice_area.mapTo(view, QPoint()).x()
    right = view.width() - left - view.choice_area.width()
    assert abs(left - right) <= 40  # in the middle


def test_pressing_the_right_name_is_correct_and_a_wrong_one_is_not(app: QApplication) -> None:
    """
    Check that the button with the clef's name scores a correct answer, and another button a wrong one.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.clef_basics.question_type = "identification"
    settings.clef_basics.clefs = {"treble", "bass", "subbass"}
    view = ExerciseView(ClefBasics(), rng=random.Random(3))
    view.show()
    answer = asked_of(view).answer
    wrong = next(b for b in view.buttons if b.text() != answer)
    wrong.click()
    assert not view.answered and view.missed and view.total == 1 and view.correct == 0
    next(b for b in view.buttons if b.text() == answer).click()
    assert view.answered and view.total == 1  # only the first try counted
    view._advance.stop()


def test_every_clef_can_be_drawn_on_a_staff(app: QApplication) -> None:
    """
    Check that the staff can draw each clef that can be asked for, the French violin and subbass clefs included.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for clef in settings.CLEF_BASICS_CLEFS:
        staff = StaffWidget()
        staff.show_notes([], clef=clef)
        bare = StaffWidget()
        bare.show_notes([], clef=clef)
        bare.clef_hidden = True
        assert staff.grab().toImage() != bare.grab().toImage(), clef  # the clef is there


def test_the_question_type_is_chosen_saved_and_loaded(app: QApplication) -> None:
    """
    Check that the Question Type page switches between the two kinds of question, saves the choice and loads it.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.ClefBasicsSettings()
    panel = sp.ClefBasicsSettingsPanel(cfg)
    changes: list[int] = []
    panel.changed.connect(lambda: changes.append(1))
    assert list(panel.types) == ["construction", "identification"] and panel.types["construction"].isChecked()
    assert panel.type_row.accessibleName() == "Question Type"
    panel.types["identification"].setChecked(True)
    assert cfg.question_type == "identification" and len(changes) == 1  # the one switched off said nothing
    panel._refresh_summaries()
    assert panel.type_row.value.text() == "Identification"
    assert str(store().value("clefBasics/type")) == "identification"
    settings.clef_basics.question_type = "construction"
    es.load_clef_basics()
    assert settings.clef_basics.question_type == "identification"
    store().setValue("clefBasics/type", "nonsense")
    es.load_clef_basics()
    assert settings.clef_basics.question_type == "identification"  # not a kind of question: left as it was
    assert settings.ClefBasicsSettings(question_type="nonsense").active_type() == "construction"


def test_the_help_follows_the_kind_of_question(app: QApplication) -> None:
    """
    Check that the help text names the kind of question that is being asked.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert "Clef Construction" in ClefBasics().instructions()
    settings.clef_basics.question_type = "identification"
    assert "Clef Identification" in ClefBasics().instructions()
    assert ClefBasics().settings_signature() != ""


# -- the settings pages -----------------------------------------------------------------------------------------------


def test_the_clefs_page_lists_the_extra_clefs_at_the_bottom(app: QApplication) -> None:
    """
    Check that the page has one box for each clef, with the French violin and subbass clefs in a group at the bottom.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    cfg = settings.ClefBasicsSettings(clefs={"treble"})
    panel = sp.ClefBasicsSettingsPanel(cfg)
    changes: list[int] = []
    panel.changed.connect(lambda: changes.append(1))
    assert list(panel.boxes) == list(settings.CLEF_BASICS_CLEFS) and list(panel.boxes)[-2:] == ["french", "subbass"]
    assert panel.clefs_row.accessibleName() == "Clefs" and not panel.boxes["treble"].isEnabled()  # the last one stays
    panel.boxes["subbass"].setChecked(True)
    panel.boxes["french"].setChecked(True)
    assert cfg.clefs == {"treble", "subbass", "french"} and len(changes) == 2
    assert panel.boxes["treble"].isEnabled()
    panel._refresh_summaries()
    assert panel.clef_pictures.clefs == ["treble", "french", "subbass"]


def test_the_other_exercises_do_not_offer_the_extra_clefs(app: QApplication) -> None:
    """
    Check that the settings of the other exercises list only the seven clefs.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    panel = sp.settings_panel_for(next(cls() for cls in REGISTRY if cls.__name__ == "KeySignatureConstruction"))
    assert isinstance(panel, sp.KeySignatureSettingsPanel)
    assert list(panel.boxes) == list(settings.CLEFS)


def test_the_clefs_are_saved_and_loaded(app: QApplication) -> None:
    """
    Check that the clefs asked for are saved, and that a saved clef that does not exist is ignored.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    sp.ClefBasicsSettingsPanel(settings.clef_basics).boxes["french"].setChecked(True)
    assert str(store().value("clefBasics/clefs")) == "treble,bass,french"
    settings.clef_basics.clefs = {"treble"}
    es.load_clef_basics()
    assert settings.clef_basics.clefs == {"treble", "bass", "french"}
    store().setValue("clefBasics/clefs", "flute,subbass")
    es.load_clef_basics()
    assert settings.clef_basics.clefs == {"subbass"}
    store().setValue("clefBasics/clefs", "flute")
    es.load_clef_basics()
    assert settings.clef_basics.clefs == {"subbass"}  # nothing valid: left as it was


def test_the_exercise_has_its_own_settings_panel(app: QApplication) -> None:
    """
    Check that the gear opens the clef basics panel, which has Question Type and Clefs pages.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    panel = sp.settings_panel_for(ClefBasics())
    assert isinstance(panel, sp.ClefBasicsSettingsPanel)
    assert panel.stack.count() == 5 and panel.choice_buttons_row is not None
