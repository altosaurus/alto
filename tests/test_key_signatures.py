"""
The key signature identification exercise.

Reading a signature drawn on a staff and naming its key, and the scales
(major, minor and the modes) and the
staffs and signatures it can use.
"""

from __future__ import annotations

import json
import random
from typing import TYPE_CHECKING

import pytest
from PySide6.QtWidgets import (
    QPushButton,
    QToolButton,
)

from alto import settings
from alto.exercises.base import Question
from alto.exercises.library import (
    KeySignatures,
    NoteNames,
)
from alto.learning import stats
from alto.learning.database import (
    Database,
    ItemRecord,
)
from alto.learning.learner import Learner
from alto.theory.scales import (
    MODE_DEGREE,
    SCALES,
    build,
    mode_tonic,
)
from alto.ui import exercise_settings as es
from alto.ui import motion
from alto.ui import settings_panel as sp
from alto.ui.exercise_view import (
    ExerciseView,
    sounds,
)
from alto.ui.question_preview import QuestionPreview
from alto.ui.store import store

if TYPE_CHECKING:
    from PySide6.QtWidgets import (
        QApplication,
        QWidget,
    )

    from alto.ui.settings_panel import KeySignatureSettingsPanel

MAJOR, MINOR = "Major (Ionian)", "Natural minor (Aeolian)"


def questions(
    n: int = 300,
    *,
    seed: int = 1,
    **choose: object,
) -> list[Question]:
    """
    `n` questions made with these settings (clefs, modes, keys).

    Parameters
    ----------
    n : int
        How many questions.
    seed : int
        The random seed.
    choose : object
        Key signature settings to change before asking.

    Returns
    -------
    list of Question
        The questions.
    """
    for name, value in choose.items():
        setattr(settings.key_signatures, name, value)
    rng = random.Random(seed)
    return [KeySignatures().generate(rng) for _ in range(n)]


def test_each_mode_starts_where_its_signature_says() -> None:
    """
    Check that each mode starts where its signature says.
    """
    assert [
        mode_tonic(2, mode=m).name
        for m in (
            MAJOR,
            "Dorian",
            "Phrygian",
            "Lydian",
            "Mixolydian",
            MINOR,
            "Locrian",
        )
    ] == [
        "D",
        "E",
        "F♯",
        "G",
        "A",
        "B",
        "C♯",
    ]
    assert (
        mode_tonic(-3, mode=MINOR).name == "C"
        and mode_tonic(0, mode="Locrian").name == "B"
    )
    assert (
        mode_tonic(7, mode="Lydian").name == "F♯"
        and mode_tonic(-7, mode="Locrian").name == "B♭"
    )


@pytest.mark.parametrize("mode", list(MODE_DEGREE))
def test_scale_in_any_mode_carries_exactly_key_signature_asked(
    mode: str,
) -> None:
    """
    Check that a scale in any mode carries exactly the key signature it
    is asked with.

    Parameters
    ----------
    mode : str
        The scale mode under test.
    """
    for count in range(-7, 8):
        tonic = mode_tonic(count, mode=mode)
        assert (
            abs(tonic.accidental) <= 1
        )  # no double sharps or flats in a name
        notes = build(tonic, intervals=SCALES[mode])
        assert (
            sum(n.accidental for n in notes) == count
            and len({n.letter for n in notes}) == 7
        )


def test_by_default_major_and_minor_keys_are_asked_on_a_staff() -> None:
    """
    Check that by default major and minor keys are asked, each shown on
    a staff.
    """
    asked = questions(400)
    assert all(q.show_staff for q in asked)
    assert {q.prompt for q in asked} == {
        "Which major key has this key signature?",
        "Which minor key has this key signature?",
    }


def test_reading_a_signature_shows_a_staff_and_asks_for_the_tonic() -> None:
    """
    Check that reading a signature shows a staff and asks for the tonic.
    """
    for q in questions(
        200,
        modes={"Dorian"},
        clefs={"alto"},
        keys={2},
    ):
        assert (
            q.show_staff and q.staff == [] and q.clef == "alto" and q.key == 2
        )
        assert q.prompt == "Which Dorian scale has this key signature?"
        assert (
            q.caption == "_ Dorian"
        )  # written under the staff, where the tonic goes
        assert q.answer == "E" and q.choices == ["E"]
        assert q.explanation.endswith(
            "E F♯ G A B C♯ D E",
        )  # E Dorian, up to its octave
        assert "2 sharps: E Dorian" in q.explanation


def test_the_staffs_the_modes_and_the_keys_are_chosen_from_the_settings() -> (
    None
):
    """
    Check that the staffs the modes and the keys are chosen from the
    settings.
    """
    asked = questions(
        600,
        clefs={"treble", "tenor"},
        modes={MAJOR, "Locrian"},
        keys={-3, 0, 4},
    )
    assert {q.clef for q in asked} == {"treble", "tenor"} and {
        q.key for q in asked
    } == {-3, 0, 4}
    assert {q.prompt for q in asked} == {
        "Which major key has this key signature?",
        "Which Locrian scale has this key signature?",
    }
    major = next(q for q in asked if q.key == 4 and "major" in q.prompt)
    assert major.answer == "E"


def test_settings_choice_with_nothing_ticked_falls_back_to() -> None:
    """
    Check that a settings choice with nothing checked falls back to
    something sensible.
    """
    cfg = settings.key_signatures
    cfg.clefs, cfg.modes, cfg.keys = set(), set(), set()
    assert (
        cfg.active_clefs(),
        cfg.active_modes(),
        cfg.active_keys(),
    ) == (
        ["treble"],
        [MAJOR],
        [0],
    )


def test_a_question_comes_back_with_its_staff_and_its_scale() -> None:
    """
    Check that a question comes back with its staff and its scale.
    """
    for q in questions(50):
        again = Question.from_dict(q.to_dict())
        assert (
            again == q
            and again.show_staff
            and again.item_key() == q.item_key()
        )


def test_the_exercise_signature_follows_the_settings() -> None:
    """
    Check that the exercise signature follows the settings.
    """
    before = KeySignatures().settings_signature()
    settings.key_signatures.modes = {"Dorian"}
    assert KeySignatures().settings_signature() != before


def test_key_signature_question_described_by_signature_in_lists() -> None:
    """
    Check that a key signature question is described by its signature in
    the lists of hard questions.
    """
    q = questions(
        1,
        keys={-3},
        clefs={"bass"},
    )[0]
    assert stats.describe(q).startswith("Bass: 3 flats. Which ")


# -- the exercise screen
# ----------------------------------------------------------------------


def test_a_signature_is_drawn_and_a_right_answer_makes_no_sound(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that a signature is drawn and a right answer makes no sound.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the
        test.
    """
    played = []
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(
        "alto.ui.exercise_view.sounds.play_notes",
        lambda notes: played.append(notes),
    )
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(
        "alto.ui.exercise_view.sounds.play_correct",
        lambda streak: played.append(streak),
    )
    view = ExerciseView(KeySignatures(), rng=random.Random(3))
    q = view.question
    assert q is not None
    assert (
        view.question_view.staff.isVisibleTo(view)
        and view.question_view.staff.key == q.key
        and view.question_view.staff.clef == q.clef
    )
    next(
        b for b in view.answer_controls.buttons if b.text() == q.answer
    ).click()
    assert view.session.answered
    view._advance.stop()
    assert played == []  # neither a tone nor the ordinary chime


def test_the_sound_button_is_a_global_mute_that_works_in_every_exercise(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that the sound button is a global mute that works in every
    exercise.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces settings, functions or attributes for the length of the
        test.
    """
    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(sounds, "enabled", True)
    assert KeySignatures.has_sound is False and NoteNames.has_sound is True
    for exercise in (KeySignatures(), NoteNames()):
        view = ExerciseView(exercise, rng=random.Random(3))
        assert (
            view.sound_btn.isEnabled()
            and view.sound_btn.toolTip().startswith("Sound on")
        )
        view.sound_btn.click()
        assert not sounds.enabled and view.sound_btn.toolTip().startswith(
            "Muted",
        )
        view.sound_btn.click()
        assert sounds.enabled
    muted = ExerciseView(
        KeySignatures(),
        rng=random.Random(3),
    )  # one exercise sees a mute made in another
    sounds.enabled = False
    muted._show_sound_state()
    assert (
        muted.sound_btn.toolTip().startswith("Muted")
        and muted.sound_btn.isEnabled()
    )


def test_the_preview_shows_the_signature_and_the_caption(
    app: QApplication,
) -> None:
    """
    Check that the preview shows the signature and the caption.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    q = questions(1)[0]
    dialog = QuestionPreview("Key Signature Identification", question=q)
    assert q.caption and dialog.grab().width() > 0
    assert not [
        b for b in dialog.findChildren(QPushButton) if b.text() == "Play"
    ]  # there is nothing to play


def test_a_question_stored_with_a_scale_to_play_still_loads() -> None:
    """
    Check that a question stored with a scale to play still loads.
    """
    q = questions(1)[0]
    old = {
        **q.to_dict(),
        "play": [[{"octave": 4, "letter": 0, "accidental": 0}]],
    }
    assert Question.from_dict(old) == q


# -- the settings pane
# ----------------------------------------------------------------------


@pytest.fixture
def pane(app: QApplication) -> sp.KeySignatureSettingsPanel:
    """
    Build the key signature settings panel, sized and shown.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.

    Returns
    -------
    KeySignatureSettingsPanel
        The panel.
    """
    panel = sp.KeySignatureSettingsPanel(settings.key_signatures)
    panel.resize(290, 600)
    panel.show()
    return panel


def back(panel: QWidget) -> None:
    """
    Click the Back button of the panel and wait for the page to slide.

    Parameters
    ----------
    panel : QWidget
        The panel.
    """
    next(
        b for b in panel.findChildren(QToolButton) if b.text() == "‹ Back"
    ).click()
    motion.settle()


def test_the_pane_opens_each_page_and_back_returns(
    pane: KeySignatureSettingsPanel,
) -> None:
    """
    Check that the pane opens each page and back returns.

    Parameters
    ----------
    pane : KeySignatureSettingsPanel
        The key signature panel under test.
    """
    for row, index in (
        (pane.clefs_row, 1),
        (pane.modes_row, 2),
        (pane.keys_row, 3),
    ):
        row.click()
        motion.settle()
        assert pane.stack.currentIndex() == index
        back(pane)
    pane.clefs_row.click()
    pane.clefs_row.click()  # ignored mid-slide
    motion.settle()
    pane._go(1)  # already there
    assert pane.stack.currentIndex() == 1


def test_the_pane_edits_and_saves_every_setting(
    pane: KeySignatureSettingsPanel,
) -> None:
    """
    Check that the pane edits and saves every setting.

    Parameters
    ----------
    pane : KeySignatureSettingsPanel
        The key signature panel under test.
    """
    cfg = settings.key_signatures
    changes = []
    pane.changed.connect(lambda: changes.append(1))
    pane.boxes["alto"].setChecked(True)
    pane.boxes["bass"].setChecked(False)
    assert cfg.clefs == {"treble", "alto"}
    pane.modes.boxes["Dorian"].setChecked(True)
    assert "Dorian" in cfg.modes
    pane.key_list.boxes[5].setChecked(True)
    pane.key_list.boxes[-6].setChecked(False)
    assert 5 in cfg.keys and -6 not in cfg.keys and len(changes) == 4
    assert store().value("keySignatures/clefs") == "treble,alto"
    assert "Dorian" in str(store().value("keySignatures/modes")).split("|")
    pane._refresh_summaries()
    assert pane.modes_row.value.text() == "3 of 7"


def test_the_saved_settings_are_read_back_and_bad_ones_ignored() -> None:
    """
    Check that the saved settings are read back and bad ones ignored.
    """
    s = store()
    s.setValue("keySignatures/clefs", "tenor,bass,nonsense")
    s.setValue("keySignatures/modes", "Lydian|Locrian|Made up")
    s.setValue("keySignatures/keys", "-4,3,99")
    es.load_key_signatures()
    cfg = settings.key_signatures
    assert cfg.clefs == {"tenor", "bass"}
    assert cfg.modes == {"Lydian", "Locrian"} and cfg.keys == {-4, 3}
    for name in (
        "clefs",
        "modes",
        "keys",
    ):
        s.setValue(f"keySignatures/{name}", "nonsense")
    s.setValue("keySignatures/keys", "99")
    es.load_key_signatures()
    assert cfg.clefs == {"tenor", "bass"} and cfg.keys == {
        -4,
        3,
    }  # nothing usable: what was there stays


def test_the_exercise_is_called_key_signature_identification() -> None:
    """
    Check that the exercise is called Key Signature Identification, in
    its name and its help.
    """
    text = KeySignatures().instructions()
    assert KeySignatures.name == "Key Signature Identification"
    assert (
        "drawn on a staff" in text
        and "Dorian" in text
        and "how many sharps or flats" not in text
    )


def test_explanation_spells_scale_from_tonic_up_to_octave() -> None:
    """
    Check that the explanation spells the scale from the tonic up to its
    octave.
    """
    q = questions(
        1,
        keys={0},
        modes={MAJOR},
    )[0]
    assert q.explanation.endswith("C D E F G A B C")


def test_the_kind_of_scale_is_written_under_the_staff_not_above_it(
    app: QApplication,
) -> None:
    """
    Check that the kind of scale is written under the staff not above
    it.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    asked = questions(200)
    assert {q.caption for q in asked} == {"_ Major", "_ minor"}
    view = ExerciseView(KeySignatures(), rng=random.Random(1))
    view.resize(900, 600)
    view.show()
    for _ in range(30):
        q = view.question
        assert q is not None
        assert (
            view.question_view.staff.caption == q.caption
            and view.prompt.isHidden() == bool(q.caption or not q.prompt)
        )
        view.next_question()


def test_question_stored_before_captions_captioned_when_comes() -> None:
    """
    Check that a stored signature question without a caption is asked
    with one.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    old = Question(
        "Which minor key has this key signature?",
        choices=["C", "D"],
        answer="C",
        clef="treble",
        key=-3,
        show_staff=True,
    )
    db.save_item(
        learner.profile.id,
        exercise="KeySignatures",
        item_key=old.item_key(),
        item=ItemRecord(
            50.0,
            seen=1,
            first_try_right=0,
            wrong_attempts=1,
            total_first_ms=1000,
            last_seen=1.0,
            signature=KeySignatures().settings_signature(),
            payload=json.dumps(old.to_dict()),
        ),
    )
    rng = random.Random(0)
    asked = [
        learner.pick(KeySignatures(), rng=rng, now=2.0) for _ in range(200)
    ]
    replayed = [q for q in asked if q.item_key() == old.item_key()]
    assert replayed and all(q.caption == "_ minor" for q in replayed)


def test_choices_include_all_selected_modes_and_keys() -> None:
    """
    Keep the full selected tonic set, including G sharp, on every
    question.
    """
    expected = {
        "C",
        "D",
        "E",
        "F",
        "G",
        "A",
        "B",
        "C♯",
        "D♯",
        "F♯",
        "G♯",
        "A♯",
        "C♭",
        "D♭",
        "E♭",
        "G♭",
        "A♭",
        "B♭",
    }
    for question in questions(
        30,
        keys=set(range(-7, 8)),
        modes={MAJOR, MINOR},
    ):
        assert set(question.choices) == expected
        assert question.grid is not None
        assert question.grid["G♯"] == (0, 4)
        assert question.grid["C"] == (1, 0)
        assert question.grid["B♭"] == (2, 6)
        refreshed = KeySignatures().refresh(question)
        assert set(refreshed.choices) == expected
        assert refreshed.grid == question.grid
