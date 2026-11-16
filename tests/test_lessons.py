"""
Tests for the lessons: the switch on the home page, the lesson page, the circle of fifths lesson and its soft tasks.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QLabel,
    QRadioButton,
)

from alto.exercises import REGISTRY
from alto.exercises.library import CircleOfFifths
from alto.lessons import LESSONS
from alto.lessons.circle_of_fifths import (
    CIRCLE_OF_FIFTHS,
    summary,
)
from alto.theory.fifths import (
    MAJORS,
    SIGNATURES,
)
from alto.ui.app_settings import AppSettingsDialog
from alto.ui.exercise_view import ExerciseView
from alto.ui.home import HomePage
from alto.ui.lesson import (
    GIVE_UP_AFTER,
    LessonsPage,
    LessonView,
    StepView,
    saved_step,
)
from alto.ui.main_window import MainWindow
from alto.ui.store import store
from alto.ui.transition_preview import (
    PAUSE_MS,
    TransitionPreview,
)
from alto.ui.transitions import (
    TRANSITIONS,
    save_transition,
    saved_transition,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from PySide6.QtWidgets import QApplication


@pytest.fixture
def clean_lessons() -> Iterator[None]:
    """
    Start a test with no saved lesson progress and the exercises showing, and leave it so.

    Yields
    ------
    None
        Once the saved state is cleared.
    """
    for key in ("lessons", "ui/homeMode"):
        store().remove(key)
    yield
    for key in ("lessons", "ui/homeMode"):
        store().remove(key)


def test_the_home_page_switches_between_exercises_and_lessons(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the switch at the top of the home page shows the exercise cards or the lesson cards, and remembers which.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    page = HomePage(REGISTRY)
    page.show()
    assert page.mode == "exercises" and page.cards[0].isVisible() and not page.lesson_cards[0].isVisible()
    page.mode_control.buttons[1].click()
    assert page.mode == "lessons" and page.lesson_cards[0].isVisible() and not page.cards[0].isVisible()
    assert HomePage(REGISTRY).mode == "lessons"  # remembered
    page.mode_control.buttons[0].click()
    assert page.mode == "exercises" and page.cards[0].isVisible()


def wait_until_still(page: HomePage) -> None:
    """
    Wait for a transition on the home page to finish, for at most three seconds.

    Parameters
    ----------
    page : HomePage
        The page.
    """
    for _ in range(150):
        if not page.canvas.running:
            return
        QTest.qWait(20)


def jump_to_the_end(page: HomePage) -> None:
    """
    Take a transition on the home page to its last frame at once, so a test need not wait for it in real time.

    Parameters
    ----------
    page : HomePage
        The page.
    """
    QTest.qWait(1)  # the transition begins from a zero-delay timer, so let that go first
    # noinspection PyProtectedMember
    animation = page.canvas._animation
    animation.setCurrentTime(animation.duration())
    wait_until_still(page)


def test_every_transition_plays_to_the_end_and_leaves_the_new_cards_showing(app: QApplication, clean_lessons: None) -> None:
    """
    Check that each transition covers the cards while it plays, finishes, and leaves the new cards in place.

    The first one is waited for in real time; the others are taken to their last frame, which ends them the same way.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    try:
        for number, transition in enumerate(TRANSITIONS):
            finish = wait_until_still if number == 0 else jump_to_the_end
            save_transition(transition.key)
            page = HomePage(REGISTRY)
            page.resize(1000, 600)
            page.show()
            QTest.qWait(30)
            page.mode_control.buttons[1].click()
            assert page.lesson_cards[0].isVisible() and not page.cards[0].isVisible()  # in place at once
            assert page.canvas.running == (transition.frame is not None), transition.key
            QTest.qWait(40)
            if transition.frame is not None:
                assert page.canvas.running and page.canvas.new and page.canvas.old, transition.key
            finish(page)
            assert not page.canvas.running and not page._hidden.isEnabled(), transition.key
            page.mode_control.buttons[0].click()  # and back again
            finish(page)
            assert page.cards[0].isVisible() and not page.lesson_cards[0].isVisible() and not page.canvas.running
            page.close()
    finally:
        store().remove("ui/homeTransition")


def test_a_second_flip_during_a_transition_ends_the_first(app: QApplication, clean_lessons: None) -> None:
    """
    Check that flipping the switch again while a transition plays settles on the side that was last asked for.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    save_transition("cascade")
    try:
        page = HomePage(REGISTRY)
        page.resize(1000, 600)
        page.show()
        QTest.qWait(30)
        page.mode_control.buttons[1].click()
        QTest.qWait(60)
        page.mode_control.buttons[0].click()
        wait_until_still(page)
        assert page.mode == "exercises" and page.cards[0].isVisible() and not page.lesson_cards[0].isVisible()
        assert not page.canvas.running
    finally:
        store().remove("ui/homeTransition")


def test_the_transition_is_cascade_until_another_is_chosen_in_the_settings(app: QApplication) -> None:
    """
    Check the default, that the settings offer all of them with "no transition", and that choosing one is remembered.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    store().remove("ui/homeTransition")
    assert saved_transition() == "cascade"
    assert len({item.key for item in TRANSITIONS}) == len(TRANSITIONS) > 11  # every one has its own key
    assert [item.key for item in TRANSITIONS][:2] == ["none", "cascade"]  # the default comes straight after "no transition"
    dialog = AppSettingsDialog()
    dialog.segment_buttons[3].click()
    assert set(dialog.transition_items) == {item.key for item in TRANSITIONS}
    assert dialog.transition_list.currentItem() is dialog.transition_items["cascade"]
    dialog.transition_list.setCurrentItem(dialog.transition_items["flip"])
    assert saved_transition() == "flip"
    dialog.transition_list.setCurrentItem(dialog.transition_items["none"])
    assert saved_transition() == "none"
    store().remove("ui/homeTransition")


def test_the_switch_has_an_icon_on_each_side(app: QApplication) -> None:
    """
    Check that both sides of the switch have an icon.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    page = HomePage(REGISTRY)
    assert [not button.icon().isNull() for button in page.mode_control.buttons] == [True, True]


def test_the_switch_is_compact_in_the_workspace_and_changes_only_the_list(app: QApplication, clean_lessons: None) -> None:
    """
    Keep the selected list independent of the activity and use compact controls in the workspace.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    control = window.home.mode_control
    window.open_exercise(CircleOfFifths)
    exercise = window.stack.currentWidget()
    assert control.isVisible() and [button.text() for button in control.buttons] == ["", ""]
    control.buttons[1].click()
    assert window.stack.currentWidget() is exercise and window.nav_stack.currentWidget() is window.lesson_nav
    window.open_lessons("circle-of-fifths")
    lesson = window.stack.currentWidget()
    control.buttons[0].click()
    assert window.stack.currentWidget() is lesson and window.nav_stack.currentWidget() is window.nav
    assert [button.text() for button in control.buttons] == ["", ""]
    window.show_home()
    assert [button.text() for button in control.buttons] == ["", ""]


def test_a_lesson_card_opens_its_lesson_and_leaving_returns_to_the_lessons(app: QApplication, clean_lessons: None) -> None:
    """
    Check that clicking a lesson card opens the lesson, with the lesson's title, and that leaving shows the lessons again.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    window.show_lessons()
    assert window.home.mode == "lessons"
    window.home.lesson_cards[0].click()
    assert window.title_label.text() == LESSONS[0].title and isinstance(window.stack.currentWidget(), LessonsPage)
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage)
    page.back_button.click()
    assert window.stack.currentWidget() is window.home and window.home.mode == "lessons"


def test_the_lessons_menu_entry_goes_to_the_lessons(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the lessons button at the top is always there, and takes you to the lessons on the home page.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    window.open_exercise(CircleOfFifths)
    window.lessons_action.trigger()
    assert window.stack.currentWidget() is window.home and window.home.mode == "lessons"


def test_the_reference_pane_has_a_button_that_opens_the_lesson(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the circle of fifths reference pane offers the lesson at its top, and that the button opens it.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    window.open_exercise(CircleOfFifths)
    view = window.stack.currentWidget()
    assert isinstance(view, ExerciseView) and view.book_btn is not None
    view.book_btn.setChecked(True)
    assert view._reference is not None and not view._reference.lesson_button.isHidden()
    view._reference.lesson_button.click()
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage) and page.view.lesson.key == "circle-of-fifths"
    page.back_button.click()
    assert window.stack.currentWidget() is view


def test_every_step_of_the_lesson_builds_and_has_something_to_read(app: QApplication) -> None:
    """
    Check that each step can be built, with its circle where it says it has one.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for step in CIRCLE_OF_FIFTHS.steps:
        view = StepView(step, rng=random.Random(1))
        assert step.title and step.text
        assert (view.circle is not None) == (step.circle != "none")
        assert (view.task is not None) == (step.make_task is not None)


def test_a_task_can_be_answered_wrong_twice_and_is_then_given(app: QApplication) -> None:
    """
    Check that a wrong answer gets a hint, and a second one gets the answer, and that nothing can be failed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = StepView(CIRCLE_OF_FIFTHS.steps[3], rng=random.Random(1))  # find the key with N sharps
    task = view.task
    assert task is not None and view.circle is not None
    right = next(iter(task.cells))
    wrong = ("outer", (right[1] + 5) % 12)
    view.circle.select(wrong[0], place=wrong[1])
    assert "Not quite" in view.feedback.text() and view.again.isHidden()
    for _ in range(GIVE_UP_AFTER - 1):
        view.circle.select(wrong[0], place=wrong[1])
    assert "Here it is" in view.feedback.text() and not view.again.isHidden()
    assert view.circle.cell == right


def test_a_right_answer_is_praised_and_another_can_be_asked(app: QApplication) -> None:
    """
    Check that the right cell is praised, and that Try another asks a fresh task.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = StepView(CIRCLE_OF_FIFTHS.steps[3], rng=random.Random(1))
    assert view.task is not None and view.circle is not None
    ring, place = next(iter(view.task.cells))
    view.circle.select(ring, place=place)
    assert "Right" in view.feedback.text() and not view.again.isHidden()
    view.again.click()
    assert view.feedback.text() == "" and view.again.isHidden()


def test_the_button_task_checks_the_letter(app: QApplication) -> None:
    """
    Check that the fifth task takes a button, praises the right letter and hints at a wrong one.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = StepView(CIRCLE_OF_FIFTHS.steps[1], rng=random.Random(3))
    assert view.task is not None
    wrong = next(button for button in view.choice_buttons if button.text() != view.task.correct)
    wrong.click()
    assert "Not quite" in view.feedback.text() and not wrong.isEnabled()
    right = next(button for button in view.choice_buttons if button.text() == view.task.correct)
    right.click()
    assert "Right" in view.feedback.text() and not any(button.isEnabled() for button in view.choice_buttons)


def test_walking_the_circle_steps_a_fifth_at_a_time(app: QApplication) -> None:
    """
    Check that the walk buttons go clockwise and counterclockwise round the outer ring, and tell the key signature.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = StepView(CIRCLE_OF_FIFTHS.steps[2], rng=random.Random(1))
    assert view.circle is not None
    for expected in (1, 2, 3):
        view.up.click()
        assert view.circle.cell == ("outer", expected)
        assert summary("outer", place=expected) in view.info.text()
    view.down.click()
    view.down.click()
    view.down.click()
    view.down.click()
    assert view.circle.cell == ("outer", 11) and "flat" in view.info.text()


def test_every_task_that_can_be_made_has_the_right_answer(app: QApplication) -> None:
    """
    Check each task maker many times: its answer is on the circle, and a task about sharps or flats counts them rightly.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    rng = random.Random(7)
    for step in CIRCLE_OF_FIFTHS.steps:
        if step.make_task is None:
            continue
        for _ in range(40):
            task = step.make_task(rng)
            assert task.prompt and task.hint and task.explanation
            if task.choices:
                assert task.correct in task.choices and len(set(task.choices)) == len(task.choices)
            else:
                assert task.cells and all(ring in {"outer", "inner"} and place in range(12) for ring, place in task.cells)
    sharps, flats = CIRCLE_OF_FIFTHS.steps[3], CIRCLE_OF_FIFTHS.steps[4]
    assert sharps.make_task is not None and flats.make_task is not None
    for _ in range(20):
        _, place = next(iter(sharps.make_task(rng).cells))
        assert SIGNATURES[place] > 0
        _, place = next(iter(flats.make_task(rng).cells))
        assert SIGNATURES[place] < 0 and MAJORS[place]


def test_a_lesson_remembers_its_step_and_leaves_from_either_end(app: QApplication, clean_lessons: None) -> None:
    """
    Check that moving through a lesson saves the step, that Back on the first step leaves, and that Finish leaves and resets.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    lesson = LESSONS[0]
    view = LessonView(lesson)
    left: list[bool] = []
    view.leave.connect(lambda: left.append(True))
    view.next_button.click()
    view.next_button.click()
    assert view.current == 2 and saved_step(lesson) == 2
    assert view.counter.text() == f"Step 3 of {len(lesson.steps)}"
    view.go(to=len(lesson.steps) - 1)
    assert view.next_button.text() == "Finish"
    view.next_button.click()
    assert left == [True] and saved_step(lesson) == 0
    first = LessonView(lesson, start=0)
    first.leave.connect(lambda: left.append(True))
    first.back_button.click()
    assert left == [True, True]


def test_a_started_lesson_says_where_to_continue_and_can_start_over(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the lesson's card on the home page says where it was left, and that Start over goes back to the first step.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    home = HomePage(REGISTRY)
    assert "Start" in [label.text() for label in home.lesson_cards[0].findChildren(QLabel)]
    page = LessonsPage("circle-of-fifths", step=3)
    home.show()  # showing the page brings its cards up to date
    assert "Continue at step 4" in [label.text() for label in home.lesson_cards[0].findChildren(QLabel)]
    page.restart_button.click()
    assert page.view.current == 0 and saved_step(LESSONS[0]) == 0


def test_the_last_step_offers_to_practise_the_exercise(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the Practise button leaves the lessons and opens the Circle of Fifths exercise.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.open_lessons("circle-of-fifths")
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage)
    page.view.go(to=len(CIRCLE_OF_FIFTHS.steps) - 1)
    step_view = page.view.pages.currentWidget()
    assert isinstance(step_view, StepView)
    step_view.practise_button.click()
    assert window.title_label.text() == "Circle of Fifths"


def test_lesson_mode_has_a_list_on_the_left_that_follows_the_steps(app: QApplication, clean_lessons: None) -> None:
    """
    Check that opening a lesson shows the lesson list in place of the exercise list, listing its steps, and keeps it in step.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    assert window.nav_stack.currentWidget() is window.nav
    window.open_lessons("circle-of-fifths")
    assert window.nav_stack.currentWidget() is window.lesson_nav
    nav = window.lesson_nav
    assert [item.text().strip().split(".", 1)[1].strip() for item in nav.step_items] == [step.title for step in LESSONS[0].steps]
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage)
    page.view.next_button.click()
    assert nav.currentItem() is nav.step_items[1]
    nav.itemClicked.emit(nav.step_items[4])  # a click on a step goes to it
    assert page.view.current == 4 and nav.currentItem() is nav.step_items[4]


def test_the_lesson_list_can_be_hidden_and_shown_with_its_button(app: QApplication, clean_lessons: None) -> None:
    """
    Check that the lesson page has the toggle for the list, and that it works as the exercise one does.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    window.open_lessons("circle-of-fifths")
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage)
    QTest.qWait(600)
    assert window.sidebar_width() > 0 and page.sidebar_button.toolTip() == "Hide lesson list"
    page.sidebar_button.click()
    QTest.qWait(600)
    assert window.sidebar_width() == 0 and page.sidebar_button.toolTip() == "Show lesson list"
    window.toggle_sidebar()  # leave it as it was found
    QTest.qWait(600)


def test_leaving_a_lesson_brings_back_the_right_list(app: QApplication, clean_lessons: None) -> None:
    """
    Check that leaving a lesson that was opened from an exercise brings back the exercise list, and from the home page, no list.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    window = MainWindow()
    window.show()
    window.open_exercise(CircleOfFifths)
    QTest.qWait(600)
    window.open_lessons("circle-of-fifths")
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage)
    page.back_button.click()
    assert window.stack.currentWidget() is not window.home and window.nav_stack.currentWidget() is window.nav
    window.show_lessons()
    window.home.lesson_cards[0].click()
    QTest.qWait(600)
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage)
    page.back_button.click()
    QTest.qWait(600)
    assert window.stack.currentWidget() is window.home and window.sidebar_width() == 0
    window.home.set_mode("exercises")


def test_the_circle_of_a_lesson_is_never_cut_off(app: QApplication, clean_lessons: None) -> None:
    """
    Check that in a window of the default size, and a smaller one, the whole circle shows on every step that has one.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    clean_lessons : None
        Clears what is saved.
    """
    for size in ((1100, 820), (1000, 640)):
        window = MainWindow()
        window.resize(*size)
        window.show()
        window.open_lessons("circle-of-fifths")
        page = window.stack.currentWidget()
        assert isinstance(page, LessonsPage)
        for number in range(len(LESSONS[0].steps)):
            page.view.go(to=number)
            QTest.qWait(40)
            step = page.view.pages.currentWidget()
            assert isinstance(step, StepView)
            if step.circle is not None:
                bottom = step.circle.mapTo(page.view, step.circle.rect().bottomLeft()).y()
                assert bottom <= page.view.height() and min(step.circle.width(), step.circle.height()) >= 300, (size, number)
        window.close_overlay()
        window.close()


def test_the_transition_settings_have_a_list_on_the_left_and_a_preview_that_plays_once(app: QApplication) -> None:
    """
    Check the layout of the Transitions section, and that a transition is played once in the preview, and not again.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    store().remove("ui/homeTransition")
    try:
        dialog = AppSettingsDialog()
        dialog.resize(1000, 640)
        dialog.show()
        dialog.segment_buttons[3].click()
        QTest.qWait(50)
        listing, preview = dialog.transition_list, dialog.transition_preview
        assert listing.mapTo(dialog, listing.rect().topLeft()).x() < preview.mapTo(dialog, preview.rect().topLeft()).x()
        assert not dialog.appearance_pages.currentWidget().findChildren(QRadioButton)  # a list, not radio buttons
        dialog.transition_list.setCurrentItem(dialog.transition_items["flip"])
        assert preview.transition.key == "flip" and saved_transition() == "flip" and preview.side == 0
        QTest.qWait(PAUSE_MS + 200)  # after a short rest it plays
        assert preview.stage.canvas.running and preview.side == 1
        for _ in range(150):
            if not preview.stage.canvas.running:
                break
            QTest.qWait(20)
        assert not preview.stage.canvas.running
        QTest.qWait(PAUSE_MS * 3)  # and it does not start again by itself
        assert not preview.stage.canvas.running and preview.side == 1
        preview.replay()  # unless asked to
        assert preview.side == 0
        QTest.qWait(PAUSE_MS + 200)
        assert preview.side == 1
        dialog.transition_list.setCurrentItem(dialog.transition_items["none"])
        QTest.qWait(PAUSE_MS + 200)
        assert not preview.stage.canvas.running and preview.side == 1  # it switches at once, with nothing to play
        dialog.close()
    finally:
        store().remove("ui/homeTransition")


def test_the_switch_in_the_preview_works(app: QApplication) -> None:
    """
    Check that pressing a side of the switch in the preview plays the transition to it, and back, as often as wanted.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    store().remove("ui/homeTransition")
    try:
        preview = TransitionPreview()
        preview.resize(700, 500)
        preview.show()
        preview.show_transition("crossfade")
        assert all(button.isEnabled() for button in preview.switch.buttons)
        preview.switch.buttons[1].click()
        assert preview.side == 1 and preview.stage.canvas.running and preview.switch.current() == 1
        QTest.qWait(PAUSE_MS + 300)  # the rest that it would have taken to play by itself passes, and nothing else starts
        assert preview.side == 1
        preview.switch.buttons[0].click()  # back again: if the last one is still playing, it ends first
        assert preview.side == 0 and preview.switch.current() == 0
        preview.switch.buttons[0].click()  # the side that is already showing: nothing happens
        assert preview.side == 0
        for _ in range(150):
            if not preview.stage.canvas.running:
                break
            QTest.qWait(20)
        assert not preview.stage.canvas.running
        preview.close()
    finally:
        store().remove("ui/homeTransition")
