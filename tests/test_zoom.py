"""
Tests for zoom: the steps, what the zoom is applied to, and the controls that change it.

The zoom scales the application font, the lengths in stylesheets, the sizes the interface fixes in pixels, the hand-drawn
notation and the icons, and the window is made again at the new size. It is changed with Ctrl and Plus or Minus, or Ctrl and
the mouse wheel, and it is saved.
"""

from __future__ import annotations

import random
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QEvent, QObject, QPoint, QPointF, Qt
from PySide6.QtGui import QColor, QFont, QWheelEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from alto.exercises.library import KeyboardNotes, NoteNames
from alto.ui import charts, main_window, zoom
from alto.ui.exercise_view import ExerciseView
from alto.ui.icons import PLAY, svg_icon
from alto.ui.instrument_picker import InstrumentPicker
from alto.ui.keyboard import KeyboardWidget
from alto.ui.staff import StaffWidget
from alto.ui.store import store
from alto.ui.theme import apply_theme


def wheel(delta: int, *, control: bool) -> QWheelEvent:
    """
    Make a turn of the mouse wheel.

    Parameters
    ----------
    delta : int
        How far it turned, 120 for one click, positive away from the user.
    control : bool
        Whether Ctrl is held. Keyword-only.

    Returns
    -------
    QWheelEvent
        The event.
    """
    modifier = Qt.KeyboardModifier.ControlModifier if control else Qt.KeyboardModifier.NoModifier
    return QWheelEvent(
        QPointF(5, 5),
        QPointF(5, 5),
        QPoint(0, 0),
        QPoint(0, delta),
        Qt.MouseButton.NoButton,
        modifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )


def test_the_zoom_moves_through_its_steps_and_stops_at_the_ends() -> None:
    """Zoom in and out one step at a time between the smallest and the largest, and say so when it changes."""
    heard: list[int] = []
    zoom.signals.changed.connect(heard.append)
    assert zoom.percent() == 100 and zoom.factor() == 1.0
    assert zoom.step(1) and zoom.percent() == 110
    assert zoom.step(-1) and zoom.step(-1) and zoom.percent() == 90
    while zoom.step(-1):
        pass
    assert zoom.percent() == zoom.STEPS[0] and not zoom.step(-1)
    while zoom.step(1):
        pass
    assert zoom.percent() == zoom.STEPS[-1] and not zoom.step(1)
    assert zoom.reset() and zoom.percent() == 100 and not zoom.reset()
    assert heard[0] == 110 and heard[-1] == 100


@pytest.mark.parametrize(("asked", "got"), [(103, 100), (1, 50), (1000, 300), (140, 150), (126, 125)])
def test_a_zoom_that_is_not_a_step_goes_to_the_nearest(asked: int, got: int) -> None:
    """
    Round a percentage to the nearest step.

    Parameters
    ----------
    asked : int
        The percentage asked for.
    got : int
        The step it becomes.
    """
    zoom.set_percent(asked)
    assert zoom.percent() == got


def test_the_zoom_is_saved_and_a_bad_saved_zoom_is_ignored() -> None:
    """Remember the zoom between sessions, and fall back to 100% for anything that is not a step."""
    zoom.set_percent(150)
    assert str(store().value(zoom.SETTING)) == "150"
    zoom._percent = 100
    zoom.load()
    assert zoom.percent() == 150
    store().setValue(zoom.SETTING, 133)
    zoom.load()
    assert zoom.percent() == 100
    store().setValue(zoom.SETTING, "big")
    zoom.load()
    assert zoom.percent() == 100


def test_lengths_scale_with_the_zoom_and_never_vanish() -> None:
    """Scale pixel lengths, keeping zero at zero and a small length at least one pixel."""
    zoom.set_percent(200)
    assert zoom.px(20) == 40 and zoom.px(0) == 0 and zoom.px(1) == 2 and zoom.px(-4) == -8
    zoom.set_percent(50)
    assert zoom.px(20) == 10 and zoom.px(1) == 1 and zoom.px(-1) == -1


def test_a_stylesheet_has_its_lengths_scaled_but_not_its_colors() -> None:
    """Scale each pixel and point length in a stylesheet, leaving colors, counts and names alone."""
    sheet = "QLabel#a1px { color: #123px; padding: 8px 12px; font-size: 14pt; margin: 0px; width: 1.5px; opacity: 0.5 }"
    assert zoom.css(sheet) == sheet
    zoom.set_percent(200)
    assert (
        zoom.css(sheet)
        == "QLabel#a1px { color: #123px; padding: 16px 24px; font-size: 28pt; margin: 0px; width: 3px; opacity: 0.5 }"
    )
    zoom.set_percent(50)
    assert "padding: 4px 6px" in zoom.css(sheet) and "font-size: 7pt" in zoom.css(sheet)


def test_the_application_font_follows_the_zoom_without_compounding(app: QApplication) -> None:
    """
    Make the font as large as the zoom says each time, always from its size at 100%.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    base = app.font().pointSizeF()
    zoom.set_percent(200)
    assert app.font().pointSizeF() == pytest.approx(base * 2)
    zoom.set_percent(150)
    assert app.font().pointSizeF() == pytest.approx(base * 1.5)
    zoom.reset()
    assert app.font().pointSizeF() == pytest.approx(base)
    pixel_font = QFont(app.font())
    pixel_font.setPixelSize(20)
    app.setFont(pixel_font)
    zoom._base_font = None
    zoom.set_percent(150)
    assert app.font().pixelSize() == 30


def test_the_theme_stylesheet_is_scaled(app: QApplication) -> None:
    """
    Scale the lengths in the application stylesheet, so that padding and corners grow with the text.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    apply_theme("studio")
    plain = app.styleSheet()
    zoom.set_percent(200)
    apply_theme("studio")
    assert app.styleSheet() != plain and "font-size: 28pt" in app.styleSheet()
    zoom.reset()
    apply_theme("studio")
    assert app.styleSheet() == plain


def test_the_wheel_zooms_with_ctrl_held_and_scrolls_without_it() -> None:
    """Take a turn of the wheel with Ctrl as a zoom step per click, and leave an ordinary turn alone."""
    handler = zoom.WheelZoom()
    nobody = QObject()
    assert not handler.eventFilter(nobody, wheel(120, control=False))
    assert zoom.percent() == 100
    assert handler.eventFilter(nobody, wheel(120, control=True)) and zoom.percent() == 110
    assert handler.eventFilter(nobody, wheel(-120, control=True)) and zoom.percent() == 100
    assert handler.eventFilter(nobody, wheel(-240, control=True)) and zoom.percent() == 80
    assert handler.eventFilter(nobody, wheel(40, control=True)) and zoom.percent() == 80  # a small turn adds up
    assert handler.eventFilter(nobody, wheel(40, control=True)) and handler.eventFilter(nobody, wheel(40, control=True))
    assert zoom.percent() == 90
    pixels = QWheelEvent(
        QPointF(),
        QPointF(),
        QPoint(0, 40),
        QPoint(),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.ControlModifier,
        Qt.ScrollPhase.ScrollUpdate,
        False,
    )
    assert handler.eventFilter(nobody, pixels) and zoom.percent() == 100
    assert not handler.eventFilter(nobody, QEvent(QEvent.Type.None_))
    handler.eventFilter(nobody, wheel(60, control=True))
    handler.eventFilter(nobody, wheel(60, control=False))  # releasing Ctrl forgets a half turn
    assert handler._turned == 0


def test_the_window_has_the_zoom_shortcuts_and_the_wheel(app: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Offer Ctrl with Plus, Equals, Minus and 0 as shortcuts that work anywhere in the app, and make the window again after a pause.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Count the times the window is made again.
    """
    window = main_window.MainWindow()
    actions = {action.objectName(): action for action in window.actions() if action.objectName().startswith("zoom")}
    assert set(actions) == {"zoomIn", "zoomOut", "zoomReset"}
    assert all(action.shortcutContext() == Qt.ShortcutContext.ApplicationShortcut for action in actions.values())
    assert {key.toString() for key in actions["zoomIn"].shortcuts()} >= {"Ctrl+="}
    assert actions["zoomOut"].shortcut().toString() == "Ctrl+-" and actions["zoomReset"].shortcut().toString() == "Ctrl+0"
    rebuilt = Mock()
    monkeypatch.setattr(window, "rebuild", rebuilt)
    actions["zoomIn"].trigger()
    actions["zoomIn"].trigger()
    assert zoom.percent() == 125
    rebuilt.assert_not_called()  # it waits until the steps stop
    window._zoom_timer.timeout.emit()
    rebuilt.assert_called_once()
    actions["zoomOut"].trigger()
    actions["zoomReset"].trigger()
    assert zoom.percent() == 100
    QTest.qWait(main_window.ZOOM_SETTLE_MS + 60)
    assert rebuilt.call_count == 2
    app.sendEvent(app, wheel(120, control=True))
    assert zoom.percent() == 110


def test_zoom_feedback_and_settled_layout(app: QApplication) -> None:
    """
    Preview a burst immediately, place its percentage left of Glossary, and hide it after the final change.

    Parameters
    ----------
    app : QApplication
        The running Qt application.
    """
    window = main_window.MainWindow()
    window.show()
    app.processEvents()
    root = window.centralWidget()
    assert window.zoom_indicator.isHidden()
    zoom.step(1)
    preview = window._zoom_preview
    assert preview.isEnabled() and window.splitter.graphicsEffect() is preview
    app.processEvents()
    assert not preview.frame.isNull()
    assert window.zoom_indicator.text() == "110%" and window.zoom_indicator.isVisible()
    zoom.step(1)
    assert window._zoom_preview is preview and preview.animation.endValue() == 1.25
    zoom.reset()
    QTest.qWait(main_window.ZOOM_SETTLE_MS + 50)
    assert window.centralWidget() is root and not window._zoom_preview.isEnabled()
    assert window.zoom_indicator.text() == "100%"

    window.open_exercise(NoteNames)
    zoom.step(-1)
    app.processEvents()
    QTest.qWait(main_window.ZOOM_SETTLE_MS + 50)
    assert not window._zoom_preview.isEnabled() and window._layout_zoom == 90
    assert window.title_label.text() == NoteNames.name and window.zoom_indicator.text() == "90%"
    assert window.zoom_indicator.isVisible()
    assert window.zoom_indicator.geometry().right() < window.glossary_button.geometry().left()
    window._reset_zoom()
    window._zoom_timer.stop()
    window._apply_zoom()
    window._zoom_notice_timer.setInterval(20)
    window._reset_zoom()
    assert window.zoom_indicator.isVisible() and window.zoom_indicator.text() == "100%"
    QTest.qWait(50)
    assert window.zoom_indicator.isHidden()


def test_the_window_opens_at_the_saved_zoom(app: QApplication) -> None:
    """
    Take the saved zoom into use as the window starts, so that the first thing drawn is already at it.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    base = app.font().pointSizeF()
    store().setValue(zoom.SETTING, 200)
    main_window.MainWindow()
    assert zoom.percent() == 200 and app.font().pointSizeF() == pytest.approx(base * 2)


def test_fixed_sizes_follow_the_zoom(app: QApplication) -> None:
    """
    Make the sizes the interface fixes in pixels as much larger as the zoom says.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    del app
    assert InstrumentPicker().list.maximumWidth() == 220
    zoom.set_percent(150)
    picker = InstrumentPicker()
    assert picker.list.maximumWidth() == 330
    assert picker.list.item(0).sizeHint().height() == 51


def test_notation_is_drawn_at_the_zoom(app: QApplication) -> None:
    """
    Space the staff lines, the keys and the pictures by the zoom.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    del app
    staff, keys = StaffWidget(max_step=10.0), KeyboardWidget()
    assert (staff.GAP, staff.side, staff.max_step, keys.pad, keys.max_key_width) == (16.0, 20.0, 10.0, 10, 38)
    zoom.set_percent(200)
    staff, keys = StaffWidget(max_step=10.0), KeyboardWidget()
    assert (staff.GAP, staff.side, staff.max_step, keys.pad, keys.max_key_width) == (32.0, 40.0, 20.0, 20, 76)
    assert StaffWidget().maximumWidth() >= 0 and staff.height() >= 0


def test_icons_are_drawn_as_large_as_the_zoom_asks(app: QApplication) -> None:
    """
    Draw an icon at the zoom, so that it stays sharp at the larger size.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    del app
    small = svg_icon(PLAY, color=QColor("#000000"), size=20).pixmap(40, 40)
    zoom.set_percent(200)
    large = svg_icon(PLAY, color=QColor("#000000"), size=20).availableSizes()[0]
    assert small.width() == 40 and large.width() == 80


def test_charts_keep_their_margins_in_proportion(app: QApplication) -> None:
    """
    Scale the margins and rows of a chart, including the ones a kind of chart sets for itself.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    del app
    bars = charts.HBarChart("Hardest")
    assert (bars.LEFT, bars.TOP, bars.ROW) == (40, 34, 26)
    zoom.set_percent(200)
    bars, calendar = charts.HBarChart("Hardest"), charts.HeatmapChart("Days")
    assert (bars.LEFT, bars.TOP, bars.ROW) == (80, 68, 52)
    assert (calendar.LEFT, calendar.TOP, calendar.BOTTOM) == (68, 88, 60)


@pytest.mark.parametrize("percent", [50, 150, 300])
def test_an_open_exercise_still_works_at_any_zoom(app: QApplication, percent: int) -> None:
    """
    Ask questions on the staff and on the keyboard at the smallest, a large and the largest zoom.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    percent : int
        The zoom.
    """
    del app
    zoom.set_percent(percent)
    for exercise in (NoteNames, KeyboardNotes):
        view = ExerciseView(exercise(), rng=random.Random(1))
        view.resize(900, 600)
        view.show()
        assert view.question is not None and not view.grab().isNull()
