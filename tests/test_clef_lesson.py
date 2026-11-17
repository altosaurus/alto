"""The Clef Basics lesson, its staves and tasks, and the reference pane of the exercise."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pytest

from alto import settings
from alto.exercises.library import (
    CLEF_FACTS,
    ClefBasics,
)
from alto.lessons import LESSONS
from alto.lessons.base import Staff
from alto.lessons.clef_basics import (
    CLEF_BASICS,
    LINES,
    SYMBOLS,
    identify_task,
    line_task,
    symbol_task,
)
from alto.ui.exercise_view import ExerciseView
from alto.ui.home import (
    HomePage,
    lesson_card,
)
from alto.ui.lesson import (
    GIVE_UP_AFTER,
    LessonsPage,
    StepView,
)
from alto.ui.main_window import MainWindow
from alto.ui.reference import (
    ClefReferencePanel,
    reference_panel_for,
)
from alto.ui.staff import clef_targets
from alto.ui.store import store

if TYPE_CHECKING:
    from collections.abc import Iterator

    from PySide6.QtWidgets import QApplication


@pytest.fixture
def clean_lessons() -> Iterator[None]:
    """
    Start a test with no saved lesson progress, and leave it so.

    Yields
    ------
    None
        Control, while the test runs.
    """
    store().remove("lessons")
    yield
    store().remove("lessons")


def test_the_lesson_is_listed_with_the_exercise_that_practices_it(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the lesson is after the circle of fifths lesson, is in the notation group and has a card with the exercise's icon.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    assert [lesson.key for lesson in LESSONS] == ["circle-of-fifths", "clef-basics", "scale-identification"]
    assert CLEF_BASICS.category == "Notation" and CLEF_BASICS.exercise == ClefBasics.__name__
    assert len(CLEF_BASICS.steps) == 10 and CLEF_BASICS.steps[-1].closing
    card = lesson_card(CLEF_BASICS)
    assert card.accessibleName().startswith("Clef Basics")
    page = HomePage([ClefBasics])
    assert len(page.lesson_cards) == len(LESSONS)


def test_every_step_builds_and_shows_what_it_says_it_does(app: QApplication) -> None:
    """
    Check that each step has words, that staves are drawn where there are some, and that a task step has a staff and a task.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for step in CLEF_BASICS.steps:
        view = StepView(step, rng=random.Random(1))
        assert step.title and step.text and view.circle is None
        assert len(view.staves) == (len(step.staves) or int(step.task_staff))
        assert (view.task is not None) == (step.make_task is not None)
        for staff, widget in zip(step.staves, view.staves, strict=False):
            assert widget.clef == staff.clef and widget.caption == staff.caption
            assert len(widget.columns) == (1 if staff.note else 0)


def test_every_clef_shown_and_every_note_can_be_drawn(app: QApplication) -> None:
    """
    Check that the lesson only shows clefs the staff can draw, and only puts notes on clefs that can have them.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for step in CLEF_BASICS.steps:
        for staff in step.staves:
            assert staff.clef in settings.CLEF_BASICS_CLEFS
            assert not staff.note or staff.clef in settings.CLEFS  # the French violin and subbass clefs have no notes
    assert Staff(clef="alto").note == ""


def test_the_lessons_facts_agree_with_the_exercise(app: QApplication) -> None:
    """
    Check that the symbol and line the lesson teaches for each clef are the ones the exercise accepts.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    names = {"G": 1, "C": 2, "F": 3}
    for clef, symbol in SYMBOLS.items():
        assert names[symbol] and any(s == symbol for s, _ in clef_targets(clef))
    assert {clef: LINES[next(iter(clef_targets(clef)))[1] // 2] for clef in ("treble", "bass", "alto", "tenor")} == {
        "treble": "Second line",
        "bass": "Fourth line",
        "alto": "Middle line",
        "tenor": "Fourth line",
    }


def test_every_task_has_a_right_answer_among_its_buttons(app: QApplication) -> None:
    """
    Check each task maker many times: the answer is one of the buttons, and the staff beside it is right.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    rng = random.Random(7)
    for _ in range(60):
        task = symbol_task(rng)
        assert task.correct in task.choices and task.clef and task.correct == f"{SYMBOLS[task.clef]} clef"
        task = identify_task(rng)
        assert task.correct in task.choices and settings.CLEF_NAMES[task.clef] == task.correct
        task = line_task(rng)
        assert task.correct in task.choices == LINES and task.clef == "" and task.hint and task.explanation


def test_the_staff_beside_a_task_follows_it(app: QApplication) -> None:
    """
    Check that the staff draws the clef of the task, and is blank when the task has none.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    named = StepView(CLEF_BASICS.steps[8], rng=random.Random(2))  # name the clef
    assert named.task is not None and named.staves[0].clef == named.task.clef and not named.staves[0].clef_hidden
    lines = StepView(CLEF_BASICS.steps[7], rng=random.Random(2))  # find the line
    assert lines.task is not None and lines.staves[0].clef_hidden
    lines.ask()
    assert lines.staves[0].clef_hidden


def test_a_clef_task_can_be_answered_wrong_twice_and_is_then_given(app: QApplication) -> None:
    """
    Check that a wrong answer gets a hint, a second one gives the answer, and the right answer is praised.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = StepView(CLEF_BASICS.steps[8], rng=random.Random(3))
    task = view.task
    assert task is not None
    wrong = [b for b in view.choice_buttons if b.text() != task.correct]
    for number in range(GIVE_UP_AFTER):
        wrong[number].click()
    assert "Here it is" in view.feedback.text() and not view.again.isHidden()
    again = StepView(CLEF_BASICS.steps[8], rng=random.Random(3))
    right = next(b for b in again.choice_buttons if b.text() == (again.task.correct if again.task else ""))
    right.click()
    assert "Right" in again.feedback.text()


def test_the_lesson_page_opens_and_the_last_step_offers_the_exercise(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the page opens the lesson by its key and that the last step's button asks to practice Clef Basics.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    page = LessonsPage("clef-basics", step=len(CLEF_BASICS.steps) - 1)
    asked: list[str] = []
    page.practice_requested.connect(asked.append)
    assert page.view.counter.text() == "Step 10 of 10"
    step_view = page.view.pages.currentWidget()
    assert isinstance(step_view, StepView)
    step_view.practice_button.click()
    assert asked == ["ClefBasics"]


def test_the_exercise_has_a_reference_pane_that_opens_the_lesson(app: QApplication, clean_lessons: None) -> None:
    """
    Check that Clef Basics has the book button, that its pane has a row for every clef and that its button opens the lesson.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    panel = reference_panel_for(ClefBasics())
    assert isinstance(panel, ClefReferencePanel)
    assert list(panel.rows) == list(settings.CLEF_BASICS_CLEFS)
    for clef, words in panel.rows.items():
        assert settings.CLEF_NAMES[clef] in words.text() and CLEF_FACTS[clef] in words.text()
    window = MainWindow()
    window.show()
    window.open_exercise(ClefBasics)
    view = window.stack.currentWidget()
    assert isinstance(view, ExerciseView) and view.book_btn is not None
    view.book_btn.setChecked(True)
    assert isinstance(view._reference, ClefReferencePanel) and not view._reference.lesson_button.isHidden()
    view._reference.lesson_button.click()
    opened = window.stack.currentWidget()
    assert isinstance(opened, LessonsPage) and opened.view.lesson.key == "clef-basics"
