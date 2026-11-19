"""
Navigation lists and tile browsing preserve activities while remaining independently selectable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from PySide6.QtCore import (
    QPoint,
    QPropertyAnimation,
    Qt,
)
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QLabel

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
from alto.ui.exercise_view import ExerciseView
from alto.ui.glossary import GlossaryPage
from alto.ui.lesson import LessonsPage
from alto.ui.main_window import MainWindow
from alto.ui.transitions import save_transition

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


def test_tiles_are_the_default_and_navigation_is_on_the_left(window: MainWindow) -> None:
    """
    Start with tiles and place navigation to the left of the separate data tools.

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
    assert window.stack.currentWidget() is window.home and window.sidebar_width() == 0


def test_grid_button_returns_to_the_workspace_after_visiting_tiles(window: MainWindow) -> None:
    """
    Return to the same exercise and pane state when the grid button is clicked again.

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
    assert not window.home.canvas.running and not window.home._transition_start.isActive()
    assert activity.question is question and window.sidebar_width() == pane_width
    control_x = window.home.mode_control.mapTo(window, QPoint()).x()
    view_x = window.view_button.mapTo(window, QPoint()).x()
    stats_x = window.stats_button.mapTo(window, QPoint()).x()
    database_x = window.database_button.mapTo(window, QPoint()).x()
    assert control_x < window.pane_button.mapTo(window, QPoint()).x() < view_x < stats_x < database_x


@pytest.mark.parametrize("source", ["exercise", "lesson", "statistics", "database", "lessons shortcut"])
def test_return_to_tiles_animates_from_a_blank_grid(window: MainWindow, source: str) -> None:
    """
    Reveal only the destination tiles at their final positions when returning from another page.

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
    cards = home.lesson_cards if source in {"lesson", "lessons shortcut"} else home.cards
    viewport = home.scroll_area.viewport()
    assert canvas.geometry() == viewport.rect()
    assert [sprite.rect.topLeft().toPoint() for sprite in canvas.new] == [card.mapTo(viewport, QPoint()) for card in cards]
    canvas._animation.setCurrentTime(150)
    assert 0 < canvas.new[0].opacity < 1
    canvas._animation.setCurrentTime(canvas._animation.duration())
    assert not canvas.running and not home._hidden.isEnabled()


@pytest.mark.parametrize("button", ["glossary_button", "stats_button", "database_button"])
def test_utility_page_slides_in_from_the_right(window: MainWindow, button: str) -> None:
    """
    Keep the outgoing grid visible as the selected utility page enters from the right.

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
    slide = next(animation for animation in stack.findChildren(QPropertyAnimation) if animation.propertyName() == b"pos")
    incoming = slide.targetObject()
    assert isinstance(incoming, QLabel) and incoming.x() == stack.width()
    assert stack.grab().toImage() == before
    slide.setCurrentTime(slide.duration() // 2)
    assert 0 < incoming.x() < stack.width()
    frame = stack.grab().toImage()
    edge = round(incoming.x() * frame.devicePixelRatio())
    assert frame.copy(0, 0, edge, frame.height()) == before.copy(0, 0, edge, frame.height())
    revealed = frame.width() - edge
    assert frame.copy(edge, 0, revealed, frame.height()) == incoming.pixmap().toImage().copy(0, 0, revealed, frame.height())
    slide.setCurrentTime(slide.duration())
    assert not incoming.isVisible() and stack.currentWidget().geometry() == stack.contentsRect()
    window.home.resume_button.click()
    assert stack.currentWidget() is window.home and window.home.canvas.running


def test_switching_utilities_mid_slide_keeps_the_original_back_destination(window: MainWindow) -> None:
    """
    Switch utilities in mid-flight, resize, and return to the same exercise.

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
    assert window.stack.currentWidget() is activity and window.stack.count() == 3


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
    assert window.home.cards[0].isVisible() and not window.home._hidden.isEnabled()
    assert not window.home.canvas.running


def test_empty_workspace_prompt_follows_the_selected_section(window: MainWindow) -> None:
    """
    Switch tile sections without opening the pane, then show the appropriate empty prompt.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.home.mode_control.buttons[1].click()
    assert window.stack.currentWidget() is window.home and window.home.mode == "lessons"
    assert window.sidebar_width() == 0
    window.pane_button.click()
    QTest.qWait(220)
    assert [button.text() for button in window.home.mode_control.buttons] == ["", ""]
    assert [button.toolTip() for button in window.home.mode_control.buttons] == ["Exercises", "Lessons"]
    assert window.view_button.accessibleName() == "Tiles"
    assert window.view_button.text() == ""
    assert window.view_button.toolTip() == "Return to tiles"
    assert window.stack.currentWidget() is window.empty_page
    assert window.empty_page.text() == "Select a lesson to begin."
    assert window.nav_stack.currentWidget() is window.lesson_nav and window.lesson_nav.count() > 0
    assert window.sidebar_width() > 0
    window.home.mode_control.buttons[0].click()
    assert window.empty_page.text() == "Select an exercise to begin."
    assert window.nav_stack.currentWidget() is window.nav
    window.view_button.click()
    QTest.qWait(220)
    assert window.stack.currentWidget() is window.home
    assert window.pane_button.accessibleName() == "Show navigation pane" and window.sidebar_width() == 0
    assert [button.text() for button in window.home.mode_control.buttons] == ["", ""]


def test_switching_lists_preserves_the_exercise(window: MainWindow) -> None:
    """
    Browse lessons from an exercise without replacing the question or clearing an answer selection.

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
    assert window.stack.currentWidget() is view and window.nav_stack.currentWidget() is window.nav
    window.view_button.click()
    window.pane_button.click()
    assert window.stack.currentWidget() is view and view.question is question
    # noinspection PyProtectedMember
    assert view._pending == selected


def test_tiles_pause_question_advancement_and_answer_timing(window: MainWindow) -> None:
    """
    Freeze a completed question while browsing tiles, then resume its pending advance.

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


def test_reopening_the_active_exercise_tile_reuses_its_question(window: MainWindow) -> None:
    """
    Return from the active exercise's tile without starting a replacement session.

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


def test_lesson_progress_and_the_exercise_survive_tiles_and_statistics(window: MainWindow) -> None:
    """
    Retain both activity pages and the lesson's back destination through utility and tile browsing.

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
    assert window.stack.currentWidget() is lesson and window.nav_stack.currentWidget() is window.nav
    window.view_button.click()
    window.pane_button.click()
    assert window.stack.currentWidget() is lesson and lesson.view.current == 2
    window.stats_button.click()
    assert window.title_label.text() == "Statistics"
    window.close_overlay()
    assert window.stack.currentWidget() is lesson and lesson.view.current == 2
    lesson.back_button.click()
    assert window.stack.currentWidget() is exercise


def test_navigation_rebuild_preserves_tiles_and_the_selected_list(window: MainWindow) -> None:
    """
    Restore the selected browser list and hidden workspace when the theme is rebuilt.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_exercise(NoteNames)
    window.home.mode_control.buttons[1].click()
    window.view_button.click()
    window.rebuild()
    assert window.stack.currentWidget() is window.home and window.home.mode == "lessons"
    assert window.pane_button.accessibleName() == "Show navigation pane"
    window.pane_button.click()
    assert isinstance(window.stack.currentWidget(), ExerciseView)
    assert window.nav_stack.currentWidget() is window.lesson_nav


def test_empty_lesson_pane_survives_rebuild(window: MainWindow) -> None:
    """
    Keep the empty lesson workspace rather than silently reverting to tiles on theme changes.

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


def test_statistics_over_a_lesson_survive_theme_rebuild(window: MainWindow) -> None:
    """
    Keep utility back navigation attached to the lesson rather than losing it during a rebuild.

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


def test_retained_pages_do_not_accumulate_when_switching_activities(window: MainWindow) -> None:
    """
    Keep one exercise and one lesson while allowing repeated tile and sidebar navigation.

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
    assert window.stack.count() == 4  # tiles, empty workspace, one exercise, one lesson
    window.open_database()
    window.close_overlay()
    assert window.stack.count() == 4


def test_opening_the_navigation_pane_dismisses_a_utility_page(window: MainWindow) -> None:
    """
    Do not leave hidden statistics pages in the stack when opening the empty navigation workspace.

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


def test_sidebar_tooltip_describes_the_selected_list(window: MainWindow) -> None:
    """
    Toggle the pane from the header without replacing the exercise or exposing a local collapse button.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.open_exercise(NoteNames)
    view = window.stack.currentWidget()
    assert isinstance(view, ExerciseView)
    QTest.qWait(220)
    window.home.mode_control.buttons[1].click()
    assert not hasattr(view, "sidebar_button")
    assert window.pane_button.toolTip() == "Hide navigation pane"
    question = view.question
    window.pane_button.click()
    QTest.qWait(220)
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
    QTest.qWait(220)
    assert window.sidebar_width() > 0
    assert window.stack.currentWidget() is view and view.question is question


def test_tiles_have_a_back_button_for_the_current_exercise(window: MainWindow) -> None:
    """
    Return directly from either tile section to the retained question and partial answer.

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
    assert abs(back.mapTo(window, QPoint()).y() - window.search_field.mapTo(window, QPoint()).y()) < 10
    assert back.mapTo(window, QPoint()).x() > window.search_row.mapTo(window, window.search_row.rect().topRight()).x()
    window.home.mode_control.buttons[1].click()
    assert back.isVisible() and back.text() == "←  Back"
    back.click()
    assert window.stack.currentWidget() is view and view.question is question
    # noinspection PyProtectedMember
    assert view._pending == selected
    assert window.nav_stack.currentWidget() is window.lesson_nav


def test_tiles_back_button_returns_to_the_lesson_step(window: MainWindow) -> None:
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


def test_search_is_below_the_quiet_icon_only_toolbar(window: MainWindow) -> None:
    """
    Keep the section pair distinct from the view action, with search on the row below.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    control_bottom = window.home.mode_control.mapTo(window, window.home.mode_control.rect().bottomLeft()).y()
    search_top = window.search_field.mapTo(window, QPoint()).y()
    view_bottom = window.view_button.mapTo(window, window.view_button.rect().bottomLeft()).y()
    assert search_top > control_bottom
    assert search_top > view_bottom
    assert window.home.mode_control.parentWidget() is window.navigation_group
    assert window.view_button.parentWidget() is window.navigation_group
    assert window.navigation_group.layout().spacing() == 10
    assert window.navigation_divider.isVisible()
    assert window.navigation_divider.width() == 1
    assert window.navigation_divider.height() < window.home.mode_control.height()
    pair_right = window.home.mode_control.mapTo(window, window.home.mode_control.rect().topRight()).x()
    assert window.view_button.mapTo(window, QPoint()).x() - pair_right >= 20
    assert [button.text() for button in window.home.mode_control.buttons] == ["", ""]
    assert [button.toolTip() for button in window.home.mode_control.buttons] == ["Exercises", "Lessons"]
    assert window.view_button.text() == ""


def test_search_filters_tiles_and_navigation_and_clear_restores_them(window: MainWindow) -> None:
    """
    Search names without case sensitivity and hide empty categories in the matching list.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.search_field.setText("  KEYBOARD  ")
    assert [card.accessibleName().split(",")[0] for card in window.home.cards if not card.isHidden()] == [
        "Keyboard Note Identification",
        "Keyboard Interval Identification",
    ]
    assert [name for name, item in window._items.items() if not item.isHidden()] == [KeyboardNotes, KeyboardIntervals]
    headings = [window.nav.item(i) for i in range(window.nav.count()) if window.nav.item(i).flags() == Qt.ItemFlag.NoItemFlags]
    assert [heading.text() for heading in headings if not heading.isHidden()] == ["NOTATION", "INTERVALS"]
    window.search_field.clear()
    assert all(not card.isHidden() for card in window.home.cards)
    assert all(not item.isHidden() for item in window._items.values())
    assert all(not heading.isHidden() for heading in headings)


def test_lesson_search_keeps_matching_lesson_steps_visible(window: MainWindow) -> None:
    """
    Apply the current search when lesson rows are rebuilt and keep their steps with the parent lesson.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    window.search_field.setText("clef")
    window.home.mode_control.buttons[1].click()
    assert window.search_field.placeholderText() == "Search lessons…"
    assert [card.accessibleName().split(",")[0] for card in window.home.lesson_cards if not card.isHidden()] == ["Clef Basics"]
    window.open_lessons("clef-basics")
    assert window.lesson_nav.step_items
    assert all(not item.isHidden() for item in window.lesson_nav.step_items)
    window.search_field.setText("does not exist")
    assert all(window.lesson_nav.item(i).isHidden() for i in range(window.lesson_nav.count()))
    window.show_home()
    assert window.home.no_results.isVisible() and window.home.no_results.text() == "No lessons found."
    window.search_field.clear()
    assert not window.home.no_results.isVisible()


def test_search_does_not_answer_or_replace_the_active_question_and_survives_rebuild(window: MainWindow) -> None:
    """
    Type into search during an exercise without triggering answer shortcuts or resetting it.

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
    assert window.stack.currentWidget() is view and view.question is question and not view.answered
    window.view_button.click()
    assert window.search_field.text() == "clef"
    window.home.resume_button.click()
    assert window.stack.currentWidget() is view and view.question is question
    window.rebuild()
    assert window.search_field.text() == "clef"
    assert [card.accessibleName().split(",")[0] for card in window.home.cards if not card.isHidden()] == ["Clef Basics"]


def test_search_row_is_no_wider_than_the_remembered_sidebar(window: MainWindow) -> None:
    """
    Match the search row to the sidebar width, including after resizing and returning to tiles.

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


def test_standalone_search_keeps_its_focus_highlighting(window: MainWindow) -> None:
    """
    Highlight search independently of the joined navigation control and preserve filtering.

    Parameters
    ----------
    window : MainWindow
        The window under test.
    """
    assert window.search_row.layout().spacing() == 0
    assert window.search_field.parentWidget() is window.search_row
    assert window.view_button.parentWidget() is window.navigation_group
    assert window.search_row.height() >= 34
    assert any(action.text() == "Search" for action in window.search_field.actions())
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
    assert [card.accessibleName().split(",")[0] for card in window.home.cards if not card.isHidden()] == [
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
