"""
The exercise screen: a question, its answer buttons, the score, and a pane of settings that slides in from the right.

One `ExerciseView` works for every exercise. It asks the exercise (or, with a profile, the learner) for the next
`Question`, shows it as a staff, a keyboard or text, offers the answer buttons, and records each answer.

Examples
--------
>>> from alto.exercises.library import NoteNames
>>> view = ExerciseView(NoteNames(), rng=random.Random(1))
>>> # noinspection PyUnresolvedReferences
>>> view.question.answer in [button.text() for button in view.buttons]
True
"""

from __future__ import annotations

import random
import re
import time
from typing import TYPE_CHECKING

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    QTimer,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QKeySequence,
    QPalette,
    QShortcut,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from alto import settings as app_settings
from alto.audio import sounds
from alto.exercises.base import (
    Exercise,
    Question,
)
from alto.learning import Learner
from alto.settings import spell
from alto.theory.pitch import Note
from alto.theory.scales import format_key_signature
from alto.ui.circle import FifthsCircle
from alto.ui.colors import blend
from alto.ui.icons import (
    BOOK,
    SLIDERS,
    SPEAKER_MUTED,
    SPEAKER_ON,
    svg_icon,
)
from alto.ui.key_fork import (
    MAX_ACCIDENTALS,
    KeyFork,
)
from alto.ui.keyboard import KeyboardWidget
from alto.ui.reference import (
    ReferencePanel,
    reference_panel_for,
)
from alto.ui.settings_panel import settings_panel_for
from alto.ui.staff import (
    MAX_STEP,
    StaffWidget,
)
from alto.ui.staff_input import (
    ScaleInput,
    StaffInput,
)
from alto.ui.widgets import (
    HelpButton,
    SidebarToggle,
)

if TYPE_CHECKING:
    from collections.abc import Callable

SCALE_GAP_MS = 280  # the time between the notes of a scale that plays after a right answer


NOTE_CHOICE = re.compile(r"^[A-G][♯♭]?m?$")  # an answer that is a note or key name: C, F♯, B♭, or a minor key such as F♯m


def choice_keys(choices: list[str]) -> list[str]:
    """
    Choose a key for each answer button, so that every answer can be given from the keyboard.

    Nine answers or fewer take the digits 1 to 9. More than that, as on the piano keyboard, take the notes' own names: the
    letter for a natural, Shift and the letter for a sharp, Ctrl and the letter for a flat. A minor key, such as F♯m, is
    typed the same way as the major key of its name. Any other long list takes 1 to 9
    and then 0, and the rest can be reached with Tab.

    Parameters
    ----------
    choices : list of str
        The answers, in the order of their buttons.

    Returns
    -------
    list of str
        A key for each answer, such as "3" or "Shift+C"; "" for an answer that has none.

    Examples
    --------
    >>> choice_keys(["major", "minor", "diminished"])
    ['1', '2', '3']
    >>> choice_keys(list("CDEFGAB") + ["C♯", "B♭"] + ["F♯"])
    ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'Shift+C', 'Ctrl+B', 'Shift+F']
    >>> choice_keys([str(n) for n in range(12)])[8:]
    ['9', '0', '', '']
    """
    if len(choices) <= 9:
        return [str(i + 1) for i in range(len(choices))]
    if all(NOTE_CHOICE.match(c) for c in choices):
        keys = []
        for c in choices:
            sign = c[1] if len(c) > 1 and c[1] in "♯♭" else ""  # a trailing m only says that the key is minor
            keys.append(c[0] if not sign else f"{'Shift' if sign == '♯' else 'Ctrl'}+{c[0]}")
        return keys
    return [*"123456789", "0", *[""] * (len(choices) - 10)]


def second_row_keys(
    first: list[str],
    *,
    labels: list[str],
) -> list[str]:
    """
    Choose a key for each button of the second row of a two-part answer, such as the octave or the inversion.

    They must not be keys that the first row has. When the first row uses the digits the second row takes the home row,
    A S D F and so on; when the first row uses letters (the notes' names) it takes the digits, and an octave that is a single
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
    >>> second_row_keys(["1", "2", "3"], labels=["root position", "1st inversion"])
    ['A', 'S']
    >>> second_row_keys(["C", "Shift+C"], labels=["3", "4", "5"])
    ['3', '4', '5']
    """
    if any(k.isalpha() or "+" in k for k in first):
        return [label if label in "123456789" and len(label) == 1 else "" for label in labels]
    return [*"ASDFGHJKL"][: len(labels)] + [""] * max(0, len(labels) - 9)


def note_name(note: Note) -> str:
    """
    Return a note's name as it is written, with its octave: F♯4.

    Parameters
    ----------
    note : Note
        The note.

    Returns
    -------
    str
        The name in the naming the app is set to, then the octave number.

    Examples
    --------
    >>> note_name(Note.parse("F#4"))
    'F♯4'
    """
    return f"{spell(note, naming=app_settings.note_names.naming)}{note.octave}"


def note_words(note: Note) -> str:
    """
    Return a note's name in words, for a screen reader: "F sharp 4".

    Parameters
    ----------
    note : Note
        The note.

    Returns
    -------
    str
        The letter, then "sharp", "flat" or "natural" if it has a sign, then the octave number.

    Examples
    --------
    >>> note_words(Note.parse("F#4")), note_words(Note.parse("Bb3")), note_words(Note.parse("C4"))
    ('F sharp 4', 'B flat 3', 'C 4')
    """
    plain = spell(Note(note.octave, letter=note.letter), naming=app_settings.note_names.naming)
    sign = {-1: " flat", 1: " sharp", 0: ""}.get(note.accidental, "")
    return f"{plain}{sign} {note.octave}"


class ExerciseView(QWidget):
    """
    The screen for practising one exercise.

    Attributes
    ----------
    PANE_WIDTH : int
        The width of the settings pane when it is open, in pixels.
    REFERENCE_WIDTH : int
        The width of the reference pane when it is open, in pixels.
    exercise : Exercise
        The exercise being practised.
    learner : Learner or None
        Records every answer and chooses what to ask next; None asks at random.
    rng : random.Random
        The random number generator for new questions.
    correct : int
        Questions answered right first time.
    total : int
        Questions answered.
    streak : int
        Right answers in a row.
    question : Question or None
        The question on screen.
    answered : bool
        True once the question has been answered right.
    missed : bool
        True once the question has been answered wrong, so it no longer counts towards the score.
    buttons : list of QPushButton
        The answer buttons on screen.
    settings_panel : QWidget or None
        The exercise's settings, or None for an exercise with none.
    staff : StaffWidget
        Shows the notes of a question.
    keyboard : KeyboardWidget
        Shows the key of a keyboard question.
    input_staff : StaffInput
        The staff to click, for "place this note" questions.
    scale_input : ScaleInput
        The staff to click, for "place the notes of this scale" questions.
    fork : KeyFork
        The fork to pick a key signature on, for "build this key signature" questions.
    answer_button : QPushButton
        Hands in what was built with the fork or placed on the scale staff.
    book_btn : QToolButton or None
        Opens the exercise's reference in a pane on the right; None for an exercise that has none.
    reference_pane : QFrame or None
        The pane that holds the reference.
    lesson_requested : Signal
        Emitted with a lesson's key when the reference pane's lesson button is pressed.

    Examples
    --------
    >>> from alto.exercises.library import NoteNames
    >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
    >>> view.score.text()
    '0/0 (–)   streak 0'
    """

    lesson_requested = Signal(str)

    PANE_WIDTH = 290
    REFERENCE_WIDTH = 400

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
            The exercise to practise.
        rng : random.Random or None, default None
            The random number generator; a fresh one if None. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns the screen. Keyword-only.
        learner : Learner or None, default None
            Where to record answers and what to ask next; None asks at random and records nothing. Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import KeySignatures
        >>> view = ExerciseView(KeySignatures(), rng=random.Random(2))
        >>> view.settings_panel is not None  # the exercise has settings behind the gear button
        True
        """
        super().__init__(parent)
        self.exercise = exercise
        self.learner = learner  # records every answer and chooses what to ask next; None asks at random
        self.rng = rng or random.Random()
        self.correct = self.total = self.streak = 0
        self.question: Question | None = None
        self.answered = False
        self.missed = False
        self._attempts = 0  # answers given to the question on screen
        self._clock = time.monotonic()  # when the last answer was given, or the question appeared

        self.score = QLabel()
        self.prompt = QLabel()
        self.prompt.setStyleSheet("font-size: 16pt;")
        self.staff = StaffWidget(max_step=MAX_STEP)
        self.keyboard = KeyboardWidget()
        self.circle = FifthsCircle()  # for questions on the circle of fifths
        self.fork = KeyFork()  # for 'build this key signature' questions
        self.fork.changed.connect(self._fork_changed)
        self.answer_row = QWidget()  # Undo and Answer, under whatever is built: the fork, or the scale on the staff
        answer_lay = QHBoxLayout(self.answer_row)
        answer_lay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self.undo_button = QPushButton("Undo")  # takes back the last note or step of a scale
        self.undo_button.setMinimumHeight(40)
        self.undo_button.setShortcut("Backspace")
        self.undo_button.clicked.connect(self._undo_scale_note)
        self.place_button = QPushButton("Place note")  # puts the note at the caret on the staff, or marks the next step
        self.place_button.setMinimumHeight(40)
        self.place_button.setShortcut("Return")  # Return does the next thing: place, then Answer once everything is placed
        self.place_button.clicked.connect(self._place_here)
        self.answer_button = QPushButton("Answer")  # hands in the signature picked on the fork, or the scale placed
        self.answer_button.setMinimumHeight(40)
        self.answer_button.setShortcut("Return")
        self.answer_button.clicked.connect(self._answer)
        answer_lay.addWidget(self.undo_button)
        answer_lay.addWidget(self.place_button, 1)
        answer_lay.addWidget(self.answer_button, 1)
        self.input_staff = StaffInput()  # for 'place this note' questions
        self.input_staff.placed.connect(self._place)
        self.input_staff.accidental_cycled.connect(self._cycle_accidental)
        self.input_staff.caret_moved.connect(self._update_placement_status)
        self.scale_input = ScaleInput()  # for 'place this scale' questions
        self.scale_input.notes_changed.connect(self._scale_changed)
        self.scale_input.accidental_cycled.connect(self._cycle_accidental)
        self.scale_input.accidental_stepped.connect(self._cycle_accidental)  # the mouse wheel steps through them too
        self.scale_input.caret_moved.connect(self._update_placement_status)
        self.place_status = QLabel()  # says what the next click or key press will do, for those who cannot see the staff
        self.place_status.setWordWrap(True)
        self.place_status.setAccessibleName("What to do next")
        self.pitch_row = QWidget()  # lower / higher, to move the note on the staff without the mouse
        prow = QHBoxLayout(self.pitch_row)
        prow.setContentsMargins(
            0,
            4,
            0,
            0,
        )
        prow.addWidget(QLabel("Note"))
        self.pitch_buttons = {}
        for name, text, steps, tip in (
            ("octave_down", "Octave ↓", -7, "An octave lower (Page Down)"),
            ("lower", "Lower ↓", -1, "One line or space lower (Down arrow)"),
            ("higher", "Higher ↑", 1, "One line or space higher (Up arrow)"),
            ("octave_up", "Octave ↑", 7, "An octave higher (Page Up)"),
        ):
            b = QPushButton(text)
            b.setMinimumHeight(40)
            b.setToolTip(tip)
            b.setAccessibleName(tip.split(" (")[0])
            b.clicked.connect(lambda _=False, n=steps: self._move_caret(n))
            self.pitch_buttons[name] = b
            prow.addWidget(b, 1)
        self.accidental_row = QWidget()  # sharp / natural / flat, for questions that need an accidental
        arow = QHBoxLayout(self.accidental_row)
        arow.setContentsMargins(
            0,
            4,
            0,
            0,
        )
        arow.addWidget(QLabel("Accidental"))
        self.accidental_group = QButtonGroup(self)
        self.accidental_group.setExclusive(False)
        self.accidental_buttons = {}
        for acc, symbol in ((-1, "♭"), (0, "♮"), (1, "♯")):
            b = QPushButton(symbol)
            b.setCheckable(True)
            b.setMinimumHeight(40)
            b.setStyleSheet("font-size: 15pt;")
            b.clicked.connect(lambda _=False, a=acc: self._pick_accidental(a))
            key, word = {-1: ("-", "Flat"), 0: ("0", "Natural"), 1: ("+", "Sharp")}[acc]
            b.setShortcut(key)
            b.setToolTip(f"{word} (key {key}; the Left and Right arrows step through the signs)")
            b.setAccessibleName(word)
            self.accidental_buttons[acc] = b
            arow.addWidget(b, 1)
        self.step_row = QWidget()  # whole / half, for marking the steps between the notes of a scale
        srow = QHBoxLayout(self.step_row)
        srow.setContentsMargins(
            0,
            4,
            0,
            0,
        )
        srow.addWidget(QLabel("Step"))
        self.step_group = QButtonGroup(self)
        self.step_buttons = {}
        for step, name in (("W", "Whole step"), ("H", "Half step")):
            b = QPushButton(step)
            b.setCheckable(True)
            b.setMinimumHeight(40)
            b.setToolTip(f"{name} (key {step}; the arrow keys, the mouse wheel and a right click switch between them)")
            b.setAccessibleName(name)
            b.setShortcut(step)
            b.setStyleSheet("font-size: 15pt; font-weight: bold;")
            b.clicked.connect(lambda _=False, s=step: self.scale_input.set_pending_step(s))
            self.step_group.addButton(b)
            self.step_buttons[step] = b
            srow.addWidget(b, 1)
        self.step_buttons["W"].setChecked(True)
        self.scale_input.step_selected.connect(self._show_step)
        self.key_staff = StaffWidget(
            gap=8.0,
            side=12.0,
            note_offset=70.0,
            margin=3.6,
            compact=True,
        )  # key signature only
        self.key_staff.setFixedWidth(210)
        self.choice_box = QGridLayout()
        self._pair_token = 0  # counts questions, so a pending 'try again' reset can tell it is out of date
        self._pending: dict[str, tuple[str, QPushButton]] = {}
        self._found: set[str] = set()  # the right answers given so far to a question that needs several
        self._busy = False
        self._advance = QTimer(self)
        self._advance.setSingleShot(True)
        self._advance.timeout.connect(self.next_question)
        self._anims: list[QVariantAnimation] = []

        top = QHBoxLayout()
        self.sidebar_button = SidebarToggle()  # wired up by the main window
        top.addWidget(self.sidebar_button)
        top.addStretch()
        top.addWidget(self.score)
        self.help_btn = HelpButton(exercise.instructions)
        top.addWidget(self.help_btn)
        reference = reference_panel_for(exercise)
        self.book_btn: QToolButton | None = None
        self.reference_pane: QFrame | None = None
        self._reference: ReferencePanel | None = reference
        if reference is not None:
            reference.lesson_requested.connect(self.lesson_requested)
        if (
            reference is not None
        ):  # an experiment: a book beside the help that opens what there is to look up, in a pane on the right
            book = QToolButton()
            book.setIcon(svg_icon(BOOK, color=self.palette().color(QPalette.ColorRole.WindowText)))
            book.setIconSize(QSize(24, 24))
            book.setCheckable(True)
            book.setAutoRaise(True)
            book.setToolTip("Reference (experimental)")
            book.setAccessibleName("Reference")
            book.toggled.connect(self._toggle_reference)  # the pane it opens is built below
            top.addWidget(book)
            self.book_btn = book
        self.sound_btn = QToolButton()
        self.sound_btn.setAutoRaise(True)
        self.sound_btn.setIconSize(QSize(24, 24))
        self.sound_btn.clicked.connect(self._toggle_sound)
        self._show_sound_state()
        top.addWidget(self.sound_btn)
        self.settings_panel = settings_panel_for(exercise)
        if self.settings_panel:
            self.gear = QToolButton()
            self.gear.setIcon(svg_icon(SLIDERS, color=self.palette().color(QPalette.ColorRole.WindowText)))
            self.gear.setIconSize(QSize(24, 24))
            self.gear.setCheckable(True)
            self.gear.setAutoRaise(True)
            self.gear.setToolTip("Exercise settings")
            self.gear.setAccessibleName("Exercise settings")
            top.addWidget(self.gear)
        main = QWidget()
        lay = QVBoxLayout(main)
        lay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        lay.addLayout(top)
        lay.addWidget(self.prompt)
        lay.addWidget(self.staff, alignment=Qt.AlignmentFlag.AlignHCenter)  # a capped staff sits in the middle
        lay.addWidget(self.circle, 1)
        lay.addWidget(self.fork, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self.input_staff, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self.scale_input, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self.place_status)
        lay.addWidget(self.pitch_row)
        lay.addWidget(self.accidental_row)
        lay.addWidget(self.step_row)
        lay.addWidget(self.answer_row)
        lay.addWidget(self.key_staff, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(self.keyboard)
        lay.addLayout(self.choice_box)
        self.octave_row = QWidget()  # shown only when the answer needs an octave as well as a name
        self.octave_box = QHBoxLayout(self.octave_row)
        self.octave_box.setContentsMargins(
            0,
            4,
            0,
            0,
        )
        lay.addWidget(self.octave_row)
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
            pane_lay.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)  # let the pane shrink to zero while animating
            self.settings_panel.setFixedWidth(self.PANE_WIDTH - 2 * 9)
            pane_lay.addWidget(self.settings_panel, 1)  # fill the pane so long pages (Range) can scroll
            self.pane.hide()
            outer.addWidget(self.pane)
            self._pane_anim = QPropertyAnimation(self.pane, b"maximumWidth", self)
            self._pane_anim.setDuration(220)
            self._pane_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._pane_anim.finished.connect(self._pane_settled)
            self.gear.toggled.connect(self._toggle_pane)
            self.settings_panel.changed.connect(self.next_question)  # apply new settings right away
            self.settings_panel.restyled.connect(self.circle.update)  # a new look keeps the question
        if reference is not None and self.book_btn is not None:
            ref_pane = QFrame()
            ref_pane.setObjectName("settingsPane")
            ref_pane.setFrameShape(QFrame.Shape.StyledPanel)
            ref_pane.setMinimumWidth(0)
            ref_pane.setMaximumWidth(0)
            book_lay = QVBoxLayout(ref_pane)
            book_lay.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
            reference.setFixedWidth(self.REFERENCE_WIDTH - 2 * 9)
            book_lay.addWidget(reference, 1)
            ref_pane.hide()
            outer.addWidget(ref_pane)
            self.reference_pane = ref_pane
            self._reference_anim = QPropertyAnimation(ref_pane, b"maximumWidth", self)
            self._reference_anim.setDuration(220)
            self._reference_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._reference_anim.finished.connect(self._reference_settled)
        self.buttons: list[QPushButton] = []
        self._arrow_keys = [
            self._bind(sequence, action=lambda action_name=name: self._key_action(action_name))
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
            self._bind(name, action=lambda letter=letter: self._jump_to_letter(letter))
            for letter, name in enumerate("CDEFGAB")  # C is 0, D is 1 ... B is 6, as a note's letter counts
        ]
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)  # the screen can be given the keyboard when it opens
        self.next_question()

    def _bind(
        self,
        sequence: str,
        *,
        action: Callable[[], object],
    ) -> QShortcut:
        """
        Bind a key to something to do, for as long as the keyboard is anywhere on this screen.

        The key is off until it is switched on, so that it only works for the questions that use it. It does not work while
        the keyboard is in the exercise list or elsewhere outside the screen, where the same keys do other things.

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
        >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
        >>> bound = view._bind("Up", action=lambda: None)
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

        The sound button is a mute for the whole app, so this changes `sounds.enabled`, not just this exercise.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
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
        Show the sound button's icon and tooltip for whether sound is on.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
        >>> view._show_sound_state()
        >>> view.sound_btn.toolTip().startswith(("Sound on", "Muted"))
        True
        """
        color = self.palette().color(QPalette.ColorRole.WindowText)
        self.sound_btn.setIcon(svg_icon(SPEAKER_ON if sounds.enabled else SPEAKER_MUTED, color=color))
        self.sound_btn.setToolTip("Sound on (click to mute)" if sounds.enabled else "Muted (click to unmute)")
        self.sound_btn.setAccessibleName("Sound on" if sounds.enabled else "Sound muted")

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
        >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
        >>> view._toggle_pane(True)
        >>> view._pane_anim.endValue()
        290
        """
        if open_ and self.book_btn is not None:
            self.book_btn.setChecked(False)  # the two panes share the right-hand side
        self._pane_anim.stop()
        self.pane.show()
        self._pane_anim.setStartValue(self.pane.maximumWidth())
        self._pane_anim.setEndValue(self.PANE_WIDTH if open_ else 0)
        self._pane_anim.start()

    def _pane_settled(self) -> None:
        """
        Hide the pane once it has finished sliding shut.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
        >>> view._pane_settled()  # the pane starts closed
        >>> view.pane.isVisible()
        False
        """
        if self.pane.maximumWidth() == 0:
            self.pane.hide()

    def _toggle_reference(self, open_: bool) -> None:
        """
        Slide the reference pane open or closed.

        Opening it closes the settings pane, as they share the right-hand side.

        Parameters
        ----------
        open_ : bool
            True to open it, False to close it.

        Examples
        --------
        >>> from alto.exercises.library import CircleOfFifths
        >>> view = ExerciseView(CircleOfFifths(), rng=random.Random(1))
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
        self._reference_anim.setEndValue(self.REFERENCE_WIDTH if open_ else 0)
        self._reference_anim.start()

    def _reference_settled(self) -> None:
        """
        Hide the reference pane once it has finished sliding shut.

        Examples
        --------
        >>> from alto.exercises.library import CircleOfFifths
        >>> view = ExerciseView(CircleOfFifths(), rng=random.Random(1))
        >>> view._reference_settled()  # the pane starts closed
        >>> view.reference_pane is not None and view.reference_pane.isVisible()
        False
        """
        if self.reference_pane is not None and self.reference_pane.maximumWidth() == 0:
            self.reference_pane.hide()

    def _pick_question(self) -> Question:
        """
        Choose the next question.

        Returns
        -------
        Question
            One drawn by what the learner needs, or at random without a profile. The one just asked is avoided.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
        >>> isinstance(view._pick_question(), Question)
        True
        """
        if self.learner is None:
            return self.exercise.generate(self.rng)
        return self.learner.pick(self.exercise, rng=self.rng, avoid=self.question.item_key() if self.question else None)

    def next_question(self) -> None:
        """
        Show the next question: its staff, keyboard or text, and a fresh set of answer buttons.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
        >>> view.next_question()
        >>> # noinspection PyUnresolvedReferences
        >>> view.answered, len(view.buttons) == len(view.question.choices)
        (False, True)
        """
        self._advance.stop()
        for animation in self._anims:  # a fade still running would colour buttons that are about to be replaced
            animation.stop()
            animation.deleteLater()
        self._anims.clear()
        q = self.question = self._pick_question()
        self.answered = False
        self.missed = False
        self._attempts = 0
        self._clock = time.monotonic()
        self._pair_token += 1  # cancels a pending 'try again' reset
        self._pending = {}  # 'name' / 'octave' -> (text, button), for two-part answers
        self._busy = False
        self.prompt.setText(q.prompt)
        self.prompt.setVisible(bool(q.prompt) and not q.caption)  # some need none; a caption goes on the staff
        construct = q.construct is not None
        scale = q.construct_scale is not None
        self.staff.setVisible((bool(q.staff) or q.show_staff) and not construct and not scale)
        self.fork.setVisible(q.build_key)
        self.circle.setVisible(q.circle is not None)
        if q.circle is not None:
            self.circle.show_question(q.circle_kind, place=q.circle, ring=q.circle_ring, key=q.circle_key, title=q.caption)
        self._found = set()  # the right answers given so far to a question that needs several
        if q.build_key:
            self.fork.locked = False
            self.fork.set_marker_color(None)
            self.fork.set_value(0, slide=False)
        self.input_staff.setVisible(construct)
        self.scale_input.setVisible(scale)
        if construct:
            self.input_staff.reset(q.clef, key=q.key)
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
        self._show_placement_rows()
        self.keyboard.setVisible(q.keyboard is not None)
        self.key_staff.setVisible(q.key_staff)
        self.key_staff.show_notes([], clef="treble", key=q.key)
        self.keyboard.max_key_width = 30.0 if q.key_staff else 38.0  # leave room for the staff above
        self.keyboard.show_key(q.keyboard.midi if q.keyboard else None, span=q.keyboard_range)
        self.staff.key_room = MAX_ACCIDENTALS if q.build_key else 0  # the staff does not change width as the signature does
        self.staff.show_notes(
            q.staff,
            clef=q.clef,
            key=0 if q.build_key else q.key,  # a signature to build starts from a blank staff
            value=q.value,
            caption=q.caption,
        )
        for b in self.buttons:
            b.setShortcut(QKeySequence())  # a button waiting to be deleted must not share its key with the new one
            b.deleteLater()
        self.buttons = []
        for col in range(self.choice_box.columnCount()):
            self.choice_box.setColumnStretch(col, 0)
        keys = choice_keys(q.choices)
        for i, c in enumerate(q.choices):
            b = QPushButton(c)
            b.setMinimumHeight(40)
            if keys[i]:  # every answer can be given from the keyboard
                b.setShortcut(keys[i])
                b.setToolTip(f"Key {keys[i]}")
            if q.octaves:
                b.setCheckable(True)
                b.clicked.connect(lambda _=False, choice=c, btn=b: self._pick("name", text=choice, button=btn))
            else:
                b.clicked.connect(lambda _=False, choice=c, btn=b: self.submit(choice, button=btn))
            row, col = q.grid[c] if q.grid else (0, i)
            self.choice_box.addWidget(b, row, col)
            self.buttons.append(b)
        for col in {(q.grid[c][1] if q.grid else i) for i, c in enumerate(q.choices)}:
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
            self.octave_box.addWidget(QLabel(q.second_label))
            second_keys = second_row_keys(keys, labels=q.octaves)
            for i, octave in enumerate(q.octaves):
                b = QPushButton(octave)
                b.setMinimumHeight(40)
                if second_keys[i]:  # a key that the first row does not use
                    b.setShortcut(second_keys[i])
                    b.setToolTip(f"Key {second_keys[i]}")
                b.setCheckable(True)
                b.clicked.connect(lambda _=False, text=octave, btn=b: self._pick("octave", text=text, button=btn))
                self.octave_box.addWidget(b, 1)
                self.buttons.append(b)
        self._update_score()

    @staticmethod
    def _style(color: QColor) -> str:
        """
        Return the style sheet that colours an answer button.

        Parameters
        ----------
        color : QColor
            The background colour, with white text on it.

        Returns
        -------
        str
            Qt style sheet text.

        Examples
        --------
        >>> ExerciseView._style(QColor("#2e7d32"))
        'QPushButton, QPushButton:disabled { background: #2e7d32; color: white; }'
        """
        return f"QPushButton, QPushButton:disabled {{ background: {color.name()}; color: white; }}"

    def _flash(
        self,
        button: QPushButton,
        *,
        target: str,
        staff: bool = False,
    ) -> None:
        """
        Fade a button (and optionally the notes) from the staff's ink to a colour over a short time.

        Parameters
        ----------
        button : QPushButton
            The button to colour.
        target : str
            The colour to fade to, such as '#2e7d32'. Keyword-only.
        staff : bool, default False
            Also colour the notes on the staff, or the highlighted key. Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
        >>> view._flash(view.buttons[0], target="#2e7d32")
        >>> len(view._anims)
        1
        """
        end, start = QColor(target), QColor("black")
        anim = QVariantAnimation(self)
        anim.setDuration(350)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)

        def step(t: float) -> None:
            """
            Set the colours for one moment of the fade.

            Parameters
            ----------
            t : float
                How far through the fade: 0 at the start, 1 at the end.

            Examples
            --------
            >>> step(0.5)  # doctest: +SKIP
            """
            c = blend(start, b=end, t=t)
            button.setStyleSheet(self._style(c))
            if staff:
                self.staff.set_note_color(c if t > 0 else None)
                if self.question and self.question.keyboard:
                    self.keyboard.set_highlight_color(c if t > 0 else self.palette().color(QPalette.ColorRole.Highlight))

        anim.valueChanged.connect(step)
        self._anims.append(anim)
        anim.start()

    def _input(self) -> StaffInput:
        """
        Return the staff the learner is clicking: the one for a scale, or the one for a single note.

        Returns
        -------
        StaffInput
            `scale_input` while a scale is asked for, otherwise `input_staff`.

        Examples
        --------
        >>> from alto.exercises.library import NoteConstruction
        >>> view = ExerciseView(NoteConstruction(), rng=random.Random(2))
        >>> view._input() is view.input_staff
        True
        """
        q = self.question
        return self.scale_input if q is not None and q.construct_scale is not None else self.input_staff

    def _set_accidental(self, accidental: int | None) -> None:
        """
        Use a sign for the next note, light its button and update the preview.

        Parameters
        ----------
        accidental : int or None
            -1 for a flat, 0 for a natural, 1 for a sharp, or None to follow the key signature.

        Examples
        --------
        >>> from alto.exercises.library import NoteConstruction
        >>> view = ExerciseView(NoteConstruction(), rng=random.Random(2))
        >>> view._set_accidental(1)
        >>> view.input_staff.accidental, view.accidental_buttons[1].isChecked()
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

        The buttons act like a radio group, and clicking the lit one again clears it.

        Parameters
        ----------
        accidental : int
            The sign of the button that was clicked: -1, 0 or 1.

        Examples
        --------
        >>> from alto.exercises.library import NoteConstruction
        >>> view = ExerciseView(NoteConstruction(), rng=random.Random(2))
        >>> view.accidental_buttons[-1].click()
        >>> view.input_staff.accidental
        -1
        >>> view.accidental_buttons[-1].click()  # clicking the lit one again clears it
        >>> view.input_staff.accidental is None
        True
        """
        lit = self.accidental_buttons[accidental].isChecked()  # the click has already toggled it
        self._set_accidental(accidental if lit else None)

    def _cycle_accidental(self, direction: int = 1) -> None:
        """
        Step to the next sign after a right click on the staff, or to the one before when the wheel is turned the other way.

        The order is no sign, sharp, flat and (under a key signature) natural, then round again. It does nothing unless the
        question asks for signs.

        Parameters
        ----------
        direction : int, default 1
            1 for the next sign, -1 for the one before.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
        >>> view._cycle_accidental()  # not a "place this note" question: nothing happens
        >>> view.input_staff.accidental is None
        True
        >>> from alto.exercises.library import ScaleConstruction
        >>> view = ExerciseView(ScaleConstruction(), rng=random.Random(1))
        >>> view._cycle_accidental(-1)  # back from no sign goes round to the flat
        >>> view.scale_input.accidental
        -1
        """
        q = self.question
        if q and (q.construct is not None or q.construct_scale is not None) and q.accidentals:
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
            current = self._input().accidental
            self._set_accidental(order[(order.index(current) + direction) % len(order)] if current in order else None)

    def _flash_note(self, target: str) -> None:
        """
        Fade the placed note from the staff's ink to a colour.

        Parameters
        ----------
        target : str
            The colour to fade to, such as '#c62828'.

        Examples
        --------
        >>> from alto.exercises.library import NoteConstruction
        >>> view = ExerciseView(NoteConstruction(), rng=random.Random(2))
        >>> view._flash_note("#c62828")
        >>> len(view._anims)
        1
        """
        end, start = QColor(target), QColor("black")
        anim = QVariantAnimation(self)
        anim.setDuration(350)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.valueChanged.connect(lambda t: self._input().set_note_color(blend(start, b=end, t=t)))
        self._anims.append(anim)
        anim.start()

    def _place(self, note: Note) -> None:
        """
        Check a note that was clicked onto the staff against the one asked for.

        A right note is scored, fades green, plays and moves on; a wrong one fades red and the staff clears so another can be
        tried.

        Parameters
        ----------
        note : Note
            The note that was placed.

        Examples
        --------
        >>> from alto.exercises.library import NoteConstruction
        >>> sounds.enabled = False
        >>> view = ExerciseView(NoteConstruction(), rng=random.Random(2))
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
        self._record(ok, choice=f"{spell(note, naming=app_settings.note_names.naming)}{note.octave}")
        self.input_staff.locked = True
        if ok:
            self.answered = True
            self._flash_note("#2e7d32")
            if self.exercise.has_sound:
                sounds.play_notes([[q.construct]])
            self._advance.start(1200)
        else:
            self.missed = True
            self._busy = True
            self._flash_note("#c62828")
            token = self._pair_token

            def retry() -> None:
                """
                Clear the staff so a wrong placement can be tried again, unless a new question has replaced it.

                Examples
                --------
                >>> retry()  # doctest: +SKIP
                """
                if token != self._pair_token:  # a new question replaced this one
                    return
                self.input_staff.locked = False
                self.input_staff.show_note(None)
                self._busy = False
                self.input_staff.refresh_preview()  # the note at the caret comes back, for the keyboard
                self._show_placement_rows()

            QTimer.singleShot(900, retry)
        self._show_placement_rows()
        self._update_score()

    def _answer(self) -> None:
        """
        Hand in what was built: the key signature on the fork, or the scale on the staff.

        Examples
        --------
        >>> from alto.exercises.library import KeySignatureConstruction
        >>> view = ExerciseView(KeySignatureConstruction(), rng=random.Random(2))
        >>> # noinspection PyUnresolvedReferences
        >>> view.fork.set_value(view.question.key, slide=False)
        >>> view._answer()
        >>> view.answered
        True
        >>> view._advance.stop()
        """
        q = self.question
        if q and q.build_key:
            self._check_built()
        elif q and q.construct_scale is not None:
            self._check_scale()

    def _scale_changed(self) -> None:
        """
        Get ready for what comes next on the scale staff: the sign is used up, and the right buttons are shown.

        Examples
        --------
        >>> from alto.exercises.library import ScaleConstruction
        >>> view = ExerciseView(ScaleConstruction(), rng=random.Random(2))
        >>> view._set_accidental(1)
        >>> view._scale_changed()
        >>> view.scale_input.accidental is None, view.answer_button.isEnabled()
        (True, False)
        """
        if self.scale_input.accidental is not None:
            self._set_accidental(None)
        self._show_placement_rows()

    def _show_placement_rows(self) -> None:
        """
        Show the buttons for what the question is waiting for, and let Place and Answer work when they can.

        For a note or a scale on the staff the pitch and sign buttons show while notes are being placed, the whole and half
        step buttons while steps are, and neither once everything is down. Place does the next thing, and Answer takes over
        from it once everything is placed. For a key signature on the fork only Answer shows.

        Examples
        --------
        >>> from alto.exercises.library import ScaleConstruction
        >>> view = ExerciseView(ScaleConstruction(), rng=random.Random(2))
        >>> view._show_placement_rows()
        >>> view.step_row.isHidden(), view.answer_button.isEnabled(), view.place_button.isEnabled()
        (True, False, True)
        """
        q = self.question
        if q is None:
            return
        note, scale, fork = q.construct is not None, q.construct_scale is not None, q.build_key
        staff = self._input()
        placing_notes = note or (scale and not self.scale_input.complete)
        steps_turn = scale and self.scale_input.placing_steps
        live = not self.answered and not self._busy
        self.answer_row.setVisible(note or scale or fork)
        self.place_status.setVisible(note or scale)
        self.pitch_row.setVisible(placing_notes)
        self.accidental_row.setVisible(q.accidentals and placing_notes)
        self.step_row.setVisible(steps_turn)
        self.undo_button.setVisible(scale)
        self.place_button.setVisible(note or scale)
        label = "Mark step" if steps_turn else "Place note"
        if self.place_button.text() != label:
            self.place_button.setText(label)
            self.place_button.setShortcut("Return")  # setting a button's text makes it forget its shortcut
        self.place_button.setEnabled(live and not (scale and self.scale_input.done))
        self.answer_button.setVisible(scale or fork)
        self.answer_button.setEnabled(live if fork else live and self.scale_input.done)
        for key in self._arrow_keys:
            key.setEnabled(note or scale or fork)
        for key in self._letter_keys:
            key.setEnabled(placing_notes and not fork)
        if note or scale:
            staff.setAccessibleName("Staff: place the scale" if scale else "Staff: place the note")
            self._update_placement_status()

    def _update_placement_status(self) -> None:
        """
        Say what the next click or key press will do, in the line under the staff and for screen readers.

        Examples
        --------
        >>> from alto.exercises.library import NoteConstruction
        >>> view = ExerciseView(NoteConstruction(), rng=random.Random(2))
        >>> view.place_status.text()
        'Press ↑ or ↓ to choose a note, then Return to place it.'
        >>> view.input_staff.move_cursor(0)
        >>> view.place_status.text().startswith("Note to place: ")
        True
        """
        shown, spoken = self._placement_text()
        self.place_status.setText(shown)
        self.place_status.setAccessibleDescription(spoken)
        q = self.question
        if q is not None and (q.construct is not None or q.construct_scale is not None):
            self._input().setAccessibleDescription(spoken)

    def _placement_text(self) -> tuple[str, str]:
        """
        Work out what to say about the staff being clicked: what is to be placed next, and where the caret is.

        Returns
        -------
        tuple of str and str
            The line shown under the staff, and the same said in words for a screen reader.

        Examples
        --------
        >>> from alto.exercises.library import ScaleConstruction
        >>> view = ExerciseView(ScaleConstruction(), rng=random.Random(2))
        >>> view._placement_text()[0]
        'Note 1 of 8: press ↑ or ↓ to choose a note, then Return to place it.'
        """
        q = self.question
        if q is None or (q.construct is None and q.construct_scale is None):
            return "", ""
        staff = self._input()
        if q.construct_scale is not None:
            if self.scale_input.placing_steps:
                number, of = len(self.scale_input.steps) + 1, self.scale_input.slots - 1
                pending = self.scale_input.pending_step
                words = "a whole step" if pending == "W" else "a half step"
                return (
                    f"Step {number} of {of}: {pending}. Press W or H to choose, then Return to mark it.",
                    f"Step {number} of {of}: {words}. Press W or H to choose, then Return to mark it.",
                )
            if self.scale_input.done:
                return "Everything is placed. Press Return to answer.", "Everything is placed. Press Return to answer."
            head = f"Note {len(self.scale_input.notes) + 1} of {self.scale_input.slots}"
        else:
            head = "Note to place"
        caret = staff.caret_note()
        if caret is not None:
            return f"{head}: {note_name(caret)}", f"{head}: {note_words(caret)}"
        if q.construct_scale is None:  # a single note has no number to put in front of the advice
            return (
                "Press ↑ or ↓ to choose a note, then Return to place it.",
                "Press the up or down arrow to choose a note, then Return to place it.",
            )
        return (
            f"{head}: press ↑ or ↓ to choose a note, then Return to place it.",
            f"{head}: press the up or down arrow to choose a note, then Return to place it.",
        )

    def _key_action(self, name: str) -> None:
        """
        Do what an arrow key or Page Up or Page Down asks, which depends on what is being answered.

        On the fork Up and Right add a sharp, Down and Left a flat, and Home goes back to none. On the staff Up and Down
        move the note a line or space and Page Up and Page Down an octave, and Left and Right step through the signs. While
        steps are marked all four arrows switch between whole and half.

        Parameters
        ----------
        name : str
            "up", "down", "left", "right", "pageup", "pagedown" or "home".

        Examples
        --------
        >>> from alto.exercises.library import KeySignatureConstruction
        >>> view = ExerciseView(KeySignatureConstruction(), rng=random.Random(2))
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
                elif name == "home":  # back to the natural sign, no sharps or flats
                    self.fork.set_value(0)
            return
        if q.construct is None and q.construct_scale is None:
            return
        if q.construct_scale is not None and self.scale_input.placing_steps:
            if name in {"up", "down", "left", "right"} and not self.scale_input.locked:
                self.scale_input.toggle_step()
        elif name in {"up", "down", "pageup", "pagedown"}:
            self._move_caret({"up": 1, "down": -1, "pageup": 7, "pagedown": -7}[name])
        elif name == "right":
            self._cycle_accidental(1)
        elif name == "left":
            self._cycle_accidental(-1)

    def _move_caret(self, steps: int) -> None:
        """
        Move the note that the keyboard would place, up or down the staff.

        Parameters
        ----------
        steps : int
            How many lines and spaces: positive is up, negative down, and 7 is an octave.

        Examples
        --------
        >>> from alto.exercises.library import NoteConstruction
        >>> view = ExerciseView(NoteConstruction(), rng=random.Random(2))
        >>> view._move_caret(1)
        >>> view.input_staff.caret is not None
        True
        """
        q = self.question
        if q is None or self.answered or self._busy or (q.construct is None and q.construct_scale is None):
            return
        if q.construct_scale is not None and not self.scale_input.placing_steps:
            self.scale_input.move_cursor(steps)
        elif q.construct is not None:
            self.input_staff.move_cursor(steps)

    def _jump_to_letter(self, letter: int) -> None:
        """
        Move the note that the keyboard would place to the nearest one with a letter name.

        Parameters
        ----------
        letter : int
            The letter, counting from C as 0.

        Examples
        --------
        >>> from alto.exercises.library import NoteConstruction
        >>> view = ExerciseView(NoteConstruction(), rng=random.Random(2))
        >>> view._jump_to_letter(4)
        >>> view.input_staff.caret % 7  # G is the fifth letter from C
        4
        """
        q = self.question
        if q is None or self.answered or self._busy:
            return
        if q.construct_scale is not None and not self.scale_input.placing_steps:
            self.scale_input.jump_to_letter(letter)
        elif q.construct is not None:
            self.input_staff.jump_to_letter(letter)

    def _place_here(self) -> None:
        """
        Place the note at the caret on the staff, or mark the next step, without the mouse.

        Examples
        --------
        >>> from alto.exercises.library import NoteConstruction
        >>> sounds.enabled = False
        >>> view = ExerciseView(NoteConstruction(), rng=random.Random(2))
        >>> view._place_here()  # the note at the starting place
        >>> view.total
        1
        >>> view._advance.stop()
        >>> sounds.enabled = True
        """
        q = self.question
        if q is None or self.answered or self._busy:
            return
        if q.construct_scale is not None:
            self.scale_input.place_caret()
        elif q.construct is not None:
            self.input_staff.place_caret()

    def _show_step(self, step: str) -> None:
        """
        Light the button of the step that the next click on the scale staff marks.

        Parameters
        ----------
        step : str
            "W" or "H".

        Examples
        --------
        >>> from alto.exercises.library import ScaleConstruction
        >>> view = ExerciseView(ScaleConstruction(), rng=random.Random(2))
        >>> view._show_step("H")
        >>> view.step_buttons["H"].isChecked(), view.step_buttons["W"].isChecked()
        (True, False)
        """
        self.step_buttons[step].setChecked(True)

    def _undo_scale_note(self) -> None:
        """
        Take back the last note placed on the scale staff.

        Examples
        --------
        >>> from alto.exercises.library import ScaleConstruction
        >>> view = ExerciseView(ScaleConstruction(), rng=random.Random(2))
        >>> view.scale_input.notes.append(Note.parse("C4"))
        >>> view._undo_scale_note()
        >>> view.scale_input.notes
        []
        """
        if not self.answered and not self._busy:
            self.scale_input.undo()

    def _check_scale(self) -> None:
        """
        Check the scale placed on the staff against the one asked for.

        A right scale is scored, turns green, plays and moves on. A wrong one turns red and the staff is cleared so that
        another can be tried; only the first try counts toward the score.

        Examples
        --------
        >>> from alto.exercises.library import ScaleConstruction
        >>> sounds.enabled = False
        >>> view = ExerciseView(ScaleConstruction(), rng=random.Random(2))
        >>> # noinspection PyTypeChecker,PyUnresolvedReferences
        >>> view.scale_input.notes = list(view.question.construct_scale)
        >>> view._check_scale()
        >>> view.answered, view.correct
        (True, 1)
        >>> view._advance.stop()
        >>> sounds.enabled = True
        """
        q = self.question
        if not q or q.construct_scale is None or self.answered or self._busy or not self.scale_input.done:
            return
        notes, steps, clef, caption = list(self.scale_input.notes), list(self.scale_input.steps), q.clef, q.caption
        with_steps, key = q.construct_steps is not None, q.key
        ok = q.check_scale(notes) and q.check_steps(steps)
        answer = " ".join(f"{spell(n, naming=app_settings.note_names.naming)}{n.octave}" for n in notes)
        self._record(ok, choice=f"{answer} | {' '.join(steps)}" if with_steps else answer)
        self.scale_input.locked = True
        if not ok:
            self._flash_note("#c62828")
        if ok:
            self.answered = True
            token = self._pair_token
            if self.exercise.has_sound:  # the notes turn green one by one as they play, even with the sound muted
                sounds.play_notes(
                    [[n] for n in notes],  # as the learner placed it, in whichever octave that was
                    gap_ms=SCALE_GAP_MS,
                    on_step=lambda i: self._light_scale_note(i, token=token),
                )
            self._advance.start(SCALE_GAP_MS * len(notes) + 400)  # on to the next question once the scale has played
        else:
            self.missed = True
            self._busy = True
            token = self._pair_token

            def retry() -> None:
                """
                Clear the staff so a wrong scale can be tried again, unless a new question has replaced it.

                Examples
                --------
                >>> retry()  # doctest: +SKIP
                """
                if token != self._pair_token:  # a new question replaced this one
                    return
                self.scale_input.reset_scale(clef, slots=len(notes), caption=caption, with_steps=with_steps, key=key)
                self._busy = False
                self._show_placement_rows()

            QTimer.singleShot(900, retry)
        self._show_placement_rows()
        self._update_score()

    def _light_scale_note(
        self,
        index: int | None,
        *,
        token: int,
    ) -> None:
        """
        Turn the notes of the scale green as they sound: the one that has just started and every one before it.

        The notes are black until the scale starts to play, and all of them are green once it has finished.

        Parameters
        ----------
        index : int or None
            The place of the note that has just started, from 0, or None once the last note has had its time.
        token : int
            Which question the scale was played for; nothing changes once another question has replaced it. Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import ScaleConstruction
        >>> view = ExerciseView(ScaleConstruction(), rng=random.Random(2))
        >>> view._light_scale_note(2, token=view._pair_token)
        >>> sorted(view.scale_input.column_colors)
        [0, 1, 2]
        >>> view._light_scale_note(None, token=view._pair_token)
        >>> len(view.scale_input.column_colors) == view.scale_input.slots
        True
        """
        if token != self._pair_token:
            return
        sounded = self.scale_input.slots if index is None else index + 1
        self.scale_input.column_colors = {i: QColor("#2e7d32") for i in range(sounded)}
        self.scale_input.update()

    def _fork_changed(self, count: int) -> None:
        """
        Show the signature picked on the fork on the staff.

        Parameters
        ----------
        count : int
            The signature picked: that many sharps if positive, flats if negative.

        Examples
        --------
        >>> from alto.exercises.library import KeySignatureConstruction
        >>> view = ExerciseView(KeySignatureConstruction(), rng=random.Random(2))
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
        Check the signature picked on the fork against the one asked for.

        A right one is scored, turns the circle green and moves on; a wrong one turns it red and the fork returns to the
        natural sign so another can be tried.

        Examples
        --------
        >>> from alto.exercises.library import KeySignatureConstruction
        >>> view = ExerciseView(KeySignatureConstruction(), rng=random.Random(2))
        >>> # noinspection PyUnresolvedReferences
        >>> view.fork.set_value(view.question.key, slide=False)
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
        self._flash_fork("#2e7d32" if ok else "#c62828")
        if ok:
            self.answered = True
            self._advance.start(1200)
        else:
            self.missed = True
            self._busy = True
            token = self._pair_token

            def retry() -> None:
                """
                Return the fork to the natural sign so a wrong signature can be tried again, unless a new question replaced it.

                Examples
                --------
                >>> retry()  # doctest: +SKIP
                """
                if token != self._pair_token:  # a new question replaced this one
                    return
                self.fork.set_marker_color(None)
                self.fork.set_value(0)
                self.fork.locked = False
                self._busy = False
                self._show_placement_rows()

            QTimer.singleShot(900, retry)
        self._show_placement_rows()
        self._update_score()

    def _flash_fork(self, target: str) -> None:
        """
        Fade the fork's circle from the ink colour to a colour.

        Parameters
        ----------
        target : str
            The colour to fade to, such as '#c62828'.

        Examples
        --------
        >>> from alto.exercises.library import KeySignatureConstruction
        >>> view = ExerciseView(KeySignatureConstruction(), rng=random.Random(2))
        >>> view._flash_fork("#c62828")
        >>> len(view._anims)
        1
        """
        end, start = QColor(target), self.palette().color(QPalette.ColorRole.Highlight)
        anim = QVariantAnimation(self)
        anim.setDuration(350)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.valueChanged.connect(lambda t: self.fork.set_marker_color(blend(start, b=end, t=t)))
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

        Only the first attempt at a question counts towards the score and the streak. Each attempt is recorded with its time,
        measured from the question appearing (first attempt) or the previous attempt.

        Parameters
        ----------
        ok : bool
            Whether the answer was right.
        choice : str, default ""
            What was answered. Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
        >>> view._record(True, choice="C")
        >>> view.total, view.correct, view.streak
        (1, 1, 1)
        """
        self._attempts += 1
        now = time.monotonic()
        seconds, self._clock = now - self._clock, now  # the first answer is timed from the question appearing
        if self.learner and self.question:
            self.learner.record(
                self.exercise,
                question=self.question,
                answer=choice,
                correct=ok,
                attempt_no=self._attempts,
                seconds=seconds,
            )
        if not self.missed:  # only the first attempt counts toward the score
            self.total += 1
            self.correct += ok
            self.streak = self.streak + 1 if ok else 0

    def _pick(
        self,
        part: str,
        *,
        text: str,
        button: QPushButton,
    ) -> None:
        """
        Choose one part of a two-part answer.

        A name and then an octave (or a chord type and an inversion), in either order; the answer is checked once both are set.

        Parameters
        ----------
        part : str
            "name" or "octave".
        text : str
            The text of the button. Keyword-only.
        button : QPushButton
            The button, which is lit while it is the chosen one. Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import ArpeggioNames
        >>> sounds.enabled = False
        >>> view = ExerciseView(ArpeggioNames(), rng=random.Random(11))
        >>> # noinspection PyUnresolvedReferences
        >>> kind, inversion = view.question.answer.split(view.question.joiner)
        >>> by_text = {button_.text(): button_ for button_ in view.buttons}
        >>> view._pick("name", text=kind, button=by_text[kind])
        >>> view._pick("octave", text=inversion, button=by_text[inversion])
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

        A right answer is scored through `submit`; a wrong one fades both buttons red and clears them so it can be tried again.

        Examples
        --------
        >>> from alto.exercises.library import ArpeggioNames
        >>> sounds.enabled = False
        >>> view = ExerciseView(ArpeggioNames(), rng=random.Random(11))
        >>> by_text = {button.text(): button for button in view.buttons}
        >>> # noinspection PyUnresolvedReferences
        >>> wrong_kind = next(c for c in view.question.choices if c != view.question.answer.split(view.question.joiner)[0])
        >>> view._pending = {"name": (wrong_kind, by_text[wrong_kind]), "octave": ("root position", by_text["root position"])}
        >>> view._submit_pair()
        >>> view.missed
        True
        >>> sounds.enabled = True
        """
        q = self.question
        assert q is not None
        (name, name_btn), (octave, octave_btn) = self._pending["name"], self._pending["octave"]
        choice = name + q.joiner + octave
        if q.check(choice):
            self._flash(octave_btn, target="#2e7d32")
            self.submit(choice, button=name_btn)  # scores it, flashes the name button, plays the note, moves on
            return
        self._record(False, choice=choice)
        self.missed = True
        self._busy = True
        for b in (name_btn, octave_btn):
            self._flash(b, target="#c62828")
        self._update_score()
        token = self._pair_token

        def reset() -> None:
            """
            Clear the two buttons after a wrong two-part answer, unless a new question has replaced them.

            Examples
            --------
            >>> reset()  # doctest: +SKIP
            """
            if token != self._pair_token:  # a new question replaced these buttons
                return
            for pressed in (name_btn, octave_btn):
                pressed.setStyleSheet("")
                pressed.setChecked(False)
            self._pending = {}
            self._busy = False

        QTimer.singleShot(700, reset)

    def submit(
        self,
        choice: str,
        *,
        button: QPushButton,
    ) -> None:
        """
        Check an answer chosen with a button.

        A right answer is scored, fades green, plays (unless the exercise is silent) and moves on after a moment; a wrong one
        fades red and its button is switched off, so another can be tried.

        Parameters
        ----------
        choice : str
            The text of the button that was pressed.
        button : QPushButton
            The button. Nothing happens if it is switched off. Keyword-only.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> sounds.enabled = False
        >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
        >>> question = view.question
        >>> # noinspection PyUnresolvedReferences
        >>> wrong = next(b for b in view.buttons if b.text() != question.answer)
        >>> view.submit(wrong.text(), button=wrong)
        >>> view.missed, wrong.isEnabled()
        (True, False)
        >>> # noinspection PyUnresolvedReferences
        >>> right = next(b for b in view.buttons if b.text() == question.answer)
        >>> # noinspection PyUnresolvedReferences
        >>> view.submit(question.answer, button=right)
        >>> view.answered
        True
        >>> view._advance.stop()
        >>> sounds.enabled = True
        """
        if self.answered or not self.question or not button.isEnabled():
            return
        q = self.question
        ok = q.check(choice)
        if ok and q.required:  # an answer with several parts: each is marked as it is found, and the last one answers
            self._found.add(choice)
            button.setEnabled(False)
            self._flash(button, target="#2e7d32")
            if not q.complete(self._found):
                self.circle.set_subtitle("and its other name")
                return
            choice = " ".join(name for name in q.required)
        self._record(ok, choice=choice)
        if q.circle is not None:  # the cell brightens and names itself, or flashes a warning
            if ok:
                self.circle.reveal()
            else:
                self.circle.flash_wrong()
        if ok:
            self.answered = True  # the other buttons stay as they are; only the one pressed animates
            self._flash(button, target="#2e7d32", staff=True)
            notes = q.staff or ([[q.keyboard]] if q.keyboard else [])
            if not self.exercise.has_sound:
                pass  # no tone for this exercise
            elif notes:
                sounds.play_notes(notes)
            else:
                sounds.play_correct(self.streak)
            self._advance.start(1200)
        else:
            self.missed = True
            button.setEnabled(False)
            self._flash(button, target="#c62828")
        self._update_score()

    def _update_score(self) -> None:
        """
        Show the score, the percentage right first time, and the streak.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> view = ExerciseView(NoteNames(), rng=random.Random(1))
        >>> view.total, view.correct = 4, 3
        >>> view._update_score()
        >>> view.score.text()
        '3/4 (75%)   streak 0'
        """
        pct = f"{100 * self.correct / self.total:.0f}%" if self.total else "–"
        self.score.setText(f"{self.correct}/{self.total} ({pct})   streak {self.streak}")
