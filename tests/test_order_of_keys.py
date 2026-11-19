"""Practice writing key signatures on the staff one sign at a time."""

import random

import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QToolButton

from alto import settings
from alto.exercises.base import Question
from alto.exercises.library import OrderOfKeys
from alto.theory import key_signatures
from alto.theory.pitch import Note
from alto.ui.exercise_view import ExerciseView
from alto.ui.main_window import MainWindow
from alto.ui.notation import STYLES
from alto.ui.settings_panel import KeySignatureSettingsPanel, load_order_of_keys
from alto.ui.staff import BOTTOM_LINE, KEY_OFFSET, KEY_STEP, StaffWidget
from alto.ui.staff_input import SignatureInput


def test_generated_signatures() -> None:
    """Check all key names, written signs and octaves in both clefs, including after storage."""
    sharps = {"treble": "F5 C5 G5 D5 A4 E5 B4", "bass": "F3 C3 G3 D3 A2 E3 B2"}
    flats = {"treble": "B4 E5 A4 D5 G4 C5 F4", "bass": "B2 E3 A2 D3 G2 C3 F2"}
    keys = set()
    rng = random.Random(0)
    for _ in range(700):
        q = OrderOfKeys().generate(rng)
        keys.add((q.clef, q.caption))
        pitches = (sharps if q.key > 0 else flats)[q.clef].split()[: abs(q.key)]
        glyph = "♯" if q.key > 0 else "♭"
        expected = " ".join(letter + glyph + octave for letter, octave in pitches) or "No accidentals"
        assert q.check(expected)
        assert Question.from_dict(q.to_dict()) == q
    assert len(keys) == 60


def test_impossible_signature_positions(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Reject an engraving pattern that would put a sign outside the signature.

    Parameters
    ----------
    monkeypatch : pytest.MonkeyPatch
        Supply a pattern that puts the second sharp a twelfth above the first.
    """
    monkeypatch.setattr(key_signatures, "_SHARP_PATTERNS", ((11, -3, -3, 4, -3, -3),))
    with pytest.raises(ValueError, match="no key signature fits the treble clef"):
        key_signatures.key_signature_positions("treble", sign=1)


def test_submit_edit_and_retry(app: QApplication) -> None:
    """
    Write a bass-clef signature by mouse, retry errors, and return to a blank question.

    Parameters
    ----------
    app : QApplication
        Application for sending staff clicks.
    """
    view = ExerciseView(OrderOfKeys(), rng=random.Random(7))
    view.settings_panel.next_question_mode = "Wait"
    view.show()
    app.processEvents()
    staff = view.scale_input
    assert isinstance(staff, SignatureInput)
    assert staff.key == 0 and not staff.columns and not staff.notes and staff.caption == "B♭ major"
    assert view.staff.isHidden() and view.prompt.isHidden() and view.accidental_buttons[0].isHidden()

    def click(pitch: str) -> None:
        """
        Click the line or space for a written pitch.

        Parameters
        ----------
        pitch : str
            The staff position, including its octave.
        """
        y = staff.staff_bottoms()["bass"] - (Note.parse(pitch).diatonic - BOTTOM_LINE["bass"]) * staff.GAP / 2
        QTest.mouseClick(staff, Qt.MouseButton.LeftButton, pos=QPoint(90, round(y)))

    view.accidental_buttons[-1].click()
    view.accidental_buttons[-1].click()
    assert staff.accidental == -1
    for pitches in (["B2"], ["E3", "B2"], ["B3", "E3"], ["B2", "E3", "A2"]):
        for pitch in pitches:
            click(pitch)
        view.answer_button.click()
        assert view.missed and not view.answered and not view.answer_button.isEnabled()
        assert "Try again" in view.place_status.text()
        for _ in pitches:
            view.undo_button.click()
    view._key_action("right")
    assert staff.accidental == 1
    click("B2")
    click("E3")
    view.answer_button.click()
    assert not view.answered
    view.undo_button.click()
    view.undo_button.click()
    view._key_action("left")
    click("B2")
    click("E3")
    view.answer_button.click()
    assert view.answered and staff.locked and view.total == 1 and view.correct == 0
    assert not view.next_button.isHidden()
    view.next_button.click()
    assert not staff.notes and not staff.locked and view.answer_button.isEnabled()
    view.close()


@pytest.mark.parametrize("seed", [20, 9])
def test_keyboard_entry_and_blank_signature(app: QApplication, seed: int) -> None:
    """
    Submit a sharp signature using keyboard controls or submit a correctly empty signature.

    Parameters
    ----------
    app : QApplication
        Application for dispatching shortcuts.
    seed : int
        Selects a sharp or empty signature.
    """
    view = ExerciseView(OrderOfKeys(), rng=random.Random(seed))
    view.settings_panel.next_question_mode = "Wait"
    view.show()
    view.activateWindow()
    assert QTest.qWaitForWindowActive(view)
    view.setFocus()
    app.processEvents()
    staff = view.scale_input
    assert isinstance(staff, SignatureInput) and view.question
    if view.question.key:
        QTest.mouseMove(staff, QPoint(90, round(staff.staff_bottoms()[staff.clef])))
        for word in view.question.answer.split():
            note = Note.parse(word.replace("♯", "#"))
            here = staff.caret_start() if staff.caret is None else staff.caret
            delta = note.diatonic - here
            for _ in range(abs(delta)):
                QTest.keyClick(view, Qt.Key.Key_Up if delta > 0 else Qt.Key.Key_Down)
            assert staff.preview == note
            assert not staff.grab().isNull()
            QTest.keyClick(view, Qt.Key.Key_P)
            QTest.qWait(160)  # Qt animates buttons activated through their shortcut.
        assert len(staff.notes) == abs(view.question.key)
        assert not view.place_button.isEnabled() and "Seven signs placed" in view.place_status.text()
    QTest.keyClick(view, Qt.Key.Key_Return)
    QTest.qWait(160)
    assert view.answered and view.correct == 1
    view.close()


@pytest.mark.parametrize("font", ["noto", "bravura"])
def test_placed_signs_match_printed_signature(app: QApplication, font: str) -> None:
    """
    Compare the completed signature with Alto’s printed one at the same size.

    Parameters
    ----------
    app : QApplication
        Application for rendering widgets.
    font : str
        Built-in or SMuFL notation to draw.
    """
    editor, printed = SignatureInput(), StaffWidget()
    editor.notation_style = printed.notation_style = next(style for style in STYLES if style.key == font)
    editor.reset_scale("treble", slots=7, caption="D major")
    printed.show_notes([], clef="treble", key=2, caption="D major")
    editor.resize(400, 330)
    printed.resize(editor.size())
    expected = printed.grab().toImage()
    blank = editor.grab().toImage()
    assert blank != expected
    editor.place_next(Note.parse("F#5"))
    editor.place_next(Note.parse("C#5"))
    assert editor.grab().toImage() == expected

    editor.reset_signature("treble", key=2, caption="D major", starting_slots=[1])
    partial = editor.grab().toImage()
    x = round(editor.side + KEY_OFFSET)
    width = round(KEY_STEP)
    assert partial.copy(x, 0, width, partial.height()) == blank.copy(x, 0, width, partial.height())
    assert partial.copy(x + width, 0, width, partial.height()) != blank.copy(x + width, 0, width, partial.height())
    editor.place_next(Note.parse("F#5"))
    assert editor.grab().toImage() == expected


def test_settings_filter_and_restore_questions(app: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Edit all three submenus and restore their selections into a fresh configuration.

    Parameters
    ----------
    app : QApplication
        Application for the exercise and its settings menu.
    monkeypatch : pytest.MonkeyPatch
        Replace the in-memory settings to simulate restarting Alto.
    """
    exercise = OrderOfKeys()
    view = ExerciseView(exercise, rng=random.Random(4))
    view.show()
    view.gear.click()
    pane = view.settings_panel
    assert isinstance(pane, KeySignatureSettingsPanel)
    assert exercise.settings_signature() == ""
    for index, (row, title, boxes, wanted) in enumerate(
        (
            (pane.clefs_row, "Clefs", pane.boxes.values(), pane.boxes["alto"]),
            (pane.modes_row, "Scales", pane.modes.boxes.values(), pane.modes.boxes["Dorian"]),
            (pane.keys_row, "Key Signatures", pane.key_list.boxes.values(), pane.key_list.boxes[-2]),
        ),
        start=1,
    ):
        assert row.accessibleName() == title
        previous = view.question
        row.click()
        QTest.qWait(300)
        assert pane.stack.currentIndex() == index and view.question is previous
        wanted.setChecked(True)
        for box in boxes:
            if box is not wanted:
                box.setChecked(False)
        page = pane.stack.currentWidget()
        assert page is not None
        back = next(button for button in page.findChildren(QToolButton) if button.text() == "‹ Back")
        previous = view.question
        back.click()
        QTest.qWait(300)
        assert pane.stack.currentIndex() == 0 and view.question is previous
    assert pane.clef_pictures.clefs == ["alto"] and pane.modes_row.value.text() == "1 of 7"
    assert view.question and (view.question.clef, view.question.caption, view.question.answer) == ("alto", "C Dorian", "B♭3 E♭4")
    assert view.scale_input.key == 0 and view.scale_input.caption == "C Dorian"
    selected = exercise.settings_signature()
    assert selected and settings.key_signatures == settings.KeySignatureSettings()
    assert settings.key_construction == settings.KeyConstructionSettings()
    with monkeypatch.context() as restart:
        restart.setattr(settings, "order_of_keys", settings.OrderOfKeysSettings())
        window = MainWindow()
        window.open_exercise(OrderOfKeys)
        reopened = window.stack.currentWidget()
        assert isinstance(reopened, ExerciseView) and reopened.question == view.question
        assert exercise.settings_signature() == selected
        window._restore_defaults()
        assert settings.order_of_keys == settings.OrderOfKeysSettings() and exercise.settings_signature() == ""


def test_random_starting_slots_match_selected_counts() -> None:
    """Sample compatible sharp and flat keys and reproduce each random set of givens from its stored question."""
    cfg = settings.order_of_keys
    cfg.clefs, cfg.modes, cfg.keys = {"treble"}, {"Dorian"}, {-7, -3, -1, 0, 1, 4}
    exercise = OrderOfKeys()
    blank_signature = exercise.settings_signature()
    cfg.starting_accidentals = {-3, 2}
    assert exercise.settings_signature() != blank_signature
    rng = random.Random(17)
    seen = {}
    for _ in range(150):
        q = exercise.generate(rng)
        given = tuple(q.starting_slots)
        assert len(given) == (3 if q.key < 0 else 2)
        assert given == tuple(sorted(set(given))) and all(0 <= slot < abs(q.key) for slot in given)
        assert Question.from_dict(q.to_dict()) == q
        seen.setdefault(q.key, {})[given] = q.item_key()
    assert seen.keys() == {-7, -3, 4}
    assert len(seen[4]) == len(set(seen[4].values())) == 6
    cfg.starting_accidentals = {0}
    assert exercise.settings_signature() == blank_signature
    data = exercise.generate(rng).to_dict()
    data.pop("starting_slots")
    assert Question.from_dict(data).starting_slots == []


def test_fill_gaps_and_undo(app: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Draw fixed signs between editable slots, undo an entry, and grade the completed signature.

    Parameters
    ----------
    app : QApplication
        Application for rendering the staff.
    monkeypatch : pytest.MonkeyPatch
        Choose the same two given slots each time the question is opened.
    """
    cfg = settings.order_of_keys
    cfg.keys, cfg.clefs, cfg.modes, cfg.starting_accidentals = {-4}, {"treble"}, {"Major (Ionian)"}, {-2}
    exercise = OrderOfKeys()
    q = exercise.generate(random.Random(1))
    q.starting_slots = [1, 3]
    monkeypatch.setattr(exercise, "generate", lambda rng: q)
    view = ExerciseView(exercise)
    staff = view.scale_input
    assert isinstance(staff, SignatureInput)
    view.settings_panel.next_question_mode = "Wait"
    b, e, a, d = [Note.parse(n) for n in ("Bb4", "Eb5", "Ab4", "Db5")]
    assert staff.entered_signature() == [None, e, None, d, None, None, None]
    assert staff.accidental == -1 and not view.undo_button.isEnabled()
    staff.place_next(a)
    view.answer_button.click()
    assert view.missed and not view.answered
    view.undo_button.click()
    assert staff.entered_signature() == [None, e, None, d, None, None, None]
    staff.place_next(b)
    staff._redraw(a)
    assert staff.preview == a and not staff.grab().isNull()
    staff.place_next(a)
    assert staff.entered_signature() == [b, e, a, d, None, None, None] and not staff.complete
    view.answer_button.click()
    assert view.answered
    view.next_button.click()
    assert staff.entered_signature() == [None, e, None, d, None, None, None]


@pytest.mark.parametrize("start", [0, 3, 6])
def test_seventh_sharp_in_six_sharp_key(start: int, app: QApplication) -> None:
    """
    Accept a seventh sign as input, grade it on submission, and let Undo restore the correct six.

    Parameters
    ----------
    start : int
        Number of sharps supplied on the staff.
    app : QApplication
        Shared Qt application.
    """
    cfg = settings.order_of_keys
    cfg.keys, cfg.starting_accidentals = {6}, {start}
    view = ExerciseView(OrderOfKeys(), rng=random.Random(10))
    staff = view.scale_input
    assert isinstance(staff, SignatureInput) and view.question
    signs = key_signatures.written_signature(view.question.clef, key=7)
    for i, sign in enumerate(signs):
        if i not in view.question.starting_slots:
            assert view.place_button.isEnabled()
            staff.place_next(sign)
    assert staff.entered_signature() == signs and not view.place_button.isEnabled()
    assert not view.missed
    view.answer_button.click()
    assert view.missed and not view.answered
    view.undo_button.click()
    assert staff.entered_signature() == [*signs[:6], None]
    view.answer_button.click()
    assert view.answered


@pytest.mark.parametrize("count", [-7, 7])
def test_fully_given_signature(count: int, app: QApplication) -> None:
    """
    Submit seven starting signs without entering or undoing any.

    Parameters
    ----------
    count : int
        Seven flats or seven sharps.
    app : QApplication
        Shared Qt application.
    """
    cfg = settings.order_of_keys
    cfg.starting_accidentals = {count}
    view = ExerciseView(OrderOfKeys())
    assert view.question and view.question.key == count and view.question.starting_slots == list(range(7))
    assert not view.place_button.isEnabled() and not view.undo_button.isEnabled()
    view.answer_button.click()
    assert view.correct == 1 and view.answered


def test_starting_accidentals_menu(app: QApplication) -> None:
    """
    Check submenu geometry, persistence and compatibility when the eligible keys change.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    view = ExerciseView(OrderOfKeys())
    view.resize(950, 700)
    view.show()
    view.gear.click()
    pane = view.settings_panel
    assert isinstance(pane, KeySignatureSettingsPanel)
    pane.starts_row.click()
    QTest.qWait(350)
    boxes = pane.starts_list.boxes
    assert boxes[0].text() == "0" and boxes[0].isChecked() and not boxes[0].isEnabled()
    assert boxes[0].mapToGlobal(QPoint()).y() < boxes[-1].mapToGlobal(QPoint()).y()
    for n in range(1, 8):
        assert boxes[n].isVisible() and boxes[-n].text() == f"{n} ♭" and boxes[n].text() == f"{n} ♯"
        flat, sharp = boxes[-n].mapToGlobal(QPoint()), boxes[n].mapToGlobal(QPoint())
        assert flat.y() == sharp.y() and flat.x() < sharp.x()
        if n > 1:
            assert sharp.y() > boxes[n - 1].mapToGlobal(QPoint()).y()
    boxes[3].click()
    boxes[0].click()
    assert pane.starts_row.value.text() == "3 ♯" and view.question and len(view.question.starting_slots) == 3
    cfg = settings.order_of_keys
    cfg.starting_accidentals = {0}
    load_order_of_keys()
    assert cfg.starting_accidentals == {3}
    for k in range(3, 8):
        pane.key_list.boxes[k].setChecked(False)
    assert cfg.starting_accidentals == {0} and not boxes[3].isEnabled()
    assert view.question and not view.question.starting_slots
