"""
The exercise screen: a question, its answer buttons, the score, and a
pane of settings that slides in from the right.

One `ExerciseView` works for every exercise. It asks the exercise (or,
with a profile, the learner) for the next
`Question`, shows it as a staff, a keyboard or text, offers the answer
buttons, and records each answer.

Examples
--------
>>> from alto.exercises.library import NoteNames
>>> view = ExerciseView(
...     NoteNames(), rng=random.Random(1)
... )
>>> # noinspection PyUnresolvedReferences
>>> view.question.answer in [
...     button.text() for button in view.buttons
... ]
True
"""

from __future__ import annotations

import math
import random
import re
import sys
import time
from dataclasses import replace
from typing import TYPE_CHECKING

from fsrs import Rating
from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QObject,
    QPropertyAnimation,
    QSize,
    Qt,
    QTimer,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QGuiApplication,
    QHideEvent,
    QKeySequence,
    QMouseEvent,
    QPalette,
    QShortcut,
    QShowEvent,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QButtonGroup,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from alto import settings as app_settings
from alto.audio import DEFAULT_NOTE_GAP_MS, MELODIC_INTERVAL_GAP_MS, sounds
from alto.exercises.base import (
    ChoiceExercise,
    Exercise,
    PicturePosition,
    Question,
)
from alto.exercises.library import (
    BEAT_METERS,
    INTERVAL_INVERSION_PROMPTS,
    BeatConstruction,
    BeatIdentification,
    IntervalConstruction,
    IntervalNames,
    KeyboardIntervals,
    NotationIdentification,
    NoteNames,
    OrderOfKeys,
    RythmicEquations,
    ScaleConstruction,
    ScaleIdentification,
    beat_meter,
    beat_positions,
)
from alto.exercises.packs import PackExercise
from alto.learning import Learner
from alto.learning.calendar import (
    CALENDAR_SCHEDULERS,
    DEFAULT_SCHEDULER,
    ReviewInterval,
)
from alto.learning.learner import PracticeComplete
from alto.learning.practice_session import PracticeSession
from alto.settings import spell
from alto.theory.beat_placement import grade_beat_marks
from alto.theory.pitch import (
    ACCIDENTAL_SYMBOLS,
    QUALITY_NAMES,
    Interval,
    Note,
)
from alto.theory.scales import format_key_signature
from alto.ui import motion
from alto.ui.answer_bank import AnswerBank
from alto.ui.circle import FifthsCircle
from alto.ui.colors import CORRECT_ANSWER_COLOR, blend
from alto.ui.degree_text import (
    DegreeButton,
    DegreeLabel,
)
from alto.ui.fingerboard import FingerboardWidget
from alto.ui.icons import (
    BOOK,
    SLIDERS,
    SPEAKER_MUTED,
    SPEAKER_ON,
    set_palette_icon,
    set_svg_icon,
)
from alto.ui.key_fork import (
    MAX_ACCIDENTALS,
    KeyFork,
)
from alto.ui.keyboard import KeyboardWidget
from alto.ui.meter_staff import BeatPlacementStaff, MeterButton, MeterStaff
from alto.ui.midi_input import MidiInput
from alto.ui.pictures import (
    RHYTHM_SYMBOL_NAMES,
    ValuePictures,
    rhythm_picture,
    symbol_icon,
)
from alto.ui.reference import reference_panel_for
from alto.ui.settings_panel import settings_panel_for
from alto.ui.staff import (
    CORNER_RADIUS,
    MAX_STEP,
    StaffWidget,
    clef_targets,
    keyboard_key_staff,
)
from alto.ui.staff_input import (
    ClefInput,
    ScaleInput,
    SignatureInput,
    StaffInput,
)
from alto.ui.staff_playback import StaffPlayback
from alto.ui.widgets import HelpButton, PracticeCounts
from alto.ui.zoom import css, px

if TYPE_CHECKING:
    from collections.abc import Callable

# the time between the notes of a scale that plays after a right answer
SCALE_GAP_MS = 280


NOTE_CHOICE = re.compile(
    r"^[A-G][♯♭]?m?$",
    # an answer that is a note or key name: C, F♯, B♭, or a minor key
    # such
    # as F♯m
)
DEGREE_CHOICE = re.compile(r"^([♯♭𝄪𝄫]?)([1-7])$")
INTERVAL_QUALITY_SYMBOLS = {
    name: symbol for symbol, name in QUALITY_NAMES.items()
}


def choice_keys(choices: list[str]) -> list[str]:
    """
    Choose a key for each answer button, so that every answer can be
    given from the keyboard.

    Nine answers or fewer take the digits 1 to 9. More than that, as on
    the piano keyboard, take the notes' own names: the
    letter for a natural, Shift and the letter for a sharp, Ctrl and the
    letter for a flat. A minor key, such as F♯m, is
    typed the same way as the major key of its name. Any other long list
    takes 1 to 9
    and then 0, and the rest can be reached with Tab. Scale-degree banks
    use the degree digit, with Shift for a sharp,
    Ctrl for a flat, and Alt added for double alterations.

    Parameters
    ----------
    choices : list of str
        The answers, in the order of their buttons.

    Returns
    -------
    list of str
        A key for each answer, such as "3" or "Shift+C"; "" for an
        answer that has none.

    Examples
    --------
    >>> choice_keys(
    ...     ["major", "minor", "diminished"]
    ... )
    ['1', '2', '3']
    >>> choice_keys(
    ...     list("CDEFGAB") + ["C♯", "B♭"] + ["F♯"]
    ... )
    ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'Shift+C', 'Ctrl+B', 'Shift+F']
    >>> choice_keys([str(n) for n in range(12)])[8:]
    ['9', '0', '', '']
    """
    if len(choices) <= 9:
        return [str(i + 1) for i in range(len(choices))]
    function_degrees = {
        name: str(index)
        for index, name in enumerate(app_settings.DEGREE_FUNCTIONS, start=1)
    }
    degrees = []
    for choice in choices:
        plain = choice.replace("̂", "")
        sign = plain[0] if plain and plain[0] in "♯♭𝄪𝄫" else ""
        label = plain[len(sign) :]
        for alteration, prefix in app_settings.FUNCTION_ALTERATIONS.items():
            if prefix and plain.startswith(prefix):
                sign, label = (
                    ACCIDENTAL_SYMBOLS[alteration],
                    plain[len(prefix) :],
                )
                break
        degrees.append(
            DEGREE_CHOICE.fullmatch(sign + function_degrees.get(label, label)),
        )
    if all(degrees):
        modifiers = {
            "": "",
            "♯": "Shift+",
            "♭": "Ctrl+",
            "𝄪": "Alt+Shift+",
            "𝄫": "Alt+Ctrl+",
        }
        return [
            modifiers[match[1]] + match[2]
            for match in degrees
            if match is not None
        ]
    if all(NOTE_CHOICE.match(c) for c in choices):
        keys = []
        for c in choices:
            sign = (
                c[1] if len(c) > 1 and c[1] in "♯♭" else ""
            )  # a trailing m only says that the key is minor
            keys.append(
                c[0]
                if not sign
                else f"{'Shift' if sign == '♯' else 'Ctrl'}+{c[0]}",
            )
        return keys
    return [*"123456789", "0", *[""] * (len(choices) - 10)]


def second_row_keys(
    first: list[str],
    *,
    labels: list[str],
) -> list[str]:
    """
    Choose a key for each button of the second row of a two-part answer,
    such as the octave or the inversion.

    They must not be keys that the first row has. When the first row
    uses the digits the second row takes the home row,
    A S D F and so on; when the first row uses letters (the notes'
    names) it takes the digits, and an octave that is a single
    digit takes that digit.

    Parameters
    ----------
    first : list of str
        The keys of the first row, as `choice_keys` chose them.
    labels : list of str
        The text of each button of the second row. Keyword-only.

    Returns
    -------
    list of str
        A key for each button; "" for one that has none.

    Examples
    --------
    >>> second_row_keys(
    ...     ["1", "2", "3"],
    ...     labels=[
    ...         "root position",
    ...         "1st inversion",
    ...     ],
    ... )
    ['A', 'S']
    >>> second_row_keys(
    ...     ["C", "Shift+C"], labels=["3", "4", "5"]
    ... )
    ['3', '4', '5']
    """
    if any(k.split("+")[-1].isalpha() for k in first):
        return [
            label if label in "123456789" and len(label) == 1 else ""
            for label in labels
        ]
    return [*"ASDFGHJKL"][: len(labels)] + [""] * max(0, len(labels) - 9)


def note_name(
    note: Note,
    *,
    key: int | None = None,
    minor: bool = False,
) -> str:
    """
    Return a note's name as it is written, with its octave: F♯4.

    Parameters
    ----------
    note : Note
        The note.
    key : int or None, default None
        The major key signature for scale degrees. Without a key
        context, degrees fall back to letter names. Keyword-only.

    minor : bool, default False
        Use natural minor scale degrees. Keyword-only.

    Returns
    -------
    str
        The name in the naming the app is set to, then the octave
        number.

    Examples
    --------
    >>> note_name(Note.parse("F#4"))
    'F♯4'
    """
    naming = app_settings.note_names.naming
    if naming in app_settings.DEGREE_NAMINGS and key is None:
        naming = "letters"
    return spell(
        note,
        naming=naming,
        key=key or 0,
        octave=True,
        minor=minor,
    )


def note_words(
    note: Note,
    *,
    key: int | None = None,
    minor: bool = False,
) -> str:
    """
    Return a note's name in words, for a screen reader: "F sharp 4".

    Parameters
    ----------
    note : Note
        The note.
    key : int or None, default None
        The major key signature for scale degrees. Without a key
        context, use letter names. Keyword-only.

    minor : bool, default False
        Use natural minor scale degrees. Keyword-only.

    Returns
    -------
    str
        The letter, then "sharp", "flat" or "natural" if it has a sign,
        then the octave number.

    Examples
    --------
    >>> (
    ...     note_words(Note.parse("F#4")),
    ...     note_words(Note.parse("Bb3")),
    ...     note_words(Note.parse("C4")),
    ... )
    ('F sharp 4', 'B flat 3', 'C 4')
    """
    naming = app_settings.note_names.naming
    if naming in app_settings.DEGREE_NAMINGS and key is not None:
        if naming == "functions":
            return (
                f"{spell(note, naming=naming, key=key, minor=minor).lower()}"
                ", octave "
                f"{note.octave}"
            )
        degree = spell(note, naming="degrees", key=key, minor=minor).replace(
            "̂",
            "",
        )
        signs = {
            "♯": "sharp ",
            "♭": "flat ",
            "𝄪": "double sharp ",
            "𝄫": "double flat ",
        }
        label = f"degree {degree[-1]}"
        return f"{signs.get(degree[0], '')}{label}, octave {note.octave}"
    if naming in app_settings.DEGREE_NAMINGS:
        naming = "letters"
    plain = spell(Note(note.octave, letter=note.letter), naming=naming)
    sign = {
        -2: " double flat",
        -1: " flat",
        1: " sharp",
        2: " double sharp",
        0: "",
    }.get(note.accidental, "")
    return f"{plain}{sign} {note.octave}"


class ExerciseView(QWidget):
    """
    The screen for practicing one exercise.

    Attributes
    ----------
    PANE_WIDTH : int
        The width of the settings pane when it is open, in pixels.
    REFERENCE_WIDTH : int
        The width of the reference pane when it is open, in pixels.
    exercise : Exercise
        The exercise being practiced.
    learner : Learner or None
        Records every answer and chooses what to ask next; None asks at
        random.
    rng : random.Random
        The random number generator for new questions.
    session : PracticeSession
        Attempt count, score, and retry status for this exercise.
    correct : int
        Questions answered right on the first try.
    total : int
        Questions answered.
    streak : int
        Right answers in a row.
    question : Question or None
        The question on screen.
    answered : bool
        True once this showing is finished, including a miss in SM-2 or
        FSRS.
    missed : bool
        True once the question has been answered wrong, so it no longer
        counts toward the score.
    buttons : list of QPushButton
        The answer buttons on screen.
    settings_panel : ExerciseSettingsPanel
        The exercise's settings, including how to advance after a
        correct answer.
    staff : StaffWidget
        Shows the notes of a question.
    keyboard : KeyboardWidget
        Shows the key of a keyboard question.
    input_staff : StaffInput
        The staff to click, for "place this note" questions.
    clef_input : ClefInput
        The blank staff a clef is put on, for "place this clef"
        questions.
    scale_input : ScaleInput
        The staff to click, for "place the notes of this scale"
        questions.
    fork : KeyFork
        The fork to pick a key signature on, for "build this key
        signature" questions.
    answer_button : QPushButton
        Hands in what was built with the fork or placed on the scale
        staff.
    book_btn : QToolButton or None
        Opens the exercise's reference in a pane on the right; None for
        an exercise that has none.
    reference_pane : QFrame or None
        The pane that holds the reference.
    lesson_requested : Signal
        Emitted with a lesson's key when the reference pane's lesson
        button is pressed.
    shuffle_requested : Signal
        Emitted when answer feedback ends or Next is clicked during
        shuffled practice.

    Examples
    --------
    >>> from alto.exercises.library import NoteNames
    >>> view = ExerciseView(
    ...     NoteNames(), rng=random.Random(1)
    ... )
    >>> view.score.text()
    '0/0 (–)   streak 0'
    """

    # Forwards signal to open a lesson.
    lesson_requested = Signal(str)
    # Signal to advance the exercise on shuffle mode.
    shuffle_requested = Signal()

    # Right-hand pane width.
    PANE_WIDTH = 290
    # Right-hand reference pane width.
    REFERENCE_WIDTH = 400
    # the answer buttons are never spread wider than this, however wide
    # the window
    CHOICE_MAX_WIDTH = 760

    def __init__(
        self,
        exercise: Exercise,
        *,
        rng: random.Random | None = None,
        parent: QWidget | None = None,
        learner: Learner | None = None,
    ) -> None:
        """
        Build the screen and show the first question.

        Parameters
        ----------
        exercise : Exercise
            The exercise to practice.
        rng : random.Random or None, default None
            The random number generator; a fresh one if None.
            Keyword-only.
        parent : QWidget or None, default None
            The widget that owns the screen. Keyword-only.
        learner : Learner or None, default None
            Where to record answers and what to ask next; None asks at
            random and records nothing. Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     KeySignatures,
        ... )
        >>> view = ExerciseView(
        ...     KeySignatures(), rng=random.Random(2)
        ... )
        >>> # the exercise has settings behind the gear button
        >>> view.settings_panel is not None
        True
        """
        super().__init__(parent)
        self.exercise = exercise
        # records every answer and chooses what to ask next; None asks
        # at random
        self.learner = learner
        self.rng = rng or random.Random()
        self.session = PracticeSession()
        self.question: Question | None = None
        self.shuffle_answers = False
        self._clock = (
            time.monotonic()
        )  # when the last answer was given, or the question appeared
        self._timing_valid = True
        app = QGuiApplication.instance()
        assert isinstance(app, QGuiApplication)
        app.applicationStateChanged.connect(self._application_state_changed)
        # Saves the clock if the exercise is interrupted, to be resumed
        # later.
        self._hidden_at: float | int | None = None
        self._advance_remaining = -1

        self.score = QLabel()
        self._speed_previews: dict[Rating, ReviewInterval] | None = None
        self._review_preview: ReviewInterval | None = None
        self._self_grading = False
        self._rating_previews: dict[Rating, ReviewInterval] = {}
        self.review_interval = QLabel()
        self.review_interval.setToolTip("Next review after a correct answer")
        self.review_interval.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
        self.queue_counts = PracticeCounts()
        self.queue_counts.hide()
        self._count_timer = QTimer(self)
        self._count_timer.setInterval(30_000)
        self._count_timer.timeout.connect(self._refresh_queue_counts)
        self.prompt = DegreeLabel()
        self.prompt.setStyleSheet(css("font-size: 16pt;"))
        self.staff = StaffWidget(max_step=MAX_STEP)
        self.staff.interval_voices = exercise.interval_voices
        self._answer_playback = StaffPlayback(
            self,
            highlight=self._light_answer_notes,
        )
        self._immediate_playback = StaffPlayback(
            self,
        )  # Continues across questions and stops when the view closes.
        self.keyboard = KeyboardWidget()
        self.fingerboard = FingerboardWidget()
        self.circle = FifthsCircle()  # for questions on the circle of fifths
        self.fork = KeyFork()  # for 'build this key signature' questions
        self.fork.changed.connect(self._fork_changed)
        # Undo and Answer, under whatever is built: the fork, or the
        # scale on the staff
        self.answer_row = QWidget()
        answer_lay = QHBoxLayout(self.answer_row)
        answer_lay.setContentsMargins(0, 0, 0, 0)
        self.undo_button = QPushButton(
            "Undo",
        )  # takes back the last note or step of a scale
        self.undo_button.setMinimumHeight(px(40))
        motion.set_shortcut(self.undo_button, key="Backspace")
        self.undo_button.clicked.connect(self._undo_scale_note)
        self.place_button = QPushButton(
            "Place note",
        )  # puts the note at the caret on the staff, or marks the next step
        self.place_button.setMinimumHeight(px(40))
        # Return does the next thing: place, then Answer once everything
        # is placed
        motion.set_shortcut(self.place_button, key="Return")
        self.place_button.clicked.connect(self._place_here)
        self.answer_button = QPushButton(
            "Answer",
        )  # hands in the signature picked on the fork, or the scale placed
        self.answer_button.setMinimumHeight(px(40))
        motion.set_shortcut(self.answer_button, key="Return")
        self.answer_button.clicked.connect(self._answer)
        self.staff.installEventFilter(
            self,
        )  # the wheel over the music or Answer moves the fork's circle too
        self.answer_button.installEventFilter(self)
        answer_lay.addWidget(self.undo_button)
        answer_lay.addWidget(self.place_button, 1)
        answer_lay.addWidget(self.answer_button, 1)
        self.input_staff = StaffInput()  # for 'place this note' questions
        self.input_staff.placed.connect(self._place)
        self.input_staff.accidental_cycled.connect(self._cycle_accidental)
        self.input_staff.caret_moved.connect(self._update_placement_status)
        self.clef_input = ClefInput()  # for 'place this clef' questions
        self.clef_input.placed.connect(self._place_clef)
        self.clef_input.changed.connect(self._show_placement_rows)
        # a button for each clef symbol, under the staff, as another way
        # to choose one
        self.symbol_row = QWidget()
        symbol_lay = QHBoxLayout(self.symbol_row)
        symbol_lay.setContentsMargins(0, 0, 0, 0)
        symbol_lay.addStretch()
        self.symbol_group = QButtonGroup(self)
        self.symbol_buttons: dict[str, QPushButton] = {}
        for symbol in app_settings.CLEF_SYMBOLS:
            button = QPushButton()
            set_palette_icon(
                button,
                lambda palette, clef=symbol: symbol_icon(
                    clef,
                    color=palette.buttonText().color(),
                ),
            )
            button.setIconSize(QSize(px(56), px(56)))
            button.setAccessibleName(app_settings.CLEF_SYMBOL_NAMES[symbol])
            button.setCheckable(True)
            button.setMinimumHeight(px(68))
            button.setToolTip(
                f"{app_settings.CLEF_SYMBOL_NAMES[symbol]}"
                " (or turn the mouse wheel, or use Left and Right)",
            )
            button.clicked.connect(
                lambda _=False, chosen=symbol: self.clef_input.select(chosen),
            )
            self.symbol_group.addButton(button)
            self.symbol_buttons[symbol] = button
            symbol_lay.addWidget(button)
        symbol_lay.addStretch()
        self.scale_input = (
            SignatureInput()
            if isinstance(exercise, OrderOfKeys)
            else ScaleInput()
        )
        self.scale_input.notes_changed.connect(self._scale_changed)
        self.scale_input.accidental_cycled.connect(self._cycle_accidental)
        self.scale_input.accidental_stepped.connect(
            self._cycle_accidental,
        )  # the mouse wheel steps through them too
        self.scale_input.caret_moved.connect(self._update_placement_status)
        # says what the next click or key press will do, for those who
        # cannot see the staff
        self.place_status = DegreeLabel()
        self.place_status.setWordWrap(True)
        self.place_status.setAccessibleName("What to do next")
        self.pitch_row = (
            QWidget()
        )  # lower / higher, to move the note on the staff without the mouse
        prow_group = QVBoxLayout(self.pitch_row)
        prow_group.setContentsMargins(0, 0, 0, 0)
        prow_group.addWidget(QLabel("Note"))
        prow = QHBoxLayout()
        prow_group.addLayout(prow)
        prow.setContentsMargins(
            0,
            4,
            0,
            0,
        )
        self.pitch_buttons = {}
        for name, text, steps, tip in (
            ("octave_down", "Octave ↓", -7, "An octave lower (Page Down)"),
            ("lower", "Lower ↓", -1, "One line or space lower (Down arrow)"),
            ("higher", "Higher ↑", 1, "One line or space higher (Up arrow)"),
            ("octave_up", "Octave ↑", 7, "An octave higher (Page Up)"),
        ):
            b = QPushButton(text)
            b.setMinimumHeight(px(40))
            b.setToolTip(tip)
            b.setAccessibleName(tip.split(" (")[0])
            b.clicked.connect(lambda _=False, n=steps: self._move_caret(n))
            self.pitch_buttons[name] = b
            prow.addWidget(b, 1)
        self.accidental_row = (
            QWidget()
        )  # sharp / natural / flat, for questions that need an accidental
        arow_group = QVBoxLayout(self.accidental_row)
        arow_group.setContentsMargins(0, 0, 0, 0)
        arow_group.addWidget(QLabel("Accidental"))
        arow = QHBoxLayout()
        arow_group.addLayout(arow)
        arow.setContentsMargins(
            0,
            4,
            0,
            0,
        )
        self.accidental_group = QButtonGroup(self)
        self.accidental_group.setExclusive(False)
        self.accidental_buttons = {}
        signs = (
            (-2, -1, 0, 1, 2)
            if isinstance(exercise, IntervalConstruction)
            else (-1, 0, 1)
        )
        for acc in signs:
            symbol = ACCIDENTAL_SYMBOLS[acc] or "♮"
            b = QPushButton(symbol)
            b.setCheckable(True)
            b.setMinimumHeight(px(40))
            b.setStyleSheet(css("font-size: 15pt;"))
            b.clicked.connect(lambda _=False, a=acc: self._pick_accidental(a))
            key, word = {
                -2: ("Ctrl+-", "Double flat"),
                -1: ("-", "Flat"),
                0: ("0", "Natural"),
                1: ("+", "Sharp"),
                2: ("Ctrl++", "Double sharp"),
            }[acc]
            motion.set_shortcut(b, key=key)
            b.setToolTip(
                f"{word}"
                " (key "
                f"{key}"
                "; the Left and Right arrows step through the signs)",
            )
            b.setAccessibleName(word)
            self.accidental_buttons[acc] = b
            arow.addWidget(b, 1)
        self.step_row = (
            QWidget()
        )  # whole / half, for marking the steps between the notes of a scale
        srow_group = QVBoxLayout(self.step_row)
        srow_group.setContentsMargins(0, 0, 0, 0)
        srow_group.addWidget(QLabel("Step"))
        srow = QHBoxLayout()
        srow_group.addLayout(srow)
        srow.setContentsMargins(
            0,
            4,
            0,
            0,
        )
        self.step_group = QButtonGroup(self)
        self.step_buttons = {}
        for step, name in (("W", "Whole step"), ("H", "Half step")):
            b = QPushButton(step)
            b.setCheckable(True)
            b.setMinimumHeight(px(40))
            b.setToolTip(
                f"{name}"
                " (key "
                f"{step}"
                "; the arrow keys, the mouse wheel and a right click "
                "switch between them)",
            )
            b.setAccessibleName(name)
            motion.set_shortcut(b, key=step)
            b.setStyleSheet(css("font-size: 15pt; font-weight: bold;"))
            b.clicked.connect(
                lambda _=False, s=step: self.scale_input.set_pending_step(s),
            )
            self.step_group.addButton(b)
            self.step_buttons[step] = b
            srow.addWidget(b, 1)
        self.step_buttons["W"].setChecked(True)
        self.scale_input.step_selected.connect(self._show_step)
        self.key_staff = keyboard_key_staff()
        # holds the answer buttons, with room around them and a widest
        # it will be
        self.choice_area = QWidget()
        self.choice_area.setMaximumWidth(px(self.CHOICE_MAX_WIDTH))
        self.choice_box = QGridLayout(self.choice_area)
        self.choice_box.setContentsMargins(
            16,
            8,
            16,
            8,
        )
        self.choice_box.setSpacing(10)
        self.interval_answers = AnswerBank(
            show_all_rows=isinstance(exercise, RythmicEquations),
        )
        self.interval_answers.hide()
        # counts questions, so a pending 'try again' reset can tell it
        # is out of date
        self._pair_token = 0
        self.destroyed.connect(
            lambda: setattr(self, "_pair_token", -1),
        )  # invalidate queued playback callbacks on deletion
        self._pending: dict[str, tuple[str, QPushButton]] = {}
        self._found: set[str] = (
            set()
        )  # the right answers given so far to a question that needs several
        self._busy = False
        self._advance = QTimer(self)
        self._advance.setSingleShot(True)
        self._advance.setTimerType(Qt.TimerType.PreciseTimer)
        self._advance.timeout.connect(self._advance_question)
        self._anims: list[QVariantAnimation] = []

        reference = reference_panel_for(exercise)
        self._reference = reference
        self.reference_pane: QFrame | None = None
        if reference is not None:
            reference.lesson_requested.connect(self.lesson_requested)
        self.settings_panel = settings_panel_for(
            exercise,
            learner=self.learner,
        )
        main = QWidget()
        lay = QVBoxLayout(main)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(self._build_toolbar())
        self.prompt.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        self.prompt.setWordWrap(True)
        prompt_row = QHBoxLayout()
        prompt_row.addStretch(1)
        prompt_row.addWidget(self.prompt, 100)
        prompt_row.addStretch(1)
        lay.addLayout(prompt_row)
        rhythm_widget: QWidget | None = None
        if isinstance(self.exercise, RythmicEquations):
            self.rhythm_equation = QFrame()
            self.rhythm_equation.setObjectName("rhythmEquation")
            self.rhythm_equation.setStyleSheet(
                css(
                    "QFrame#rhythmEquation { background: white; "
                    "border-radius: "
                    f"{CORNER_RADIUS}"
                    "px; } "
                    "QFrame#rhythmEquation QLabel { color: black; }",
                ),
            )
            paper_palette = self.rhythm_equation.palette()
            paper_palette.setColor(QPalette.ColorRole.Text, QColor("black"))
            paper_palette.setColor(QPalette.ColorRole.Base, QColor("white"))
            self.rhythm_equation.setPalette(paper_palette)
            self.rhythm_terms = QHBoxLayout(self.rhythm_equation)
            self.rhythm_terms.setContentsMargins(
                px(24),
                px(16),
                px(24),
                px(16),
            )
            self.rhythm_terms.setSpacing(px(14))
            self.rhythm_terms.setSizeConstraint(
                QLayout.SizeConstraint.SetFixedSize,
            )
            rhythm_widget = self.rhythm_equation
        elif isinstance(self.exercise, (BeatConstruction, BeatIdentification)):
            if isinstance(self.exercise, BeatConstruction):
                self.beat_placement = BeatPlacementStaff()
                self.beat_placement.changed.connect(self._show_placement_rows)
                self.beat_placement.cursor_moved.connect(
                    lambda p: self.rhythm_scroll.ensureVisible(
                        round(p.x()),
                        round(p.y()),
                    ),
                )
                self.beat_staff = self.beat_placement
            else:
                self.beat_staff = MeterStaff()
            rhythm_widget = self.beat_staff
        if rhythm_widget is not None:
            self.rhythm_scroll = QScrollArea()
            self.rhythm_scroll.setFrameShape(QFrame.Shape.NoFrame)
            self.rhythm_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rhythm_scroll.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
            )
            self.rhythm_scroll.setWidgetResizable(
                isinstance(rhythm_widget, MeterStaff),
            )
            self.rhythm_scroll.setWidget(rhythm_widget)
            self.rhythm_scroll.viewport().setAutoFillBackground(False)
            rhythm_widget.installEventFilter(self)
            self.rhythm_scroll.installEventFilter(self)
            lay.addWidget(self.rhythm_scroll)
        placement_layout = lay
        if isinstance(self.scale_input, SignatureInput):
            signature_area = QWidget()
            placement_layout = QVBoxLayout(signature_area)
            placement_layout.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(
                signature_area,
                alignment=Qt.AlignmentFlag.AlignHCenter,
            )
        self._music_layout = QGridLayout()
        placement_layout.addLayout(self._music_layout)
        visuals = (
            self.staff,
            self.circle,
            self.fork,
            self.input_staff,
            self.scale_input,
            self.clef_input,
            self.key_staff,
        )
        for row, visual in enumerate(visuals):
            self._music_layout.addWidget(visual, row, 0)
        self._music_layout.addWidget(
            self.review_interval,
            0,
            1,
            -1,
            1,
            Qt.AlignmentFlag.AlignBottom,
        )
        placement_layout.addWidget(self.symbol_row)
        placement_layout.addWidget(self.place_status)
        placement_layout.addWidget(self.pitch_row)
        placement_layout.addWidget(self.accidental_row)
        placement_layout.addWidget(self.step_row)
        placement_layout.addWidget(self.answer_row)
        lay.addWidget(self.keyboard)
        lay.addWidget(self.fingerboard)
        self._keyboard_interval_row = QWidget()
        self._keyboard_interval_layout = QHBoxLayout(
            self._keyboard_interval_row,
        )
        self._keyboard_interval_layout.setContentsMargins(0, 0, 0, 0)
        self._keyboard_interval_row.installEventFilter(self)
        lay.addWidget(self._keyboard_interval_row)
        answers = QWidget()
        answers.setMaximumWidth(px(self.CHOICE_MAX_WIDTH))
        answer_layout = QVBoxLayout(answers)
        answer_layout.setContentsMargins(0, 0, 0, 0)
        self.quality_label = QLabel("Quality")
        answer_layout.addWidget(self.quality_label)
        answer_layout.addWidget(self.choice_area)
        answer_layout.addWidget(self.interval_answers)
        self.interval_label = QLabel("Interval")
        answer_layout.addWidget(self.interval_label)
        self.octave_row = (
            QWidget()
        )  # shown only when the answer has a second part
        self.octave_box = QHBoxLayout(self.octave_row)
        self.octave_box.setContentsMargins(0, 4, 0, 0)
        answer_layout.addWidget(self.octave_row)
        answer_row = QHBoxLayout()
        answer_row.addStretch(1)
        answer_row.addWidget(answers, 100)
        answer_row.addStretch(1)
        lay.addLayout(answer_row)
        self.rating_row = QWidget()
        grade_layout = QGridLayout(self.rating_row)
        grade_layout.setContentsMargins(0, 0, 0, 0)
        self.grade_controls: dict[Rating, tuple[QLabel, QPushButton]] = {}
        for column, grade in enumerate(
            (Rating.Hard, Rating.Good, Rating.Easy),
        ):
            label = QLabel()
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button = QPushButton(grade.name)
            label.setBuddy(button)
            grade_layout.addWidget(label, 0, column)
            grade_layout.addWidget(button, 1, column)
            button.clicked.connect(
                lambda _checked=False, rating=grade: self._apply_rating(
                    rating,
                ),
            )
            self.grade_controls[grade] = label, button
        lay.addWidget(self.rating_row, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.next_button = QPushButton("Next")
        self.next_button.setMinimumHeight(px(40))
        motion.set_shortcut(self.next_button, key="Return")
        self.next_button.clicked.connect(self._advance_question)
        lay.addWidget(
            self.next_button,
            alignment=Qt.AlignmentFlag.AlignHCenter,
        )
        lay.addStretch()
        outer = QHBoxLayout(self)
        outer.addWidget(main, 1)
        if self.settings_panel:
            # Collapsible pane on the right, toggled by the gear.
            self.pane = QFrame()
            self.pane.setObjectName("settingsPane")
            self.pane.setFrameShape(QFrame.Shape.StyledPanel)
            self.pane.setMinimumWidth(0)
            self.pane.setMaximumWidth(0)
            pane_lay = QVBoxLayout(self.pane)
            pane_lay.setSizeConstraint(
                QLayout.SizeConstraint.SetNoConstraint,
            )  # let the pane shrink to zero while animating
            settings_header = QHBoxLayout()
            settings_header.addStretch()
            self.settings_collapse = QToolButton()
            self.settings_collapse.setText("−")
            self.settings_collapse.setAutoRaise(True)
            self.settings_collapse.setToolTip("Collapse exercise settings")
            self.settings_collapse.setAccessibleName(
                "Collapse exercise settings",
            )
            self.settings_collapse.clicked.connect(
                lambda: self.gear.setChecked(False),
            )
            settings_header.addWidget(self.settings_collapse)
            pane_lay.addLayout(settings_header)
            self.settings_panel.setFixedWidth(px(self.PANE_WIDTH - 2 * 9))
            pane_lay.addWidget(
                self.settings_panel,
                1,
            )  # fill the pane so long pages (Range) can scroll
            self.pane.hide()
            outer.addWidget(self.pane)
            self._pane_anim = QPropertyAnimation(
                self.pane,
                b"maximumWidth",
                self,
            )
            self._pane_anim.setDuration(220)
            self._pane_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._pane_anim.finished.connect(self._pane_settled)
            self.gear.toggled.connect(self._toggle_pane)
            self.settings_panel.changed.connect(
                self.next_question,
            )  # apply new settings right away
            self.settings_panel.restyled.connect(
                self.circle.update,
            )  # a new look keeps the question
            self.settings_panel.restyled.connect(self._redraw_keyboards)
        book = self.book_btn
        if reference is not None and book is not None:
            ref_pane = QFrame()
            ref_pane.setObjectName("settingsPane")
            ref_pane.setFrameShape(QFrame.Shape.StyledPanel)
            ref_pane.setMinimumWidth(0)
            ref_pane.setMaximumWidth(0)
            book_lay = QVBoxLayout(ref_pane)
            book_lay.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
            reference_header = QHBoxLayout()
            reference_header.addStretch()
            self.reference_collapse = QToolButton()
            self.reference_collapse.setText("−")
            self.reference_collapse.setAutoRaise(True)
            self.reference_collapse.setToolTip("Collapse reference")
            self.reference_collapse.setAccessibleName("Collapse reference")
            self.reference_collapse.clicked.connect(
                lambda: book.setChecked(False),
            )
            reference_header.addWidget(self.reference_collapse)
            book_lay.addLayout(reference_header)
            reference.setFixedWidth(px(self.REFERENCE_WIDTH - 2 * 9))
            book_lay.addWidget(reference, 1)
            ref_pane.hide()
            outer.addWidget(ref_pane)
            self.reference_pane = ref_pane
            self._reference_anim = QPropertyAnimation(
                ref_pane,
                b"maximumWidth",
                self,
            )
            self._reference_anim.setDuration(220)
            self._reference_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._reference_anim.finished.connect(self._reference_settled)
        self.buttons: list[QPushButton] = []
        self._arrow_keys = [
            self._bind(
                sequence,
                action=lambda action_name=name: self._key_action(action_name),
            )
            for sequence, name in (
                ("Up", "up"),
                ("Down", "down"),
                ("Left", "left"),
                ("Right", "right"),
                ("PgUp", "pageup"),
                ("PgDown", "pagedown"),
                ("Home", "home"),
            )
        ]
        self._letter_keys = [
            self._bind(
                name,
                action=lambda letter=letter: self._jump_to_letter(letter),
            )
            for letter, name in enumerate(
                "CDEFGAB",
            )  # C is 0, D is 1 ... B is 6, as a note's letter counts
        ]
        self.setFocusPolicy(
            Qt.FocusPolicy.ClickFocus,
        )  # the screen can be given the keyboard when it opens
        self.next_question()

    def _build_toolbar(self) -> QHBoxLayout:
        """
        Build the row of exercise controls above the staff.

        Returns
        -------
        QHBoxLayout
            The row to add to the exercise's main layout.

        Examples
        --------
        Note Identification shows its score and help button in this row.
        """
        top = QHBoxLayout()
        self.lesson_back_button = QPushButton("← Back to lesson")
        self.lesson_back_button.hide()
        top.addWidget(self.lesson_back_button)
        top.addStretch()
        top.addWidget(self.queue_counts)
        top.addWidget(self.score)
        self.help_btn = HelpButton(self.exercise.instructions)
        top.addWidget(self.help_btn)
        self.book_btn: QToolButton | None = None
        if self._reference is not None:
            book = QToolButton()
            set_svg_icon(book, BOOK)
            book.setIconSize(QSize(px(24), px(24)))
            book.setCheckable(True)
            book.setAutoRaise(True)
            book.setToolTip("Reference")
            book.setAccessibleName("Reference")
            book.toggled.connect(self._toggle_reference)
            top.addWidget(book)
            self.book_btn = book
        self.midi_input = None
        if isinstance(
            self.exercise,
            (NoteNames, IntervalConstruction, ScaleConstruction),
        ) and sys.platform.startswith("linux"):
            self.midi_input = MidiInput()
            self.midi_input.note_pressed.connect(self._place_midi)
            top.addWidget(self.midi_input)
        self.sound_btn = QToolButton()
        self.sound_btn.setAutoRaise(True)
        self.sound_btn.setIconSize(QSize(px(24), px(24)))
        self.sound_btn.clicked.connect(self._toggle_sound)
        self._show_sound_state()
        top.addWidget(self.sound_btn)
        if self.settings_panel:
            self.gear = QToolButton()
            set_svg_icon(self.gear, SLIDERS)
            self.gear.setIconSize(QSize(px(24), px(24)))
            self.gear.setCheckable(True)
            self.gear.setAutoRaise(True)
            self.gear.setToolTip("Exercise settings")
            self.gear.setAccessibleName("Exercise settings")
            top.addWidget(self.gear)
        return top

    @property
    def answered(self) -> bool:
        """
        Read the current question's status from the practice session.

        Returns
        -------
        bool
            Whether this question is finished.

        Examples
        --------
        >>> ExerciseView(NoteNames()).answered
        False
        """
        return self.session.answered

    @property
    def missed(self) -> bool:
        """
        Read the current question's status from the practice session.

        Returns
        -------
        bool
            Whether an attempt on this question was incorrect.

        Examples
        --------
        >>> ExerciseView(NoteNames()).missed
        False
        """
        return self.session.missed

    @property
    def total(self) -> int:
        """
        Read the exercise score from the practice session.

        Returns
        -------
        int
            Questions scored in this exercise.

        Examples
        --------
        >>> ExerciseView(NoteNames()).total
        0
        """
        return self.session.total

    @property
    def correct(self) -> int:
        """
        Read the exercise score from the practice session.

        Returns
        -------
        int
            Questions answered correctly on the first attempt.

        Examples
        --------
        >>> ExerciseView(NoteNames()).correct
        0
        """
        return self.session.correct

    @property
    def streak(self) -> int:
        """
        Read the exercise score from the practice session.

        Returns
        -------
        int
            Consecutive correct first attempts.

        Examples
        --------
        >>> ExerciseView(NoteNames()).streak
        0
        """
        return self.session.streak

    def _application_state_changed(self, state: Qt.ApplicationState) -> None:
        """
        Exclude the current presentation from speed grading if practice
        is interrupted.

        Parameters
        ----------
        state : Qt.ApplicationState
            New application activation state.

        Examples
        --------
        Switching to another application while a question is visible
        invalidates its timing.
        """
        if state != Qt.ApplicationState.ApplicationActive:
            self._timing_valid = False

    def hideEvent(self, event: QHideEvent) -> None:
        """
        Pause automatic advancement and answer timing while browsing
        another page.

        Parameters
        ----------
        event : QHideEvent
            The notification that the exercise is being hidden.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(NoteNames())
        >>> view.show()
        >>> view.hide()
        >>> view._advance.isActive()
        False
        """
        self._count_timer.stop()
        if self.midi_input is not None:
            self.midi_input.disconnect_port()
        if self._hidden_at is None:
            self._timing_valid = False
            self._hidden_at = time.monotonic()
            self._advance_remaining = self._advance.remainingTime()
            self._advance.stop()
        super().hideEvent(event)

    def showEvent(self, event: QShowEvent) -> None:
        """
        Resume the exercise's answer clock and pending advance when it
        reappears.

        Parameters
        ----------
        event : QShowEvent
            The notification that the exercise is visible again.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(NoteNames())
        >>> view.show()
        >>> view.hide()
        >>> view.show()
        >>> view._hidden_at is None
        True
        """
        if self._hidden_at is not None:
            self._clock += time.monotonic() - self._hidden_at
            self._hidden_at = None
            if self._advance_remaining >= 0:
                motion.start_timer(
                    self._advance,
                    delay=max(1, self._advance_remaining),
                )
            self._advance_remaining = -1
        if self.learner and (
            self._scheduler_mode != self.learner.mode or self.question is None
        ):
            self.next_question()
        else:
            self._refresh_queue_counts()
        super().showEvent(event)

    def _bind(
        self,
        sequence: str,
        *,
        action: Callable[[], object],
    ) -> QShortcut:
        """
        Bind a key to something to do, for as long as the keyboard is
        anywhere on this screen.

        The key is off until it is switched on, so that it only works
        for the questions that use it. It does not work while
        the keyboard is in the exercise list or elsewhere outside the
        screen, where the same keys do other things.

        Parameters
        ----------
        sequence : str
            The key, such as "Up" or "C".
        action : callable
            What to do when it is pressed. Keyword-only.

        Returns
        -------
        QShortcut
            The binding, which starts off.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> bound = view._bind(
        ...     "Up", action=lambda: None
        ... )
        >>> bound.isEnabled(), bound.key().toString()
        (False, 'Up')
        """
        binding = QShortcut(QKeySequence(sequence), self)
        binding.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        binding.setEnabled(False)
        binding.activated.connect(action)
        return binding

    def _toggle_sound(self) -> None:
        """
        Switch the app's sound on or off and show the button to match.

        The sound button is a mute for the whole app, so this changes
        `sounds.enabled`, not just this exercise.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> before = sounds.enabled
        >>> view._toggle_sound()
        >>> sounds.enabled == (not before)
        True
        >>> view._toggle_sound()
        """
        sounds.enabled = not sounds.enabled
        self._show_sound_state()

    def _show_sound_state(self) -> None:
        """
        Show the sound button's icon and tooltip for whether sound is
        on.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> view._show_sound_state()
        >>> view.sound_btn.toolTip().startswith(
        ...     ("Sound on", "Muted")
        ... )
        True
        """
        set_svg_icon(
            self.sound_btn,
            SPEAKER_ON if sounds.enabled else SPEAKER_MUTED,
        )
        self.sound_btn.setToolTip(
            "Sound on (click to mute)"
            if sounds.enabled
            else "Muted (click to unmute)",
        )
        self.sound_btn.setAccessibleName(
            "Sound on" if sounds.enabled else "Sound muted",
        )

    def settings_state(self) -> tuple[bool, int, int] | None:
        """
        Remember the exercise settings pane, selected page, and scroll
        position before a theme rebuild.

        Returns
        -------
        tuple of (bool, int, int) or None
            Whether the pane is open, its page index, and its vertical
            scroll position; None without settings.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... ).settings_state()
        (False, 0, 0)
        """
        panel = self.settings_panel
        if panel is None or self.gear is None:
            return None
        stack = panel.findChild(QStackedWidget)
        page = stack.currentWidget() if stack is not None else panel
        scroll = page.findChild(QScrollArea) if page is not None else None
        return (
            self.gear.isChecked(),
            stack.currentIndex() if stack is not None else 0,
            (scroll.verticalScrollBar().value() if scroll is not None else 0),
        )

    def restore_settings_state(self, state: tuple[bool, int, int]) -> None:
        """
        Restore exercise settings navigation immediately after
        rebuilding the view.

        Parameters
        ----------
        state : tuple of (bool, int, int)
            Whether the pane was open, the selected page, and its
            vertical scroll position.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> view.restore_settings_state((True, 0, 0))
        >>> view.settings_state()
        (True, 0, 0)
        """
        panel = self.settings_panel
        if panel is None or self.gear is None:
            return
        open_, index, position = state
        stack = panel.findChild(QStackedWidget)
        if stack is not None and 0 <= index < stack.count():
            stack.setCurrentIndex(index)
        self.gear.setChecked(open_)
        self._pane_anim.stop()
        self.pane.setMaximumWidth(px(self.PANE_WIDTH) if open_ else 0)
        self.pane.setVisible(open_)
        page = stack.currentWidget() if stack is not None else panel
        scroll = page.findChild(QScrollArea) if page is not None else None
        if scroll is not None:
            bar = scroll.verticalScrollBar()
            QTimer.singleShot(0, scroll, lambda: bar.setValue(position))

    def _toggle_pane(self, open_: bool) -> None:
        """
        Slide the settings pane open or closed.

        Parameters
        ----------
        open_ : bool
            True to open it, False to close it.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> view._toggle_pane(True)
        >>> view._pane_anim.endValue()
        290
        """
        if open_ and self.book_btn is not None:
            self.book_btn.setChecked(
                False,
            )  # the two panes share the right-hand side
        self._pane_anim.stop()
        self.pane.show()
        self._pane_anim.setStartValue(self.pane.maximumWidth())
        self._pane_anim.setEndValue(px(self.PANE_WIDTH) if open_ else 0)
        self._pane_anim.start()

    def _pane_settled(self) -> None:
        """
        Hide the pane once it has finished sliding shut.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> view._pane_settled()  # the pane starts closed
        >>> view.pane.isVisible()
        False
        """
        if self.pane.maximumWidth() == 0:
            self.pane.hide()

    def _toggle_reference(self, open_: bool) -> None:
        """
        Slide the reference pane open or closed.

        Opening it closes the settings pane, as they share the
        right-hand side.

        Parameters
        ----------
        open_ : bool
            True to open it, False to close it.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     CircleOfFifths,
        ... )
        >>> view = ExerciseView(
        ...     CircleOfFifths(), rng=random.Random(1)
        ... )
        >>> view._toggle_reference(True)
        >>> view._reference_anim.endValue()
        400
        """
        if open_ and self.settings_panel:
            self.gear.setChecked(False)
        pane = self.reference_pane
        if pane is None:
            return
        self._reference_anim.stop()
        pane.show()
        self._reference_anim.setStartValue(pane.maximumWidth())
        self._reference_anim.setEndValue(
            px(self.REFERENCE_WIDTH) if open_ else 0,
        )
        self._reference_anim.start()

    def _reference_settled(self) -> None:
        """
        Hide the reference pane once it has finished sliding shut.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     CircleOfFifths,
        ... )
        >>> view = ExerciseView(
        ...     CircleOfFifths(), rng=random.Random(1)
        ... )
        >>> view._reference_settled()  # the pane starts closed
        >>> (
        ...     view.reference_pane is not None
        ...     and view.reference_pane.isVisible()
        ... )
        False
        """
        if (
            self.reference_pane is not None
            and self.reference_pane.maximumWidth() == 0
        ):
            self.reference_pane.hide()

    def _pick_question(self) -> Question:
        """
        Choose the next question.

        Returns
        -------
        Question
            One drawn by what the learner needs, or at random without a
            profile. The one just asked is avoided.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> isinstance(view._pick_question(), Question)
        True
        """
        if self.learner is None:
            return self.exercise.generate(self.rng)
        avoid = self.question.item_key() if self.question else None
        if self._scheduler_mode in CALENDAR_SCHEDULERS and not self.missed:
            avoid = None
        return self.learner.pick(self.exercise, rng=self.rng, avoid=avoid)

    def scheduling_changed(self) -> None:
        """
        Refresh the visible exercise or invalidate its queue until it is
        reopened.

        Examples
        --------
        Lowering the daily allowance on the home page also applies to a
        previously opened exercise.
        """
        if self.isVisible():
            self.next_question()
        else:
            # showEvent rechecks the budget without drawing a hidden
            # card.
            self._scheduler_mode = ""

    def _advance_question(self) -> None:
        """
        Advance a graded answer in shuffle mode or draw the next
        question locally.

        Examples
        --------
        A calendar retry timer checks the current exercise again when no
        question is on screen.
        """
        if self._rating_previews:
            return
        if (
            self.shuffle_answers
            and self.answered
            and self.question is not None
        ):
            self.shuffle_requested.emit()
        else:
            self.next_question()

    def _rhythm_term(self, token: str) -> QWidget:
        """
        Render a note, number, sign, or blank on the equation paper.

        Parameters
        ----------
        token : str
            One term in the printed equation.

        Returns
        -------
        QWidget
            The symbol picture or text label for this term.

        Examples
        --------
        >>> ExerciseView(RythmicEquations())._rhythm_term("2").text()
        '2'
        """
        picture = rhythm_picture(token)
        if picture is not None:
            picture.setPalette(self.rhythm_equation.palette())
            return picture
        label = QLabel("□" if token == "_" else token)
        label.setStyleSheet(css("font-size: 22pt;"))
        return label

    def next_question(self) -> None:
        """
        Show the next question: its staff, keyboard or text, and a fresh
        set of answer buttons.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> view.next_question()
        >>> # noinspection PyUnresolvedReferences
        >>> (
        ...     view.answered,
        ...     len(view.buttons)
        ...     == len(view.question.choices),
        ... )
        (False, True)
        """
        self._answer_playback.stop()
        self._advance.stop()
        self._advance_remaining = -1
        # a fade still running would color buttons that are about to be
        # replaced
        for animation in self._anims:
            animation.stop()
            animation.deleteLater()
        self._anims.clear()
        self.next_button.hide()
        self.answer_button.setStyleSheet("")
        self.place_button.setStyleSheet("")
        self._scheduler_mode = (
            self.learner.mode if self.learner else DEFAULT_SCHEDULER
        )
        self._self_grading = (
            self.learner is not None
            and self._scheduler_mode in CALENDAR_SCHEDULERS
            and self.learner.self_grading
        )
        self.settings_panel.refresh_limits(
            self._scheduler_mode,
            self_grading=self._self_grading,
        )
        self._rating_previews.clear()
        self.rating_row.hide()
        empty_sample = None
        try:
            q = self._pick_question()
        except PracticeComplete as empty:
            empty_sample = self.exercise.generate(self.rng)
            message = "You’re caught up for now."
            if empty.retry_at is not None:
                clock = time.strftime(
                    "%H:%M:%S",
                    time.localtime(empty.retry_at),
                )
                message = (
                    f"Next review at {clock}."
                    if self._self_grading
                    or (
                        self.learner
                        and self.learner.response_times(
                            type(self.exercise).__name__,
                        ).ready
                    )
                    else (
                        "Waiting for a missed card. Practice resumes at "
                        f"{clock}"
                        "."
                    )
                )
                self._advance.start(
                    max(1, math.ceil((empty.retry_at - time.time()) * 1000)),
                )
            q = (
                Question(message, choices=[], answer="")
                if empty_sample.answer
                else empty_sample
            )
        self.question = q
        self.next_button.setText("Next")
        if (
            self.settings_panel is not None
            and self.settings_panel.choice_buttons_row is not None
        ):
            self.settings_panel.choice_buttons_row.setVisible(
                bool(q.choices)
                or (empty_sample is not None and bool(empty_sample.choices)),
            )
        self.session = self.session.new_question(
            available=empty_sample is None,
        )
        self._clock = time.monotonic()
        self._timing_valid = True
        self._pair_token += 1  # cancels a pending 'try again' reset
        # 'name' / 'octave' -> (text, button), for two-part answers
        self._pending = {}
        self._busy = False
        self.staff.column_colors.clear()
        prompt = q.prompt
        if (
            isinstance(self.exercise, NoteNames)
            and q.staff
            and not q.identify_scale
            and app_settings.note_names.naming in app_settings.DEGREE_NAMINGS
        ):
            prompt = self.exercise.card_prompt(q)
        self.prompt.setText(prompt)
        self.prompt.setVisible(
            bool(prompt) and not q.caption,
        )  # some need none; a caption goes on the staff
        if isinstance(self.exercise, RythmicEquations):
            while self.rhythm_terms.count():
                item = self.rhythm_terms.takeAt(0)
                if item is not None and (widget := item.widget()) is not None:
                    widget.hide()
                    widget.deleteLater()
            self.rhythm_scroll.setVisible(bool(q.choices))
            if q.choices:
                self.prompt.setText(q.caption)
                self.prompt.setVisible(bool(q.caption))
                self.rhythm_equation.setAccessibleName(
                    " ".join(
                        "blank" if token == "_" else token
                        for token in q.prompt.split()
                    )
                    .replace("~", " tied to ")
                    .replace("|", " beamed with "),
                )
                for term in q.prompt.split():
                    self.rhythm_terms.addWidget(
                        self._rhythm_term(term),
                        alignment=Qt.AlignmentFlag.AlignVCenter,
                    )
                self.rhythm_scroll.horizontalScrollBar().setValue(0)
        named_meter = (
            isinstance(self.exercise, BeatIdentification)
            and q.answer not in BEAT_METERS
        )
        if isinstance(self.exercise, BeatConstruction):
            self.beat_placement.setVisible(bool(q.rhythm))
            if q.rhythm:
                self.beat_placement.reset(
                    q.rhythm,
                    meter=BEAT_METERS[q.answer],
                )
        elif isinstance(self.exercise, BeatIdentification):
            self.beat_staff.setVisible(bool(q.rhythm))
            if q.rhythm:
                self.beat_staff.show_score(
                    q.rhythm,
                    meter=beat_meter(q.answer),
                    show_signature=named_meter,
                )
        if isinstance(self.exercise, (BeatConstruction, BeatIdentification)):
            self.rhythm_scroll.horizontalScrollBar().setValue(0)
        construct = q.construct is not None
        scale = q.places_sequence
        clef = bool(q.place_clef)
        self.staff.setVisible(
            (bool(q.staff) or q.show_staff)
            and not construct
            and not scale
            and not clef,
        )
        self.fork.setVisible(q.build_key)
        self.circle.setVisible(q.circle is not None)
        if q.circle is not None:
            self.circle.set_question(q)
        self._found = (
            set()
        )  # the right answers given so far to a question that needs several
        if q.build_key:
            self.fork.locked = False
            self.fork.set_marker_color(None)
            self.fork.set_value(0, slide=False)
        self.input_staff.setVisible(construct)
        self.scale_input.setVisible(scale)
        self.clef_input.setVisible(clef)
        self.symbol_row.setVisible(clef)
        if clef:
            self.clef_input.reset(
                list(app_settings.CLEF_SYMBOLS),
                caption=q.caption,
            )
        staff_key = q.written_key
        if construct:
            self.input_staff.reset(
                q.clef,
                key=staff_key,
                caption=q.caption,
                placement=q,
            )
        if q.construct_scale is not None:
            self.scale_input.reset_scale(
                q.clef,
                slots=len(q.construct_scale),
                caption=q.caption,
                with_steps=q.construct_steps is not None,
                key=q.key,
            )
        if construct or scale:
            for b in self.accidental_buttons.values():
                b.setChecked(False)
        if q.place_signature:
            assert isinstance(self.scale_input, SignatureInput)
            self.scale_input.reset_signature(
                q.clef,
                key=q.key,
                caption=q.caption,
                starting_slots=q.starting_slots,
            )
            self._set_accidental(-1 if q.starting_slots and q.key < 0 else 1)
        self._show_placement_rows()
        self.keyboard.setVisible(
            q.keyboard is not None or bool(q.keyboard_notes),
        )
        position = q.fingerboard or q.picture
        self.fingerboard.show_position(position)
        self.fingerboard.setVisible(position is not None)
        self.key_staff.setVisible(q.key_staff)
        self.key_staff.show_notes([], clef="treble", key=q.key)
        self.keyboard.max_key_width = px(
            30.0 if q.key_staff else 38.0,
        )  # leave room for the staff above
        if q.keyboard_notes:
            self.keyboard.show_keys(
                [note.midi for note in q.keyboard_notes],
                span=q.keyboard_range,
            )
        else:
            self.keyboard.show_key(
                q.keyboard.midi if q.keyboard else None,
                span=q.keyboard_range,
            )
        self.staff.key_room = (
            MAX_ACCIDENTALS if q.build_key else 0
        )  # the staff does not change width as the signature does
        self.staff.show_notes(
            q.staff,
            clef=q.clef,
            key=0 if q.build_key else staff_key,
            value=q.value,
            notation_excerpt=q.notation_excerpt,
            notation_target=q.notation_target,
            locate_notation=q.notation_target is not None and not q.choices,
            caption=q.caption,
        )
        visible_staff = self.input_staff if construct else self.staff
        self.prompt.setMaximumWidth(
            visible_staff.maximumWidth()
            if not visible_staff.isHidden()
            else px(self.CHOICE_MAX_WIDTH),
        )
        for b in self.buttons:
            b.setShortcut(
                QKeySequence(),
                # a button waiting to be deleted must not share its key
                # with
                # the new one
            )
            b.hide()
            b.deleteLater()
        self.buttons = []
        for col in range(self.choice_box.columnCount()):
            self.choice_box.setColumnStretch(col, 0)
        interval_bank = (
            isinstance(self.exercise, KeyboardIntervals)
            and not q.octaves
            and (
                app_settings.keyboard_intervals.all_interval_buttons
                or len(q.choices) > 6
            )
        )
        if isinstance(self.exercise, IntervalNames):
            interval_bank = (
                app_settings.intervals.button_mode == "all"
                or len(q.choices) > 6
            )
        if isinstance(self.exercise, ChoiceExercise):
            interval_bank = len(q.choices) > 6 and (
                not q.grid or isinstance(self.exercise, NotationIdentification)
            )
            interval_bank = interval_bank or named_meter or q.identify_scale
            self.interval_answers.setAccessibleName("Answer choices")
        compact_intervals = isinstance(
            self.exercise,
            KeyboardIntervals,
        ) and bool(q.octaves)
        scale_buttons = bool(q.octaves) and q.second_label == "Mode"
        self.quality_label.setText("Tonic" if scale_buttons else "Quality")
        self.quality_label.setVisible(compact_intervals or scale_buttons)
        self.interval_label.setText(
            "Interval" if compact_intervals else q.second_label,
        )
        self.interval_label.setVisible(bool(q.octaves))
        self.choice_area.setVisible(
            not interval_bank and not self.staff.locate_notation,
        )
        self.interval_answers.setVisible(interval_bank and bool(q.choices))
        labels = (
            [choice.partition(" ")[0] for choice in q.choices]
            if q.identify_scale
            else q.choices
        )
        if (
            isinstance(self.exercise, RythmicEquations)
            and q.answer.isdecimal()
        ):
            keys = q.choices
        else:
            keys = choice_keys(labels)
        for i, c in enumerate(q.choices):
            if (
                isinstance(self.exercise, BeatIdentification)
                and not named_meter
            ):
                b = MeterButton(c, meter=BEAT_METERS[c])
                b.setMinimumHeight(px(50))
            else:
                b = DegreeButton(labels[i])
                b.setMinimumHeight(px(40))
            if (
                isinstance(self.exercise, RythmicEquations)
                and c in RHYTHM_SYMBOL_NAMES
            ):
                b.setAccessibleName(RHYTHM_SYMBOL_NAMES[c])
                b.setText("")
                b.setIcon(ValuePictures.icon(c))
                b.setIconSize(QSize(px(32), px(64)))
            if (
                isinstance(self.exercise, IntervalNames)
                and c in INTERVAL_QUALITY_SYMBOLS
            ):
                b.setText(INTERVAL_QUALITY_SYMBOLS[c])
                b.setAccessibleName(c)
            for function in app_settings.DEGREE_FUNCTIONS:
                if c.endswith(function):
                    prefix = c[: -len(function)].rstrip()
                    if prefix:
                        b.setText(f"{prefix}\n{function}")
                    b.setMinimumHeight(px(56))
                    b.setAccessibleName(c)
                    break
            if keys[i]:  # every answer can be given from the keyboard
                motion.set_shortcut(b, key=keys[i])
                b.setToolTip(f"Key {keys[i]}")
            if q.octaves:
                b.setCheckable(True)
                b.clicked.connect(
                    lambda _=False, choice=c, btn=b: self._pick(
                        "name",
                        text=choice,
                        button=btn,
                    ),
                )
            else:
                b.clicked.connect(
                    lambda _=False, choice=c, btn=b: self.submit(
                        choice,
                        button=btn,
                    ),
                )
            row, col = q.grid[c] if q.grid else (0, i)
            if not interval_bank:
                self.choice_box.addWidget(b, row, col)
            self.buttons.append(b)
        bank_positions = (
            [q.grid[c] for c in q.choices]
            if interval_bank
            and isinstance(self.exercise, IntervalNames)
            and q.grid
            else None
        )
        self.interval_answers.set_buttons(
            list(self.buttons) if interval_bank else [],
            positions=bank_positions,
        )
        if not interval_bank:
            for col in {
                (q.grid[c][1] if q.grid else i)
                for i, c in enumerate(q.choices)
            }:
                self.choice_box.setColumnStretch(col, 1)  # equal-width columns
        while self.octave_box.count():
            item = self.octave_box.takeAt(0)
            widget = item.widget() if item is not None else None
            if isinstance(widget, QAbstractButton):
                widget.setShortcut(QKeySequence())
            if widget is not None:
                widget.deleteLater()
        self.octave_row.setVisible(bool(q.octaves))
        if q.octaves:
            second_keys = second_row_keys(keys, labels=q.octaves)
            wrap_second = scale_buttons or (
                isinstance(self.exercise, KeyboardIntervals)
                and len(q.octaves) > 10
            )
            number_bank = AnswerBank() if wrap_second else None
            number_buttons = []
            for i, octave in enumerate(q.octaves):
                b = QPushButton(octave)
                b.setMinimumHeight(px(40))
                if second_keys[i]:  # a key that the first row does not use
                    motion.set_shortcut(b, key=second_keys[i])
                    b.setToolTip(f"Key {second_keys[i]}")
                b.setCheckable(True)
                b.clicked.connect(
                    lambda _=False, text=octave, btn=b: self._pick(
                        "octave",
                        text=text,
                        button=btn,
                    ),
                )
                if number_bank is None:
                    self.octave_box.addWidget(b, 1)
                else:
                    number_buttons.append(b)
                self.buttons.append(b)
            if number_bank is not None:
                number_bank.setAccessibleName(
                    "Mode buttons"
                    if scale_buttons
                    else "Interval number buttons",
                )
                number_bank.set_buttons(number_buttons)
                self.octave_box.addWidget(number_bank, 1)
        if empty_sample is not None:
            self.question = None
            self.next_button.setText("Check again")
            self.next_button.show()
        self._show_review_interval()
        self._update_score()

    def _show_review_interval(self) -> None:
        """
        Show the correct-answer interval beside the exercise or under
        the keyboard's right edge.

        Examples
        --------
        A new FSRS question shows 10 min before the learner submits an
        answer.
        """
        self._review_preview = None
        self._speed_previews = None
        self.review_interval.hide()
        self._keyboard_interval_row.hide()
        self._music_layout.setAlignment(Qt.AlignmentFlag(0))
        if (
            self._self_grading
            or self.question is None
            or self.learner is None
            or self._scheduler_mode not in CALENDAR_SCHEDULERS
        ):
            return
        exercise = type(self.exercise).__name__
        if self.learner.response_times(exercise).ready:
            self._speed_previews = self.learner.calendar.passing_intervals(
                exercise,
                profile=self.learner.profile.id,
                key=self.question.item_key(),
                mode=self._scheduler_mode,
                now=time.time(),
            )
            self._display_interval(
                *(
                    f"{grade.name}: {option.duration}"
                    for grade, option in self._speed_previews.items()
                ),
            )
            return
        self._review_preview = self.learner.calendar.correct_interval(
            exercise,
            profile=self.learner.profile.id,
            key=self.question.item_key(),
            mode=self._scheduler_mode,
            now=time.time(),
        )
        self._display_interval(self._review_preview.duration)

    def _display_interval(self, *intervals: str) -> None:
        """
        Position the next interval beside the music or below the
        keyboard.

        Parameters
        ----------
        intervals : str
            One scheduled interval or the three labeled passing
            outcomes.

        Examples
        --------
        A correct timed answer can display “Easy · 4 days”.
        """
        staff = self.keyboard.isHidden()
        if len(intervals) == 1:
            heading = "Next interval:"
            text = ("\n" if staff else " ").join((heading, intervals[0]))
        else:
            heading = "Next intervals:"
            if staff:
                intervals = tuple(reversed(intervals))
            text = ("\n" if staff else "    ").join(intervals)
        self.review_interval.setAccessibleName(
            f"{heading} {', '.join(intervals)}",
        )
        self.review_interval.setText(text)
        self.review_interval.setMaximumWidth(
            self.review_interval.sizeHint().width(),
        )
        if staff:
            self.review_interval.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
            )
            self._music_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self._music_layout.addWidget(
                self.review_interval,
                0,
                1,
                -1,
                1,
                Qt.AlignmentFlag.AlignBottom,
            )
        else:
            self.review_interval.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            )
            self._keyboard_interval_layout.addWidget(
                self.review_interval,
                alignment=Qt.AlignmentFlag.AlignRight,
            )
            self._align_keyboard_interval()
            self._keyboard_interval_row.show()
        self.review_interval.show()

    def _align_keyboard_interval(self) -> None:
        """
        Align the grade row with the last key, allowing longer text to
        extend left.

        Examples
        --------
        A short keyboard stays centered with the interval row ending
        beneath its right edge.
        """
        width = self._keyboard_interval_row.width()
        margin = min(
            (width - self.keyboard.full_width()) // 2,
            width - self.review_interval.sizeHint().width(),
        )
        self._keyboard_interval_layout.setContentsMargins(
            0,
            0,
            max(0, margin),
            0,
        )

    @staticmethod
    def _style(color: QColor) -> str:
        """
        Return the style sheet that colors an answer button.

        Parameters
        ----------
        color : QColor
            The background color, with white text on it.

        Returns
        -------
        str
            Qt style sheet text.

        Examples
        --------
        >>> ExerciseView._style(
        ...     QColor(CORRECT_ANSWER_COLOR)
        ... )
        'QPushButton, QPushButton:disabled { background: #2e7d32; color:
        white; }'
        """
        return (
            "QPushButton, QPushButton:disabled { background: "
            f"{color.name()}"
            "; color: white; }"
        )

    def _flash(
        self,
        button: QPushButton | None,
        *,
        target: str = CORRECT_ANSWER_COLOR,
        staff: bool = False,
    ) -> None:
        """
        Fade a button (and optionally the notes) from the staff's ink to
        a color over a short time.

        Parameters
        ----------
        button : QPushButton or None
            The button to color, if the learner used one.
        target : str
            The feedback color. Defaults to the correct-answer green.
            Keyword-only.
        staff : bool, default False
            Also color the notes on the staff, or the highlighted key.
            Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> view._flash(view.buttons[0])
        >>> len(view._anims)
        1
        """
        end, start = QColor(target), QColor("black")
        anim = QVariantAnimation(self)
        anim.setDuration(180)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)

        def step(t: float) -> None:
            """
            Set the colors for one moment of the fade.

            Parameters
            ----------
            t : float
                How far through the fade: 0 at the start, 1 at the end.

            Examples
            --------
            >>> step(0.5)  # doctest: +SKIP
            """
            c = blend(start, b=end, t=t)
            if button is not None:
                button.setStyleSheet(self._style(c))
            if staff:
                self.staff.set_note_color(c if t > 0 else None)
                if self.question and (
                    self.question.keyboard or self.question.keyboard_notes
                ):
                    self.keyboard.set_highlight_color(
                        c
                        if t > 0
                        else self.palette().color(
                            QPalette.ColorRole.Highlight,
                        ),
                    )

        anim.valueChanged.connect(step)
        self._anims.append(anim)
        anim.start()

    def _input(self) -> StaffInput:
        """
        Return the staff the learner is clicking: the one for a scale,
        or the one for a single note.

        Returns
        -------
        StaffInput
            `scale_input` while a scale is asked for, otherwise
            `input_staff`.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> view = ExerciseView(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view._input() is view.input_staff
        True
        """
        q = self.question
        return (
            self.scale_input
            if q is not None and q.places_sequence
            else self.input_staff
        )

    def _set_accidental(self, accidental: int | None) -> None:
        """
        Use a sign for the next note, light its button and update the
        preview.

        Parameters
        ----------
        accidental : int or None
            -1 for a flat, 0 for a natural, 1 for a sharp, or None to
            follow the key signature.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> view = ExerciseView(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view._set_accidental(1)
        >>> (
        ...     view.input_staff.accidental,
        ...     view.accidental_buttons[1].isChecked(),
        ... )
        (1, True)
        >>> view._set_accidental(None)
        >>> view.input_staff.accidental is None
        True
        """
        for a, b in self.accidental_buttons.items():
            b.setChecked(accidental is not None and a == accidental)
        staff = self._input()
        staff.accidental = accidental
        staff.refresh_preview()
        self._update_placement_status()

    def _pick_accidental(self, accidental: int) -> None:
        """
        Handle a click on a sign button.

        The buttons act like a radio group, and clicking the lit one
        again clears it.

        Parameters
        ----------
        accidental : int
            The sign of the button that was clicked: -1, 0 or 1.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> view = ExerciseView(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view.accidental_buttons[-1].click()
        >>> view.input_staff.accidental
        -1
        >>> view.accidental_buttons[
        ...     -1
        ... ].click()  # clicking the lit one again clears it
        >>> view.input_staff.accidental is None
        True
        """
        lit = self.accidental_buttons[
            accidental
        ].isChecked()  # the click has already toggled it
        self._set_accidental(
            accidental
            if lit or (self.question and self.question.place_signature)
            else None,
        )

    def _cycle_accidental(self, direction: int = 1) -> None:
        """
        Step to the next sign after a right click on the staff, or to
        the one before when the wheel is turned the other way.

        The order is no sign, sharp, flat and (under a key signature)
        natural, then around again. It does nothing unless the
        question asks for signs.

        Parameters
        ----------
        direction : int, default 1
            1 for the next sign, -1 for the one before.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> # not a "place this note" question: nothing happens
        >>> view._cycle_accidental()
        >>> view.input_staff.accidental is None
        True
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> view = ExerciseView(
        ...     ScaleConstruction(),
        ...     rng=random.Random(1),
        ... )
        >>> view._cycle_accidental(
        ...     -1
        ... )  # back from no sign goes around to the flat
        >>> view.scale_input.accidental
        -1
        """
        q = self.question
        if q and q.place_signature:
            self._set_accidental(-1 if self.scale_input.accidental == 1 else 1)
        elif (
            q
            and (q.construct is not None or q.construct_scale is not None)
            and q.accidentals
        ):
            order = (
                [
                    None,
                    1,
                    -1,
                    0,
                ]
                if q.key
                else [None, 1, -1]
            )  # without a key a natural is the same as no sign
            if isinstance(self.exercise, IntervalConstruction):
                order.extend([2, -2])
            current = self._input().accidental
            self._set_accidental(
                order[(order.index(current) + direction) % len(order)]
                if current in order
                else None,
            )

    def _flash_note(self, target: str = CORRECT_ANSWER_COLOR) -> None:
        """
        Fade the placed note from the staff's ink to a color.

        Parameters
        ----------
        target : str
            The feedback color. Defaults to the correct-answer green.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> view = ExerciseView(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view._flash_note("#c62828")
        >>> len(view._anims)
        1
        """
        end, start = QColor(target), QColor("black")
        anim = QVariantAnimation(self)
        anim.setDuration(180)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.valueChanged.connect(
            lambda t: self._input().set_note_color(blend(start, b=end, t=t)),
        )
        self._anims.append(anim)
        anim.start()

    def _place_midi(self, pitch: int) -> None:
        """
        Use a played pitch to identify a note, place an interval
        endpoint, or enter the next scale note.

        Parameters
        ----------
        pitch : int
            MIDI note number, including its octave.

        Examples
        --------
        Playing MIDI note 67 answers a perfect fifth above C4 with G4.
        """
        q = self.question
        if (
            not self.isVisible()
            or QApplication.activeModalWidget()
            or QApplication.activePopupWidget()
        ):
            return
        if q is None or self.answered or self._busy:
            return
        if (
            isinstance(self.exercise, NoteNames)
            and not q.identify_scale
            and q.staff
            and q.staff[0]
        ):
            self._identify_midi(pitch, question=q)
        elif q.construct_scale and not self.scale_input.complete:
            spelling = next(
                (n for n in q.construct_scale if n.pitch_class == pitch % 12),
                None,
            )
            note = (
                replace(
                    spelling,
                    octave=spelling.octave + (pitch - spelling.midi) // 12,
                )
                if spelling is not None
                else Note.parse(app_settings.key_name(pitch))
            )
            self.scale_input.place_next(note)
            if self.scale_input.done:
                self._check_scale()
        elif q.construct is not None:
            note = q.construct
            if note.midi != pitch:
                alternatives = (Note.parse(name) for name in q.accept)
                note = next(
                    (alt for alt in alternatives if alt.midi == pitch),
                    Note.parse(app_settings.key_name(pitch)),
                )
            self._place(note)

    def _identify_midi(self, pitch: int, *, question: Question) -> None:
        """
        Grade a keyboard pitch and show the answer in the question's
        naming system.

        Parameters
        ----------
        pitch : int
            Played MIDI note number.
        question : Question
            Note identification question on the staff.

        Examples
        --------
        A played F sharp identifies a written G flat, including when the
        answer buttons use solfège.
        """
        target = question.staff[0][0]
        for _, button in self._pending.values():
            button.setChecked(False)
        self._pending.clear()
        prompt = self.exercise.card_prompt(question)
        if pitch % 12 != target.pitch_class or (
            question.octaves and pitch != target.midi
        ):
            played = app_settings.key_name(pitch)
            self.submit(f"Played {played}", button=None)
            if not self.answered:
                self.prompt.setText(f"Played {played}. Try again. {prompt}")
                self.prompt.show()
            return
        self.prompt.setText(prompt)
        octave = str(target.octave)
        name = (
            question.answer.removesuffix(question.joiner + octave)
            if question.octaves
            else question.answer
        )
        self.buttons[question.choices.index(name)].click()
        if question.octaves:
            self.buttons[
                len(question.choices) + question.octaves.index(octave)
            ].click()

    def _place(self, note: Note) -> None:
        """
        Check a note that was clicked onto the staff against the one
        asked for.

        A correct placement uses the selected Next Question setting. A
        wrong note fades red before the scheduler handles the miss.

        Parameters
        ----------
        note : Note
            The note that was placed.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> sounds.enabled = False
        >>> view = ExerciseView(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> # noinspection PyTypeChecker,PyUnresolvedReferences
        >>> view._place(view.question.construct)
        >>> view.answered, view.correct
        (True, 1)
        >>> view._advance.stop()
        >>> sounds.enabled = True
        """
        q = self.question
        if not q or q.construct is None or self.answered or self._busy:
            return
        ok = q.check_placed(note)
        self._record(
            ok,
            choice=note_name(
                note,
                key=None if q.notes_only else q.key,
                minor=q.minor,
            ),
        )
        self.input_staff.locked = True
        self.input_staff.show_note(note)
        if ok:
            self._finish_answer(
                self.place_button,
                notes=q.placement_columns(note),
            )
        else:
            self._busy = True
            self._flash_note("#c62828")
            token = self._pair_token

            def retry() -> None:
                """
                Clear the staff so a wrong placement can be tried again,
                unless a new question has replaced it.

                Examples
                --------
                >>> retry()  # doctest: +SKIP
                """
                if (
                    token != self._pair_token
                ):  # a new question replaced this one
                    return
                self.input_staff.locked = False
                self.input_staff.show_note(None)
                self._busy = False
                # the note at the caret comes back, for the keyboard
                self.input_staff.refresh_preview()
                self._show_placement_rows()

            self._after_miss(retry)
        self._show_placement_rows()
        self._update_score()

    def _answer(self) -> None:
        """
        Hand in what was built: the key signature on the fork, or the
        scale on the staff.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     KeySignatureConstruction,
        ... )
        >>> view = ExerciseView(
        ...     KeySignatureConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> # noinspection PyUnresolvedReferences
        >>> view.fork.set_value(
        ...     view.question.key, slide=False
        ... )
        >>> view._answer()
        >>> view.answered
        True
        >>> view._advance.stop()
        """
        q = self.question
        if q and isinstance(self.exercise, BeatConstruction):
            self._check_beats()
        elif q and q.build_key:
            self._check_built()
        elif q and q.place_clef:
            self.clef_input.place_caret()
        elif (
            q
            and q.place_signature
            and self.answer_button.isEnabled()
            and not self.answered
        ):
            assert isinstance(self.scale_input, SignatureInput)
            choice = (
                " ".join(
                    str(note)
                    for note in self.scale_input.entered_signature()
                    if note is not None
                )
                or "No accidentals"
            )
            ok = q.check(choice)
            self._record(ok, choice=choice)
            if ok:
                self.scale_input.locked = True
                self._finish_answer(self.answer_button)
                self._show_placement_rows()
            else:
                self.scale_input.set_note_color(QColor("#c62828"))
                self.answer_button.setEnabled(False)
                self._after_miss()
                if self.answered:
                    self.scale_input.locked = True
                    self._show_placement_rows()
                else:
                    self.place_status.setText(
                        (
                            "Try again. Use Undo to change the signature, "
                            "or add another sign."
                        ),
                    )
            self._update_score()
        elif q and q.construct_scale is not None:
            self._check_scale()

    def _check_beats(self) -> None:
        """
        Grade the marked beat positions using the shared feedback flow.

        Examples
        --------
        >>> view = ExerciseView(
        ...     BeatConstruction(), rng=random.Random(1)
        ... )
        >>> view._check_beats()  # an empty response is not submitted
        >>> view.answered
        False
        """
        q = self.question
        score = self.beat_placement
        if not q or not self.answer_button.isEnabled() or self.answered:
            return
        ok, choice = grade_beat_marks(
            score.marks,
            expected=beat_positions(BEAT_METERS[q.answer]),
        )
        self._record(ok, choice=choice)
        score.feedback = ok
        score.update()
        if ok:
            self._finish_answer(self.answer_button)
        else:
            self._after_miss()
        self._show_placement_rows()
        self._update_score()

    def _scale_changed(self) -> None:
        """
        Get ready for what comes next on the scale staff: the sign is
        used up, and the right buttons are shown.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> view = ExerciseView(
        ...     ScaleConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view._set_accidental(1)
        >>> view._scale_changed()
        >>> (
        ...     view.scale_input.accidental is None,
        ...     view.answer_button.isEnabled(),
        ... )
        (True, False)
        """
        if self.question and self.question.place_signature:
            self.scale_input.set_note_color(None)
        elif self.scale_input.accidental is not None:
            self._set_accidental(None)
        self._show_placement_rows()

    def _show_placement_rows(self) -> None:
        """
        Show the buttons for what the question is waiting for, and let
        Place and Answer work when they can.

        For a note or a scale on the staff the pitch and sign buttons
        show while notes are being placed, the whole and half
        step buttons while steps are, and neither once everything is
        down. Place does the next thing, and Answer takes over
        from it once everything is placed. For a key signature on the
        fork only Answer shows.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> view = ExerciseView(
        ...     ScaleConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view._show_placement_rows()
        >>> (
        ...     view.step_row.isHidden(),
        ...     view.answer_button.isEnabled(),
        ...     view.place_button.isEnabled(),
        ... )
        (True, False, True)
        """
        q = self.question
        if q is None:
            return
        note, sequence, fork = (
            q.construct is not None,
            q.places_sequence,
            q.build_key,
        )
        clef = bool(q.place_clef)
        beats = isinstance(self.exercise, BeatConstruction) and bool(q.rhythm)
        staff = self._input()
        placing_notes = note or (sequence and not self.scale_input.complete)
        steps_turn = sequence and self.scale_input.placing_steps
        live = not self.answered and not self._busy
        for (
            symbol,
            button,
        ) in (
            self.symbol_buttons.items()
        ):  # one for each symbol that can be chosen, the chosen one pressed
            button.setVisible(clef and symbol in self.clef_input.options)
            button.setChecked(symbol == self.clef_input.selected)
            button.setEnabled(live)
        self.answer_row.setVisible(note or sequence or fork or clef or beats)
        self.place_status.setVisible(note or sequence or beats)
        self.pitch_row.setVisible(placing_notes and not q.place_signature)
        self.accidental_buttons[0].setVisible(not q.place_signature)
        self.accidental_row.setEnabled(live and placing_notes)
        self.accidental_row.setVisible(
            q.place_signature or (q.accidentals and placing_notes),
        )
        self.step_row.setVisible(steps_turn)
        self.undo_button.setVisible(sequence or beats)
        self.place_button.setVisible(note or sequence)
        label = (
            "Place sign"
            if q.place_signature
            else "Mark step"
            if steps_turn
            else "Place note"
        )
        if self.place_button.text() != label:
            self.place_button.setText(label)
            motion.set_shortcut(
                self.place_button,
                key="P" if q.place_signature else "Return",
            )
        self.place_button.setEnabled(
            live and not (sequence and self.scale_input.done),
        )
        self.answer_button.setVisible(sequence or fork or clef or beats)
        self.answer_button.setEnabled(
            live
            and (fork or clef or q.place_signature or self.scale_input.done),
        )
        self.undo_button.setEnabled(live and bool(self.scale_input.notes))
        if beats:
            score = self.beat_placement
            score.setEnabled(live)
            self.answer_button.setEnabled(
                live and bool(score.marks) and score.feedback is not False,
            )
            self.undo_button.setEnabled(live and bool(score.marks))
            count = len(score.marks)
            if score.feedback is False:
                self.place_status.setText("Check where each beat begins.")
            elif score.feedback is True:
                self.place_status.setText("Correct.")
            elif count:
                self.place_status.setText(f"Beats marked: {count}")
            else:
                self.place_status.setText(
                    "Mark each beat, including the start of each measure.",
                )
        for key in self._arrow_keys:
            key.setEnabled(note or sequence or fork or clef)
        for key in self._letter_keys:
            key.setEnabled(placing_notes and not fork)
        if note or sequence:
            action = "place the scale" if sequence else "place the note"
            staff.setAccessibleName(
                "Staff: write the key signature"
                if q.place_signature
                else f"Staff: {action}",
            )
            self._update_placement_status()

    def _update_placement_status(self) -> None:
        """
        Say what the next click or key press will do, in the line under
        the staff and for screen readers.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> view = ExerciseView(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view.place_status.text()
        'Press ↑ or ↓ to choose a note, then Return to place it.'
        >>> view.input_staff.move_cursor(0)
        >>> view.place_status.text().startswith(
        ...     "Note to place: "
        ... )
        True
        """
        shown, spoken = self._placement_text()
        self.place_status.setText(shown)
        self.place_status.setAccessibleDescription(spoken)
        q = self.question
        if q is not None and (q.construct is not None or q.places_sequence):
            self._input().setAccessibleDescription(spoken)

    def _placement_text(self) -> tuple[str, str]:
        """
        Work out what to say about the staff being clicked: what is to
        be placed next, and where the caret is.

        Returns
        -------
        tuple of str and str
            The line shown under the staff, and the same said in words
            for a screen reader.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> view = ExerciseView(
        ...     ScaleConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view._placement_text()[0]
        'Note 1 of 8: press ↑ or ↓ to choose a note, then Return to
        place it.'
        """
        q = self.question
        if q is None or (q.construct is None and not q.places_sequence):
            return "", ""
        if self._busy and q.construct and q.staff:
            placed = self.input_staff.columns[-1][-1]
            right_position = any(
                q.check_placed(
                    Note.from_diatonic(placed.diatonic, accidental=sign),
                )
                for sign in self.accidental_buttons
            )
            text = (
                "Check the accidental."
                if right_position
                else "Check the staff position."
            )
            return text, text
        if self.answered and self.missed:
            return "", ""
        staff = self._input()
        if q.place_signature:
            caret = staff.caret_note()
            if self.answered:
                text = "Correct."
            elif self.scale_input.complete:
                text = "Seven signs placed. Press Answer to submit."
            elif caret:
                text = f"Next sign: {caret}. Press P to place it."
            else:
                text = (
                    "Choose ♯ or ♭ and place the missing signs from left "
                    "to right."
                )
            return text, text
        if q.construct_scale is not None:
            if self.scale_input.placing_steps:
                number, of = (
                    len(self.scale_input.steps) + 1,
                    self.scale_input.slots - 1,
                )
                pending = self.scale_input.pending_step
                words = "a whole step" if pending == "W" else "a half step"
                return (
                    (
                        "Step "
                        f"{number}"
                        " of "
                        f"{of}"
                        ": "
                        f"{pending}"
                        ". Press W or H to choose, then Return to mark it."
                    ),
                    (
                        "Step "
                        f"{number}"
                        " of "
                        f"{of}"
                        ": "
                        f"{words}"
                        ". Press W or H to choose, then Return to mark it."
                    ),
                )
            if self.scale_input.done:
                return (
                    "Everything is placed. Press Return to answer.",
                    "Everything is placed. Press Return to answer.",
                )
            head = (
                "Note "
                f"{len(self.scale_input.notes) + 1}"
                " of "
                f"{self.scale_input.slots}"
            )
        else:
            head = "Note to place"
        caret = staff.caret_note()
        if caret is not None:
            key = (
                q.key if q.construct is not None and not q.notes_only else None
            )
            display = note_name(caret, key=key, minor=q.minor)
            spoken = note_words(caret, key=key, minor=q.minor)
            return f"{head}: {display}", f"{head}: {spoken}"
        if (
            q.construct_scale is None
        ):  # a single note has no number to put in front of the advice
            return (
                "Press ↑ or ↓ to choose a note, then Return to place it.",
                (
                    "Press the up or down arrow to choose a note, then "
                    "Return to place it."
                ),
            )
        return (
            f"{head}: press ↑ or ↓ to choose a note, then Return to place it.",
            (
                f"{head}"
                ": press the up or down arrow to choose a note, then Return to"
                " place it."
            ),
        )

    def _key_action(self, name: str) -> None:
        """
        Do what an arrow key or Page Up or Page Down asks, which depends
        on what is being answered.

        On the fork Up and Right add a sharp, Down and Left a flat, and
        Home goes back to none. On the staff Up and Down
        move the note a line or space and Page Up and Page Down an
        octave, and Left and Right step through the signs. While
        steps are marked all four arrows switch between whole and half.

        Parameters
        ----------
        name : str
            "up", "down", "left", "right", "pageup", "pagedown" or
            "home".

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     KeySignatureConstruction,
        ... )
        >>> view = ExerciseView(
        ...     KeySignatureConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view._key_action("up")
        >>> view.fork.value
        1
        """
        q = self.question
        if q is None or self.answered or self._busy:
            return
        if q.build_key:
            step = {"up": 1, "right": 1, "down": -1, "left": -1}.get(name)
            if not self.fork.locked:
                if step is not None:
                    self.fork.set_value(self.fork.value + step)
                elif (
                    name == "home"
                ):  # back to the natural sign, no sharps or flats
                    self.fork.set_value(0)
            return
        if q.place_clef:
            if name in {"up", "down"}:
                self.clef_input.move_caret(1 if name == "up" else -1)
            elif name in {"left", "right"}:
                self.clef_input.step_symbol(1 if name == "right" else -1)
            return
        if q.construct is None and not q.places_sequence:
            return
        if q.construct_scale is not None and self.scale_input.placing_steps:
            if (
                name in {"up", "down", "left", "right"}
                and not self.scale_input.locked
            ):
                self.scale_input.toggle_step()
        elif name in {"up", "down", "pageup", "pagedown"}:
            self._move_caret(
                {"up": 1, "down": -1, "pageup": 7, "pagedown": -7}[name],
            )
        elif name == "right":
            self._cycle_accidental(1)
        elif name == "left":
            self._cycle_accidental(-1)

    def _move_caret(self, steps: int) -> None:
        """
        Move the note that the keyboard would place, up or down the
        staff.

        Parameters
        ----------
        steps : int
            How many lines and spaces: positive is up, negative down,
            and 7 is an octave.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> view = ExerciseView(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view._move_caret(1)
        >>> view.input_staff.caret is not None
        True
        """
        q = self.question
        if (
            q is None
            or self.answered
            or self._busy
            or (q.construct is None and not q.places_sequence)
        ):
            return
        if q.places_sequence and not self.scale_input.placing_steps:
            self.scale_input.move_cursor(steps)
        elif q.construct is not None:
            self.input_staff.move_cursor(steps)

    def _jump_to_letter(self, letter: int) -> None:
        """
        Move the note that the keyboard would place to the nearest one
        with a letter name.

        Parameters
        ----------
        letter : int
            The letter, counting from C as 0.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> view = ExerciseView(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view._jump_to_letter(4)
        >>> view.input_staff.caret % 7  # G is the fifth letter from C
        4
        """
        q = self.question
        if q is None or self.answered or self._busy:
            return
        if q.places_sequence and not self.scale_input.placing_steps:
            self.scale_input.jump_to_letter(letter)
        elif q.construct is not None:
            self.input_staff.jump_to_letter(letter)

    def _place_here(self) -> None:
        """
        Place the note at the caret on the staff, or mark the next step,
        without the mouse.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> sounds.enabled = False
        >>> view = ExerciseView(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view._place_here()  # the note at the starting place
        >>> view.total
        1
        >>> view._advance.stop()
        >>> sounds.enabled = True
        """
        q = self.question
        if q is None or self.answered or self._busy:
            return
        if q.places_sequence:
            self.scale_input.place_caret()
        elif q.construct is not None:
            self.input_staff.place_caret()

    def _show_step(self, step: str) -> None:
        """
        Light the button of the step that the next click on the scale
        staff marks.

        Parameters
        ----------
        step : str
            "W" or "H".

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> view = ExerciseView(
        ...     ScaleConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view._show_step("H")
        >>> (
        ...     view.step_buttons["H"].isChecked(),
        ...     view.step_buttons["W"].isChecked(),
        ... )
        (True, False)
        """
        self.step_buttons[step].setChecked(True)

    def _undo_scale_note(self) -> None:
        """
        Take back the last note placed on the scale staff.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> view = ExerciseView(
        ...     ScaleConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view.scale_input.notes.append(
        ...     Note.parse("C4")
        ... )
        >>> view._undo_scale_note()
        >>> view.scale_input.notes
        []
        """
        if not self.answered and not self._busy:
            if isinstance(self.exercise, BeatConstruction):
                self.beat_placement.undo()
            else:
                self.scale_input.undo()

    def _check_scale(self) -> None:
        """
        Check the scale placed on the staff against the one asked for.

        A correct scale uses the selected Next Question setting. A wrong
        scale turns red.
        Only the first try counts toward the score.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> sounds.enabled = False
        >>> view = ExerciseView(
        ...     ScaleConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> # noinspection PyTypeChecker,PyUnresolvedReferences
        >>> view.scale_input.notes = list(
        ...     view.question.construct_scale
        ... )
        >>> view._check_scale()
        >>> view.answered, view.correct
        (True, 1)
        >>> view._advance.stop()
        >>> sounds.enabled = True
        """
        q = self.question
        if (
            not q
            or q.construct_scale is None
            or self.answered
            or self._busy
            or not self.scale_input.done
        ):
            return
        notes, steps, clef, caption = (
            list(self.scale_input.notes),
            list(self.scale_input.steps),
            q.clef,
            q.caption,
        )
        with_steps, key = q.construct_steps is not None, q.key
        ok = q.check_scale(notes) and q.check_steps(steps)
        answer = " ".join(note_name(n) for n in notes)
        self._record(
            ok,
            choice=f"{answer} | {' '.join(steps)}" if with_steps else answer,
        )
        self.scale_input.locked = True
        if ok:
            self._finish_answer(
                self.answer_button,
                notes=[[note] for note in notes],
            )
        else:
            self._flash_note("#c62828")
            self._busy = True
            token = self._pair_token

            def retry() -> None:
                """
                Clear the staff so a wrong scale can be tried again,
                unless a new question has replaced it.

                Examples
                --------
                >>> retry()  # doctest: +SKIP
                """
                if (
                    token != self._pair_token
                ):  # a new question replaced this one
                    return
                self.scale_input.reset_scale(
                    clef,
                    slots=len(notes),
                    caption=caption,
                    with_steps=with_steps,
                    key=key,
                )
                self._busy = False
                self._show_placement_rows()

            self._after_miss(retry)
        self._show_placement_rows()
        self._update_score()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: PLR0917  (Qt calls it with both)
        """
        Handle staff clicks in notation questions and forward wheel
        turns to the fork or clef staff.

        Parameters
        ----------
        watched : QObject
            The staff or the Answer button.
        event : QEvent
            The incoming pointer or widget event.

        Returns
        -------
        bool
            True when the exercise handles the event.

        Examples
        --------
        >>> from PySide6.QtCore import QPoint, QPointF
        >>> from PySide6.QtGui import QWheelEvent
        >>> from alto.exercises.library import (
        ...     KeySignatureConstruction,
        ... )
        >>> view = ExerciseView(
        ...     KeySignatureConstruction(),
        ...     rng=random.Random(1),
        ... )
        >>> view.show()
        >>> here = QPointF(5, 5)
        >>> turn = QWheelEvent(
        ...     here,
        ...     here,
        ...     QPoint(0, 0),
        ...     QPoint(0, 120),
        ...     Qt.MouseButton.NoButton,
        ...     Qt.KeyboardModifier.NoModifier,
        ...     Qt.ScrollPhase.NoScrollPhase,
        ...     False,
        ... )
        >>> view.eventFilter(view.answer_button, turn)
        True
        >>> view.fork.value
        1
        """
        if (
            event.type() == QEvent.Type.Resize
            and isinstance(
                self.exercise,
                (RythmicEquations, BeatConstruction, BeatIdentification),
            )
            and watched in (self.rhythm_scroll.widget(), self.rhythm_scroll)
        ):
            content = self.rhythm_scroll.widget()
            assert content is not None
            height = content.height()
            if content.width() > self.rhythm_scroll.width():
                height += (
                    self.rhythm_scroll.horizontalScrollBar()
                    .sizeHint()
                    .height()
                )
            self.rhythm_scroll.setFixedHeight(height)
        if (
            event.type() == QEvent.Type.Resize
            and watched is self._keyboard_interval_row
        ):
            self._align_keyboard_interval()
        if (
            event.type() == QEvent.Type.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
            and watched is self.staff
            and self.staff.locate_notation
            and not self.answered
            and self.question
        ):
            choice = (
                self.question.answer
                if self.staff.hits_notation(event.position().toPoint())
                else "Incorrect location"
            )
            self.submit(choice, button=None)
            return True
        if isinstance(event, QWheelEvent) and watched in (
            self.staff,
            self.answer_button,
        ):
            if self.fork.isVisible():
                self.fork.wheelEvent(event)
                return True
            if self.clef_input.isVisible():
                self.clef_input.wheelEvent(event)
                return True
        return super().eventFilter(watched, event)

    def _place_clef(  # noqa: PLR0917 (Qt passes both signal arguments positionally)
        self,
        symbol: str,
        step: int,
    ) -> None:
        """
        Check a clef symbol that was put on the staff against the clef
        asked for.

        The symbol and the place must both be those that make the clef:
        the C clef on the second line is the mezzo-soprano clef,
        and anywhere else it is not. The baritone clef is either the F
        clef on the middle line or the C clef on the top line.
        A correct clef uses the selected Next Question setting. A wrong
        clef turns red.

        Parameters
        ----------
        symbol : str
            The symbol that was placed, "G", "C" or "F".
        step : int
            Where it was placed: 0 for the bottom line, 1 for the space
            above it, up to 8 for the top line.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     ClefBasics,
        ... )
        >>> view = ExerciseView(
        ...     ClefBasics(), rng=random.Random(2)
        ... )
        >>> # noinspection PyUnresolvedReferences
        >>> view._place_clef(
        ...     *sorted(
        ...         clef_targets(
        ...             view.question.place_clef
        ...         )
        ...     )[0]
        ... )
        >>> view.answered, view.correct
        (True, 1)
        >>> view._advance.stop()
        """
        q = self.question
        if not q or not q.place_clef or self.answered or self._busy:
            return
        ok = (symbol, step) in clef_targets(q.place_clef)
        self._record(ok, choice=f"{symbol} clef at {step}")
        self.clef_input.locked = True
        if ok:
            self._finish_answer(self.answer_button)
        else:
            self._flash_clef("#c62828")
            self._busy = True
            token = self._pair_token

            def retry() -> None:
                """
                Clear the staff so a wrong clef can be tried again,
                unless a new question has replaced it.

                Examples
                --------
                >>> retry()  # doctest: +SKIP
                """
                if (
                    token != self._pair_token
                ):  # a new question replaced this one
                    return
                self.clef_input.locked = False
                self.clef_input.clear_placed()
                self._busy = False
                self._show_placement_rows()

            self._after_miss(retry)
        self._show_placement_rows()
        self._update_score()

    def _flash_clef(self, target: str = CORRECT_ANSWER_COLOR) -> None:
        """
        Fade the placed clef from black to a color.

        Parameters
        ----------
        target : str
            The feedback color. Defaults to the correct-answer green.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     ClefBasics,
        ... )
        >>> view = ExerciseView(
        ...     ClefBasics(), rng=random.Random(2)
        ... )
        >>> view._flash_clef("#c62828")
        >>> len(view._anims)
        1
        """
        end, start = QColor(target), QColor("black")
        anim = QVariantAnimation(self)
        anim.setDuration(180)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.valueChanged.connect(
            lambda t: self.clef_input.set_clef_color(blend(start, b=end, t=t)),
        )
        self._anims.append(anim)
        anim.start()

    def _fork_changed(self, count: int) -> None:
        """
        Show the signature picked on the fork on the staff.

        Parameters
        ----------
        count : int
            The signature picked: that many sharps if positive, flats if
            negative.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     KeySignatureConstruction,
        ... )
        >>> view = ExerciseView(
        ...     KeySignatureConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view.fork.set_value(-3)
        >>> view.staff.key
        -3
        """
        q = self.question
        if q and q.build_key:
            self.staff.show_notes(
                q.staff,
                clef=q.clef,
                key=count,
                value=q.value,
                caption=q.caption,
            )

    def _check_built(self) -> None:
        """
        Check the signature picked on the fork against the one asked
        for.

        A correct signature uses the selected Next Question setting. A
        wrong signature turns the circle red.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     KeySignatureConstruction,
        ... )
        >>> view = ExerciseView(
        ...     KeySignatureConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> # noinspection PyUnresolvedReferences
        >>> view.fork.set_value(
        ...     view.question.key, slide=False
        ... )
        >>> view._check_built()
        >>> view.answered, view.correct
        (True, 1)
        >>> view._advance.stop()
        """
        q = self.question
        if not q or not q.build_key or self.answered or self._busy:
            return
        count = self.fork.value
        ok = q.check_built(count)
        self._record(ok, choice=format_key_signature(count))
        self.fork.locked = True
        if ok:
            self._finish_answer(self.answer_button)
        else:
            self._flash_fork("#c62828")
            self._busy = True
            token = self._pair_token

            def retry() -> None:
                """
                Return the fork to the natural sign so a wrong signature
                can be tried again, unless a new question replaced it.

                Examples
                --------
                >>> retry()  # doctest: +SKIP
                """
                if (
                    token != self._pair_token
                ):  # a new question replaced this one
                    return
                self.fork.set_marker_color(None)
                self.fork.set_value(0)
                self.fork.locked = False
                self._busy = False
                self._show_placement_rows()

            self._after_miss(retry)
        self._show_placement_rows()
        self._update_score()

    def _flash_fork(self, target: str = CORRECT_ANSWER_COLOR) -> None:
        """
        Fade the fork's circle from the ink color to a color.

        Parameters
        ----------
        target : str
            The feedback color. Defaults to the correct-answer green.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     KeySignatureConstruction,
        ... )
        >>> view = ExerciseView(
        ...     KeySignatureConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view._flash_fork("#c62828")
        >>> len(view._anims)
        1
        """
        end, start = (
            QColor(target),
            self.palette().color(QPalette.ColorRole.Highlight),
        )
        anim = QVariantAnimation(self)
        anim.setDuration(180)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.valueChanged.connect(
            lambda t: self.fork.set_marker_color(blend(start, b=end, t=t)),
        )
        self._anims.append(anim)
        anim.start()

    def _record(
        self,
        ok: bool,
        *,
        choice: str = "",
    ) -> None:
        """
        Count an answer and log it.

        Only the first attempt at a question counts toward the score and
        the streak. Each attempt is recorded with its time,
        measured from the question appearing (first attempt) or the
        previous attempt.

        Parameters
        ----------
        ok : bool
            Whether the answer was right.
        choice : str, default ""
            What was answered. Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> view._record(True, choice="C")
        >>> view.total, view.correct, view.streak
        (1, 1, 1)
        """
        progress = self.session.after_attempt(
            ok,
            calendar_review=self._scheduler_mode in CALENDAR_SCHEDULERS,
            shuffle=self.shuffle_answers,
        )
        if progress is self.session:
            return
        now = time.monotonic()
        assigned = None
        if self.learner and self.question:
            assigned = self.learner.record(
                self.exercise,
                question=self.question,
                answer=choice,
                correct=ok,
                attempt_no=progress.attempts,
                seconds=now - self._clock,
                preview=self._review_preview,
                passing_previews=self._speed_previews,
                self_grading=self._self_grading,
                timing_valid=self._timing_valid,
            )
        self.session = progress
        self._clock = now
        if assigned is not None:
            self._display_interval(
                f"{assigned.rating.name} · {assigned.duration}",
            )
        if not ok and self.learner:
            self.review_interval.hide()
            self._keyboard_interval_row.hide()

    def _pick(
        self,
        part: str,
        *,
        text: str,
        button: QPushButton,
    ) -> None:
        """
        Choose one part of a two-part answer.

        A name and then an octave (or a chord type and an inversion), in
        either order; the answer is checked once both are set.

        Parameters
        ----------
        part : str
            "name" or "octave".
        text : str
            The text of the button. Keyword-only.
        button : QPushButton
            The button, which is lit while it is the chosen one.
            Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     ArpeggioNames,
        ... )
        >>> sounds.enabled = False
        >>> view = ExerciseView(
        ...     ArpeggioNames(), rng=random.Random(11)
        ... )
        >>> # noinspection PyUnresolvedReferences
        >>> kind, inversion = (
        ...     view.question.answer.split(
        ...         view.question.joiner
        ...     )
        ... )
        >>> by_text = {
        ...     button_.text(): button_
        ...     for button_ in view.buttons
        ... }
        >>> view._pick(
        ...     "name", text=kind, button=by_text[kind]
        ... )
        >>> view._pick(
        ...     "octave",
        ...     text=inversion,
        ...     button=by_text[inversion],
        ... )
        >>> view.answered
        True
        >>> view._advance.stop()
        >>> sounds.enabled = True
        """
        if self.answered or self._busy:
            return
        previous = self._pending.get(part)
        if previous and previous[1] is not button:
            previous[1].setChecked(False)
        button.setChecked(True)
        self._pending[part] = (text, button)
        if len(self._pending) == 2:
            self._submit_pair()

    def _submit_pair(self) -> None:
        """
        Check a two-part answer once both parts are chosen.

        A right answer is scored through `submit`. A wrong pair flashes
        red.

        Examples
        --------
        >>> from alto.exercises.library import (
        ...     ArpeggioNames,
        ... )
        >>> sounds.enabled = False
        >>> view = ExerciseView(
        ...     ArpeggioNames(), rng=random.Random(11)
        ... )
        >>> by_text = {
        ...     button.text(): button
        ...     for button in view.buttons
        ... }
        >>> # noinspection PyUnresolvedReferences
        >>> wrong_kind = next(
        ...     c
        ...     for c in view.question.choices
        ...     if c
        ...     != view.question.answer.split(
        ...         view.question.joiner
        ...     )[0]
        ... )
        >>> view._pending = {
        ...     "name": (
        ...         wrong_kind,
        ...         by_text[wrong_kind],
        ...     ),
        ...     "octave": (
        ...         "root position",
        ...         by_text["root position"],
        ...     ),
        ... }
        >>> view._submit_pair()
        >>> view.missed
        True
        >>> sounds.enabled = True
        """
        q = self.question
        assert q is not None
        (name, name_btn), (octave, octave_btn) = (
            self._pending["name"],
            self._pending["octave"],
        )
        choice = name + q.joiner + octave
        if q.check(choice):
            self.submit(
                choice,
                button=name_btn,
            )  # scores it, flashes the name button, plays the note, moves on
            return
        self._record(False, choice=choice)
        self._busy = True
        for b in (name_btn, octave_btn):
            self._flash(b, target="#c62828")
        self._update_score()
        token = self._pair_token

        def reset() -> None:
            """
            Clear the two buttons after a wrong two-part answer, unless
            a new question has replaced them.

            Examples
            --------
            >>> reset()  # doctest: +SKIP
            """
            if (
                token != self._pair_token
            ):  # a new question replaced these buttons
                return
            for pressed in (name_btn, octave_btn):
                pressed.setStyleSheet("")
                pressed.setChecked(False)
            self._pending = {}
            self._busy = False

        self._after_miss(reset, delay=400)

    def submit(
        self,
        choice: str,
        *,
        button: QPushButton | None,
    ) -> None:
        """
        Check an answer chosen with a button or by clicking the
        notation.

        A correct answer uses the selected Next Question setting. An
        incorrect button flashes red.
        In SM-2 and FSRS the card returns at its scheduled retry time.
        ASRS and ARTS allow another answer on the same showing.

        Parameters
        ----------
        choice : str
            The text of the button that was pressed.
        button : QPushButton or None
            The pressed button, or None for a staff click. Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> sounds.enabled = False
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> question = view.question
        >>> # noinspection PyUnresolvedReferences
        >>> wrong = next(
        ...     b
        ...     for b in view.buttons
        ...     if b.text() != question.answer
        ... )
        >>> view.submit(wrong.text(), button=wrong)
        >>> view.missed, wrong.isEnabled()
        (True, False)
        >>> # noinspection PyUnresolvedReferences
        >>> right = next(
        ...     b
        ...     for b in view.buttons
        ...     if b.text() == question.answer
        ... )
        >>> # noinspection PyUnresolvedReferences
        >>> view.submit(question.answer, button=right)
        >>> view.answered
        True
        >>> view._advance.stop()
        >>> sounds.enabled = True
        """
        if (
            self.answered
            or not self.question
            or (button is not None and not button.isEnabled())
        ):
            return
        q = self.question
        ok = q.check(choice)
        if (
            ok and q.required and button is not None
        ):  # mark each part as it is found
            self._found.add(choice)
            button.setEnabled(False)
            if not q.complete(self._found):
                self._flash(button)
                self.circle.set_subtitle("and its other name")
                return
            choice = " ".join(name for name in q.required)
        self._record(ok, choice=choice)
        if ok:
            if button is None:
                self.prompt.setText(q.caption or q.prompt)
            if isinstance(self.exercise, RythmicEquations):
                blank = q.prompt.split().index("_")
                item = self.rhythm_terms.takeAt(blank)
                if item is not None and (widget := item.widget()) is not None:
                    widget.hide()
                    widget.deleteLater()
                self.rhythm_terms.insertWidget(
                    blank,
                    self._rhythm_term(choice),
                    alignment=Qt.AlignmentFlag.AlignVCenter,
                )
                self.rhythm_equation.setAccessibleName(
                    " ".join(
                        choice if token == "_" else token
                        for token in q.prompt.split()
                    )
                    .replace("~", " tied to ")
                    .replace("|", " beamed with "),
                )
            notes = q.sounding_columns()
            if (
                isinstance(self.exercise, IntervalNames)
                and q.prompt in INTERVAL_INVERSION_PROMPTS.values()
            ):
                first, second = (note for column in q.staff for note in column)
                low, high = sorted(
                    (first, second),
                    key=lambda note: (note.diatonic, note.midi),
                )
                raised = high.transpose(
                    Interval.between(low, high=high).inversion,
                )
                if len(q.staff) == 1:
                    notes = [[high] if high == raised else [high, raised]]
                else:
                    notes = (
                        [[raised], [high]]
                        if first == high and first != second
                        else [[high], [raised]]
                    )
                self.staff.show_notes(
                    notes,
                    clef=q.clef,
                    key=q.key,
                    value=q.value,
                )
            position = q.fingerboard or q.picture
            if isinstance(position, PicturePosition) and position.notes:
                notes = [
                    [Note.parse(name) for name in position.notes],
                ]  # the keys of an interval, sounded together as a chord
            elif position and position.note:
                notes = [[Note.parse(position.note)]]
            self._finish_answer(button, notes=notes)
        else:
            if q.circle is not None:
                self.circle.flash_wrong()
            if button is None:
                self.prompt.setText(f"Try again. {q.prompt}")
            else:
                # Disabling a focused button would move focus to the
                # next answer.
                button.clearFocus()
                button.setEnabled(False)
                self._flash(button, target="#c62828")
            self._after_miss()
        self._update_score()

    def _redraw_keyboards(self) -> None:
        """
        Draw a plugin's keyboards over the range the learner is
        choosing, keeping the question.

        Examples
        --------
        Dragging the range selector shortens or lengthens the manuals on
        screen at once.
        """
        picture = self.question.picture if self.question else None
        if (
            isinstance(self.exercise, PackExercise)
            and self.exercise.is_keyboard
            and picture is not None
            and picture.keys
        ):
            self.fingerboard.show_position(
                replace(picture, span=self.exercise.chosen_span()),
            )

    def _after_miss(
        self,
        retry: Callable[[], None] | None = None,
        *,
        delay: int = 450,
    ) -> None:
        """
        Finish a missed calendar or shuffled question, or reopen the
        input for another attempt.

        Parameters
        ----------
        retry : callable or None
            Reset the input when another attempt on this showing is
            allowed.
        delay : int
            Duration of the wrong-answer feedback in milliseconds.

        Examples
        --------
        A missed SM-2 card receives a fresh first attempt when its
        scheduled retry comes due.
        """
        if self.answered:
            for button in self.buttons:
                button.setEnabled(False)
            self.prompt.setText(
                "Incorrect. This card will return for review."
                if self._scheduler_mode in CALENDAR_SCHEDULERS
                else "Incorrect.",
            )
            self.prompt.show()
            wait = (
                not self._self_grading
                and self.settings_panel.next_question_mode == "Wait"
            )
            self.next_button.setVisible(wait)
            immediate = (
                self._self_grading
                or self.settings_panel.next_question_mode == "Immediately"
            )
            self._advance_after_feedback(90 if immediate else delay)
        elif retry is not None:
            motion.later(delay, owner=self, step=retry)

    def _finish_answer(
        self,
        button: QPushButton | None,
        *,
        notes: list[list[Note]] | None = None,
    ) -> None:
        """
        Show correct-answer feedback and apply the exercise's Next
        Question preference.

        Parameters
        ----------
        button : QPushButton or None
            The answer control, if the question has one.
        notes : list of list of Note or None
            The answered pitches grouped by onset, including notes
            placed by the learner.

        Examples
        --------
        Wait runs the usual playback and keeps the correct buttons green
        until Next is pressed.
        """
        q = self.question
        assert q is not None
        mode = (
            "Wait"
            if self._self_grading
            else self.settings_panel.next_question_mode
        )
        if self._self_grading:
            assert self.learner is not None
            self._rating_previews = self.learner.calendar.passing_intervals(
                type(self.exercise).__name__,
                profile=self.learner.profile.id,
                key=q.item_key(),
                mode=self._scheduler_mode,
                now=time.time(),
            )
            for rating, (label, control) in self.grade_controls.items():
                preview = self._rating_previews[rating]
                label.setText(preview.duration)
                control.setAccessibleDescription(
                    f"Next review in {preview.duration}",
                )
            self.rating_row.show()
        buttons = [choice for _, choice in self._pending.values()] or (
            [button] if button is not None else []
        )
        immediate = mode == "Immediately"
        if immediate:
            for choice in buttons:
                choice.setStyleSheet(self._style(QColor(CORRECT_ANSWER_COLOR)))
            # Allow one visible flash before replacing the controls.
            motion.start_timer(self._advance, delay=90 if buttons else 0)
        else:
            self.next_button.setVisible(
                mode == "Wait" and not self._self_grading,
            )
            if mode == "Wait":
                for answer in self.buttons:
                    answer.setEnabled(False)
            for choice in buttons:
                self._flash(choice)
            if q.circle is not None:
                self.circle.reveal()
        if isinstance(self.exercise, BeatConstruction):
            playback = (
                self._immediate_playback
                if immediate
                else self._answer_playback
            )
            # Keep the main beat at 600 ms in every meter.
            quarter_ms = 600 if BEAT_METERS[q.answer][1] == 4 else 400
            playback.play_rhythm(q.rhythm, quarter_ms=quarter_ms)
            return
        if notes and self.exercise.has_sound:
            scale = q.construct_scale is not None or isinstance(
                self.exercise,
                ScaleIdentification,
            )
            gap = DEFAULT_NOTE_GAP_MS
            if scale:
                gap = SCALE_GAP_MS
            elif not immediate and (q.fingerboard or q.picture):
                gap = self.fingerboard.feedback_gap_ms()
            elif self.staff.interval_voices and len(notes) == 2:
                gap = MELODIC_INTERVAL_GAP_MS
            instrument = self.exercise.sound_instrument(
                self.fingerboard.sound_key,
            )  # the choice made a moment ago counts
            if immediate and self.shuffle_answers:
                sounds.play_notes(
                    notes,
                    gap_ms=gap,
                    warmup=scale,
                    instrument=instrument,
                )  # The sequence can outlast this exercise view.
            else:
                playback = (
                    self._immediate_playback
                    if immediate
                    else self._answer_playback
                )
                playback.play(
                    notes,
                    gap_ms=gap,
                    warmup=scale,
                    instrument=instrument,
                )
            return
        if self.exercise.has_sound and q.picture is None:
            sounds.play_correct(self.streak)
        if immediate:
            return
        if q.picture is not None:
            self.fingerboard.animate_silent_answer(600)
        elif q.place_clef:
            self._flash_clef()
        elif q.build_key:
            self._flash_fork()
        elif q.construct is not None or q.places_sequence:
            self._flash_note()
        else:
            self._flash(None, staff=True)
        self._advance_after_feedback(600)

    def _apply_rating(self, rating: Rating) -> None:
        """
        Schedule the completed card at the displayed interval and
        advance the exercise.

        Parameters
        ----------
        rating : Rating
            Passing grade selected by the learner.

        Examples
        --------
        Choosing Hard after a correct response still counts as a correct
        first attempt.
        """
        preview = self._rating_previews.get(rating)
        if preview is None:
            return
        assert self.learner is not None and self.question is not None
        self.learner.calendar.grade(
            type(self.exercise).__name__,
            profile=self.learner.profile.id,
            key=self.question.item_key(),
            mode=self._scheduler_mode,
            correct=True,
            manual_rating=rating,
            now=time.time(),
            preview=preview,
        )
        self._rating_previews.clear()
        self.rating_row.hide()
        self._advance_question()

    def _advance_after_feedback(self, delay: int) -> None:
        """
        Schedule the next question when automatic advancement is active.

        Parameters
        ----------
        delay : int
            Time in milliseconds to leave the completed feedback
            visible.

        Examples
        --------
        A question waiting for Next stays on screen after its final
        playback callback.
        """
        if self._rating_previews or not self.next_button.isHidden():
            return
        if self._hidden_at is not None:
            self._advance_remaining = delay
        else:
            motion.start_timer(self._advance, delay=delay)

    def _light_answer_notes(self, index: int | None) -> None:
        """
        Color the notes at the current audio onset and clear the
        feedback when playback ends.

        Parameters
        ----------
        index : int or None
            The sounding column, or None after the final column or an
            interruption.

        Examples
        --------
        >>> view = ExerciseView(
        ...     ScaleIdentification(),
        ...     rng=random.Random(2),
        ... )
        >>> view._record(True)
        >>> view._light_answer_notes(2)
        >>> list(view.staff.column_colors)
        [2]
        """
        q = self.question
        if q is None or not self.answered:
            return
        if isinstance(self.exercise, BeatConstruction):
            column = (
                index
                if index is not None and not q.rhythm[index].endswith("-rest")
                else None
            )
            self.beat_placement.highlight_column(column)
            if index is None:
                self._advance_after_feedback(0)
            return
        green = QColor(CORRECT_ANSWER_COLOR)
        if q.fingerboard or q.picture:
            self.fingerboard.set_sounding(index is not None)
        elif q.keyboard_notes or q.keyboard is not None:
            self.keyboard.set_highlight_color(
                green
                if index is not None
                else self.palette().color(QPalette.ColorRole.Highlight),
            )
        else:
            staff = (
                self._input()
                if q.construct is not None or q.construct_scale is not None
                else self.staff
            )
            staff.column_colors = {index: green} if index is not None else {}
            staff.update()
        if index is None:
            delay = (
                400
                if q.construct_scale is not None
                or isinstance(self.exercise, ScaleIdentification)
                else 150
            )
            self._advance_after_feedback(delay)

    def _update_score(self) -> None:
        """
        Show the score, the percentage right on the first try, and the
        streak.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> for correct in (True, True, True, False):
        ...     view.next_question()
        ...     view._record(correct)
        >>> view._update_score()
        >>> view.score.text()
        '3/4 (75%)   streak 0'
        """
        pct = f"{100 * self.correct / self.total:.0f}%" if self.total else "–"
        self.score.setText(
            f"{self.correct}/{self.total} ({pct})   streak {self.streak}",
        )
        self._refresh_queue_counts()

    def _refresh_queue_counts(self) -> None:
        """
        Update the calendar counts beside the score and streak while the
        exercise is visible.

        Examples
        --------
        A newly introduced card stays in the blue count until the first
        answer is submitted.
        """
        if (
            self.learner is None
            or self._scheduler_mode not in CALENDAR_SCHEDULERS
        ):
            self.queue_counts.hide()
            self._count_timer.stop()
            return
        if self.isVisible():
            key = (
                self.question.item_key()
                if self.question is not None and self.session.attempts == 0
                else None
            )
            counts, current = self.learner.calendar.study_counts(
                self.exercise,
                profile=self.learner.profile.id,
                mode=self._scheduler_mode,
                now=time.time(),
                current_key=key,
            )
            self.queue_counts.set_counts(
                counts,
                studying=True,
                current=current,
            )
            self.queue_counts.show()
            self._count_timer.start()
