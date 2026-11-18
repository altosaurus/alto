"""
The circle of fifths and the exercise on it.

The circle itself (its twelve keys, its geometry and colors, and what it shows for each kind of question, a right answer and a
wrong one), the exercise with its three kinds of question, the answers that need two buttons, and the exercise screen.
"""

from __future__ import annotations

import random

import pytest
from PySide6.QtCore import QPointF
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QImage,
    QPainter,
)
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
)

from alto import settings
from alto.circle_schemes import (
    PRESETS,
    preset,
)
from alto.exercises import REGISTRY
from alto.exercises.base import Question
from alto.exercises.library import (
    MAJOR_CHOICES,
    MAJOR_GRID,
    MINOR_CHOICES,
    MINOR_GRID,
    NUMERAL_CHOICES,
    CircleOfFifths,
    NoteNames,
)
from alto.learning import (
    Database,
    Learner,
)
from alto.theory.fifths import (
    CELLS_OF_A_KEY,
    MAJORS,
    MINORS,
    NUMERALS,
    SIGNATURES,
    cells_of_key,
    display_major,
    display_minor,
    numeral_chords,
    place_of_major,
    relative_minor,
)
from alto.theory.pitch import (
    MAJOR_KEYS,
    Note,
)
from alto.theory.scales import mode_tonic
from alto.ui import circle as circle_module
from alto.ui import settings_panel as sp
from alto.ui.circle import (
    GLOW_MS,
    WRONG_COLOR,
    WRONG_MS,
    FifthsCircle,
    wedge_color,
    wedge_middle,
    wedge_path,
    write_text,
)
from alto.ui.exercise_view import (
    ExerciseView,
    choice_keys,
)
from alto.ui.home import (
    EXERCISE_ICONS,
    ExerciseCard,
)
from alto.ui.question_preview import QuestionPreview
from alto.ui.store import store
from keys import (
    opened,
    press,
)

KINDS = ("major", "minor", "numeral")


def pitch_class(name: str) -> int:
    """
    Return the pitch class of a key's name, from 0 for C.

    Parameters
    ----------
    name : str
        A key such as "A", "B♭" or "F♯m"; a trailing m is ignored.

    Returns
    -------
    int
        The semitones above C, from 0 to 11.
    """
    return Note.parse(name.removesuffix("m").replace("♯", "#").replace("♭", "b") + "4").midi % 12


def asked(
    kind: str | None = None,
    *,
    n: int = 240,
    seed: int = 1,
) -> list[Question]:
    """
    `n` questions made by the exercise, all of one kind or of every kind.

    Parameters
    ----------
    kind : str or None, default None
        "major", "minor" or "numeral"; every kind if None.
    n : int
        How many questions. Keyword-only.
    seed : int
        The random seed. Keyword-only.

    Returns
    -------
    list of Question
        The questions.
    """
    settings.circle.questions = {kind} if kind else set(settings.CIRCLE_QUESTIONS)
    rng = random.Random(seed)
    return [CircleOfFifths().generate(rng) for _ in range(n)]


def screen(
    kind: str,
    *,
    seed: int = 4,
) -> tuple[ExerciseView, Question]:
    """
    Make an exercise screen that asks one kind of question.

    Parameters
    ----------
    kind : str
        "major", "minor" or "numeral".
    seed : int
        The random seed. Keyword-only.

    Returns
    -------
    tuple of ExerciseView and Question
        The screen, and its first question.
    """
    settings.circle.questions = {kind}
    view = ExerciseView(CircleOfFifths(), rng=random.Random(seed))
    view.resize(900, 900)
    q = view.question
    assert q is not None and q.circle is not None
    return view, q


def finish(view: ExerciseView) -> None:
    """
    Stop the screen from going on to the next question by itself, so that a test can look at the one on screen.

    Parameters
    ----------
    view : ExerciseView
        The screen.
    """
    # noinspection PyProtectedMember
    view._advance.stop()


def button(
    view: ExerciseView,
    text: str,
) -> QPushButton:
    """
    Return the answer button with some text.

    Parameters
    ----------
    view : ExerciseView
        The screen.
    text : str
        The button's text.

    Returns
    -------
    QPushButton
        The button.
    """
    return next(b for b in view.buttons if b.text() == text)


def double_name_question(
    kind: str,
    *,
    seed: int = 4,
) -> tuple[ExerciseView, Question]:
    """
    Make a screen whose question is about a wedge that has two names, by asking until one comes up.

    Parameters
    ----------
    kind : str
        "major" or "minor".
    seed : int
        The random seed. Keyword-only.

    Returns
    -------
    tuple of ExerciseView and Question
        The screen, and its question, whose answer needs two buttons.

    Raises
    ------
    AssertionError
        If none comes up.
    """
    view, q = screen(kind, seed=seed)
    for _ in range(200):
        q = view.question
        assert q is not None
        if q.required:
            return view, q
        finish(view)
        view.next_question()
    raise AssertionError("no question with two names came up")


# -- the theory of the circle -----------------------------------------------------------------------------------------


def test_the_circle_has_twelve_places_each_a_fifth_above_the_one_before() -> None:
    """
    Check that there are twelve places, and that each major key is a fifth (seven semitones) above the one before it.
    """
    assert len(MAJORS) == len(MINORS) == len(SIGNATURES) == 12
    for place in range(12):
        nxt = (place + 1) % 12
        assert (pitch_class(MAJORS[nxt][0]) - pitch_class(MAJORS[place][0])) % 12 == 7, place
        assert (pitch_class(MINORS[nxt][0]) - pitch_class(MINORS[place][0])) % 12 == 7, place


def test_a_minor_is_the_relative_of_the_major_beside_it() -> None:
    """
    Check that each pair shares a key signature, and that the minor is three semitones below the major.

    The other name of a key must be the same key spelled another way.
    """
    for place, (majors, minors) in enumerate(zip(MAJORS, MINORS, strict=True)):
        count = SIGNATURES[place]
        assert MAJOR_KEYS[count] == majors[0], place
        assert mode_tonic(count, mode="Natural minor (Aeolian)").name + "m" == minors[0], place
        assert (pitch_class(majors[0]) - pitch_class(minors[0])) % 12 == 3, place
        assert {pitch_class(name) for name in majors} == {pitch_class(majors[0])}
        assert {pitch_class(name) for name in minors} == {pitch_class(minors[0])}


def test_the_signatures_go_up_by_one_to_the_right_and_down_to_the_left() -> None:
    """
    Check that the key signatures read 0 to 6 sharps clockwise and then 5 to 1 flats, as on the circle.
    """
    assert SIGNATURES == (0, 1, 2, 3, 4, 5, 6, -5, -4, -3, -2, -1)
    assert MAJORS[6] == ("F♯", "G♭") and MAJORS[5] == ("B", "C♭") and MAJORS[7] == ("D♭", "C♯")
    assert MINORS[5] == ("G♯m", "A♭m") and MINORS[6] == ("D♯m", "E♭m") and MINORS[7] == ("B♭m", "A♯m")


def test_a_key_is_found_by_either_of_its_names() -> None:
    """
    Check the lookups by name, and that an unknown key is refused.
    """
    assert [place_of_major(name) for name in ("C", "A", "B", "C♭", "F♯", "G♭", "D♭", "C♯", "F")] == [0, 3, 5, 5, 6, 6, 7, 7, 11]
    assert relative_minor("C") == "Am" and relative_minor("A") == "F♯m" and relative_minor("E♭") == "Cm"
    assert relative_minor("C♭") == "G♯m" and relative_minor("C♯") == "B♭m"
    with pytest.raises(ValueError, match="no major key"):
        place_of_major("H")


def test_a_key_is_written_out_for_a_question_with_both_names_when_it_has_two() -> None:
    """
    Check the way a pair is named in a question.
    """
    assert display_major(3) == "A major" and display_major(5) == "B major / C♭ major"
    assert display_minor(3) == "F♯ minor" and display_minor(7) == "B♭ minor / A♯ minor"


def test_the_six_chords_of_a_key_are_its_own_wedge_and_the_wedge_on_each_side_on_both_rings() -> None:
    """
    Check which cells hold I, ii, iii, IV, V and vi, as in the reference: IV to the left of the key and V to the right.
    """
    assert NUMERALS == ("I", "ii", "iii", "IV", "V", "vi")
    assert CELLS_OF_A_KEY[("outer", -1)] == "IV" and CELLS_OF_A_KEY[("outer", 1)] == "V" and CELLS_OF_A_KEY[("inner", 0)] == "vi"
    cells = cells_of_key(0)  # C major, as in the reference picture
    assert {cell: numeral for cell, numeral in cells.items()} == {
        ("outer", 11): "IV",  # F
        ("outer", 0): "I",  # C
        ("outer", 1): "V",  # G
        ("inner", 11): "ii",  # Dm
        ("inner", 0): "vi",  # Am
        ("inner", 1): "iii",  # Em
    }
    for key in range(12):
        around = cells_of_key(key)
        assert len(around) == 6 and sorted(around.values(), key=NUMERALS.index) == list(NUMERALS)
        assert {place for (_, place) in around} == {(key - 1) % 12, key, (key + 1) % 12}
        assert all(ring == "outer" for (ring, _), n in around.items() if n.isupper())  # capitals: major chords, the outer ring
        assert all(
            ring == "inner" for (ring, _), n in around.items() if n.islower()
        )  # small letters: minor chords, the inner ring


def test_the_chords_of_a_key_are_spelled_as_that_key_spells_them() -> None:
    """
    Check the chord names, including where a wedge has two names and the key decides which is right.
    """
    assert numeral_chords(0) == {"I": "C", "ii": "Dm", "iii": "Em", "IV": "F", "V": "G", "vi": "Am"}
    assert numeral_chords(6)["V"] == "C♯" and numeral_chords(7)["IV"] == "G♭" and numeral_chords(7)["V"] == "A♭"
    for key in range(12):
        chords = numeral_chords(key)
        for (ring, place), numeral in cells_of_key(key).items():
            names = MINORS[place] if ring == "inner" else MAJORS[place]
            assert chords[numeral] in names, (key, numeral)  # the chord is one of the names that cell carries


# -- the drawing ------------------------------------------------------------------------------------------------------


def test_each_wedge_is_30_degrees_clockwise_from_the_top() -> None:
    """
    Check that a point in the middle of each wedge is inside its own shape and no other, going clockwise from the top.
    """
    center = QPointF(200, 200)
    for index in range(12):
        shapes = [wedge_path(center=center, inner=100, outer=190, index=i) for i in range(12)]
        point = wedge_middle(center=center, radius=150, index=index)
        assert [shape.contains(point) for shape in shapes] == [i == index for i in range(12)], index
    assert wedge_middle(center=center, radius=100, index=0).y() < 200
    assert wedge_middle(center=center, radius=100, index=3).x() > 200
    assert wedge_middle(center=center, radius=100, index=6).y() > 200
    assert wedge_middle(center=center, radius=100, index=9).x() < 200


def test_in_the_spectrum_scheme_the_hues_go_once_round_the_color_wheel_from_red_at_the_top() -> None:
    """
    Check that the spectrum scheme's wedges have twelve different hues, red at the top, each brighter when lit.
    """
    spectrum = preset("spectrum")
    hues = [wedge_color(i, inner=False, scheme=spectrum).hue() for i in range(12)]
    assert hues[0] == 0 and hues == sorted(hues) and len(set(hues)) == 12
    for index in range(12):
        assert (
            wedge_color(index, inner=False, lift=1.0, scheme=spectrum).lightness()
            > wedge_color(index, inner=False, scheme=spectrum).lightness()
        )
        assert (
            wedge_color(index, inner=True, scheme=spectrum).lightness()
            < wedge_color(index, inner=False, scheme=spectrum).lightness()
        )


def test_the_circle_is_drawn_in_the_scheme_chosen_in_the_settings() -> None:
    """
    Check that a wedge without a scheme named takes the colors of the chosen one.
    """
    settings.circle.scheme = "spectrum"
    assert wedge_color(0, inner=False).hue() == 0
    settings.circle.scheme = "midnight"
    assert wedge_color(0, inner=False).hue() == round(222)


def test_no_lit_wedge_is_too_bright_for_white_names() -> None:
    """
    Check that every wedge, lit or quiet, looks no brighter than white text can be read on, whatever its hue.

    Yellows and greens look far brighter than blues at the same lightness, so they are brought down to the same level.
    """
    for scheme in (s for s in PRESETS.values() if not s.light):
        for index in range(12):
            for inner in (False, True):
                for lift in (0.0, 0.3, 0.5, 1.0):
                    c = wedge_color(index, inner=inner, lift=lift, scheme=scheme)
                    assert 0.299 * c.redF() + 0.587 * c.greenF() + 0.114 * c.blueF() <= 0.44, (scheme.key, index, inner, lift)


def test_a_wrong_answer_is_flashed_in_the_red_of_the_wrong_buttons() -> None:
    """
    Check that the cell flashes the same red as a wrong answer's button.
    """
    assert WRONG_COLOR.name() == "#c62828"


# -- the widget -------------------------------------------------------------------------------------------------------


def test_a_relative_major_question_shows_the_minors_and_asks_about_an_outer_cell(app: QApplication) -> None:
    """
    Check what the circle holds for a relative major question: every minor named, the major blank, the outer cell asked.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    circle = FifthsCircle()
    circle.show_question("major", place=3, title="F♯ minor")
    assert circle.target == ("outer", 3) and circle.shown == {"outer": set(), "inner": set(range(12))}
    assert circle.title == "F♯ minor" and circle.subtitle == "relative major?" and circle.signature is None
    assert circle.lit == set() and circle.numerals == {}
    assert "F♯m" in circle.accessibleDescription() and circle.accessibleName() == "Circle of fifths"
    assert circle.lift_of("outer", place=3) == 0.5 and circle.lift_of("inner", place=3) == 0.3  # the cell, and its pair
    assert circle.lift_of("outer", place=8) == 0.0
    circle.reset()
    assert circle.target is None and circle.title == "" and circle.shown == {"outer": set(), "inner": set()}


def test_a_relative_minor_question_shows_the_majors_and_asks_about_an_inner_cell(app: QApplication) -> None:
    """
    Check the other way around: every major named, the minor blank, and the inner cell is the one asked.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    circle = FifthsCircle()
    circle.show_question("minor", place=3, title="A major")
    assert circle.target == ("inner", 3) and circle.shown == {"outer": set(range(12)), "inner": set()}
    assert circle.subtitle == "relative minor?" and "relative minor" in circle.accessibleDescription()
    circle.reveal(animate=False)
    assert circle.shown["inner"] == {3} and circle.title == "F♯ minor" and circle.subtitle == "3 sharps" and circle.signature == 3


def test_a_numeral_question_lights_the_chords_of_the_key_and_shows_its_staff(app: QApplication) -> None:
    """
    Check that for a Roman numeral question the key's staff is in the middle at once and its six chords are lit.

    Every name is written but the numerals.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    circle = FifthsCircle()
    circle.show_question("numeral", place=11, ring="outer", key=0, title="C major")  # F, the IV of C
    assert (
        circle.lit == {11, 0, 1} and circle.signature == 0 and circle.title == "C major" and circle.subtitle == "Roman numeral?"
    )
    assert circle.shown == {"outer": set(range(12)), "inner": set(range(12))} and circle.numerals == {}
    assert circle.target == ("outer", 11)
    assert circle.lift_of("outer", place=0) == 0.38 and circle.lift_of("inner", place=1) == 0.38  # the others of the key are lit
    assert circle.lift_of("outer", place=5) == 0.0 and circle.lift_of("outer", place=11) == 0.5
    assert "F" in circle.accessibleDescription() and "Roman numeral" in circle.accessibleDescription()
    circle.reveal(animate=False)
    assert circle.numerals == cells_of_key(0) and circle.lift_of("outer", place=11) == 1.0
    assert "IV F" in circle.accessibleDescription() and "vi Am" in circle.accessibleDescription()


def test_a_right_answer_names_the_cell_and_shows_its_key_signature(app: QApplication) -> None:
    """
    Check that revealing writes the key in the middle with its signature, and brightens the cell gradually.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    circle = FifthsCircle()
    circle.show_question("major", place=3, title="F♯ minor")
    circle.reveal()
    assert circle.shown["outer"] == {3} and circle.title == "A major" and circle.subtitle == "3 sharps" and circle.signature == 3
    assert "A major" in circle.accessibleDescription() and "F♯m" in circle.accessibleDescription()
    assert circle._glow < 1.0
    QTest.qWait(GLOW_MS + 150)
    assert circle._glow == pytest.approx(1.0)
    flat = FifthsCircle()
    flat.show_question("major", place=7, title="B♭ minor")
    flat.reveal(animate=False)
    assert flat.title == "D♭ major" and flat.subtitle == "5 flats" and flat.signature == -5


def test_a_wrong_answer_flashes_the_cell_and_then_lets_it_go(app: QApplication) -> None:
    """
    Check that the warning shows at full strength on the right ring, fades, and is gone after its time.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for kind, ring in (("major", "outer"), ("minor", "inner")):
        circle = FifthsCircle()
        circle.show_question(kind, place=3, title="x")
        circle.flash_wrong()
        assert circle._warning == (ring, 3, 1.0)
        QTest.qWait(WRONG_MS // 2)
        assert circle._warning is not None and 0.0 < circle._warning[2] < 1.0
        QTest.qWait(WRONG_MS)
        assert circle._warning is None and circle.target == (ring, 3)


def test_nothing_flashes_when_nothing_is_asked(app: QApplication) -> None:
    """
    Check that a circle with no question has no cell to flash.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    nothing = FifthsCircle()
    nothing.flash_wrong()
    assert nothing._warning is None


def test_what_is_drawn_for_each_state(app: QApplication) -> None:
    """
    Check by looking at the pixels: the asked cell is lit, a wrong answer is the opposite color, a right one is brighter.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    settings.circle.scheme = "spectrum"
    circle = FifthsCircle()
    circle.resize(520, 520)
    # the red cell at the top, where the red flash has to be told apart by its stripes
    circle.show_question("major", place=0, title="A minor")
    center, radius = circle.geometry_of()
    spot = wedge_middle(center=center, radius=0.87 * radius, index=0)

    def color() -> QColor:
        """
        Return the color of the outer cell at the top, as drawn now.

        Returns
        -------
        QColor
            The pixel in the middle of the cell.
        """
        return circle.grab().toImage().pixelColor(int(spot.x()), int(spot.y()))

    asked_color = color()
    assert asked_color.hue() <= 8 or asked_color.hue() >= 352
    assert asked_color.lightness() > wedge_color(0, inner=False).lightness()
    circle._warning = ("outer", 0, 1.0)
    warned = color()
    assert abs(warned.red() - WRONG_COLOR.red()) < 12 and warned.green() < 70 and warned.blue() < 70, warned.name()
    assert warned != asked_color
    circle._warning = None
    circle.reveal(animate=False)
    lit = color()
    assert lit.hue() <= 8 or lit.hue() >= 352 and lit.lightness() > asked_color.lightness()  # brighter than when asked


def test_the_circle_is_square_and_fits_whatever_room_it_has(app: QApplication) -> None:
    """
    Check that the circle is centered, never bigger than the room, and that it draws at any size.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    circle = FifthsCircle()
    for width, height in ((300, 300), (700, 320), (320, 700), (900, 900)):
        circle.resize(width, height)
        center, radius = circle.geometry_of()
        side = float(min(width, height))
        assert center.toTuple() == (width / 2, height / 2) and radius <= side / 2
        assert not circle.grab().isNull()


# -- the exercise -----------------------------------------------------------------------------------------------------


def test_the_exercise_is_called_circle_of_fifths_and_is_silent() -> None:
    """
    Check its name, its group and that it makes no sound.
    """
    assert CircleOfFifths in REGISTRY and CircleOfFifths.name == "Circle of Fifths"
    assert CircleOfFifths.category == "Scales & keys" and CircleOfFifths.has_sound is False
    assert all(cls.name != "Relative Majors" for cls in REGISTRY)


def test_the_options_choose_the_kinds_of_question() -> None:
    """
    Check that each kind can be asked alone, that several can be mixed, and that none chosen means all of them.
    """
    for kind in KINDS:
        assert {q.circle_kind for q in asked(kind, n=60)} == {kind}
    assert {q.circle_kind for q in asked(n=300)} == set(KINDS)
    settings.circle.questions = {"major", "numeral"}
    rng = random.Random(3)
    assert {CircleOfFifths().generate(rng).circle_kind for _ in range(100)} == {"major", "numeral"}
    settings.circle.questions = set()
    assert settings.circle.active_questions() == list(KINDS)
    assert {CircleOfFifths().generate(rng).circle_kind for _ in range(100)} == set(KINDS)


def test_the_settings_signature_and_the_help_follow_the_options() -> None:
    """
    Check that a stored question is only asked again under the same options, and that the help follows them.
    """
    before = CircleOfFifths().settings_signature()
    settings.circle.questions = {"numeral"}
    assert CircleOfFifths().settings_signature() != before
    text = CircleOfFifths().instructions()
    assert "Roman numerals" in text and "Relative major" not in text and "Relative minor" not in text
    assert "vii°" in text and "Capitals are major chords" in text
    settings.circle.questions = {"major", "minor"}
    text = CircleOfFifths().instructions()
    assert "Relative major" in text and "Relative minor" in text and "Roman numerals" not in text
    assert "press both names" in text.lower() or "press both" in text.lower()


def test_a_relative_major_question_names_the_minor_and_wants_the_major() -> None:
    """
    Check every place comes up, that the minor named is the one on the circle, and what the answer and the buttons are.
    """
    questions = asked("major")
    assert {q.circle for q in questions} == set(range(12))
    for q in questions:
        assert q.circle is not None
        assert q.prompt.startswith(f"Which major key is the relative major of {display_minor(q.circle)}?")
        assert q.caption == f"{MINORS[q.circle][0][:-1]} minor" and q.circle_ring == "outer" and q.circle_key is None
        assert q.answer == MAJORS[q.circle][0] and q.choices == list(MAJOR_CHOICES) and q.grid == MAJOR_GRID
        assert not q.staff and not q.key and q.accept == ()


def test_a_relative_minor_question_names_the_major_and_wants_the_minor() -> None:
    """
    Check the same the other way around: the major named, the minor wanted, and the minor keys on the buttons.
    """
    questions = asked("minor")
    assert {q.circle for q in questions} == set(range(12))
    for q in questions:
        assert q.circle is not None
        assert q.prompt.startswith(f"Which minor key is the relative minor of {display_major(q.circle)}?")
        assert q.caption == f"{MAJORS[q.circle][0]} major" and q.circle_ring == "inner"
        assert q.answer == MINORS[q.circle][0] and q.choices == list(MINOR_CHOICES) and q.grid == MINOR_GRID


def test_a_key_with_two_names_needs_both_and_a_key_with_one_needs_just_that_one() -> None:
    """
    Check that B and C♭, F♯ and G♭, and D♭ and C♯ (and the minors G♯m and A♭m and the rest) are all needed, and no more.
    """
    for kind, names_of in (("major", MAJORS), ("minor", MINORS)):
        by_place = {q.circle: q for q in asked(kind)}
        for place, names in enumerate(names_of):
            q = by_place[place]
            if len(names) == 2:
                assert q.required == names and q.answer == names[0], (kind, place)
                assert "Press both of its names." in q.prompt
                assert not q.complete({names[0]}) and not q.complete({names[1]}) and q.complete(set(names))
                assert all(q.check(name) for name in names)  # each is right, but one is not enough
            else:
                assert q.required == () and "Press both" not in q.prompt, (kind, place)
                assert q.complete({names[0]})
            wrong = [c for c in q.choices if c not in names]
            assert not any(q.check(c) for c in wrong)


def test_a_numeral_question_names_a_chord_of_a_key_and_wants_its_numeral() -> None:
    """
    Check that every key and every one of its six chords comes up, with the chord spelled as the key spells it.
    """
    questions = asked("numeral", n=600)
    assert {q.circle_key for q in questions} == set(range(12))
    assert {(q.circle_key, q.circle_ring, q.circle) for q in questions} == {
        (key, ring, place) for key in range(12) for (ring, place) in cells_of_key(key)
    }
    for q in questions:
        assert q.circle is not None and q.circle_key is not None
        key = q.circle_key
        chords = numeral_chords(key)
        assert q.prompt == f"In {MAJORS[key][0]} major, which Roman numeral is the chord {chords[q.answer]}?"
        assert cells_of_key(key)[(q.circle_ring, q.circle)] == q.answer and q.answer in NUMERALS
        assert q.choices == NUMERAL_CHOICES and q.caption == f"{MAJORS[key][0]} major" and q.required == () and q.grid is None
        assert all(f"{n} {chords[n]}" in q.explanation for n in NUMERALS)
    assert any(q.circle_key == 6 and q.answer == "V" and "C♯" in q.prompt for q in questions)  # not D♭, in F♯ major


def test_a_numeral_is_a_capital_for_a_major_chord_and_small_for_a_minor_one() -> None:
    """
    Check that the outer ring asks for capitals and the inner ring for small letters, and no seventh chord is asked.
    """
    for q in asked("numeral", n=300):
        assert q.answer.isupper() == (q.circle_ring == "outer")
    assert "vii°" not in NUMERAL_CHOICES and len(NUMERAL_CHOICES) == 6


def test_the_minor_answers_are_laid_out_like_the_major_ones() -> None:
    """
    Check that there is a button for every minor key on the circle, letters in the middle row, sharps above, flats below.
    """
    assert sorted(MINOR_CHOICES) == sorted({name for names in MINORS for name in names})  # the fifteen names on the circle
    assert set(MINOR_GRID) == set(MINOR_CHOICES) and len(set(MINOR_GRID.values())) == 15
    assert sorted(n for n, (row, _) in MINOR_GRID.items() if row == 1) == sorted(f"{x}m" for x in "ABCDEFG")
    assert all("♯" in n for n, (row, _) in MINOR_GRID.items() if row == 0)
    assert all("♭" in n for n, (row, _) in MINOR_GRID.items() if row == 2)
    for name, (_, column) in MINOR_GRID.items():
        middle = [n for n, (r, c) in MINOR_GRID.items() if r == 1 and c == column]
        assert middle == [name[0] + "m"] or not middle, name


def test_the_answers_are_the_fifteen_major_keys_laid_out_like_a_piano() -> None:
    """
    Check that there is a button for every major key, the letters in the middle row, sharps above and flats below.
    """
    assert sorted(MAJOR_CHOICES) == sorted(MAJOR_KEYS.values())
    assert set(MAJOR_GRID) == set(MAJOR_CHOICES) and len(set(MAJOR_GRID.values())) == 15
    assert sorted(name for name, (row, _) in MAJOR_GRID.items() if row == 1) == list("ABCDEFG")
    assert all(name.endswith("♯") for name, (row, _) in MAJOR_GRID.items() if row == 0)
    assert all(name.endswith("♭") for name, (row, _) in MAJOR_GRID.items() if row == 2)


def test_a_question_comes_back_with_everything_it_needs() -> None:
    """
    Check that a stored question keeps its kind, ring, key and required answers, and that old ones have none.
    """
    for q in asked(n=60):
        again = Question.from_dict(q.to_dict())
        assert again == q and again.item_key() == q.item_key()
        assert again.required == q.required and again.circle_kind == q.circle_kind and again.circle_ring == q.circle_ring
    sample = next(q for q in asked("major") if q.required)
    old = {k: v for k, v in sample.to_dict().items() if k not in {"required", "circle_kind", "circle_ring", "circle_key"}}
    plain = Question.from_dict(old)
    assert plain.required == () and plain.circle_kind == "" and plain.circle_ring == "outer" and plain.circle_key is None
    keys = {q.item_key() for q in asked(n=2400)}
    assert len(keys) == 12 + 12 + 72  # a question for each place twice over, and each of six chords in each of twelve keys


def test_the_questions_that_need_several_answers_say_when_they_are_complete() -> None:
    """
    Check the rule that decides when all the answers are in.
    """
    both = Question("", choices=["B", "C♭", "D"], answer="B", required=("B", "C♭"))
    assert (
        not both.complete(set()) and not both.complete({"B"}) and both.complete({"B", "C♭"}) and both.complete({"C♭", "B", "x"})
    )
    one = Question("", choices=["B", "C"], answer="B")
    assert one.complete({"B"}) and not one.complete(set()) and not one.complete({"C"})


# -- the exercise screen ----------------------------------------------------------------------------------------------


@pytest.mark.parametrize("kind", KINDS)
def test_the_screen_shows_the_circle_for_each_kind_with_its_buttons_under_it(
    app: QApplication,
    kind: str,
) -> None:
    """
    Check that the circle is shown with the question in it and the right buttons, in the right grid, under it.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    kind : str
        The kind of question.
    """
    view, q = screen(kind)
    view.show()
    assert view.circle.isVisibleTo(view) and view.circle.kind == kind and view.circle.title == q.caption
    assert view.circle.target == (q.circle_ring, q.circle)
    assert not view.staff.isVisibleTo(view) and not view.fork.isVisibleTo(view) and view.prompt.isHidden()
    assert [b.text() for b in view.buttons] == q.choices
    if q.grid is not None:
        for name, (row, column) in q.grid.items():
            item = view.choice_box.itemAtPosition(row, column)
            assert item is not None
            widget = item.widget()
            assert isinstance(widget, QPushButton) and widget.text() == name
    other = ExerciseView(NoteNames(), rng=random.Random(4))
    other.show()
    assert not other.circle.isVisibleTo(other)


def test_a_right_answer_with_one_name_lights_the_cell_and_moves_on(app: QApplication) -> None:
    """
    Check that for a key with a single name one button answers: it scores, reveals the cell and goes on.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for kind in KINDS:
        view, first = screen(kind)
        for _ in range(60):
            first = view.question
            assert first is not None
            if not first.required:
                break
            finish(view)
            view.next_question()
        assert first is not None and first.circle is not None and not first.required
        before = view.correct
        button(view, first.answer).click()
        assert view.answered and view.correct == before + 1 and view.circle._glow >= 0.0
        if kind == "numeral":
            assert view.circle.numerals == cells_of_key(first.circle_key or 0)
        else:
            assert view.circle.shown[first.circle_ring] == {first.circle} or first.circle in view.circle.shown[first.circle_ring]
        finish(view)


def test_a_key_with_two_names_needs_two_buttons(app: QApplication) -> None:
    """
    Check that the first right name does not answer: its button is marked and switched off, and the circle asks for the other.

    Nothing is scored until the second is pressed.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    for kind in ("major", "minor"):
        view, q = double_name_question(kind)
        first, second = q.required
        button(view, first).click()
        assert not view.answered and not view.missed and not button(view, first).isEnabled()
        assert view.total == 0 and view.correct == 0  # nothing is scored on a half answer
        assert view.circle.subtitle == "and its other name"
        button(view, second).click()
        assert view.answered and not view.missed and (view.correct, view.total) == (1, 1)
        finish(view)


def test_the_two_names_can_be_pressed_in_either_order(app: QApplication) -> None:
    """
    Check that the second name first works just as well.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, q = double_name_question("major", seed=7)
    for name in reversed(q.required):
        button(view, name).click()
    assert view.answered and not view.missed and view.correct == 1
    finish(view)


def test_a_wrong_name_in_the_middle_of_two_misses_the_question_but_keeps_what_was_right(app: QApplication) -> None:
    """
    Check that a wrong button after a right one fails the first try, flashes the cell and keeps the right name marked.

    The question can then be finished.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, q = double_name_question("major")
    first, second = q.required
    button(view, first).click()
    wrong = next(b for b in view.buttons if b.text() not in q.required)
    wrong.click()
    assert view.missed and not view.answered and (view.total, view.correct, view.streak) == (1, 0, 0)
    assert view.circle._warning is not None and not wrong.isEnabled() and not button(view, first).isEnabled()
    QTest.qWait(WRONG_MS + 200)
    assert view.circle._warning is None and view.circle.target == ("outer", q.circle)
    button(view, second).click()
    assert view.answered and view.correct == 0 and view.total == 1  # only the first try counts toward the score
    finish(view)


def test_a_wrong_first_name_misses_at_once(app: QApplication) -> None:
    """
    Check that a wrong button as the very first press is a miss, as for any question.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, q = double_name_question("minor")
    wrong = next(b for b in view.buttons if b.text() not in q.required)
    wrong.click()
    assert view.missed and (view.total, view.correct) == (1, 0) and view.circle._warning is not None
    assert view.circle._warning[:2] == ("inner", q.circle)
    finish(view)


def test_a_two_name_answer_is_recorded_once_with_both_names(app: QApplication) -> None:
    """
    Check that the learner's history gets one attempt for the pair, not one for each press, naming both.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    db = Database()
    learner = Learner(db, profile=db.add_profile("Ada"))
    settings.circle.questions = {"major"}
    view = ExerciseView(CircleOfFifths(), rng=random.Random(4), learner=learner)
    view.resize(900, 900)
    for _ in range(200):
        q = view.question
        assert q is not None
        if q.required:
            break
        finish(view)
        view.next_question()
    q = view.question
    assert q is not None and q.required
    for name in q.required:
        button(view, name).click()
    finish(view)
    rows = db.conn.execute("SELECT answer, correct FROM attempts").fetchall()
    assert [(r[0], r[1]) for r in rows] == [(" ".join(q.required), 1)]


def test_a_numeral_question_flashes_the_ring_that_was_asked_and_shows_all_six_numerals_when_right(app: QApplication) -> None:
    """
    Check the Roman numeral screen: a wrong numeral flashes the cell asked, and the right one writes all six.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, q = screen("numeral")
    wrong = next(b for b in view.buttons if b.text() != q.answer)
    wrong.click()
    assert view.missed and view.circle._warning is not None and view.circle._warning[:2] == (q.circle_ring, q.circle)
    assert view.circle.signature == SIGNATURES[q.circle_key or 0]  # its staff was there all along
    QTest.qWait(WRONG_MS + 200)
    button(view, q.answer).click()
    assert view.answered and len(view.circle.numerals) == 6 and view.circle.numerals == cells_of_key(q.circle_key or 0)
    assert view.circle.subtitle == " ".join(NUMERALS)
    finish(view)


def test_a_wrong_answer_flashes_the_cell_and_can_be_tried_again(app: QApplication) -> None:
    """
    Check that a wrong button flashes the cell, counts against the first try, switches itself off, and leaves the rest.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view, q = screen("major")
    wrong = next(b for b in view.buttons if b.text() not in q.required and b.text() != q.answer)
    wrong.click()
    assert view.missed and not view.answered and (view.total, view.correct, view.streak) == (1, 0, 0)
    assert view.circle._warning is not None and view.circle._warning[:2] == ("outer", q.circle)
    assert not wrong.isEnabled() and view.circle.shown["outer"] == set()
    QTest.qWait(WRONG_MS + 200)
    assert view.circle._warning is None
    for name in q.required or (q.answer,):
        button(view, name).click()
    assert view.answered and view.correct == 0
    finish(view)


# -- keyboard ---------------------------------------------------------------------------------------------------------


def test_every_minor_key_has_its_own_key_on_the_keyboard() -> None:
    """
    Check that a minor key is typed like the major key of its name, and that no two keys of a set are the same.
    """
    keys = choice_keys(list(MINOR_CHOICES))
    assert len(set(keys)) == 15 and all(keys)
    assert dict(zip(MINOR_CHOICES, keys, strict=True)) == {
        "C♯m": "Shift+C",
        "D♯m": "Shift+D",
        "F♯m": "Shift+F",
        "G♯m": "Shift+G",
        "A♯m": "Shift+A",
        "Cm": "C",
        "Dm": "D",
        "Em": "E",
        "Fm": "F",
        "Gm": "G",
        "Am": "A",
        "Bm": "B",
        "E♭m": "Ctrl+E",
        "A♭m": "Ctrl+A",
        "B♭m": "Ctrl+B",
    }
    assert choice_keys(NUMERAL_CHOICES) == list("123456")


@pytest.mark.parametrize("kind", KINDS)
def test_each_kind_is_answered_from_the_keyboard_alone(
    app: QApplication,
    kind: str,
) -> None:
    """
    Check that the keys answer questions of each kind, pressing both keys of a key with two names.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    kind : str
        The kind of question.
    """
    settings.circle.questions = {kind}
    view = opened(CircleOfFifths(), seed=5)
    two = 0
    for _ in range(20):
        q = view.question
        assert q is not None
        keys = choice_keys(q.choices)
        for name in q.required or (q.answer,):
            press(view, keys[q.choices.index(name)])
        assert view.answered and not view.missed, q.prompt
        two += bool(q.required)
        finish(view)
        view.next_question()
    assert view.correct == 20 and (kind == "numeral" or two > 0)


# -- the options ------------------------------------------------------------------------------------------------------


def test_the_circle_has_a_settings_panel_with_the_three_kinds(app: QApplication) -> None:
    """
    Check that the exercise has a Questions page, that it changes and saves the setting, and that one kind always stays on.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    view = ExerciseView(CircleOfFifths(), rng=random.Random(4))
    pane = view.settings_panel
    assert isinstance(pane, sp.CircleSettingsPanel) and pane.stack.count() == 5
    assert pane.questions_row.value.text() == "3 of 3"
    assert list(pane.questions.boxes) == list(settings.CIRCLE_QUESTIONS)
    pane.questions.boxes["major"].setChecked(False)
    pane.questions.boxes["minor"].setChecked(False)
    assert settings.circle.questions == {"numeral"} and not pane.questions.boxes["numeral"].isEnabled()  # the last one stays
    assert store().value("circle/questions") == "numeral"
    assert view.question is not None and view.question.circle_kind == "numeral"  # a new question under the new options
    pane._refresh_summaries()
    assert pane.questions_row.value.text() == "1 of 3"
    settings.circle.questions = set(settings.CIRCLE_QUESTIONS)
    sp.load_circle()
    assert settings.circle.questions == {"numeral"}
    store().setValue("circle/questions", "minor,nonsense")
    sp.load_circle()
    assert settings.circle.questions == {"minor"}
    store().setValue("circle/questions", "nonsense")
    sp.load_circle()
    assert settings.circle.questions == {"minor"}  # nothing usable: what was there stays
    pane.questions_row.click()
    QTest.qWait(300)
    assert pane.stack.currentIndex() == 1


# -- the home page and the popup --------------------------------------------------------------------------------------


@pytest.mark.parametrize("kind", KINDS)
def test_the_stored_question_popup_shows_the_circle_with_its_answer(
    app: QApplication,
    kind: str,
) -> None:
    """
    Check that the popup for a stored question of each kind shows the circle, answered.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    kind : str
        The kind of question.
    """
    q = asked(kind, n=1)[0]
    dialog = QuestionPreview("Circle of Fifths", question=q)
    circles = dialog.findChildren(FifthsCircle)
    assert len(circles) == 1 and circles[0].kind == kind and circles[0].target == (q.circle_ring, q.circle)
    assert circles[0]._glow == 1.0 and dialog.grab().width() > 0
    if kind == "numeral":
        assert len(circles[0].numerals) == 6
    else:
        assert circles[0].signature is not None


def test_the_home_card_has_the_new_name_and_its_own_icon(app: QApplication) -> None:
    """
    Check the card says Circle of Fifths, has an icon of its own, and fits.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    """
    assert EXERCISE_ICONS["CircleOfFifths"] not in {EXERCISE_ICONS["ScaleIdentification"], EXERCISE_ICONS["KeySignatures"]}
    assert "RelativeMajors" not in EXERCISE_ICONS
    card = ExerciseCard(CircleOfFifths)
    card.show()
    app.processEvents()
    assert card.accessibleName().startswith("Circle of Fifths") and card.accessibleDescription() == CircleOfFifths.description
    for label in card.findChildren(QPushButton):
        assert label is not None


def test_a_sharp_or_flat_is_never_measured_in_the_text_font(
    app: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Check that only the letters of a name are measured with the text font, since it has no ♯ or ♭.

    Qt searches other fonts for a missing glyph, about 40 ms for each new size, and the width of a sign comes from the notation
    font anyway. Measuring them was what made the first look at the circle, and every resize of it, slow.

    Parameters
    ----------
    app : QApplication
        The shared Qt application.
    monkeypatch : pytest.MonkeyPatch
        Replaces the font metrics with one that records what it measures.
    """
    measured: list[str] = []

    class Recording(QFontMetricsF):
        """Font metrics that remember each text they measure."""

        # noinspection PyMethodOverriding
        def horizontalAdvance(self, text: str) -> float:  # noqa: N802
            """
            Measure a text and remember it.

            Parameters
            ----------
            text : str
                What to measure.

            Returns
            -------
            float
                The width.
            """
            measured.append(text)
            return super().horizontalAdvance(text)

    # noinspection PyUnresolvedReferences
    monkeypatch.setattr(circle_module, "QFontMetricsF", Recording)
    image = QImage(200, 100, QImage.Format.Format_ARGB32)
    painter = QPainter(image)
    write_text(painter, center=QPointF(100, 50), text="B♭m", pixels=23, weight=QFont.Weight.Bold, color=QColor("white"))
    painter.end()
    assert measured and not any(sign in text for text in measured for sign in "♯♭♮")
