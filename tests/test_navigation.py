"""
Navigation lists and tile browsing preserve activities while remaining
independently selectable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import (
    QPoint,
    QPropertyAnimation,
    Qt,
)
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import QLabel, QToolButton

from alto import settings
from alto.exercises.library import (
    KeyboardIntervals,
    KeyboardNotes,
    NoteNames,
)
from alto.learning import (
    Database,
    Learner,
)
from alto.ui import motion
from alto.ui.exercise_view import ExerciseView
from alto.ui.glossary import GlossaryPage
from alto.ui.lesson import LessonsPage
from alto.ui.main_window import MainWindow
from alto.ui.transitions import SIDEBAR_SLIDE_MS, save_transition
from alto.ui.widgets import SidebarToggle

if TYPE_CHECKING:
    from collections.abc import Iterator

    from PySide6.QtWidgets import QApplication


@pytest.fixture
def window(app: QApplication) -> Iterator[MainWindow]:
    """
    Provide a visible window with data tools enabled.

    Parameters
    ----------
    app : QApplication
        The shared application.

    Yields
    ------
    MainWindow
        The navigation window.
    """
    db = Database()
    page = MainWindow(Learner(db, profile=db.add_profile("Ada")))
    page.resize(1100, 820)
    page.show()
    yield page
    page.close()
    page.deleteLater()


def test_tiles_are_the_default_and_navigation_is_on_the_left(
    window: MainWindow,
) -> None:
    """
    Start with tiles and place navigation to the left of the separate
    data tools.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    assert window.stack.currentWidget() is window.home
    assert window.sidebar_width() == 0
    assert window.pane_button.accessibleName() == "Show navigation pane"
    assert window.view_button.text() == ""
    assert window.pane_button.toolTip() == "Show navigation pane"
    assert window.home.resume_button.isHidden()
    window.view_button.click()
    assert window.stack.currentWidget() is window.empty_page
    window.view_button.click()
    assert (
        window.stack.currentWidget() is window.home
        and window.sidebar_width() == 0
    )


def test_grid_button_returns_to_the_workspace_after_visiting_tiles(
    window: MainWindow,
) -> None:
    """
    Return to the same exercise and pane state when the grid button is
    clicked again.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_exercise(NoteNames)
    activity = window.stack.currentWidget()
    assert isinstance(activity, ExerciseView)
    question = activity.question
    pane_width = window.sidebar_width()
    window.view_button.click()
    assert window.stack.currentWidget() is window.home
    window.view_button.click()
    assert window.stack.currentWidget() is activity
    assert (
        not window.home.canvas.running
        and not window.home._transition_start.isActive()
    )
    assert (
        activity.question is question and window.sidebar_width() == pane_width
    )
    control_x = window.home.mode_control.mapTo(window, QPoint()).x()
    view_x = window.view_button.mapTo(window, QPoint()).x()
    stats_x = window.stats_button.mapTo(window, QPoint()).x()
    database_x = window.database_button.mapTo(window, QPoint()).x()
    assert (
        control_x
        < window.pane_button.mapTo(window, QPoint()).x()
        < view_x
        < stats_x
        < database_x
    )


@pytest.mark.parametrize(
    "source",
    ["exercise", "lesson", "statistics", "database", "lessons shortcut"],
)
def test_return_to_tiles_animates_from_a_blank_grid(
    window: MainWindow,
    source: str,
) -> None:
    """
    Reveal only the destination tiles at their final positions when
    returning from another page.

    Parameters
    ----------
    window : MainWindow
        The visible navigation window.
    source : str
        Navigation route back to the grid.
    """
    home = window.home
    save_transition("cascade")
    if source == "statistics":
        window.open_stats()
        window.close_overlay()
    elif source == "database":
        window.open_database()
        window.view_button.click()
    elif source == "lesson":
        window.open_lessons("circle-of-fifths")
        window.view_button.click()
    else:
        window.open_exercise(NoteNames)
        window._set_sidebar(True, animate=False)
        if source == "lessons shortcut":
            window.show_lessons()
        else:
            window.view_button.click()

    canvas = home.canvas
    assert window.stack.currentWidget() is home and window.sidebar_width() == 0
    assert canvas.running and not canvas.old and not canvas.new
    assert home._hidden.isEnabled() and home._hidden.opacity() == 0
    QTest.qWait(1)
    cards = (
        home.lesson_cards
        if source in {"lesson", "lessons shortcut"}
        else home.cards
    )
    viewport = home.scroll_area.viewport()
    assert canvas.geometry() == viewport.rect()
    assert [sprite.rect.topLeft().toPoint() for sprite in canvas.new] == [
        card.mapTo(viewport, QPoint()) for card in cards
    ]
    canvas._animation.setCurrentTime(150)
    assert 0 < canvas.new[0].opacity < 1
    canvas._animation.setCurrentTime(canvas._animation.duration())
    assert not canvas.running and not home._hidden.isEnabled()


@pytest.mark.parametrize(
    "button",
    ["glossary_button", "stats_button", "database_button"],
)
def test_utility_page_slides_in_from_the_right(
    window: MainWindow,
    button: str,
) -> None:
    """
    Keep the outgoing grid visible as the selected utility page enters
    from the right.

    Parameters
    ----------
    window : MainWindow
        The visible navigation window.
    button : str
        Toolbar button for the destination.
    """
    save_transition("cascade")
    stack = window.stack
    before = stack.grab().toImage()
    getattr(window, button).click()
    slide = next(
        animation
        for animation in stack.findChildren(QPropertyAnimation)
        if animation.propertyName() == b"pos"
    )
    incoming = slide.targetObject()
    assert isinstance(incoming, QLabel) and incoming.x() == stack.width()
    assert stack.grab().toImage() == before
    slide.setCurrentTime(slide.duration() // 2)
    assert 0 < incoming.x() < stack.width()
    frame = stack.grab().toImage()
    edge = round(incoming.x() * frame.devicePixelRatio())
    assert frame.copy(0, 0, edge, frame.height()) == before.copy(
        0,
        0,
        edge,
        frame.height(),
    )
    revealed = frame.width() - edge
    assert frame.copy(
        edge,
        0,
        revealed,
        frame.height(),
    ) == incoming.pixmap().toImage().copy(0, 0, revealed, frame.height())
    slide.setCurrentTime(slide.duration())
    assert (
        not incoming.isVisible()
        and stack.currentWidget().geometry() == stack.contentsRect()
    )
    window.home.resume_button.click()
    assert stack.currentWidget() is window.home and window.home.canvas.running


def test_switching_utilities_mid_slide_keeps_the_original_back_destination(
    window: MainWindow,
) -> None:
    """
    Switch utilities in mid-flight, resize, and return to the same
    exercise.

    Parameters
    ----------
    window : MainWindow
        The visible navigation window.
    """
    window.open_exercise(NoteNames)
    activity = window.stack.currentWidget()
    window.glossary_button.click()
    window.stats_button.click()
    window.database_button.click()
    window.resize(1300, 900)
    QTest.qWait(260)
    page = window.stack.currentWidget()
    assert page is not None and page.geometry() == window.stack.contentsRect()
    window.home.resume_button.click()
    assert (
        window.stack.currentWidget() is activity and window.stack.count() == 3
    )


def test_grid_return_honors_disabled_transitions(window: MainWindow) -> None:
    """
    Show the live grid immediately when transitions are disabled.

    Parameters
    ----------
    window : MainWindow
        The visible navigation window.
    """
    save_transition("none")
    window.open_glossary()
    assert not window.stack.findChildren(QPropertyAnimation)
    window.close_overlay()
    window.open_exercise(NoteNames)
    window.view_button.click()
    assert (
        window.home.cards[0].isVisible()
        and not window.home._hidden.isEnabled()
    )
    assert not window.home.canvas.running


def test_empty_workspace_prompt_follows_the_selected_section(
    window: MainWindow,
) -> None:
    """
    Switch tile sections without opening the pane, then show the
    appropriate empty prompt.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.home.mode_control.buttons[1].click()
    assert (
        window.stack.currentWidget() is window.home
        and window.home.mode == "lessons"
    )
    assert window.sidebar_width() == 0
    window.pane_button.click()
    motion.settle()
    assert [button.text() for button in window.home.mode_control.buttons] == [
        "",
        "",
    ]
    assert [
        button.toolTip() for button in window.home.mode_control.buttons
    ] == ["Exercises", "Lessons"]
    assert window.view_button.accessibleName() == "Tiles"
    assert window.view_button.text() == ""
    assert window.view_button.toolTip() == "Return to tiles"
    assert window.stack.currentWidget() is window.empty_page
    assert window.empty_page.text() == "Select a lesson to begin."
    assert (
        window.nav_stack.currentWidget() is window.lesson_nav
        and window.lesson_nav.count() > 0
    )
    assert window.sidebar_width() > 0
    window.home.mode_control.buttons[0].click()
    assert window.empty_page.text() == "Select an exercise to begin."
    assert window.nav_stack.currentWidget() is window.nav
    window.view_button.click()
    motion.settle()
    assert window.stack.currentWidget() is window.home
    assert (
        window.pane_button.accessibleName() == "Show navigation pane"
        and window.sidebar_width() == 0
    )
    assert [button.text() for button in window.home.mode_control.buttons] == [
        "",
        "",
    ]


@pytest.mark.parametrize("section", ["exercises", "lessons"])
@pytest.mark.parametrize("origin", ["tiles", "exercise", "lesson"])
def test_section_buttons_leave_the_glossary(
    window: MainWindow,
    section: str,
    origin: str,
) -> None:
    """
    Open either catalog from the glossary and retain the prior activity.

    Parameters
    ----------
    window : MainWindow
        The visible navigation window.
    section : str
        The requested toolbar destination.
    origin : str
        The page from which the glossary was opened.
    """
    if origin == "exercise":
        window.open_exercise(NoteNames)
    elif origin == "lesson":
        window.open_lessons("circle-of-fifths")
    previous = window.stack.currentWidget()
    window.glossary_button.click()
    assert isinstance(window.stack.currentWidget(), GlossaryPage)
    window.home.mode_control.buttons[int(section == "lessons")].click()
    assert window.stack.currentWidget() is window.home
    assert window.home.mode == section
    assert not window.glossary_button.isChecked()
    cards = (
        window.home.lesson_cards if section == "lessons" else window.home.cards
    )
    assert any(card.isVisible() for card in cards)
    if origin != "tiles":
        window.home.resume_button.click()
        assert window.stack.currentWidget() is previous


def test_switching_lists_preserves_the_exercise(window: MainWindow) -> None:
    """
    Browse lessons from an exercise without replacing the question or
    clearing an answer selection.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    settings.keyboard.require_octave = True
    window.open_exercise(KeyboardNotes)
    view = window.stack.currentWidget()
    assert isinstance(view, ExerciseView) and view.question is not None
    question = view.question
    view.buttons[0].click()
    # noinspection PyProtectedMember
    selected = dict(view._pending)
    window.home.mode_control.buttons[1].click()
    assert window.stack.currentWidget() is view and view.question is question
    assert window.nav_stack.currentWidget() is window.lesson_nav
    # noinspection PyProtectedMember
    assert view._pending == selected
    window.home.mode_control.buttons[0].click()
    assert (
        window.stack.currentWidget() is view
        and window.nav_stack.currentWidget() is window.nav
    )
    window.view_button.click()
    window.pane_button.click()
    assert window.stack.currentWidget() is view and view.question is question
    # noinspection PyProtectedMember
    assert view._pending == selected


def test_tiles_pause_question_advancement_and_answer_timing(
    window: MainWindow,
) -> None:
    """
    Freeze a completed question while browsing tiles, then resume its
    pending advance.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_exercise(NoteNames)
    view = window.stack.currentWidget()
    assert isinstance(view, ExerciseView) and view.question is not None
    question = view.question
    view.buttons[question.choices.index(question.answer)].click()
    assert view.answered
    # noinspection PyProtectedMember
    clock = view._clock
    window.view_button.click()
    QTest.qWait(1400)
    assert view.question is question
    window.pane_button.click()
    assert window.stack.currentWidget() is view and view.question is question
    # noinspection PyProtectedMember
    assert view._clock - clock >= 1.0
    # noinspection PyProtectedMember
    assert view._advance.isActive()
    # noinspection PyProtectedMember
    view._advance.stop()


def test_reopening_the_active_exercise_tile_reuses_its_question(
    window: MainWindow,
) -> None:
    """
    Return from the active exercise's tile without starting a
    replacement session.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_exercise(NoteNames)
    view = window.stack.currentWidget()
    assert isinstance(view, ExerciseView)
    question = view.question
    window.show_home()
    window.open_exercise(NoteNames)
    assert window.stack.currentWidget() is view and view.question is question


def test_lesson_progress_and_the_exercise_survive_tiles_and_statistics(
    window: MainWindow,
) -> None:
    """
    Retain both activity pages and the lesson's back destination through
    utility and tile browsing.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_exercise(NoteNames)
    exercise = window.stack.currentWidget()
    window.open_lessons("circle-of-fifths")
    lesson = window.stack.currentWidget()
    assert isinstance(lesson, LessonsPage)
    lesson.view.go(to=2)
    window.home.mode_control.buttons[0].click()
    assert (
        window.stack.currentWidget() is lesson
        and window.nav_stack.currentWidget() is window.nav
    )
    window.view_button.click()
    window.pane_button.click()
    assert window.stack.currentWidget() is lesson and lesson.view.current == 2
    window.stats_button.click()
    assert window.title_label.text() == "Statistics"
    window.close_overlay()
    assert window.stack.currentWidget() is lesson and lesson.view.current == 2
    lesson.back_button.click()
    assert window.stack.currentWidget() is exercise


def test_navigation_rebuild_preserves_tiles_and_the_selected_list(
    window: MainWindow,
) -> None:
    """
    Restore the selected browser list and hidden workspace when the
    theme is rebuilt.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_exercise(NoteNames)
    window.home.mode_control.buttons[1].click()
    window.view_button.click()
    window.rebuild()
    assert (
        window.stack.currentWidget() is window.home
        and window.home.mode == "lessons"
    )
    assert window.pane_button.accessibleName() == "Show navigation pane"
    window.pane_button.click()
    assert isinstance(window.stack.currentWidget(), ExerciseView)
    assert window.nav_stack.currentWidget() is window.lesson_nav


def test_empty_lesson_pane_survives_rebuild(window: MainWindow) -> None:
    """
    Keep the empty lesson workspace rather than silently reverting to
    tiles on theme changes.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.home.mode_control.buttons[1].click()
    window.pane_button.click()
    window.rebuild()
    assert window.stack.currentWidget() is window.empty_page
    assert window.empty_page.text() == "Select a lesson to begin."
    assert window.view_button.accessibleName() == "Tiles"


def test_statistics_over_a_lesson_survive_theme_rebuild(
    window: MainWindow,
) -> None:
    """
    Keep utility back navigation attached to the lesson rather than
    losing it during a rebuild.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_exercise(NoteNames)
    window.open_lessons("circle-of-fifths")
    lesson = window.stack.currentWidget()
    assert isinstance(lesson, LessonsPage)
    lesson.view.go(to=3)
    window.open_stats()
    window.rebuild()
    assert window.title_label.text() == "Statistics"
    window.close_overlay()
    lesson = window.stack.currentWidget()
    assert isinstance(lesson, LessonsPage) and lesson.view.current == 3
    lesson.back_button.click()
    assert isinstance(window.stack.currentWidget(), ExerciseView)


def test_retained_pages_do_not_accumulate_when_switching_activities(
    window: MainWindow,
) -> None:
    """
    Keep one exercise and one lesson while allowing repeated tile and
    sidebar navigation.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    for _ in range(3):
        for exercise in (NoteNames, KeyboardNotes):
            window.open_exercise(exercise)
            window.open_lessons("circle-of-fifths")
            window.show_home()
            window.toggle_navigation()
    assert (
        window.stack.count() == 4
    )  # tiles, empty workspace, one exercise, one lesson
    window.open_database()
    window.close_overlay()
    assert window.stack.count() == 4


def test_opening_the_navigation_pane_dismisses_a_utility_page(
    window: MainWindow,
) -> None:
    """
    Do not leave hidden statistics pages in the stack when opening the
    empty navigation workspace.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_stats()
    window.pane_button.click()
    assert window.stack.currentWidget() is window.empty_page
    assert window.stack.count() == 2
    window.view_button.click()
    window.pane_button.click()
    assert window.stack.currentWidget() is window.empty_page


def test_sidebar_tooltip_describes_the_selected_list(
    window: MainWindow,
) -> None:
    """
    Toggle the pane from the header without replacing the exercise or
    exposing a local collapse button.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_exercise(NoteNames)
    view = window.stack.currentWidget()
    assert isinstance(view, ExerciseView)
    motion.settle()
    window.home.mode_control.buttons[1].click()
    assert not hasattr(view, "sidebar_button")
    assert window.pane_button.toolTip() == "Hide navigation pane"
    question = view.question
    window.pane_button.click()
    motion.settle()
    assert window.sidebar_width() == 0
    assert window.stack.currentWidget() is view and view.question is question
    assert window.pane_button.toolTip() == "Show navigation pane"
    window.rebuild()
    view = window.stack.currentWidget()
    assert isinstance(view, ExerciseView)
    question = view.question
    assert window.sidebar_width() == 0
    assert window.pane_button.toolTip() == "Show navigation pane"
    window.pane_button.click()
    motion.settle()
    assert window.sidebar_width() > 0
    assert window.stack.currentWidget() is view and view.question is question


def test_tiles_have_a_back_button_for_the_current_exercise(
    window: MainWindow,
) -> None:
    """
    Return directly from either tile section to the retained question
    and partial answer.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    settings.keyboard.require_octave = True
    window.open_exercise(KeyboardNotes)
    view = window.stack.currentWidget()
    assert isinstance(view, ExerciseView)
    question = view.question
    view.buttons[0].click()
    # noinspection PyProtectedMember
    selected = dict(view._pending)
    window.view_button.click()
    back = window.home.resume_button
    assert back.isVisible() and back.text() == "←  Back"
    assert (
        abs(
            back.mapTo(window, QPoint()).y()
            - window.search_field.mapTo(window, QPoint()).y(),
        )
        < 10
    )
    assert (
        back.mapTo(window, QPoint()).x()
        > window.search_row.mapTo(
            window,
            window.search_row.rect().topRight(),
        ).x()
    )
    window.home.mode_control.buttons[1].click()
    assert back.isVisible() and back.text() == "←  Back"
    back.click()
    assert window.stack.currentWidget() is view and view.question is question
    # noinspection PyProtectedMember
    assert view._pending == selected
    assert window.nav_stack.currentWidget() is window.lesson_nav


def test_tiles_back_button_returns_to_the_lesson_step(
    window: MainWindow,
) -> None:
    """
    Provide the same direct return path for the active lesson.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_lessons("circle-of-fifths")
    page = window.stack.currentWidget()
    assert isinstance(page, LessonsPage)
    page.view.go(to=2)
    window.view_button.click()
    assert window.home.resume_button.text() == "←  Back"
    window.home.mode_control.buttons[0].click()
    assert window.home.resume_button.text() == "←  Back"
    window.home.resume_button.click()
    assert window.stack.currentWidget() is page and page.view.current == 2


def test_search_is_below_the_quiet_icon_only_toolbar(
    window: MainWindow,
) -> None:
    """
    Keep the section pair distinct from the view action, with search on
    the row below.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    control_bottom = window.home.mode_control.mapTo(
        window,
        window.home.mode_control.rect().bottomLeft(),
    ).y()
    search_top = window.search_field.mapTo(window, QPoint()).y()
    view_bottom = window.view_button.mapTo(
        window,
        window.view_button.rect().bottomLeft(),
    ).y()
    assert search_top > control_bottom
    assert search_top > view_bottom
    assert window.home.mode_control.parentWidget() is window.navigation_group
    assert window.view_button.parentWidget() is window.navigation_group
    assert window.navigation_group.layout().spacing() == 10
    assert window.navigation_divider.isVisible()
    assert window.navigation_divider.width() == 1
    assert (
        window.navigation_divider.height() < window.home.mode_control.height()
    )
    pair_right = window.home.mode_control.mapTo(
        window,
        window.home.mode_control.rect().topRight(),
    ).x()
    assert window.view_button.mapTo(window, QPoint()).x() - pair_right >= 20
    assert [button.text() for button in window.home.mode_control.buttons] == [
        "",
        "",
    ]
    assert [
        button.toolTip() for button in window.home.mode_control.buttons
    ] == ["Exercises", "Lessons"]
    assert window.view_button.text() == ""


def test_search_filters_tiles_and_navigation_and_clear_restores_them(
    window: MainWindow,
) -> None:
    """
    Search names without case sensitivity and hide empty categories in
    the matching list.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.search_field.setText("  KEYBOARD  ")
    assert [
        card.accessibleName().split(",")[0]
        for card in window.home.cards
        if not card.isHidden()
    ] == [
        "Keyboard Note Identification",
        "Keyboard Interval Identification",
    ]
    assert [
        name for name, item in window._items.items() if not item.isHidden()
    ] == [KeyboardNotes, KeyboardIntervals]
    headings = [
        window.nav.item(i)
        for i in range(window.nav.count())
        if window.nav.item(i).flags() == Qt.ItemFlag.NoItemFlags
    ]
    assert [
        heading.text() for heading in headings if not heading.isHidden()
    ] == ["NOTATION", "INTERVALS"]
    window.search_field.clear()
    assert all(not card.isHidden() for card in window.home.cards)
    assert all(not item.isHidden() for item in window._items.values())
    assert all(not heading.isHidden() for heading in headings)


def test_shuffle_uses_matching_exercises_from_another_category(
    window: MainWindow,
) -> None:
    """
    Shuffle from the grid or an exercise while respecting search,
    checkboxes and the last category.

    Parameters
    ----------
    window : MainWindow
        The visible navigation window.
    """
    home = window.home
    shuffle = window.shuffle_button
    assert shuffle.isVisible() and not shuffle.icon().isNull()
    assert (
        shuffle.mapTo(window, shuffle.rect().topRight()).x()
        < home.category_filter.mapTo(window, QPoint()).x()
    )
    window.search_field.setText("keyboard")
    assert set(window._shuffle_choices()) == {KeyboardNotes, KeyboardIntervals}
    home._filter_leaves[KeyboardIntervals.name].setCheckState(
        0,
        Qt.CheckState.Unchecked,
    )
    shuffle.click()
    assert window.stack.currentWidget() is window._exercise_page
    assert window.nav.currentItem() is window._items[KeyboardNotes]
    assert shuffle.isVisible() and shuffle.isChecked()
    first = window._exercise_page
    assert first is not None and not first.shuffle_answers
    home.category_filter.click()
    assert (
        home.filter_sidebar.isVisible()
        and window.stack.currentWidget() is first
    )
    home._filter_leaves[KeyboardIntervals.name].setCheckState(
        0,
        Qt.CheckState.Checked,
    )
    assert {
        cls for cls, row in window._items.items() if not row.isHidden()
    } == {KeyboardNotes, KeyboardIntervals}
    assert first.shuffle_answers and first.question is not None
    first.settings_panel.next_question_mode = "Wait"
    first.submit(first.question.answer, button=None)
    assert (
        first.next_button.isVisible() and window.stack.currentWidget() is first
    )
    first.next_button.click()
    second = window._exercise_page
    assert (
        second is not None
        and second.question is not None
        and second.shuffle_answers
    )
    assert window.nav.currentItem() is window._items[KeyboardIntervals]
    second.settings_panel.next_question_mode = "Immediately"
    second.submit("wrong", button=None)
    assert second.answered and second._advance.isActive()
    shuffled = QSignalSpy(second.shuffle_requested)
    motion.settle()  # the next question comes, from the other exercise
    assert shuffled.count() == 1
    assert window.nav.currentItem() is window._items[KeyboardNotes]
    assert shuffle.isChecked()
    shuffle.click()
    current = window._exercise_page
    assert (
        current is not None
        and current.question is not None
        and not current.shuffle_answers
    )
    current.settings_panel.next_question_mode = "Immediately"
    current.submit(current.question.answer, button=None)
    motion.settle()  # the next question comes
    assert window._exercise_page is current and not current.answered
    shuffle.click()
    assert window._exercise_page is current and current.shuffle_answers
    window.rebuild()
    shuffle = window.shuffle_button
    assert (
        shuffle.isChecked()
        and window.nav.currentItem() is window._items[KeyboardNotes]
    )
    window.search_field.setText("no matching exercise")
    assert shuffle.isEnabled()
    shuffle.click()
    assert not shuffle.isEnabled()
    window.show_home()
    window.home.mode_control.buttons[1].click()
    assert shuffle.isHidden()


def test_shuffle_between_two_notation_exercises(window: MainWindow) -> None:
    """
    Alternate the two selected note exercises and allow shuffle to be
    toggled throughout practice.

    Parameters
    ----------
    window : MainWindow
        The visible practice window.
    """
    home = window.home
    home.category_filter.click()
    home._filter_root.setCheckState(0, Qt.CheckState.Unchecked)
    for cls in (NoteNames, KeyboardNotes):
        home._filter_leaves[cls.name].setCheckState(0, Qt.CheckState.Checked)
    window.open_exercise(NoteNames)
    shuffle = window.shuffle_button
    assert shuffle.isEnabled()
    shuffle.click()
    for expected in (KeyboardNotes, NoteNames):
        view = window._exercise_page
        assert (
            view is not None
            and view.question is not None
            and shuffle.isChecked()
        )
        view.settings_panel.next_question_mode = "Wait"
        view.submit(view.question.answer, button=None)
        view.next_button.click()
        assert window.nav.currentItem() is window._items[expected]
        shuffle.click()
        assert not shuffle.isChecked() and shuffle.isEnabled()
        shuffle.click()
    home._filter_leaves[KeyboardNotes.name].setCheckState(
        0,
        Qt.CheckState.Unchecked,
    )
    shuffle.click()
    assert not shuffle.isChecked() and shuffle.isEnabled()
    window.show_home()
    shuffle.click()
    assert (
        shuffle.isChecked()
        and window.stack.currentWidget() is window._exercise_page
    )
    assert window.nav.currentItem() is window._items[NoteNames]


@pytest.mark.parametrize("pace", ["After Animation", "Immediately"])
# about when the next question comes after the answer is played
@pytest.mark.motion
def test_shuffle_after_correct_audio_answer(
    window: MainWindow,
    pace: str,
) -> None:
    """
    Advance a correct keyboard answer at the selected pace while keeping
    shuffle checked.

    Parameters
    ----------
    window : MainWindow
        The visible practice window.
    pace : str
        The automatic advancement mode for this answer.
    """
    window.search_field.setText("keyboard")
    window.open_exercise(KeyboardNotes)
    window.shuffle_button.click()
    view = window._exercise_page
    assert view is not None and view.question is not None
    view.settings_panel.next_question_mode = pace
    changes = QSignalSpy(view.shuffle_requested)
    view.submit(view.question.answer, button=None)
    assert window.stack.currentWidget() is view
    assert changes.wait(3000)
    assert window.nav.currentItem() is window._items[KeyboardIntervals]
    assert window.shuffle_button.isChecked()


def test_calendar_shuffle_with_no_other_cards_ready(
    window: MainWindow,
) -> None:
    """
    Continue locally when the other matching category has reached its
    daily limit.

    Parameters
    ----------
    window : MainWindow
        The practice window with a learner profile.
    """
    learner = window.learner
    assert learner is not None
    learner.set_mode("SM-2")
    profile = learner.profile.id
    learner.calendar.set_limits(profile, new_cards=0, reviews=0)
    window.search_field.setText("keyboard")
    window.shuffle_button.click()
    view = window._exercise_page
    assert view is not None and view.question is None
    learner.calendar.set_limits(
        profile,
        exercise=type(view.exercise).__name__,
        new_cards=2,
        reviews=0,
    )
    view.next_button.click()
    question = view.question
    assert question is not None
    view.settings_panel.next_question_mode = "Wait"
    view.submit(question.answer, button=None)
    view.next_button.click()
    assert (
        window._exercise_page is view
        and view.question is not None
        and view.question is not question
    )


def test_shuffle_prefers_another_category_with_cards_ready(
    window: MainWindow,
) -> None:
    """
    Prefer ready cards outside the current category, then use a selected
    sibling when those run out.

    Parameters
    ----------
    window : MainWindow
        The visible practice window.
    """
    learner = window.learner
    assert learner is not None
    learner.set_mode("SM-2")
    learner.calendar.set_limits(
        learner.profile.id,
        exercise="KeyboardIntervals",
        new_cards=1,
        reviews=0,
    )
    window.home.restore_tile_filters(
        {
            "exercises": frozenset(
                cls.name
                for cls in (NoteNames, KeyboardNotes, KeyboardIntervals)
            ),
        },
    )
    window.open_exercise(NoteNames)
    window.shuffle_button.click()
    window._shuffle_exercise()
    assert window.nav.currentItem() is window._items[KeyboardIntervals]
    view = window._exercise_page
    assert view is not None and view.question is not None
    view.submit(view.question.answer, button=None)
    window.open_exercise(NoteNames)
    window._shuffle_exercise()
    assert window.nav.currentItem() is window._items[KeyboardNotes]


def test_category_filter_on_the_search_row(window: MainWindow) -> None:
    """
    Combine tile search with a category and keep valid selections when
    switching sections.

    Parameters
    ----------
    window : MainWindow
        The visible navigation window.
    """
    home = window.home
    picker = home.category_filter
    assert (
        picker.isVisible() and not picker.icon().isNull() and not picker.text()
    )
    assert picker.isCheckable() and home.filter_sidebar.isHidden()
    picker.click()
    assert home.filter_sidebar.isVisible()
    center = picker.mapTo(window, picker.rect().center())
    assert (
        center.x()
        > window.search_row.mapTo(
            window,
            window.search_row.rect().topRight(),
        ).x()
    )
    assert (
        abs(
            center.y()
            - window.search_row.mapTo(
                window,
                window.search_row.rect().center(),
            ).y(),
        )
        <= 1
    )
    tree = home.category_tree
    root = tree.topLevelItem(0)
    groups = {
        root.child(i).text(0): root.child(i) for i in range(root.childCount())
    }
    assert groups.keys() == {card.category for card in home.cards}
    checked, unchecked, partial = (
        Qt.CheckState.Checked,
        Qt.CheckState.Unchecked,
        Qt.CheckState.PartiallyChecked,
    )
    assert root.checkState(0) == checked
    root.setCheckState(0, unchecked)
    assert home.no_results.isVisible()
    intervals = groups["Intervals"]
    intervals.setCheckState(0, checked)
    assert all(
        intervals.child(i).checkState(0) == checked
        for i in range(intervals.childCount())
    )
    assert root.checkState(0) == partial
    window.search_field.setText("keyboard")
    assert [
        card.exercise_class for card in home.cards if card.isVisible()
    ] == [KeyboardIntervals]
    window.search_field.clear()
    home.mode_control.buttons[1].click()
    assert {
        card.category for card in home.lesson_cards if card.isVisible()
    } == {"Intervals"}
    home.mode_control.buttons[0].click()
    root = tree.topLevelItem(0)
    groups = {
        root.child(i).text(0): root.child(i) for i in range(root.childCount())
    }
    intervals = groups["Intervals"]
    intervals.child(0).setCheckState(0, unchecked)
    assert intervals.checkState(0) == partial
    groups["Chords"].setCheckState(0, checked)
    visible = {card.title for card in home.cards if card.isVisible()}
    assert (
        intervals.child(0).text(0) not in visible
        and intervals.child(1).text(0) in visible
    )
    assert {card.category for card in home.cards if card.isVisible()} == {
        "Chords",
        "Intervals",
    }
    next(card for card in home.cards if card.isVisible()).click()
    assert picker.isVisible() and home.filter_sidebar.isVisible()
    assert {
        cls.name for cls, row in window._items.items() if not row.isHidden()
    } == visible
    window.open_stats()
    assert picker.isHidden() and not home.filter_sidebar.isVisible()
    window.close_overlay()
    assert picker.isVisible() and home.filter_sidebar.isVisible()
    window.show_home()
    assert picker.isVisible()
    window.rebuild()
    QTest.qWait(1)
    home = window.home
    assert home.filter_sidebar.isVisible() and home.category_filter.isChecked()
    assert {card.title for card in home.cards if card.isVisible()} == visible
    root = home.category_tree.topLevelItem(0)
    root.setCheckState(0, checked)
    assert all(card.isVisible() for card in home.cards)


def test_shuffle_after_filtering_out_the_current_exercise(
    window: MainWindow,
) -> None:
    """
    Finish the question on screen, then pick a checked sibling or return
    to an empty grid.

    Parameters
    ----------
    window : MainWindow
        The visible practice window.
    """
    home = window.home
    window.open_exercise(NoteNames)
    window.shuffle_button.click()
    home.category_filter.click()
    view = window._exercise_page
    assert view is not None
    question = view.question
    home._filter_root.setCheckState(0, Qt.CheckState.Unchecked)
    home._filter_leaves[KeyboardNotes.name].setCheckState(
        0,
        Qt.CheckState.Checked,
    )
    assert question is not None and view.question is question
    assert (
        [cls for cls, row in window._items.items() if not row.isHidden()]
        == window._shuffle_choices()
        == [KeyboardNotes]
    )
    view.settings_panel.next_question_mode = "Wait"
    view.submit(question.answer, button=None)
    view.next_button.click()
    view = window._exercise_page
    assert (
        view is not None
        and isinstance(view.exercise, KeyboardNotes)
        and view.question is not None
    )
    home._filter_root.setCheckState(0, Qt.CheckState.Unchecked)
    assert all(
        window.nav.item(i).isHidden() for i in range(window.nav.count())
    )
    view.settings_panel.next_question_mode = "Wait"
    view.submit(view.question.answer, button=None)
    view.next_button.click()
    assert window.stack.currentWidget() is home and home.no_results.isVisible()


def test_filter_sidebar_reflows_the_grid_and_keeps_selections(
    window: MainWindow,
) -> None:
    """
    Browse the tree beside the tiles and recover the full grid width
    when the sidebar closes.

    Parameters
    ----------
    window : MainWindow
        The visible navigation window.
    """
    home = window.home
    tree, sidebar = home.category_tree, home.filter_sidebar
    for mode in ("exercises", "lessons"):
        home.set_mode(mode, animate=False)
        tree.collapseAll()
        QTest.qWait(1)
        full_width = home.scroll_area.width()
        columns = home._columns
        home.category_filter.click()
        slide = home._filter_slide
        assert slide.duration() == SIDEBAR_SLIDE_MS
        slide.setCurrentTime(slide.duration() // 2)
        halfway = sidebar.width()
        assert halfway > 0
        slide.setCurrentTime(slide.duration())
        QTest.qWait(1)
        assert abs(sidebar.width() - 2 * halfway) <= 1
        assert tree.isVisible() and tree.hasFocus()
        assert home._filter_root.isExpanded() and all(
            group.isExpanded() for group in home._filter_groups
        )
        branch_left = tree.columnViewportPosition(tree.treePosition())
        assert branch_left >= tree.viewport().width() - tree.columnWidth(1)
        group = home._filter_groups[0]
        y = tree.visualItemRect(group).center().y()
        toggle = QPoint(branch_left + 3 * tree.indentation() // 2, y)
        QTest.mouseClick(
            tree.viewport(),
            Qt.MouseButton.LeftButton,
            pos=toggle,
        )
        assert (
            not group.isExpanded()
            and group.checkState(0) == Qt.CheckState.Checked
        )
        QTest.mouseClick(
            tree.viewport(),
            Qt.MouseButton.LeftButton,
            pos=toggle,
        )
        assert group.isExpanded()
        checkbox = QPoint(tree.indentation() + 16, y)
        QTest.mouseClick(
            tree.viewport(),
            Qt.MouseButton.LeftButton,
            pos=checkbox,
        )
        assert (
            group.isExpanded()
            and group.checkState(0) == Qt.CheckState.Unchecked
        )
        QTest.mouseClick(
            tree.viewport(),
            Qt.MouseButton.LeftButton,
            pos=checkbox,
        )
        assert sidebar.geometry().right() == sidebar.parentWidget().width() - 1
        assert (
            home.scroll_area.mapTo(
                window,
                home.scroll_area.rect().topRight(),
            ).x()
            < sidebar.mapTo(window, QPoint()).x()
        )
        assert (
            home.scroll_area.width() < full_width and home._columns < columns
        )
        last = home._filter_groups[-1].child(
            home._filter_groups[-1].childCount() - 1,
        )
        assert last is not None
        tree.scrollToBottom()
        assert (
            tree.viewport()
            .rect()
            .contains(tree.visualRect(tree.indexFromItem(last, 0)))
        )
        last.setCheckState(0, Qt.CheckState.Unchecked)
        filtered = home.tile_filters[mode]
        collapse = next(
            button
            for button in sidebar.findChildren(QToolButton)
            if button.accessibleName() == "Collapse filters"
        )
        collapse.click()
        slide.setCurrentTime(slide.duration() // 2)
        assert sidebar.isVisible() and sidebar.width() == halfway
        home.category_filter.click()
        assert sidebar.width() == halfway
        slide.setCurrentTime(slide.duration())
        assert sidebar.width() > halfway
        collapse.click()
        slide.setCurrentTime(0)
        QTest.qWait(1)
        assert sidebar.isHidden() and not home.category_filter.isChecked()
        assert (
            home.scroll_area.width() == full_width and home._columns == columns
        )
        assert home.tile_filters[mode] == filtered
        home.category_filter.click()
        assert last.checkState(0) == Qt.CheckState.Unchecked
        home.category_filter.click()
        slide.setCurrentTime(0)


def test_filter_order_fonts_and_icons_match_navigation(
    window: MainWindow,
) -> None:
    """
    Compare the order, category typography, and activity icons in both
    filters with their navigation lists.

    Parameters
    ----------
    window : MainWindow
        The navigation window with its exercise and lesson lists.
    """
    home = window.home
    tree = home.category_tree
    for mode, nav in (
        ("exercises", window.nav),
        ("lessons", window.lesson_nav),
    ):
        home.set_mode(mode, animate=False)
        rows = {nav.item(i).text(): nav.item(i) for i in range(nav.count())}
        size = nav.iconSize()
        assert tree.iconSize() == size
        root = tree.topLevelItem(0)
        filter_rows = []
        for index in range(root.childCount()):
            group = root.child(index)
            filter_rows.append(group.text(0).upper())
            filter_rows.extend(
                group.child(i).text(0) for i in range(group.childCount())
            )
            heading = rows[group.text(0).upper()]
            assert group.font(0) == heading.font()
            assert group.foreground(0) == heading.foreground()
        assert filter_rows == list(rows)
        for title, leaf in home._filter_leaves.items():
            row = rows[title]
            assert leaf.font(0).resolve(tree.font()) == row.font().resolve(
                nav.font(),
            )
            assert not leaf.icon(0).isNull()
            assert (
                leaf.icon(0).pixmap(size).toImage()
                == row.icon().pixmap(size).toImage()
            )


def test_lesson_search_keeps_matching_lesson_steps_visible(
    window: MainWindow,
) -> None:
    """
    Apply the current search when lesson rows are rebuilt and keep their
    steps with the parent lesson.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.search_field.setText("clef")
    window.home.mode_control.buttons[1].click()
    assert window.search_field.placeholderText() == "Search lessons…"
    assert [
        card.accessibleName().split(",")[0]
        for card in window.home.lesson_cards
        if not card.isHidden()
    ] == ["Clef Basics"]
    window.open_lessons("clef-basics")
    assert window.lesson_nav.step_items
    assert all(not item.isHidden() for item in window.lesson_nav.step_items)
    window.search_field.setText("does not exist")
    assert all(
        window.lesson_nav.item(i).isHidden()
        for i in range(window.lesson_nav.count())
    )
    window.show_home()
    assert (
        window.home.no_results.isVisible()
        and window.home.no_results.text() == "No lessons found."
    )
    window.search_field.clear()
    assert not window.home.no_results.isVisible()


def test_search_does_not_answer_or_replace_active_question_and(
    window: MainWindow,
) -> None:
    """
    Type into search during an exercise without triggering answer
    shortcuts or resetting it.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_exercise(NoteNames)
    view = window.stack.currentWidget()
    assert isinstance(view, ExerciseView)
    question = view.question
    window.search_field.setFocus()
    QTest.keyClicks(window.search_field, "clef")
    assert (
        window.stack.currentWidget() is view
        and view.question is question
        and not view.answered
    )
    window.view_button.click()
    assert window.search_field.text() == "clef"
    window.home.resume_button.click()
    assert window.stack.currentWidget() is view and view.question is question
    window.rebuild()
    assert window.search_field.text() == "clef"
    assert [
        card.accessibleName().split(",")[0]
        for card in window.home.cards
        if not card.isHidden()
    ] == ["Clef Basics"]


def test_search_row_is_no_wider_than_the_remembered_sidebar(
    window: MainWindow,
) -> None:
    """
    Match the search row to the sidebar width, including after resizing
    and returning to tiles.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    assert window.search_row.width() == window.SIDEBAR_DEFAULT
    window.pane_button.click()
    QTest.qWait(220)
    window.splitter.setSizes([300, 800])
    # noinspection PyProtectedMember
    window._sidebar_dragged()
    assert window.search_row.width() == window.sidebar_width()
    assert window.search_field.width() < window.search_row.width()
    assert window.search_field.geometry().right() < window.search_row.width()
    width = window.sidebar_width()
    window.view_button.click()
    QTest.qWait(220)
    assert window.search_row.width() == width


def test_standalone_search_keeps_its_focus_highlighting(
    window: MainWindow,
) -> None:
    """
    Highlight search independently of the joined navigation control and
    preserve filtering.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    assert window.search_row.layout().spacing() == 0
    assert window.search_field.parentWidget() is window.search_row
    assert window.view_button.parentWidget() is window.navigation_group
    assert window.search_row.height() >= 34
    assert any(
        action.text() == "Search" for action in window.search_field.actions()
    )
    window.search_field.setFocus()
    QTest.qWait(10)
    assert window.search_row.property("focusWithin") is True
    window.view_button.setFocus()
    QTest.qWait(10)
    assert window.search_row.property("focusWithin") is False
    window.home.mode_control.buttons[0].setFocus()
    QTest.qWait(10)
    assert window.search_row.property("focusWithin") is False
    window.search_field.setText("keyboard")
    assert [
        card.accessibleName().split(",")[0]
        for card in window.home.cards
        if not card.isHidden()
    ] == [
        "Keyboard Note Identification",
        "Keyboard Interval Identification",
    ]


def test_glossary_location_survives_theme_rebuild(window: MainWindow) -> None:
    """
    Keep the glossary and its selected content when applying a theme.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_exercise(NoteNames)
    window.open_glossary()
    page = window.stack.currentWidget()
    assert isinstance(page, GlossaryPage)
    page.search.setText("octave")
    for row in range(page.terms.count()):
        if page.terms.item(row).text() == "octave register":
            page.terms.setCurrentRow(row)
            break
    page.activity_switch.set_current(1)
    page._show_activities(1)
    page._next_example()
    window.rebuild()
    restored = window.stack.currentWidget()
    assert isinstance(restored, GlossaryPage)
    assert restored.search.text() == "octave"
    assert restored.terms.currentItem().text() == "octave register"
    assert restored.activity_switch.current() == 1
    assert restored._example_index == 1
    window.close_overlay()
    assert isinstance(window.stack.currentWidget(), ExerciseView)


def test_sidebar_toggle_follows_the_browsing_section(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Label a page's sidebar toggle for the current browsing section.

    Parameters
    ----------
    window : MainWindow
        Navigation window with its workspace pages.
    monkeypatch : pytest.MonkeyPatch
        Attaches a toggle to the page for this test.
    """
    toggle = SidebarToggle(window.home)
    monkeypatch.setattr(window.home, "sidebar_button", toggle, raising=False)
    for mode, noun in (
        ("lessons", "lesson list"),
        ("exercises", "exercise list"),
    ):
        window.home.set_mode(mode, animate=False)
        window._update_sidebar_button()
        assert toggle.noun == noun and noun in toggle.toolTip()


def test_restored_lesson_returns_to_its_original_page(
    window: MainWindow,
) -> None:
    """
    Keep the lesson return destination across a theme rebuild.

    Parameters
    ----------
    window : MainWindow
        Window browsing lessons from the tiles.
    """
    window.open_lessons("circle-of-fifths")
    state = window._page_state()
    window._restore_page(state)
    assert window._lesson_return is not None
    expected = (
        window.empty_page if state.lesson_parent == "empty" else window.home
    )
    assert window._lesson_return[0] is expected
