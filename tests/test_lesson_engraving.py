"""Rendered spacing and reflow of the short scores in Alto's lessons."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QPalette
from PySide6.QtTest import QTest

from alto.lessons.clef_basics import CLEF_BASICS
from alto.lessons.key_signatures import KEY_SIGNATURES
from alto.lessons.scale_identification import SCALE_IDENTIFICATION
from alto.theory.pitch import Note
from alto.ui import engraving, theme
from alto.ui.lesson import StepView
from alto.ui.notation import BY_KEY
from alto.ui.staff import StaffWidget, _repaint_staffs
from alto.ui.style import app_style

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


@pytest.mark.parametrize(
    ("clef", "key", "notes"),
    [
        ("treble", 1, ["F4"]),
        ("bass", -3, []),
        ("treble", 2, ["D4", "E4", "F#4", "G4"]),
    ],
)
def test_excerpt_ink_stays_put(app: QApplication, clef: str, key: int, notes: list[str]) -> None:
    """
    Compare actual staff pixels at two pane widths for the three house-style examples.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    clef : str
        Staff clef.
    key : int
        Written key signature.
    notes : list of str
        Notes of the example.
    """
    staff = StaffWidget(gap=8, lesson_layout=True)
    staff.show_notes([[Note.parse(name)] for name in notes], clef=clef, key=key, value="quarter")
    staff.resize(280, staff.height())
    staff.show()
    narrow = staff.grab().toImage()
    staff.resize(480, staff.height())
    wide = staff.grab().toImage()
    (row,) = staff._lesson_systems(480)
    assert row.right < 230
    assert narrow == wide
    assert row.right + staff.side <= wide.width() < row.right + staff.side + 1
    bottom = round(row.bottoms[clef])
    assert min(wide.pixelColor(26, y).lightness() for y in (bottom - 1, bottom)) < 190
    assert min(wide.pixelColor(wide.width() - 4, y).lightness() for y in (bottom - 1, bottom)) == 255
    if len(notes) == 4:
        assert [b - a for a, b in zip(row.centers, row.centers[1:])] == pytest.approx([28] * 3)
    staff.close()


def test_local_accidentals_clear_chords_and_captions(app: QApplication) -> None:
    """
    Check chord signs, low ledger lines, and caption room across notation fonts.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    staff = StaffWidget(gap=8, lesson_layout=True)
    staff.show_notes([[Note.parse("F#1"), Note.parse("Gb1")]], clef="grand", caption="Two pitches on the lower staff")
    staff.resize(180, staff.height())
    staff.show()
    for style in BY_KEY.values():
        staff.notation_style = style
        _repaint_staffs()
        (row,) = staff._lesson_systems(staff.width())
        near, far = row.signs[0]
        assert far < near < 0
        assert row.caption_rect.top() > row.bottoms["bass"] + staff.GAP
        assert row.caption_rect.bottom() <= staff.height()
        assert not staff.grab().isNull()
    staff.close()


def test_lesson_scale_wrap_keeps_each_labeled_step(app: QApplication) -> None:
    """
    Follow the scale lesson into the explorer and resize the staff with its highlights active.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    step = next(step for step in SCALE_IDENTIFICATION.steps if step.scale)
    view = StepView(step)
    assert view.scale_explorer is not None
    staff = view.scale_explorer.staff
    assert staff.lesson_layout
    staff.show_notes(staff.columns, key=2)
    staff.setParent(None)
    staff.resize(180, staff.height())
    staff.column_colors[3] = staff.palette().highlight().color()
    staff.show()
    wrapped = staff._lesson_systems(staff.width())
    assert len(wrapped) > 1
    assert all(row.right + staff.side <= staff.width() and row.key_x == wrapped[0].key_x for row in wrapped)
    pitches = [row.first + i for row in wrapped for i in range(len(row.centers))]
    assert pitches == list(range(8))
    assert len(staff.wedges) == len(pitches) - 1
    narrow_height = staff.height()
    assert not staff.grab().isNull()
    staff.resize(520, narrow_height)
    assert len(staff._lesson_systems(520)) == 1
    assert staff.height() < narrow_height
    staff.close()


def test_lesson_engraving_entry_points(app: QApplication) -> None:
    """
    Check that illustrated examples and refreshed staff questions use the same geometry.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    first = StepView(KEY_SIGNATURES.steps[0])
    assert all(staff.lesson_layout for staff in first.staves)
    upper, lower = first.staves
    assert upper._lesson_systems(300)[0].centers == lower._lesson_systems(300)[0].centers
    question = StepView(next(step for step in KEY_SIGNATURES.steps if step.task_staff))
    question.ask()
    assert question.task is not None
    assert question.staves[0].lesson_layout and question.staves[0].key == question.task.key


def test_signature_and_local_natural_gaps(app: QApplication) -> None:
    """
    Measure the positions passed to the engraver for a natural following a two-sharp signature.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    staff = StaffWidget(gap=8, lesson_layout=True)
    staff.notation_style = BY_KEY["bravura"]
    staff.show_notes([[Note.parse("F4")]], key=2)
    with patch.object(engraving, "draw_accidental", wraps=engraving.draw_accidental) as draw_sign:
        staff.grab()
    first, second, natural = [call.kwargs for call in draw_sign.call_args_list]
    assert [first["sign"], second["sign"], natural["sign"]] == [1, 1, 0]
    sharp_width = engraving.accidental_width(font="bravura", sign=1, gap=8)
    natural_width = engraving.accidental_width(font="bravura", sign=0, gap=8)
    assert second["x"] - (first["x"] + sharp_width) == pytest.approx(2)
    assert natural["x"] - (second["x"] + sharp_width) == pytest.approx(12)
    (row,) = staff._lesson_systems(staff.width())
    # Whole noteheads are centered on their column. Their left and right clearances determine the staff end.
    left_edge = natural["x"] + natural_width + 2
    right_edge = 2 * row.centers[0] - left_edge
    assert row.right - right_edge == pytest.approx(16, abs=1)


def test_caption_fits_the_lesson_paper_at_each_width(app: QApplication) -> None:
    """
    A long caption can set the width of the paper and wrap when the pane is narrowed.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    staff = StaffWidget(gap=8, side=8, lesson_layout=True)
    staff.show_notes([], clef="bass", key=-3, caption="Three flats after the bass clef")
    staff.show()
    staff.resize(520, staff.height())
    (wide,) = staff._lesson_systems(staff.width())
    assert wide.caption_rect.right() > wide.right
    assert staff.width() == wide.caption_rect.right() + staff.side
    staff.resize(staff.minimumWidth(), staff.height())
    (narrow,) = staff._lesson_systems(staff.width())
    assert narrow.caption_rect.height() > wide.caption_rect.height()
    assert narrow.caption_rect.right() + staff.side <= staff.width()
    assert narrow.caption_rect.bottom() + staff.GAP <= staff.height()
    staff.close()


def test_key_signatures_opening_matches_the_responsive_example(app: QApplication, request: pytest.FixtureRequest) -> None:
    """
    Resize the first page and check the actual edges of both examples, divider, text, and playback.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    request : pytest.FixtureRequest
        Restores the application palette after rendering.
    """
    original = app.palette()
    request.addfinalizer(lambda: app.setPalette(original))
    palette = QPalette(original)
    palette.setColor(QPalette.ColorRole.Base, QColor("#282828"))
    palette.setColor(QPalette.ColorRole.Mid, QColor("#707070"))
    app.setPalette(palette)
    view = StepView(KEY_SIGNATURES.steps[0])
    view.setStyleSheet(app_style(palette))
    view.show()
    illustration = view.illustration
    assert illustration is not None and view.hear_button is not None
    panel = illustration.panel
    first, second = view.staves
    (divider,) = illustration.dividers
    for width in (1100, 430, 245, 1100):
        view.resize(width, 520)
        app.processEvents()
        panel_pos = panel.mapTo(illustration, QPoint())
        assert panel.isAncestorOf(view.hear_button) and panel.isAncestorOf(first) and panel.isAncestorOf(second)
        assert second.geometry().bottom() < view.hear_button.y() < panel.height()
        image = panel.grab().toImage()
        white = QColor("white")
        y = first.geometry().center().y()
        assert image.pixelColor(0, y) == palette.mid().color()
        assert image.pixelColor(1, y) == white
        assert image.pixelColor(panel.width() // 2, view.hear_button.y() - 1) == white
        assert image.pixelColor(view.hear_button.x() + 6, view.hear_button.geometry().center().y()) == white
        if width > 245:
            assert first.y() == second.y()
            assert divider.isVisible() and first.geometry().right() < divider.x() < second.x()
            assert image.pixelColor(divider.x() - 1, y) == image.pixelColor(divider.x() + 1, y) == white
            assert image.pixelColor(divider.x(), y) == palette.mid().color()
        else:
            assert first.geometry().bottom() < second.y() and not divider.isVisible()
            assert image.pixelColor(first.geometry().center().x(), second.y() - 1) == white
        if width == 1100:
            assert panel_pos.y() == illustration.prose.y()
            assert panel_pos.x() > illustration.prose.geometry().right()
            assert illustration.prose.text() == view.step.text and not illustration.rest.isVisible()
        else:
            assert illustration.prose.geometry().bottom() < panel_pos.y()
            assert panel_pos.y() + panel.height() <= illustration.rest.y()
            assert illustration.rest.isVisible() and illustration.prose.text() + illustration.rest.text() == view.step.text
    view.close()


def test_paper_playback_uses_light_variant_in_dark_theme(app: QApplication, request: pytest.FixtureRequest) -> None:
    """
    Compare the rendered playback button before and after switching a live lesson to Studio Dark.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    request : pytest.FixtureRequest
        Restores the application theme when the test ends.
    """
    request.addfinalizer(lambda: theme.apply_theme("system"))
    theme.apply_theme("studio")
    view = StepView(KEY_SIGNATURES.steps[0])
    view.show()
    button = view.hear_button
    assert button is not None
    images = []
    for key in ("studio", "studio_dark"):
        theme.apply_theme(key)
        app.processEvents()
        QTest.mouseMove(view, QPoint(1, 1))
        button.clearFocus()
        rest = button.grab().toImage()
        assert button.palette().buttonText().color() == QColor("#545a65")
        assert view.again.palette().buttonText().color() == app.palette().buttonText().color()
        QTest.mouseMove(button, button.rect().center())
        hover = button.grab().toImage()
        QTest.mouseMove(view, QPoint(1, 1))
        button.setFocus()
        focus = button.grab().toImage()
        button.setDown(True)
        pressed = button.grab().toImage()
        button.setDown(False)
        button.setDisabled(True)
        disabled = button.grab().toImage()
        button.setEnabled(True)
        assert all(state != rest for state in (hover, focus, pressed, disabled))
        images.append((rest, hover, focus, pressed, disabled))
    assert images[0] == images[1]
    view.close()


def test_knowledge_check_wraps_answers_and_keeps_feedback_together(app: QApplication) -> None:
    """
    Resize a five-choice question while a hint is visible, answer it, and retry.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    assert StepView(KEY_SIGNATURES.steps[0]).task_box.isHidden()
    view = StepView(next(step for step in CLEF_BASICS.steps if step.title == "The clef’s line"))
    view.show()
    callout = view.task_box
    assert callout.accessibleName() == "Knowledge check"
    assert view.feedback.isHidden() and view.again.isHidden()
    assert view.task is not None
    wrong = next(button for button in view.choice_buttons if button.text() != view.task.correct)
    wrong.click()
    for width in (1040, 310, 1040):
        view.resize(width, 620)
        app.processEvents()
        rows = {button.y() for button in view.choice_buttons}
        assert (len(rows) == 1) == (width == 1040)
        for widget in [view.prompt, *view.choice_buttons, view.feedback]:
            assert callout.isAncestorOf(widget) and widget.isVisible()
            assert callout.rect().contains(widget.mapTo(callout, widget.rect().bottomRight()))
        assert not wrong.isEnabled() and view.task.hint in view.feedback.text()
    next(button for button in view.choice_buttons if button.text() == view.task.correct).click()
    assert view.task.explanation in view.feedback.text()
    assert callout.isAncestorOf(view.again) and view.again.isVisible()
    view.again.click()
    assert view.feedback.isHidden() and view.again.isHidden()
    assert all(button.isEnabled() for button in view.choice_buttons)
    view.close()
