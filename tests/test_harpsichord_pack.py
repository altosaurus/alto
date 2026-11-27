"""
Tests for the harpsichord example plugin and the keyboard support it
relies on.
"""

from __future__ import annotations

import json
import random
import shutil
from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock

import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from alto import settings
from alto.exercises.base import REGISTRY, PicturePosition, Question
from alto.exercises.packs import PackExercise, load_packs, read_pack
from alto.instrument_packs import PackKeyboard, read_keyboard_style
from alto.theory.pitch import Note
from alto.ui.colors import CORRECT_ANSWER_COLOR
from alto.ui.exercise_settings import (
    load_pack_options,
    save_pack_options,
)
from alto.ui.exercise_view import ExerciseView
from alto.ui.fingerboard import FingerboardWidget
from alto.ui.pack_settings_panel import PackKeyboardSettingsPanel
from alto.ui.store import store
from pack_fixtures import ensure_icons, ensure_pictures, ensure_sounds

# noinspection PyUnresolvedReferences
from test_instrument_packs import isolated_packs  # noqa: F401  # the autouse fixture that keeps registrations local

# The pack as a test fixture. The tutorial and the ZIP that readers
# download live in the harpsichord-plugin-tutorial repository.
PACK = Path(__file__).resolve().parent / "packs/harpsichord/pack.json"
ensure_icons(PACK.parent)  # the tile icons are plain ones
ensure_pictures(
    PACK.parent,
)  # the photographs are plain pictures of the same size
ensure_sounds(
    PACK.parent,
    seconds=1.6,
    # the recordings are made as tones, since the real ones are in the
    # tutorial repository
)
LOWER, UPPER = "Lower manual", "Upper manual"


def _install(
    tmp_path: Path,
    *,
    edit: Callable[[dict], None] | None = None,
) -> list[str]:
    """
    Copy the example pack into an isolated plugins folder, optionally
    edit its manifest, and load it.

    Parameters
    ----------
    tmp_path : Path
        The isolated plugins folder's parent.
    edit : callable or None, default None
        Called with the manifest before it is written back.

    Returns
    -------
    list of str
        The problems found while loading.
    """
    folder = tmp_path / "plugins" / "harpsichord"
    shutil.copytree(PACK.parent, folder)
    if edit is not None:
        data = json.loads(PACK.read_text())
        edit(data)
        (folder / "pack.json").write_text(json.dumps(data))
    return load_packs(tmp_path / "plugins")


def _intervals() -> PackExercise:
    """
    Make the interval exercise from the registry.

    Returns
    -------
    PackExercise
        The harpsichord's interval exercise.
    """
    exercise = next(
        cls
        for cls in REGISTRY
        if cls.name == "Harpsichord Interval Identification"
    )()
    assert isinstance(exercise, PackExercise)
    return exercise


def test_keys_exist_by_their_letter_names() -> None:
    """
    Find natural and sharp keys by name, with no sharp above E or B and
    no flats.
    """
    board = PackKeyboard("Manual", "C4", "E5")
    assert board.naturals == 10
    assert [
        board.has(name)
        for name in (
            "C4",
            "C#4",
            "E4",
            "E#4",
            "F4",
            "B4",
            "A#4",
            "E5",
            "E6",
            "Db4",
            "E5#",
            "D#5",
            "C#5",
        )
    ] == [
        True,
        True,
        True,
        False,
        True,
        True,
        True,
        True,
        False,
        False,
        False,
        True,
        True,
    ]
    assert not board.has("F5") and not board.has("D#6")


def test_keyboard_style_reads_colors_and_numbers() -> None:
    """
    Read a keyboard look: colors as #rrggbb, a top and a bottom color
    for keys, and numbers within their ranges.
    """
    style = read_keyboard_style(
        {
            "white": ["#2a211c", "#120d0a"],
            "cap": "#eee3c8",
            "length": 4.5,
            "gap": 1,
        },
        where="pack.v.va",
    )
    assert style is not None
    assert dict(style.colors) == {
        "white": ("#2a211c", "#120d0a"),
        "cap": "#eee3c8",
    }
    assert dict(style.numbers) == {"length": 4.5, "gap": 1.0}
    assert read_keyboard_style(None, where="pack.v.va") is None


def test_harpsichord_pack_contents(app: QApplication) -> None:
    """
    Load the example and check what it contributes: two exercises, two
    lessons and the glossary entries that link them.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    del app
    classes = {cls.name: cls for cls in read_pack(PACK)}
    assert set(classes) == {
        "Harpsichord Interval Identification",
        "Parts of the Harpsichord",
    }
    parts = classes["Parts of the Harpsichord"]
    answers = {card.answer for card in parts.cards}
    assert {
        "Lid",
        "Prop stick",
        "Leg",
        "Upper manual",
        "Lower manual",
        "Nameboard",
        "Jackrail",
        "Cheek",
        "Apron",
        "Natural key",
        "Sharp key",
        "Tuning pin",
        "Damper",
        "Wrest plank",
        "Bentside",
        "Spine",
    } <= answers
    for card in parts.cards:
        assert (
            card.picture is not None
            and card.answer in card.choices
            and len(card.choices) == 4
        )
        left, top, width, height = card.picture.focus
        assert (
            left <= card.picture.point[0] <= left + width
            and top <= card.picture.point[1] <= top + height
        )
    first = classes["Harpsichord Interval Identification"]
    assert [lesson.title for lesson in first.lessons] == [
        "Parts of the Harpsichord",
        "Intervals on a Double Harpsichord",
    ]
    assert {term.name for term in first.terms} >= {
        "harpsichord",
        "manual",
        "jackrail",
        "wrest plank",
        "bentside",
    }
    for term in first.terms:
        assert term.exercises and term.lessons, term.name


def test_interval_cards_are_correct(app: QApplication) -> None:
    """
    Check every interval card: the answer is the number of half steps
    between the two keys, and both keys exist.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    del app
    exercise = next(
        cls
        for cls in read_pack(PACK)
        if cls.name == "Harpsichord Interval Identification"
    )()
    model = None
    seen = set()
    for card in exercise.cards:
        picture = card.picture
        assert (
            picture is not None
            and picture.view == ""
            and picture.keys
            and len(picture.notes) == 2
        )
        assert picture.span == ("E1", "F6")
        low, high = (Note.parse(name) for name in picture.notes)
        assert 1 <= high.midi - low.midi <= 12
        assert (
            card.answer
            == settings.KEYBOARD_INTERVAL_NAMES[high.midi - low.midi - 1]
        )
        assert card.answer in card.choices and len(card.choices) == 12
        model = model or exercise.pack_instrument
        for (board, name), note in zip(
            picture.keys,
            picture.notes,
            strict=True,
        ):
            keyboard = model.keyboard(board)
            assert keyboard is not None and keyboard.has(name) and name == note
        seen.add(card.item_key())
    assert len(seen) == len(exercise.cards) == 2664
    assert (
        exercise.card_count() == len(exercise.active_cards()) == 888
    )  # the default range, C3 to C5
    placements = set()
    for card in exercise.cards:
        assert card.picture is not None
        placements.add(tuple(board for board, _ in card.picture.keys))
    assert placements == {
        (LOWER, LOWER),
        (UPPER, UPPER),
        (LOWER, UPPER),
        (UPPER, LOWER),
    }
    for card in random.Random(1).sample(exercise.cards, 20):
        assert (
            Question.from_dict(json.loads(json.dumps(card.to_dict()))) == card
        )


def test_manuals_are_drawn_with_the_keys_highlighted(
    app: QApplication,
    tmp_path: Path,
) -> None:
    """
    Draw both manuals, upper above lower, in the pack's look, with each
    question's keys highlighted on the right manual.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    tmp_path : Path
        The isolated plugins folder's parent.
    """
    del app
    assert _install(tmp_path) == []
    exercise = _intervals()
    card = next(
        card
        for card in exercise.active_cards()
        if card.picture
        and card.picture.keys == ((UPPER, "A#3"), (LOWER, "F4"))
    )
    assert card.picture is not None
    board = FingerboardWidget()
    board.resize(720, 340)
    board.show()
    board.show_position(card.picture)
    assert board._manuals_shown() and list(board._manuals) == [UPPER, LOWER]
    upper, lower = board._manuals[UPPER], board._manuals[LOWER]
    assert (upper.highlight, upper.additional_highlights) == (
        Note.parse("A#3").midi,
        set(),
    )
    assert (lower.highlight, lower.additional_highlights) == (
        Note.parse("F4").midi,
        set(),
    )
    assert (upper.lo, upper.hi) == (
        Note.parse("C3").midi,
        Note.parse("C5").midi,
    )
    assert (
        upper.style.cap == "#eee3c8" and upper.key_length == 4.5
    )  # the pack's look, not the learner's
    assert (
        upper.geometry().bottom() < lower.geometry().top()
    )  # the upper manual sits above the lower
    marked = board.grab().toImage()
    board.set_sounding(True)
    assert (
        upper.highlight_color
        == lower.highlight_color
        == QColor(CORRECT_ANSWER_COLOR)
    )
    assert board.grab().toImage() != marked
    board.show_position(
        PicturePosition(
            card.picture.instrument,
            (10, 10),
            "",
            0.0,
            (),
            True,
            "",
        ),
    )
    assert (
        not board._manuals_shown()
    )  # an ordinary picture position is drawn from the photograph again


def test_manuals_shrink_to_the_height_they_are_given(
    app: QApplication,
    tmp_path: Path,
) -> None:
    """
    Fit two drawn manuals into a short pane, such as the glossary's,
    instead of letting them run past it.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    tmp_path : Path
        The isolated plugins folder's parent.
    """
    del app
    assert _install(tmp_path) == []
    card = _intervals().active_cards()[0]
    assert card.picture is not None
    board = FingerboardWidget()
    board.show()
    sizes = []
    for height in (150, 190, 230):
        board.resize(700, height)
        board.show_position(card.picture)
        assert (
            sum(widget.height() for widget in board._manuals.values())
            <= height
        )
        sizes.append(board._manuals[LOWER].height())
    assert sizes == sorted(sizes) and len(set(sizes)) == 3
    assert board.sizeHint().height() > 300  # asks for room for the widest keys


def test_answering_plays_both_keys(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Play the lower and the higher key together, as one chord, on the
    pack's own instrument when the interval is named correctly.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    tmp_path : Path
        The isolated plugins folder's parent.
    monkeypatch : pytest.MonkeyPatch
        Observe the notes that are played.
    """
    del app
    assert _install(tmp_path) == []
    exercise = _intervals()
    assert exercise.has_sound
    card = exercise.cards[0]
    view = ExerciseView(exercise, rng=random.Random(1))
    view.question = card
    view.question_view.fingerboard.show_position(card.picture)
    view.settings_panel.next_question_mode = "Wait"
    played = Mock()
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(view._answer_playback, "play", played)
    view.submit(
        card.answer,
        button=next(
            b for b in view.answer_controls.buttons if b.text() == card.answer
        ),
    )
    notes = played.call_args.args[0]
    assert card.picture is not None
    assert [[str(Note.parse(name)) for name in card.picture.notes]] == [
        [str(n) for n in chord] for chord in notes
    ]
    assert len(notes) == 1 and len(notes[0]) == 2
    assert (
        played.call_args.kwargs["instrument"]
        == "pack.harpsichord.flemish-harpsichord"
    )


def test_lessons_show_keys_on_the_photograph(app: QApplication) -> None:
    """
    Resolve the lesson pictures that highlight keys on the drawn
    keyboards.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    """
    del app
    first = read_pack(PACK)[0]
    lesson = next(
        lesson
        for lesson in first.lessons
        if lesson.title.startswith("Intervals")
    )
    shown = [
        step.picture
        for step in lesson.steps
        if isinstance(step.picture, PicturePosition) and step.picture.keys
    ]
    assert len(shown) >= 4
    keys = set()
    for picture in shown:
        assert (
            isinstance(picture, PicturePosition)
            and picture.view == ""
            and not picture.marker
            and picture.span == ("C3", "C5")
        )
        keys.update(picture.keys)
    assert keys >= {(LOWER, "C4"), (LOWER, "E4"), (UPPER, "A4")}


KEYBOARDS = lambda d: d["instruments"][0]["keyboards"][0]  # noqa: E731
STYLE = lambda d: d["instruments"][0]["keyboard_style"]  # noqa: E731


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda d: KEYBOARDS(d).update(name=LOWER), "its own name"),
        (lambda d: KEYBOARDS(d).update(name="<b>x</b>"), "plain-text name"),
        (lambda d: KEYBOARDS(d).update(lowest="F#1"), "natural key"),
        (lambda d: KEYBOARDS(d).update(highest="C1"), "below its highest"),
        (lambda d: KEYBOARDS(d).update(corners=[[0, 0]] * 4), "only a name"),
        (lambda d: KEYBOARDS(d).update(highest="C9"), "Expected a note"),
        (
            lambda d: d["instruments"][0].update(keyboards=[]),
            "up to 4 keyboards",
        ),
        (lambda d: STYLE(d).update(shine="#ffffff"), "keyboard_style"),
        (lambda d: STYLE(d).update(cap="cream"), "#rrggbb"),
        (lambda d: STYLE(d).update(white=["#111111"]), "two colors"),
        (lambda d: STYLE(d).update(length=20), "length"),
        (lambda d: STYLE(d).update(gap="wide"), "gap"),
        (
            lambda d: d["instruments"][0].update(keyboard_style={}),
            "keyboard_style",
        ),
        (lambda d: d["instruments"][0].pop("keyboards"), "Declare keyboards"),
        (
            lambda d: d["exercises"][0].update(keyboards=["Pedals"]),
            "does not have",
        ),
        (lambda d: d["exercises"][0].update(keyboards=[LOWER, LOWER]), "once"),
        (
            lambda d: d["exercises"][0].update(intervals=["M9"]),
            "distinct intervals",
        ),
        (
            lambda d: d["exercises"][0].update(intervals=[]),
            "distinct intervals",
        ),
        (
            lambda d: d["exercises"][0].update(placements=["above"]),
            "placements",
        ),
        (
            lambda d: d["exercises"][0].update(
                placements=["across"],
                keyboards=[LOWER],
            ),
            "two or more keyboards",
        ),
        (
            lambda d: d["exercises"][0].update(lowest="C5", highest="C3"),
            "below its highest",
        ),
        (lambda d: d["exercises"][0].update(lowest="C9"), "Expected a note"),
        (
            lambda d: d["exercises"][0].update(prompt="<b>Name it</b>"),
            "plain-text prompt",
        ),
        (
            lambda d: d["exercises"][0].update(settings={"accidentals": True}),
            "settings",
        ),
        (
            lambda d: d["lessons"][1]["steps"][1]["picture"].update(
                keys=[[LOWER, "C4"], [LOWER, "E#4"]],
            ),
            "no key",
        ),
        (
            lambda d: d["lessons"][1]["steps"][1]["picture"].update(
                keys=[[LOWER, "C4"]] * 5,
            ),
            "one to 4 keys",
        ),
        (
            lambda d: d["lessons"][1]["steps"][1]["picture"].update(
                keys=[["Pedals", "C4"]],
            ),
            "no key",
        ),
        (
            lambda d: d["lessons"][1]["steps"][1]["picture"].update(
                span=["C5", "C3"],
            ),
            "below its highest",
        ),
        (
            lambda d: d["lessons"][1]["steps"][1]["picture"].update(
                span=["C3"],
            ),
            "span",
        ),
        (
            lambda d: d["lessons"][1]["steps"][1]["picture"].update(
                focus=[0, 0, 100, 100],
            ),
            "only instrument, keys and span",
        ),
    ],
)
def test_bad_keyboards_are_refused(
    tmp_path: Path,
    edit: Callable[[dict], None],
    message: str,
) -> None:
    """
    Refuse a pack whose keyboards, interval exercise or key pictures are
    malformed.

    Parameters
    ----------
    tmp_path : Path
        The isolated plugins folder's parent.
    edit : callable
        Damages the manifest.
    message : str
        Text the problem report must contain.
    """
    problems = _install(tmp_path, edit=edit)
    assert len(problems) == 1 and message in problems[0], problems


def test_range_and_intervals_choose_the_cards(
    app: QApplication,
    tmp_path: Path,
) -> None:
    """
    Ask only the cards inside the learner's range and intervals, with
    those intervals as the answer buttons.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    tmp_path : Path
        The isolated plugins folder's parent.
    """
    del app
    assert _install(tmp_path) == []
    exercise = _intervals()
    cls = type(exercise)
    assert cls.key_span == (28, 89) and cls.key_default == (48, 72)
    settings.pack_exercises.pop(cls.__name__, None)
    panel = PackKeyboardSettingsPanel(cls)
    assert (panel.low_label.text(), panel.high_label.text()) == ("C3", "C5")
    panel._set_keys(60, 67)  # C4 to G4: nothing wider than a fifth fits
    assert (
        panel._commit_timer.isActive()
    )  # saving and the new question wait for the drag to pause
    panel.flush()
    assert not panel._commit_timer.isActive()
    assert cls.options().keys == (60, 67)
    cards = exercise.active_cards()
    assert cards and {card.answer for card in cards} <= {
        "m2",
        "M2",
        "m3",
        "M3",
        "P4",
        "A4 / d5",
        "P5",
    }
    assert all(
        card.picture and card.picture.span == ("C4", "G4") for card in cards
    )
    assert all(
        not box.isEnabled()
        for name, box in (
            panel.interval_page.boxes if panel.interval_page else {}
        ).items()
        if name in ("m6", "P8")
    )
    assert panel.interval_page is not None
    for name, box in panel.interval_page.boxes.items():
        box.setChecked(name in ("M3", "P5"))
    assert cls.options().intervals == frozenset({"M3", "P5"})
    cards = exercise.active_cards()
    assert {card.answer for card in cards} == {"M3", "P5"} and all(
        card.choices == ["M3", "P5"] for card in cards
    )
    changed = exercise.practice_signature()
    panel._set_keys(*cls.key_default)
    panel._select_all_toggled(True)
    assert cls.options().keys is None and cls.options().intervals is None
    assert (
        exercise.practice_signature() == cls.catalog_signature != changed
    )  # the starting settings keep their history
    settings.pack_exercises.pop(cls.__name__, None)


def test_range_and_intervals_are_remembered(
    app: QApplication,
    tmp_path: Path,
) -> None:
    """
    Save the learner's range and intervals and restore them, ignoring
    anything that no longer fits the exercise.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    tmp_path : Path
        The isolated plugins folder's parent.
    """
    del app
    assert _install(tmp_path) == []
    cls = type(_intervals())
    chosen = settings.PackExerciseSettings(
        clefs={"alto"},
        keys=(55, 70),
        intervals=frozenset({"m3", "P5"}),
    )
    settings.pack_exercises[cls.__name__] = chosen
    save_pack_options(cls.__name__)
    settings.pack_exercises[cls.__name__] = settings.PackExerciseSettings(
        clefs={"alto"},
    )
    load_pack_options()
    assert cls.options().keys == (
        55,
        70,
    ) and cls.options().intervals == frozenset({"m3", "P5"})
    store().setValue(f"packExercises/{cls.__name__}/keys", "10-20")
    store().setValue(f"packExercises/{cls.__name__}/intervals", "M9")
    load_pack_options()
    assert cls.options().keys is None and cls.options().intervals is None
    settings.pack_exercises.pop(cls.__name__, None)


def test_manuals_follow_the_range_while_it_is_dragged(
    app: QApplication,
    tmp_path: Path,
) -> None:
    """
    Redraw the manuals over the range at every step of a drag, before
    the new question is asked.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    tmp_path : Path
        The isolated plugins folder's parent.
    """
    del app
    assert _install(tmp_path) == []
    exercise = _intervals()
    cls = type(exercise)
    settings.pack_exercises.pop(cls.__name__, None)
    view = ExerciseView(exercise, rng=random.Random(1))
    view.show()
    panel = view.settings_panel
    assert isinstance(panel, PackKeyboardSettingsPanel)
    manual = view.question_view.fingerboard._manuals[LOWER]
    assert (manual.lo, manual.hi) == (48, 72)
    asked = view.question
    panel._set_keys(36, 84)
    assert (
        (manual.lo, manual.hi) == (36, 84)
        and view.question is asked
        and panel._commit_timer.isActive()
    )
    panel._set_keys(55, 67)
    assert (manual.lo, manual.hi) == (55, 67)
    panel.flush()
    assert (
        view.question is not asked
    )  # the new question is asked once the drag pauses
    assert cls.chosen_span() == ("G3", "G4")
    settings.pack_exercises.pop(cls.__name__, None)


def test_sound_choices_are_grouped_by_plugin_then_kind(
    app: QApplication,
    tmp_path: Path,
) -> None:
    """
    Offer the plugin's own instruments first, then other harpsichords,
    then every other instrument, and let the learner choose.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    tmp_path : Path
        The isolated plugins folder's parent.
    """
    del app
    other = tmp_path / "plugins" / "other-keys"
    (other / "images").mkdir(parents=True)
    (other / "sounds").mkdir()
    shutil.copy(
        PACK.parent / "images/harpsichord-overview.webp",
        other / "images/overview.webp",
    )
    shutil.copy(PACK.parent / "sounds/C4.wav", other / "sounds/C4.wav")
    clavier = {
        "id": "clavier",
        "name": "Clavier",
        "image": "images/overview.webp",
        "kind": "Harpsichord",
        "samples": {"C4": "sounds/C4.wav"},
    }
    question = {
        "prompt": "Which part?",
        "point": [10, 10],
        "choices": ["Lid", "Leg"],
        "answer": "Lid",
    }
    exercise = {
        "id": "parts",
        "title": "Parts",
        "type": "image-choice",
        "instrument": "clavier",
        "questions": [question],
    }
    manifest = {
        "format": 2,
        "id": "other-keys",
        "name": "Other Keys",
        "instruments": [clavier],
        "exercises": [exercise],
    }
    (other / "pack.json").write_text(json.dumps(manifest))
    assert _install(tmp_path) == []
    cls = type(_intervals())
    groups = cls.sound_options()
    assert [heading for heading, _ in groups] == [
        "From Harpsichord Instrument Pack",
        "Other harpsichords",
        "Other instruments",
    ]
    assert groups[0][1] == [
        ("pack.harpsichord.flemish-harpsichord", "Flemish harpsichord"),
    ]
    assert groups[1][1] == [
        ("pack.other-keys.clavier", "Clavier (Other Keys)"),
    ]
    keys = [key for key, _ in groups[2][1]]
    assert (
        keys[:2] == ["piano", "flute"]
        and "pack.other-keys.clavier" not in keys
    )
    settings.pack_exercises.pop(cls.__name__, None)
    panel = PackKeyboardSettingsPanel(cls)
    assert (
        panel.sound_row is not None
        and panel.sound_row.value.text() == "Flemish harpsichord"
    )
    panel._sound_chosen("pack.other-keys.clavier")
    assert cls.options().sound == "pack.other-keys.clavier"
    assert (
        _intervals().sound_instrument("pack.harpsichord.flemish-harpsichord")
        == "pack.other-keys.clavier"
    )
    assert panel.sound_row.value.text() == "Clavier (Other Keys)"
    panel._sound_chosen("pack.harpsichord.flemish-harpsichord")
    assert (
        cls.options().sound is None
    )  # the plugin's own sound is the default, so nothing is stored
    settings.pack_exercises.pop(cls.__name__, None)


def test_manuals_choose_which_keys_are_highlighted(
    app: QApplication,
    tmp_path: Path,
) -> None:
    """
    Highlight both keys on the checked manuals only, and remember the
    choice.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    tmp_path : Path
        The isolated plugins folder's parent.
    """
    del app
    assert _install(tmp_path) == []
    exercise = _intervals()
    cls = type(exercise)
    assert set(cls.manual_names) == {"Upper manual", "Lower manual"}
    settings.pack_exercises.pop(cls.__name__, None)
    panel = PackKeyboardSettingsPanel(cls)
    assert panel.manual_page is not None
    assert panel.manuals_row.value.text() == "Both"
    both = exercise.active_cards()
    pictures = [card.picture for card in both if card.picture is not None]
    assert {board for picture in pictures for board, _ in picture.keys} == set(
        cls.manual_names,
    )
    panel.manual_page.boxes["Lower manual"].setChecked(False)
    assert cls.options().manuals == frozenset({"Upper manual"})
    assert panel.manuals_row.value.text() == "Upper"
    upper = exercise.active_cards()
    assert upper and len(upper) < len(both)
    shown = [card.picture for card in upper if card.picture is not None]
    assert all(
        board == "Upper manual"
        for picture in shown
        for board, _ in picture.keys
    )
    assert exercise.practice_signature() != cls.catalog_signature
    save_pack_options(cls.__name__)
    settings.pack_exercises[cls.__name__] = settings.PackExerciseSettings(
        clefs={"alto"},
    )
    load_pack_options()
    assert cls.options().manuals == frozenset({"Upper manual"})
    panel = PackKeyboardSettingsPanel(
        cls,
    )  # the reload replaced the options the first panel edits
    assert (
        panel.manual_page is not None
        and panel.manuals_row.value.text() == "Upper"
    )
    panel.manual_page.boxes["Lower manual"].setChecked(True)
    assert cls.options().manuals is None
    assert exercise.practice_signature() == cls.catalog_signature
    settings.pack_exercises.pop(cls.__name__, None)


def test_changing_the_sound_applies_to_the_question_on_screen(
    app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Sound the instrument chosen in settings at once, even for the
    question already on screen.

    Parameters
    ----------
    app : QApplication
        Shared Qt application.
    tmp_path : Path
        The isolated plugins folder's parent.
    monkeypatch : pytest.MonkeyPatch
        Observe the instrument that is played.
    """
    del app
    assert _install(tmp_path) == []
    exercise = _intervals()
    cls = type(exercise)
    settings.pack_exercises.pop(cls.__name__, None)
    view = ExerciseView(exercise, rng=random.Random(1))
    view.next_question()
    view.settings_panel.next_question_mode = "Wait"
    played = Mock()
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(view._answer_playback, "play", played)
    cls.options().sound = "horn"
    # the live redraw runs before the new question does
    view._redraw_keyboards()
    card = view.question
    assert card is not None
    view.submit(
        card.answer,
        button=next(
            b for b in view.answer_controls.buttons if b.text() == card.answer
        ),
    )
    assert played.call_args.kwargs["instrument"] == "horn"
    settings.pack_exercises.pop(cls.__name__, None)
