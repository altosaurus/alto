"""
Rendering and replay of questions about individual parts of written
music.
"""

from __future__ import annotations

import json
import random
import xml.etree.ElementTree as ET
from dataclasses import replace
from typing import TYPE_CHECKING

import numpy as np
import pytest
from PySide6.QtCore import QEvent, QPoint, QRectF, Qt
from PySide6.QtGui import QFontDatabase, QImage
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import QToolButton

from alto import settings
from alto.exercises import Question
from alto.exercises.library import NotationIdentification
from alto.learning.stats import describe
from alto.notation_excerpts import excerpts
from alto.notation_terms import CATALOG, MARKS, SIMILAR_MARKS
from alto.ui import motion
from alto.ui.engraving import notation_glyph
from alto.ui.exercise_page import ExercisePage
from alto.ui.exercise_settings import load_notation_terms
from alto.ui.notation import BY_KEY, STYLES
from alto.ui.question_preview import QuestionPreview
from alto.ui.score_excerpt import score_artwork
from alto.ui.settings_panel import NotationSettingsPanel
from alto.ui.staff import StaffWidget

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


def test_notation_highlights_in_saved_questions(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check the highlight geometry in each notation font, including both
    stem directions.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Generate legacy staff questions to exercise their saved layout.
    """
    monkeypatch.setattr("alto.exercises.library.passages_by_term", dict)
    rng = random.Random(7)
    exercise = NotationIdentification()
    settings.notation.terms = {"Notehead", "Stem", "Clef", "Staff line"}
    examples = {}
    for _ in range(100):
        question = exercise.generate(rng)
        assert question.notation_target is not None
        part, index = question.notation_target
        direction = part == "Stem" and question.staff[index][0].midi >= 71
        examples.setdefault((part, direction), question)
    assert len(examples) == 5
    for (part, _), question in examples.items():
        saved = Question.from_dict(json.loads(json.dumps(question.to_dict())))
        assert saved == question and saved.check(part)
        preview = QuestionPreview(exercise.name, question=saved)
        staff = preview.findChild(StaffWidget)
        assert (
            staff is not None
            and staff.notation_target == question.notation_target
        )
        for style in STYLES:
            staff.notation_style = style
            image = (
                staff.grab()
                .toImage()
                .convertToFormat(QImage.Format.Format_RGBA8888)
            )
            pixels = np.frombuffer(image.constBits(), dtype=np.uint8).reshape(
                image.height(),
                image.width(),
                4,
            )
            ys, xs = np.where((pixels[:, :, 2] > 100) & (pixels[:, :, 0] < 90))
            assert xs.size, (style.key, part)
            width, height = np.ptp(xs) + 1, np.ptp(ys) + 1
            if part == "Staff line":
                assert width > image.width() / 2 and height < staff.GAP
            elif part == "Stem":
                assert height > 2 * staff.GAP and width < staff.GAP
            elif part == "Notehead":
                assert (
                    staff.GAP / 2 < height < 1.5 * staff.GAP
                    and staff.GAP < width < 2 * staff.GAP
                )
            else:
                assert height > 4 * staff.GAP and max(xs) < image.width() / 2


@pytest.mark.parametrize(
    "term",
    ["Notehead", "Stem", "Staff line", "Quarter rest", "Sharp", "Tie", "Turn"],
)
def test_notation_question_in_the_exercise(
    app: QApplication,
    term: str,
) -> None:
    """
    Verify that a correct answer turns the original blue marking green
    in the same place.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    term : str
        The component to practice.
    """
    settings.notation.terms = {term}
    view = ExercisePage(NotationIdentification(), rng=random.Random(7))
    question = view.question
    assert (
        question is not None
        and view.question_view.staff.notation_target
        == question.notation_target
    )
    before = (
        view.question_view.staff.grab()
        .toImage()
        .convertToFormat(QImage.Format.Format_RGBA8888)
    )
    view.control_area.answers.buttons[question.choices.index(term)].click()
    assert view.session.answered and view.session.correct == 1
    view.controller._advance.stop()
    animation = view.controller.animations.tracked[-1]
    animation.setCurrentTime(animation.duration())
    after = (
        view.question_view.staff.grab()
        .toImage()
        .convertToFormat(QImage.Format.Format_RGBA8888)
    )
    original = (
        np.frombuffer(before.constBits(), dtype=np.uint8)
        .reshape(-1, 4)
        .astype(int)
    )
    feedback = (
        np.frombuffer(after.constBits(), dtype=np.uint8)
        .reshape(-1, 4)
        .astype(int)
    )
    blue = original[:, 2] - original[:, 0]
    green = feedback[:, 1] - feedback[:, 0]
    # Account for different ink intensities in antialiased edge pixels.
    assert (blue > 25).any() and (green > 12).any()
    assert (green[blue > 25] > 4).all() and (blue[green > 12] > 8).all()


def test_selecting_notation_terms_filters_questions_and_restores_the_selection(
    app: QApplication,
) -> None:
    """
    Change terms through the exercise gear and verify the next question,
    replay signature, and saved state.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    exercise = NotationIdentification()
    view = ExercisePage(exercise, rng=random.Random(17))
    view.show()
    assert view.toolbar.gear is not None
    view.toolbar.gear.click()
    panel = view.settings_panel
    assert isinstance(panel, NotationSettingsPanel) and panel.isVisible()
    assert (
        panel.type_row.value.text() == "Answer Button"
        and panel.terms_row.value.text() == "All"
    )
    assert (
        not panel.group_picker.isVisible()
        and not panel.types["button"].isVisible()
    )
    page_changed = QSignalSpy(panel.stack.currentChanged)
    question = view.question
    panel.type_row.click()
    motion.settle()
    assert (
        page_changed.count()
        and panel.types["staff"].isVisible()
        and view.question is question
    )
    panel.types["staff"].click()
    assert panel.type_row.value.text() == "Click on Staff"
    panel.types["button"].click()
    question = view.question
    next(
        b
        for b in panel.findChildren(QToolButton)
        if b.isVisible() and b.text() == "‹ Back"
    ).click()
    motion.settle()
    assert (
        page_changed.count()
        and panel.type_row.isVisible()
        and view.question is question
    )
    panel.terms_row.click()
    motion.settle()
    assert page_changed.count() and panel.group_picker.isVisible()
    assert exercise.settings_signature() == ""
    panel.group_picker.textActivated.emit("Staff and rhythm")
    for term in panel.terms.selected() - {"Notehead", "Clef"}:
        panel.terms.boxes[term].click()
    pair_signature = exercise.settings_signature()
    rng = random.Random(9)
    assert pair_signature and {
        exercise.generate(rng).answer for _ in range(50)
    } == {"Notehead", "Clef"}
    panel.terms.boxes["Clef"].click()
    assert panel.terms_row.value.text() == "1 selected"
    assert view.question is not None and view.question.answer == "Notehead"
    assert (
        view.question.choices == ["Notehead"]
        and len(view.control_area.answers.buttons) == 1
    )
    assert panel.terms.boxes["Notehead"].isEnabled()
    assert exercise.settings_signature() != pair_signature
    settings.notation.terms = set(settings.NOTATION_TERMS)
    load_notation_terms()
    assert NotationSettingsPanel().terms.selected() == {"Notehead"}
    panel.group_picker.textActivated.emit("All terms")
    assert exercise.settings_signature() == ""
    next(
        b
        for b in panel.findChildren(QToolButton)
        if b.isVisible() and b.text() == "‹ Back"
    ).click()
    motion.settle()
    assert (
        page_changed.count()
        and panel.terms_row.isVisible()
        and panel.terms_row.value.text() == "All"
    )


@pytest.mark.parametrize("mode", ["button", "staff"])
def test_select_none_clears_and_restores_notation_terms(
    app: QApplication,
    mode: str,
) -> None:
    """
    Clear a custom selection, reopen it, and resume through the switch,
    a checkbox, or a group.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    mode : str
        The question type to practice.
    """
    settings.notation.question_type = mode
    original = {"Fermata", "Arpeggio sign"}
    settings.notation.terms = original.copy()
    view = ExercisePage(NotationIdentification(), rng=random.Random(11))
    panel = view.settings_panel
    assert isinstance(panel, NotationSettingsPanel)
    changes = QSignalSpy(panel.changed)
    panel.select_none.click()
    assert changes.count() == 1 and panel.select_none.isOn()
    assert (
        not panel.terms.selected() and panel.terms_row.value.text() == "None"
    )
    assert (
        view.question
        and not view.question.answer
        and "Select a notation term" in view.question_view.prompt.text()
    )
    assert (
        view.question_view.staff is None
        and not view.control_area.answers.buttons
        and not view.controller._advance.isActive()
        and view.session.total == 0
    )

    settings.notation.terms = set(settings.NOTATION_TERMS)
    load_notation_terms()
    reopened = ExercisePage(NotationIdentification(), rng=random.Random(12))
    panel = reopened.settings_panel
    assert (
        isinstance(panel, NotationSettingsPanel)
        and panel.select_none.isOn()
        and not panel.terms.selected()
    )
    panel.types["staff" if mode == "button" else "button"].click()
    panel.select_none.click()
    assert panel.terms.selected() == original and not panel.select_none.isOn()
    assert reopened.question and reopened.question.answer in original

    panel.select_none.click()
    panel.terms.boxes["Tie"].click()
    assert (
        not panel.select_none.isOn()
        and reopened.question
        and reopened.question.answer == "Tie"
    )
    panel.terms.boxes["Tie"].click()
    assert panel.select_none.isOn() and not settings.notation.terms
    panel.group_picker.textActivated.emit("Ornaments")
    assert not panel.select_none.isOn() and settings.notation.terms == set(
        CATALOG["Ornaments"],
    )


@pytest.mark.slow  # every term in every notation font: 1,600 pictures
def test_each_notation_term_draws_a_highlight(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Select every term individually and verify its saved question paints
    visible colored ink.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Exercise the generated notation renderer in every available
        font.
    """
    monkeypatch.setattr("alto.exercises.library.passages_by_term", dict)
    exercise = NotationIdentification()
    rng = random.Random(5)
    staff = StaffWidget(max_step=100)
    staff.resize(340, 330)
    for term, (_, glyph) in MARKS.items():
        settings.notation.terms = {term}
        question = exercise.generate(rng)
        assert question.check(term) and question.choices == [term]
        if isinstance(glyph, int):
            assert not notation_glyph("bravura", codepoint=glyph).isEmpty(), (
                term
            )
        saved = Question.from_dict(json.loads(json.dumps(question.to_dict())))
        staff.show_notes(
            saved.staff,
            clef=saved.clef,
            key=saved.key,
            notation_target=saved.notation_target,
            notation_excerpt=saved.notation_excerpt,
            value=saved.value,
        )
        for style in STYLES:
            staff.notation_style = style
            image = (
                staff.grab()
                .toImage()
                .convertToFormat(QImage.Format.Format_RGBA8888)
            )
            pixels = np.frombuffer(image.constBits(), dtype=np.uint8).reshape(
                image.height(),
                image.width(),
                4,
            )
            ys, xs = np.where((pixels[:, :, 2] > 100) & (pixels[:, :, 0] < 90))
            assert xs.size and min(xs) > 0 and max(xs) < image.width() - 1, (
                term,
                style.key,
            )
            assert min(ys) > 0 and max(ys) < image.height() - 1, (
                term,
                style.key,
            )
            index = xs.size // 2
            assert staff.hits_notation(
                QPoint(int(xs[index]), int(ys[index])),
            ), (term, style.key)


def test_notation_choices_favor_lookalikes_within_the_category() -> None:
    """
    Keep choices in the target category and usually offer all four turn
    variants together.
    """
    rng = random.Random(31)
    exercise = NotationIdentification()
    for family in SIMILAR_MARKS:
        assert any(set(family) <= group.keys() for group in CATALOG.values())
    for group in CATALOG.values():
        settings.notation.terms = set(group)
        for _ in range(20):
            question = exercise.generate(rng)
            assert (
                question.answer in question.choices
                and len(set(question.choices)) == 4
                and set(question.choices) <= group.keys()
            )
    settings.notation.terms = set(CATALOG["Ornaments"])
    variants = {"Turn", "Inverted turn", "Slashed turn", "Vertical turn"}
    turns = [
        q
        for _ in range(5000)
        if (q := exercise.generate(rng)).answer == "Turn"
    ][:500]
    matched = sum(set(q.choices) == variants for q in turns)
    assert 350 < matched < 475


def test_notation_choices_follow_mixed_selections_on_generation() -> None:
    """
    Offer only the three checked terms even when the old question
    contained other distractors.
    """
    exercise = NotationIdentification()
    rng = random.Random(42)
    original = exercise.generate(rng)
    selected = {
        original.answer,
        *[
            term
            for term in ("Stem", "Sharp", "Fermata")
            if term != original.answer
        ][:2],
    }
    settings.notation.terms = selected
    for question in (exercise.generate(rng), exercise.refresh(original)):
        assert (
            set(question.choices) == selected
            and set(question.grid or {}) == selected
        )
    assert exercise.refresh(original).item_key() == original.item_key()


@pytest.mark.parametrize(
    "term",
    ["Staff line", "Stem", "Notehead", "Quarter note", "Segno"],
)
def test_click_on_staff_practice(app: QApplication, term: str) -> None:
    """
    Switch question types and answer by clicking an unmarked score at
    its displayed size.

    Parameters
    ----------
    app : QApplication
        The shared application.
    term : str
        The only enabled component.
    """
    settings.notation.terms = {term}
    exercise = NotationIdentification()
    view = ExercisePage(exercise, rng=random.Random(14))
    panel = view.settings_panel
    assert isinstance(panel, NotationSettingsPanel)
    button_signature = exercise.settings_signature()
    assert panel.types["button"].isChecked()
    panel.types["staff"].click()
    q = view.question
    assert q is not None and q.answer == term and q.notation_target
    assert term.lower() in q.prompt and q.prompt.startswith("Click")
    assert (
        not view.control_area.answers.buttons
        and view.control_area.answers.choice_area.isHidden()
    )
    assert exercise.settings_signature() != button_signature
    assert "click" in exercise.instructions()
    assert (
        exercise.refresh(
            Question.from_dict(json.loads(json.dumps(q.to_dict()))),
        )
        == q
    )
    settings.notation.question_type = "button"
    load_notation_terms()
    assert NotationSettingsPanel().types["staff"].isChecked()

    view.resize(900, 600)
    view.show()
    app.processEvents()
    staff = view.question_view.staff
    assert staff is not None
    before = (
        staff.grab().toImage().convertToFormat(QImage.Format.Format_RGBA8888)
    )
    pixels = (
        np.frombuffer(before.constBits(), dtype=np.uint8)
        .reshape(-1, 4)
        .astype(int)
    )
    assert not np.any(pixels[:, 2] - pixels[:, 0] > 100)
    preview = StaffWidget()
    preview.show_notes(
        q.staff,
        value=q.value,
        notation_target=q.notation_target,
        notation_excerpt=q.notation_excerpt,
    )
    preview.resize(staff.size())
    image = (
        preview.grab().toImage().convertToFormat(QImage.Format.Format_RGBA8888)
    )
    marked = (
        np.frombuffer(image.constBits(), dtype=np.uint8)
        .reshape(image.height(), image.width(), 4)
        .astype(int)
    )
    ys, xs = np.where(marked[:, :, 2] - marked[:, :, 0] > 100)
    mid = len(xs) // 2
    target = QPoint(int(xs[mid]), int(ys[mid]))

    QTest.mouseClick(staff, Qt.MouseButton.LeftButton, pos=QPoint(12, 12))
    assert (
        view.session.missed
        and not view.session.answered
        and "Try again" in view.question_view.prompt.text()
    )
    QTest.mouseClick(staff, Qt.MouseButton.LeftButton, pos=target)
    assert (
        view.session.answered
        and view.controller._advance.isActive()
        and view.session.total == 1
        and view.session.correct == 0
    )
    view.next_question()
    panel.types["button"].click()
    assert (
        exercise.settings_signature() == button_signature
        and len(view.control_area.answers.buttons) == 1
    )
    QTest.mouseClick(staff, Qt.MouseButton.LeftButton, pos=target)
    assert not view.session.answered
    view.control_area.answers.buttons[0].click()
    assert view.session.answered and view.session.correct == 1


def test_hover_previews_the_component_that_a_staff_click_would_select(
    app: QApplication,
) -> None:
    """
    Move between a notehead, a marking, and empty paper before answering
    the question.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.notation.terms = {"Segno"}
    settings.notation.question_type = "staff"
    view = ExercisePage(NotationIdentification(), rng=random.Random(9))
    view.resize(800, 600)
    view.show()
    app.processEvents()
    staff = view.question_view.staff
    assert staff is not None
    q = view.question
    assert q is not None and staff.hasMouseTracking()
    preview = StaffWidget()

    def blue_ink(widget: StaffWidget) -> np.ndarray:
        """
        Measure the blue highlight across the score.

        Parameters
        ----------
        widget : StaffWidget
            Staff to render.

        Returns
        -------
        ndarray
            Mask of highlighted pixels.
        """
        image = (
            widget.grab()
            .toImage()
            .convertToFormat(QImage.Format.Format_RGBA8888)
        )
        pixels = (
            np.frombuffer(image.constBits(), dtype=np.uint8)
            .reshape(image.height(), image.width(), 4)
            .astype(int)
        )
        return pixels[:, :, 2] - pixels[:, :, 0] > 100

    for target in (("Notehead", 0), q.notation_target):
        if target == q.notation_target:
            view.resize(435, 750)
            app.processEvents()
            assert staff.size() != preview.size()
        preview.resize(staff.size())
        preview.show_notes(
            q.staff,
            clef=q.clef,
            value=q.value,
            notation_target=target,
        )
        expected = blue_ink(preview)
        ys, xs = np.where(expected)
        point = QPoint(int(xs[len(xs) // 2]), int(ys[len(ys) // 2]))
        QTest.mouseMove(staff, point)
        assert np.array_equal(blue_ink(staff), expected)
        assert staff.hits_notation(point) == (target == q.notation_target)
        assert view.session.total == 0 and view.question is q

    app.sendEvent(staff, QEvent(QEvent.Type.Leave))
    assert not blue_ink(staff).any()
    QTest.mouseMove(staff, QPoint(10, 10))
    assert not blue_ink(staff).any()
    QTest.mouseClick(staff, Qt.MouseButton.LeftButton, pos=point)
    assert view.session.answered and view.session.correct == 1
    view.controller._advance.stop()
    animation = view.controller.animations.tracked[-1]
    animation.setCurrentTime(animation.duration())
    QTest.mouseMove(staff, point)
    assert not blue_ink(staff).any()

    panel = view.settings_panel
    assert isinstance(panel, NotationSettingsPanel)
    panel.types["button"].click()
    assert not staff.hasMouseTracking()
    original = blue_ink(staff)
    QTest.mouseMove(staff, QPoint(10, 10))
    assert original.any() and np.array_equal(blue_ink(staff), original)


def test_notation_uses_bundled_glyphs_without_system_music_font(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Match the Bravura component outlines when the system cannot supply
    Noto Music.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Simulate a system without Noto Music.
    """
    monkeypatch.setattr("alto.exercises.library.passages_by_term", dict)
    monkeypatch.setattr(QFontDatabase, "hasFamily", lambda family: False)
    staff = StaffWidget()
    staff.resize(400, 330)
    exercise = NotationIdentification()
    for term in ("Notehead", "Stem", "Clef"):
        settings.notation.terms = {term}
        question = exercise.generate(random.Random(7))
        staff.show_notes(
            question.staff,
            value=question.value,
            notation_target=question.notation_target,
        )
        masks = []
        for style in ("bravura", "noto"):
            staff.notation_style = BY_KEY[style]
            image = (
                staff.grab()
                .toImage()
                .convertToFormat(QImage.Format.Format_RGBA8888)
            )
            pixels = (
                np.frombuffer(image.constBits(), dtype=np.uint8)
                .reshape(-1, 4)
                .astype(int)
            )
            masks.append(pixels[:, 2] - pixels[:, 0] > 100)
        assert masks[0].any() and np.array_equal(*masks), term


def test_repertoire_assets_match_their_manifests(app: QApplication) -> None:
    """
    Check every bundled marker, its hit map, source credit, and retained
    MusicXML.

    Parameters
    ----------
    app : QApplication
        The application used to load Qt images.
    """
    for excerpt in excerpts().values():
        metadata = json.loads(
            (excerpt.folder / "excerpt.json").read_text(encoding="utf-8"),
        )
        assert "CC0" in metadata["rights"] and metadata["source"].endswith(
            ".mxl",
        )
        music = ET.parse(excerpt.folder / "score.musicxml")
        assert music.findtext("identification/rights") == "OpenScore (CC0)"
        assert [
            int(m.attrib["number"]) for m in music.findall("part/measure")
        ] == list(
            range(metadata["measures"][0], metadata["measures"][1] + 1),
        )
        score = ET.parse(excerpt.folder / "score.svg")
        markers = [
            int(e.attrib["id"][5:])
            for e in score.iter()
            if e.get("id", "").startswith("mark-")
        ]
        assert sorted(markers) == list(range(len(excerpt.targets)))
        assert set(excerpt.targets) <= MARKS.keys()
        artwork = score_artwork(excerpt)
        assert set(np.unique(artwork.hits)) == set(
            range(len(excerpt.targets) + 1),
        )


def test_repertoire_replay_and_generated_fallback(app: QApplication) -> None:
    """
    Reopen an excerpt in the answer card and keep a selected term
    outside the collection playable.

    Parameters
    ----------
    app : QApplication
        The application used to draw the saved question.
    """
    settings.notation.terms = {"Crescendo hairpin", "Koron"}
    rng = random.Random(34)
    exercise = NotationIdentification()
    questions = [exercise.generate(rng) for _ in range(32)]
    assert {q.answer for q in questions} == settings.notation.terms
    assert all(set(q.choices) == settings.notation.terms for q in questions)
    assert all(
        q.staff and not q.notation_excerpt
        for q in questions
        if q.answer == "Koron"
    )
    question = next(q for q in questions if q.notation_excerpt)
    saved = Question.from_dict(json.loads(json.dumps(question.to_dict())))
    assert saved == question and saved.item_key() == question.item_key()
    assert (
        saved.notation_excerpt
        and describe(saved)
        == f"{excerpts()[saved.notation_excerpt].credit} → {saved.answer}"
    )
    assert (
        replace(saved, notation_excerpt="different-version").item_key()
        != saved.item_key()
    )
    preview = QuestionPreview(exercise.name, question=saved)
    staff = preview.findChild(StaffWidget)
    assert (
        staff is not None
        and staff.excerpt is not None
        and saved.notation_excerpt
    )
    assert (
        staff.excerpt.excerpt == excerpts()[saved.notation_excerpt]
        and staff.notation_target == saved.notation_target
    )
    legacy = next(q for q in questions if q.staff)
    payload = legacy.to_dict()
    del payload["notation_excerpt"]
    assert Question.from_dict(payload).item_key() == legacy.item_key()


def test_click_any_matching_excerpt_marking(app: QApplication) -> None:
    """
    Hover and click the second accent, then keep its feedback on that
    exact symbol after moving the mouse.

    Parameters
    ----------
    app : QApplication
        The shared application.
    """
    settings.notation.terms = {"Accent"}
    settings.notation.question_type = "staff"
    view = ExercisePage(NotationIdentification(), rng=random.Random(11))
    question = view.question
    assert (
        question
        and question.notation_target
        and question.notation_excerpt
        and not question.choices
    )
    staff = view.question_view.staff
    assert staff is not None
    assert staff.excerpt
    target = next(
        i
        for i, term in enumerate(staff.excerpt.excerpt.targets)
        if term == "Accent" and i != question.notation_target[1]
    )
    view.show()
    point = QPoint()
    for width in (450, 1000):
        view.resize(width, 650)
        app.processEvents()
        rect = staff.excerpt.music_rect(QRectF(staff.rect()))
        hit_map = np.asarray(staff.excerpt.hits)
        ys, xs = np.where(hit_map == target + 1)
        point = QPoint(
            round(
                rect.left()
                + xs[len(xs) // 2] * rect.width() / hit_map.shape[1],
            ),
            round(
                rect.top()
                + ys[len(xs) // 2] * rect.height() / hit_map.shape[0],
            ),
        )
        QTest.mouseMove(staff, point)
        assert staff._notation_at(point) == ("Accent", target)
        assert not staff.hits_notation(QPoint(0, 0))
    QTest.mouseClick(staff, Qt.MouseButton.LeftButton, pos=point)
    assert view.session.answered and view.session.correct == 1
    view.controller._advance.stop()
    animation = view.controller.animations.tracked[-1]
    animation.setCurrentTime(animation.duration())
    assert staff._clicked_component == ("Accent", target)
    after = staff.grab().toImage()
    QTest.mouseMove(staff, QPoint(2, 2))
    assert staff.grab().toImage() == after


@pytest.mark.parametrize(
    ("term", "prompt"),
    [
        ("Sharp", "Click a sharp beside a note."),
        ("Barline", "Click a single barline."),
    ],
)
def test_excerpt_prompt_distinguishes_related_ink(
    term: str,
    prompt: str,
) -> None:
    """
    Distinguish note accidentals from the key signature and single from
    final barlines.

    Parameters
    ----------
    term : str
        Selected notation component.
    prompt : str
        Instruction that describes which occurrence counts.
    """
    settings.notation.terms = {term}
    settings.notation.question_type = "staff"
    question = NotationIdentification().generate(random.Random(1))
    assert question.notation_excerpt and question.prompt == prompt
