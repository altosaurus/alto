"""Music displays and placement controls for an exercise question."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import TYPE_CHECKING, TypeVar

from PySide6.QtCore import QEvent, QObject, QSize, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPalette
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from alto import settings
from alto.exercises.base import Exercise, Question
from alto.exercises.library import (
    BEAT_METERS,
    BeatConstruction,
    BeatIdentification,
    IntervalConstruction,
    NoteNames,
    RythmicEquations,
    beat_meter,
)
from alto.exercises.packs import PackExercise
from alto.learning.practice_session import PracticeSession
from alto.theory.note_naming import DEGREE_NAMINGS, note_name, note_words
from alto.theory.pitch import ACCIDENTAL_SYMBOLS, Note
from alto.ui import motion
from alto.ui.circle import FifthsCircle
from alto.ui.colors import CORRECT_ANSWER_COLOR
from alto.ui.degree_text import DegreeLabel
from alto.ui.fingerboard import FingerboardWidget
from alto.ui.icons import set_palette_icon
from alto.ui.key_fork import MAX_ACCIDENTALS, KeyFork
from alto.ui.keyboard import KeyboardWidget
from alto.ui.meter_staff import BeatPlacementStaff, MeterStaff
from alto.ui.pictures import rhythm_picture, symbol_icon
from alto.ui.staff import (
    CORNER_RADIUS,
    MAX_STEP,
    StaffWidget,
    keyboard_key_staff,
)
from alto.ui.staff_input import (
    ClefInput,
    ScaleInput,
    SignatureInput,
    StaffInput,
)
from alto.ui.zoom import css, px

if TYPE_CHECKING:
    from alto.ui.exercise_controller import AnswerResult

_Widget = TypeVar("_Widget", bound=QWidget)


class QuestionView(QWidget):
    """
    Present a question's prompt, music, and placement editor.

    A question can use several displays together, such as a keyboard
    with a key signature above it. It has at most one placement editor.

    Examples
    --------
    >>> view = QuestionView()
    >>> q = Question("", choices=[], answer="C", show_staff=True)
    >>> _ = view.show_question(q, interval_voices=False)
    >>> isinstance(view.staff, StaffWidget) and view.editor is None
    True
    """

    note_submitted = Signal(object)
    scale_submitted = Signal(object, object)
    clef_submitted = Signal(str, int)
    fork_submitted = Signal(int)
    signature_submitted = Signal(object)
    beats_submitted = Signal(object)
    location_selected = Signal(bool)

    widget_created = Signal(QWidget)
    caret_moved = Signal(int)
    accidental_selected = Signal(int)
    beats_changed = Signal()

    def __init__(
        self,
        exercise: Exercise | None = None,
        *,
        center_controls: bool = False,
    ) -> None:
        """
        Make room for the question and its placement controls.

        Parameters
        ----------
        exercise : Exercise or None
            Exercise whose rhythm display and entry controls to build.
        center_controls : bool
            Center the editor and controls together for Order of Keys.

        Examples
        --------
        >>> QuestionView().keyboard is None
        True
        """
        super().__init__()
        self.exercise = exercise
        self.displayed_question: Question | None = None
        self._queue_notice = False
        self.progress = PracticeSession()
        self.busy = False
        self.caret_moved.connect(self.move_caret)
        self.accidental_selected.connect(self.pick_accidental)
        self.placement_hint = ""
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )
        self.rows = QVBoxLayout(self)
        self.rows.setContentsMargins(0, 0, 0, 0)
        self.prompt = DegreeLabel(self)
        self.prompt.setStyleSheet(css("font-size: 16pt;"))
        self.prompt.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        self.prompt.setWordWrap(True)
        prompt_row = QHBoxLayout()
        prompt_row.addStretch(1)
        prompt_row.addWidget(self.prompt, 100)
        prompt_row.addStretch(1)
        self.rows.addLayout(prompt_row)
        self.controls = QVBoxLayout()
        if center_controls:
            panel = QWidget()
            panel.setLayout(self.controls)
            self.controls.setContentsMargins(0, 0, 0, 0)
            self.rows.addWidget(panel, alignment=Qt.AlignmentFlag.AlignHCenter)
        else:
            self.rows.addLayout(self.controls)
        self.grid = QGridLayout()
        # Empty grid rows should take up no space between displays.
        for row in range(4):
            self.grid.addItem(QSpacerItem(0, 0), row, 0)
        self.controls.addLayout(self.grid)
        self._pictures = QGridLayout()
        self.rows.addLayout(self._pictures)
        self.review_interval_label = QLabel(self)
        self.review_interval_label.setToolTip(
            "Next review after a correct answer",
        )
        self.review_interval_label.hide()
        self._keyboard_interval_row = QWidget()
        self._keyboard_interval_layout = QHBoxLayout(
            self._keyboard_interval_row,
        )
        self._keyboard_interval_layout.setContentsMargins(0, 0, 0, 0)
        self.rows.addWidget(self._keyboard_interval_row)
        self._keyboard_interval_row.hide()
        self._keyboard_interval_row.installEventFilter(self)
        self.staff: StaffWidget | None = None
        self.keyboard: KeyboardWidget | None = None
        self.key_staff: StaffWidget | None = None
        self.circle: FifthsCircle | None = None
        self.fingerboard: FingerboardWidget | None = None
        self.editor: StaffInput | ClefInput | KeyFork | None = None
        if exercise is not None:
            self._build_placement_controls(exercise)
            self._build_rhythm_display(exercise)

    def _display(
        self,
        widget: _Widget | None,
        *,
        needed: bool,
        create: Callable[[], _Widget],
        layout: QGridLayout,
        row: int,
    ) -> _Widget | None:
        """
        Mount a requested display, reuse it, or remove it.

        Parameters
        ----------
        widget : QWidget or None
            Current display.
        needed : bool
            Whether the question uses this display.
        create : callable
            Constructor for the display.
        layout : QGridLayout
            Grid containing the display.
        row : int
            Row occupied by the widget.

        Returns
        -------
        QWidget or None
            Display for this question.

        Examples
        --------
        Consecutive keyboard questions reuse the same keyboard.
        """
        if needed and widget is None:
            widget = create()
            layout.addWidget(widget, row, 0)
            self.widget_created.emit(widget)
            widget.show()
        elif not needed and widget is not None:
            layout.removeWidget(widget)
            widget.hide()
            widget.deleteLater()
            return None
        return widget

    def show_prompt(self, text: str) -> None:
        """
        Show an instruction above the music.

        Parameters
        ----------
        text : str
            Instruction or feedback to display.

        Examples
        --------
        A MIDI miss shows the played pitch above the staff.
        """
        self.prompt.setText(text)
        self.prompt.show()

    def restore_prompt(self, q: Question) -> None:
        """
        Restore the question text and keep its current visibility.

        Parameters
        ----------
        q : Question
            Question whose caption or instruction replaces the feedback.

        Examples
        --------
        A correct MIDI answer clears the previous retry message.
        """
        self.prompt.setText(q.caption or q.prompt)

    def _show_question_prompt(
        self,
        q: Question,
        *,
        answer_width: int | None,
    ) -> None:
        """
        Show the instruction above the music when needed.

        Parameters
        ----------
        q : Question
            Question supplying the instruction and staff caption.
        answer_width : int or None
            Width limit to use without a staff, if supplied.

        Examples
        --------
        A rhythm equation shows its caption above the equation paper.
        """
        staff = self.note_input if q.construct is not None else self.staff
        width = self.maximumWidth() if answer_width is None else answer_width
        self.prompt.setMaximumWidth(staff.maximumWidth() if staff else width)
        if isinstance(self.exercise, RythmicEquations) and q.choices:
            self.prompt.setText(q.caption)
            self.prompt.setVisible(bool(q.caption))
            return
        prompt = q.prompt
        if (
            isinstance(self.exercise, NoteNames)
            and q.staff
            and not q.identify_scale
            and settings.note_names.naming in DEGREE_NAMINGS
        ):
            prompt = self.exercise.card_prompt(q)
        self.prompt.setText(prompt)
        self.prompt.setVisible(bool(prompt) and not q.caption)

    def show_question(
        self,
        q: Question,
        *,
        interval_voices: bool | None = None,
        answer_width: int | None = None,
        empty_queue: bool = False,
    ) -> bool:
        """
        Render the displays and editor requested by a question.

        Parameters
        ----------
        q : Question
            Music to display and input required.
        interval_voices : bool or None
            Override the exercise’s default interval voicing.
        answer_width : int or None
            Limit the prompt to the answer area when there is no staff.
            Defaults to the width limit of this view.
        empty_queue : bool
            Display a queue notice with no question available for input.

        Returns
        -------
        bool
            Whether the answer controls should use named meters.

        Examples
        --------
        Key Signature Construction shows both the staff and a key fork.
        """
        self.displayed_question = q
        self._queue_notice = empty_queue
        self.placement_hint = ""
        named_meter = self.show_rhythm(q)
        self._set_editor(q)
        self.staff = self._display(
            self.staff,
            needed=(bool(q.staff) or q.show_staff)
            and not (
                q.construct is not None or q.places_sequence or q.place_clef
            ),
            create=lambda: StaffWidget(max_step=MAX_STEP),
            layout=self.grid,
            row=0,
        )
        if self.staff is not None:
            self.staff.installEventFilter(self)
            if interval_voices is None:
                interval_voices = bool(
                    self.exercise and self.exercise.interval_voices,
                )
            self.staff.interval_voices = interval_voices
            self.staff.column_colors.clear()
            self.staff.key_room = MAX_ACCIDENTALS if q.build_key else 0
            self.staff.show_notes(
                q.staff,
                clef=q.clef,
                key=0 if q.build_key else q.written_key,
                value=q.value,
                notation_excerpt=q.notation_excerpt,
                notation_target=q.notation_target,
                locate_notation=q.notation_target is not None
                and not q.choices,
                caption=q.caption,
            )
        self._show_question_prompt(q, answer_width=answer_width)
        self.circle = self._display(
            self.circle,
            needed=q.circle is not None,
            create=FifthsCircle,
            layout=self.grid,
            row=1,
        )
        if self.circle is not None:
            self.circle.set_question(q)
        self.key_staff = self._display(
            self.key_staff,
            needed=q.key_staff,
            create=keyboard_key_staff,
            layout=self.grid,
            row=3,
        )
        if self.key_staff is not None:
            self.key_staff.show_notes([], clef="treble", key=q.key)
        self.keyboard = self._display(
            self.keyboard,
            needed=q.keyboard is not None or bool(q.keyboard_notes),
            create=KeyboardWidget,
            layout=self._pictures,
            row=0,
        )
        if self.keyboard is not None:
            self.keyboard.max_key_width = px(30.0 if q.key_staff else 38.0)
            if q.keyboard_notes:
                self.keyboard.show_keys(
                    [note.midi for note in q.keyboard_notes],
                    span=q.keyboard_range,
                )
            elif q.keyboard is not None:
                self.keyboard.show_key(q.keyboard.midi, span=q.keyboard_range)
        position = q.fingerboard or q.picture
        self.fingerboard = self._display(
            self.fingerboard,
            needed=position is not None,
            create=FingerboardWidget,
            layout=self._pictures,
            row=1,
        )
        if self.fingerboard is not None:
            self.fingerboard.show_position(position)
        if self.exercise is not None:
            self.symbol_row.setVisible(bool(q.place_clef))
            if q.construct is not None or q.places_sequence:
                for button in self.accidental_buttons.values():
                    button.setChecked(False)
            if q.place_signature:
                self.set_accidental(
                    -1 if q.starting_slots and q.key < 0 else 1,
                )
        return named_meter

    @property
    def active_beat_editor(self) -> BeatPlacementStaff | None:
        """Return the beat editor for the displayed rhythm."""
        q = self.displayed_question
        if isinstance(self.exercise, BeatConstruction) and q and q.rhythm:
            return self.beat_placement
        return None

    @property
    def interactive_question(self) -> Question | None:
        """Return the question that accepts input and feedback."""
        return None if self._queue_notice else self.displayed_question

    def show_intervals(self, intervals: tuple[str, ...]) -> None:
        """
        Position review intervals beside the current music.

        Parameters
        ----------
        intervals : tuple[str, ...]
            Review durations formatted for display.

        Examples
        --------
        Speed grading shows the three possible passing intervals.
        """
        self._keyboard_interval_row.hide()
        self.grid.setAlignment(Qt.AlignmentFlag(0))
        if not intervals:
            self.review_interval_label.hide()
            return
        staff = self.keyboard is None
        if len(intervals) == 1:
            heading = "Next interval:"
            text = ("\n" if staff else " ").join((heading, intervals[0]))
        else:
            heading = "Next intervals:"
            if staff:
                intervals = tuple(reversed(intervals))
            text = ("\n" if staff else "    ").join(intervals)
        self.review_interval_label.setAccessibleName(
            f"{heading} {', '.join(intervals)}",
        )
        self.review_interval_label.setText(text)
        self.review_interval_label.setMaximumWidth(
            self.review_interval_label.sizeHint().width(),
        )
        if staff:
            self.review_interval_label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
            )
            self.grid.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.grid.addWidget(
                self.review_interval_label,
                0,
                1,
                -1,
                1,
                Qt.AlignmentFlag.AlignBottom,
            )
        else:
            self.review_interval_label.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            )
            self._keyboard_interval_layout.addWidget(
                self.review_interval_label,
                alignment=Qt.AlignmentFlag.AlignRight,
            )
            self._align_keyboard_interval()
            self._keyboard_interval_row.show()
        self.review_interval_label.show()

    def _align_keyboard_interval(self) -> None:
        """
        Align the grade row with the last key, allowing longer text to
        extend left.

        Examples
        --------
        A short keyboard stays centered with the interval row ending
        beneath its right edge.
        """
        if self.keyboard is None:
            return
        width = self._keyboard_interval_row.width()
        margin = min(
            (width - self.keyboard.full_width()) // 2,
            width - self.review_interval_label.sizeHint().width(),
        )
        self._keyboard_interval_layout.setContentsMargins(
            0,
            0,
            max(0, margin),
            0,
        )

    def _set_editor(self, q: Question) -> None:
        """
        Mount the question's placement editor and reset its contents.

        Parameters
        ----------
        q : Question
            Question specifying the editor and its initial state.

        Examples
        --------
        A scale question uses a ScaleInput and a clef uses a ClefInput.
        """
        kind: type[StaffInput | KeyFork | ClefInput] | None = None
        if q.build_key:
            kind = KeyFork
        elif q.place_clef:
            kind = ClefInput
        elif q.place_signature:
            kind = SignatureInput
        elif q.places_sequence:
            kind = ScaleInput
        elif q.construct is not None:
            kind = StaffInput
        if self.editor is not None and type(self.editor) is not kind:
            if isinstance(self.editor, ClefInput):
                self.editor.placed.disconnect(self.clef_submitted)
            elif type(self.editor) is StaffInput:
                self.editor.placed.disconnect(self.note_submitted)
            self.grid.removeWidget(self.editor)
            self.editor.hide()
            self.editor.deleteLater()
            self.editor = None
        if kind is not None and self.editor is None:
            self.editor = kind()
            if isinstance(self.editor, ClefInput):
                self.editor.placed.connect(self.clef_submitted)
            elif type(self.editor) is StaffInput:
                self.editor.placed.connect(self.note_submitted)
            if (
                isinstance(self.editor, StaffInput)
                and self.exercise is not None
            ):
                self.editor.accidental_cycled.connect(self.cycle_accidental)
                self.editor.caret_moved.connect(self.update_placement_status)
                if isinstance(self.editor, ScaleInput):
                    self.editor.accidental_stepped.connect(
                        self.cycle_accidental,
                    )
                    self.editor.step_selected.connect(self.show_step)
            elif isinstance(self.editor, KeyFork):
                self.editor.changed.connect(self.fork_changed)
            self.grid.addWidget(self.editor, 2, 0)
            self.widget_created.emit(self.editor)
            self.editor.show()
        editor = self.editor
        if isinstance(editor, KeyFork):
            editor.reset()
        elif isinstance(editor, ClefInput):
            editor.reset(list(settings.CLEF_SYMBOLS), caption=q.caption)
        elif isinstance(editor, SignatureInput):
            editor.reset_signature(
                q.clef,
                key=q.key,
                caption=q.caption,
                starting_slots=q.starting_slots,
            )
        elif isinstance(editor, ScaleInput) and q.construct_scale is not None:
            editor.reset_scale(
                q.clef,
                slots=len(q.construct_scale),
                caption=q.caption,
                with_steps=q.construct_steps is not None,
                key=q.key,
            )
        elif isinstance(editor, StaffInput):
            editor.reset(
                q.clef,
                key=q.written_key,
                caption=q.caption,
                placement=q,
            )

    @property
    def note_input(self) -> StaffInput:
        """
        Access the active note placement editor.

        Returns
        -------
        StaffInput
            The editor mounted for this question.

        Examples
        --------
        Used by the note placement input handlers.
        """
        assert isinstance(self.editor, StaffInput)
        return self.editor

    @property
    def scale_input(self) -> ScaleInput:
        """
        Access the active scale or signature editor.

        Returns
        -------
        ScaleInput
            The editor mounted for this question.

        Examples
        --------
        Used by the scale or signature input handlers.
        """
        assert isinstance(self.editor, ScaleInput)
        return self.editor

    @property
    def clef_input(self) -> ClefInput:
        """
        Access the active clef placement editor.

        Returns
        -------
        ClefInput
            The editor mounted for this question.

        Examples
        --------
        Used by the clef placement input handlers.
        """
        assert isinstance(self.editor, ClefInput)
        return self.editor

    def _build_placement_controls(self, exercise: Exercise) -> None:
        """
        Build the placement controls for the
        exercise.

        Parameters
        ----------
        exercise : Exercise
            Exercise whose questions and controls are in use.

        Examples
        --------
        Interval Construction offers double sharps and double flats.
        """
        # a button for each clef symbol, under the staff, as another way
        # to choose one
        self.symbol_row = QWidget()
        symbol_lay = QHBoxLayout(self.symbol_row)
        symbol_lay.setContentsMargins(0, 0, 0, 0)
        symbol_lay.addStretch()
        self.symbol_group = QButtonGroup(self)
        self.symbol_buttons: dict[str, QPushButton] = {}
        for symbol in settings.CLEF_SYMBOLS:
            button = QPushButton()
            set_palette_icon(
                button,
                lambda palette, clef=symbol: symbol_icon(
                    clef,
                    color=palette.buttonText().color(),
                ),
            )
            button.setIconSize(QSize(px(56), px(56)))
            button.setAccessibleName(settings.CLEF_SYMBOL_NAMES[symbol])
            button.setCheckable(True)
            button.setMinimumHeight(px(68))
            button.setToolTip(
                f"{settings.CLEF_SYMBOL_NAMES[symbol]}"
                " (or turn the mouse wheel, or use Left and Right)",
            )
            button.clicked.connect(
                lambda _=False, chosen=symbol: self.clef_input.select(
                    chosen,
                ),
            )
            self.symbol_group.addButton(button)
            self.symbol_buttons[symbol] = button
            symbol_lay.addWidget(button)
        symbol_lay.addStretch()
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
            b.clicked.connect(
                lambda _=False, n=steps: self.caret_moved.emit(n),
            )
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
            b.clicked.connect(
                lambda _=False, a=acc: self.accidental_selected.emit(a),
            )
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
        for control in (
            self.symbol_row,
            self.place_status,
            self.pitch_row,
            self.accidental_row,
            self.step_row,
        ):
            self.controls.addWidget(control)

    def _build_rhythm_display(self, exercise: Exercise) -> None:
        """
        Mount the rhythm staff or equation paper for this exercise.

        Parameters
        ----------
        exercise : Exercise
            Exercise whose rhythm display is being built.

        Examples
        --------
        Beat Construction mounts a staff that accepts beat placements.
        """
        rhythm_widget: QWidget | None = None
        if isinstance(exercise, RythmicEquations):
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
        elif isinstance(exercise, (BeatConstruction, BeatIdentification)):
            if isinstance(exercise, BeatConstruction):
                self.beat_placement = BeatPlacementStaff()
                self.beat_placement.changed.connect(self.beats_changed.emit)
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
            self.rows.insertWidget(1, self.rhythm_scroll)

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
        >>> from alto.ui.exercise_page import ExercisePage
        >>> page = ExercisePage(RythmicEquations())
        >>> page.question_view._rhythm_term("2").text()
        '2'
        """
        picture = rhythm_picture(token)
        if picture is not None:
            picture.setPalette(self.rhythm_equation.palette())
            return picture
        label = QLabel("□" if token == "_" else token)
        label.setStyleSheet(css("font-size: 22pt;"))
        return label

    def show_rhythm(self, q: Question) -> bool:
        """
        Draw the question's rhythm and report whether it uses a named
        meter.

        Parameters
        ----------
        q : Question
            Question to draw.

        Returns
        -------
        bool
            Whether answer buttons should use named meters.

        Examples
        --------
        A named meter can show its signature on the question staff.
        """
        if isinstance(self.exercise, RythmicEquations):
            while self.rhythm_terms.count():
                item = self.rhythm_terms.takeAt(0)
                if item is not None and (widget := item.widget()) is not None:
                    widget.hide()
                    widget.deleteLater()
            self.rhythm_scroll.setVisible(bool(q.choices))
            if q.choices:
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
        return named_meter

    def fill_equation(self, q: Question, *, answer: str) -> None:
        """
        Replace the equation blank with the accepted answer.

        Parameters
        ----------
        q : Question
            Question to draw.
        answer : str
            Text to insert in the blank.

        Examples
        --------
        A correct response replaces the blank with a note or count.
        """
        blank = q.prompt.split().index("_")
        item = self.rhythm_terms.takeAt(blank)
        if item is not None and (widget := item.widget()) is not None:
            widget.hide()
            widget.deleteLater()
        self.rhythm_terms.insertWidget(
            blank,
            self._rhythm_term(answer),
            alignment=Qt.AlignmentFlag.AlignVCenter,
        )
        self.rhythm_equation.setAccessibleName(
            " ".join(answer if t == "_" else t for t in q.prompt.split())
            .replace("~", " tied to ")
            .replace("|", " beamed with "),
        )

    def set_accidental(self, accidental: int | None) -> None:
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
        >>> import random
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view.question_view.set_accidental(1)
        >>> (
        ...     view.question_view.note_input.accidental,
        ...     view.question_view.accidental_buttons[1].isChecked(),
        ... )
        (1, True)
        >>> view.question_view.set_accidental(None)
        >>> view.question_view.note_input.accidental is None
        True
        """
        for a, b in self.accidental_buttons.items():
            b.setChecked(accidental is not None and a == accidental)
        staff = self.note_input
        staff.accidental = accidental
        staff.refresh_preview()
        self.update_placement_status()

    def pick_accidental(self, accidental: int) -> None:
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
        >>> import random
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view.question_view.accidental_buttons[-1].click()
        >>> view.question_view.note_input.accidental
        -1
        >>> view.question_view.accidental_buttons[
        ...     -1
        ... ].click()  # clicking the lit one again clears it
        >>> view.question_view.note_input.accidental is None
        True
        """
        q = self.interactive_question
        if q is None:
            return
        lit = self.accidental_buttons[
            accidental
        ].isChecked()  # the click has already toggled it
        self.set_accidental(
            accidental if lit or q.place_signature else None,
        )

    def cycle_accidental(self, direction: int = 1) -> None:
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
        >>> import random
        >>> from alto.exercises.library import NoteNames
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteNames(), rng=random.Random(1)
        ... )
        >>> # not a "place this note" question: nothing happens
        >>> view.question_view.cycle_accidental()
        >>> view.question_view.editor is None
        True
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     ScaleConstruction(),
        ...     rng=random.Random(1),
        ... )
        >>> view.question_view.cycle_accidental(
        ...     -1
        ... )  # back from no sign goes around to the flat
        >>> view.question_view.scale_input.accidental
        -1
        """
        q = self.interactive_question
        if q and q.place_signature:
            self.set_accidental(
                -1 if self.scale_input.accidental == 1 else 1,
            )
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
            current = self.note_input.accidental
            self.set_accidental(
                order[(order.index(current) + direction) % len(order)]
                if current in order
                else None,
            )

    def update_placement_status(self) -> None:
        """
        Say what the next click or key press will do, in the line under
        the staff and for screen readers.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view.question_view.place_status.text()
        'Press ↑ or ↓ to choose a note, then Return to place it.'
        >>> view.question_view.note_input.move_cursor(0)
        >>> view.question_view.place_status.text().startswith(
        ...     "Note to place: "
        ... )
        True
        """
        shown, spoken = self.placement_text()
        self.place_status.setText(shown)
        self.place_status.setAccessibleDescription(spoken)
        q = self.interactive_question
        if q is not None and (q.construct is not None or q.places_sequence):
            self.note_input.setAccessibleDescription(spoken)

    def placement_text(self) -> tuple[str, str]:
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
        >>> import random
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     ScaleConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view.question_view.placement_text()[0]
        'Note 1 of 8: press ↑ or ↓ to choose a note, then Return to
        place it.'
        """
        q = self.interactive_question
        if q is None or (q.construct is None and not q.places_sequence):
            return "", ""
        if self.busy and self.placement_hint:
            hint = self.placement_hint
            return hint, hint
        if self.progress.answered and self.progress.missed:
            return "", ""
        staff = self.note_input
        if q.place_signature:
            caret = staff.caret_note()
            if self.progress.answered:
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
            naming = settings.note_names.naming
            display = note_name(caret, naming=naming, key=key, minor=q.minor)
            spoken = note_words(caret, naming=naming, key=key, minor=q.minor)
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

    def key_action(self, name: str) -> None:
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
        >>> import random
        >>> from alto.exercises.library import (
        ...     KeySignatureConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     KeySignatureConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view.question_view.key_action("up")
        >>> assert isinstance(view.question_view.editor, KeyFork)
        >>> view.question_view.editor.value
        1
        """
        q = self.interactive_question
        if q is None or self.progress.answered or self.busy:
            return
        if isinstance(self.editor, KeyFork):
            self.editor.move_selection(name)
            return
        if q.place_clef:
            if name in {"up", "down"}:
                self.clef_input.move_caret(
                    1 if name == "up" else -1,
                )
            elif name in {"left", "right"}:
                self.clef_input.step_symbol(
                    1 if name == "right" else -1,
                )
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
            self.move_caret(
                {"up": 1, "down": -1, "pageup": 7, "pagedown": -7}[name],
            )
        elif name == "right":
            self.cycle_accidental(1)
        elif name == "left":
            self.cycle_accidental(-1)

    def move_caret(self, steps: int) -> None:
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
        >>> import random
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view.question_view.move_caret(1)
        >>> view.question_view.note_input.caret is not None
        True
        """
        q = self.interactive_question
        if (
            q is None
            or self.progress.answered
            or self.busy
            or (q.construct is None and not q.places_sequence)
        ):
            return
        if q.places_sequence and not self.scale_input.placing_steps:
            self.scale_input.move_cursor(steps)
        elif q.construct is not None:
            self.note_input.move_cursor(steps)

    def jump_to_letter(self, letter: int) -> None:
        """
        Move the note that the keyboard would place to the nearest one
        with a letter name.

        Parameters
        ----------
        letter : int
            The letter, counting from C as 0.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view.question_view.jump_to_letter(4)
        >>> view.question_view.note_input.caret % 7  # G, starting at C
        4
        """
        q = self.interactive_question
        if q is None or self.progress.answered or self.busy:
            return
        if q.places_sequence and not self.scale_input.placing_steps:
            self.scale_input.jump_to_letter(letter)
        elif q.construct is not None:
            self.note_input.jump_to_letter(letter)

    def place_here(self) -> None:
        """
        Place the note at the caret on the staff, or mark the next step,
        without the mouse.

        Examples
        --------
        >>> import random
        >>> from alto.audio import sounds
        >>> from alto.exercises.library import (
        ...     NoteConstruction,
        ... )
        >>> sounds.enabled = False
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     NoteConstruction(), rng=random.Random(2)
        ... )
        >>> view.question_view.place_here()
        >>> view.session.total
        1
        >>> view.controller._advance.stop()
        >>> sounds.enabled = True
        """
        q = self.interactive_question
        if q is None or self.progress.answered or self.busy:
            return
        if q.places_sequence:
            self.scale_input.place_caret()
        elif q.construct is not None:
            self.note_input.place_caret()

    def show_step(self, step: str) -> None:
        """
        Light the button of the step that the next click on the scale
        staff marks.

        Parameters
        ----------
        step : str
            "W" or "H".

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     ScaleConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> view.question_view.show_step("H")
        >>> (
        ...     view.question_view.step_buttons["H"].isChecked(),
        ...     view.question_view.step_buttons["W"].isChecked(),
        ... )
        (True, False)
        """
        self.step_buttons[step].setChecked(True)

    def undo_scale_note(self) -> None:
        """
        Take back the last note placed on the scale staff.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import (
        ...     ScaleConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     ScaleConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> from alto.theory.pitch import Note
        >>> view.question_view.scale_input.notes.append(
        ...     Note.parse("C4")
        ... )
        >>> view.question_view.undo_scale_note()
        >>> view.question_view.scale_input.notes
        []
        """
        if (
            self.interactive_question
            and not self.progress.answered
            and not self.busy
        ):
            if isinstance(self.exercise, BeatConstruction):
                self.beat_placement.undo()
            else:
                self.scale_input.undo()

    def fork_changed(self, count: int) -> None:
        """
        Show the signature picked on the fork on the staff.

        Parameters
        ----------
        count : int
            The signature picked: that many sharps if positive, flats if
            negative.

        Examples
        --------
        >>> import random
        >>> from alto.exercises.library import (
        ...     KeySignatureConstruction,
        ... )
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     KeySignatureConstruction(),
        ...     rng=random.Random(2),
        ... )
        >>> assert isinstance(view.question_view.editor, KeyFork)
        >>> view.question_view.editor.set_value(-3)
        >>> view.question_view.staff.key
        -3
        """
        q = self.interactive_question
        if q and q.build_key and self.staff is not None:
            self.staff.show_notes(
                q.staff,
                clef=q.clef,
                key=count,
                value=q.value,
                caption=q.caption,
            )

    def redraw_keyboards(self) -> None:
        """
        Draw a plugin's keyboards over the range the learner is
        choosing, keeping the question.

        Examples
        --------
        Dragging the range selector shortens or lengthens the manuals on
        screen at once.
        """
        q = self.interactive_question
        picture = q.picture if q else None
        if (
            isinstance(self.exercise, PackExercise)
            and self.exercise.is_keyboard
            and picture is not None
            and self.fingerboard is not None
            and picture.keys
        ):
            self.fingerboard.show_position(
                replace(picture, span=self.exercise.chosen_span()),
            )

    def show_result(self, result: AnswerResult) -> None:
        """
        Display a graded answer on the current notation and editor.

        Parameters
        ----------
        result : AnswerResult
            Graded input and the music to reveal.
        """
        q = self.interactive_question
        if q is None:
            return
        self.placement_hint = result.hint
        kind = result.kind
        editor = self.editor
        if kind == "beats":
            self.beat_placement.feedback = result.correct
            self.beat_placement.update()
        elif (
            kind in ("note", "scale", "signature", "fork", "clef")
            and editor is not None
        ):
            editor.locked = (
                kind != "signature" or result.correct or self.progress.answered
            )
            if kind == "note":
                self.note_input.show_note(result.note)
        if result.correct:
            if kind in ("midi", "notation"):
                self.restore_prompt(q)
            if isinstance(self.exercise, RythmicEquations):
                self.fill_equation(q, answer=result.choice)
            if result.reveal_interval and self.staff and result.notes:
                self.staff.show_notes(
                    result.notes,
                    clef=q.clef,
                    key=q.key,
                    value=q.value,
                )

    def reset_placement(self, kind: str) -> None:
        """
        Reopen the current placement editor after an incorrect answer.

        Parameters
        ----------
        kind : str
            Type of answer being retried.
        """
        q = self.interactive_question
        if q is None:
            return
        self.placement_hint = ""
        if kind == "note":
            staff = self.note_input
            staff.locked = False
            staff.show_note(None)
            staff.refresh_preview()
        elif kind == "clef":
            self.clef_input.locked = False
            self.clef_input.clear_placed()
        elif kind == "fork" and isinstance(self.editor, KeyFork):
            self.editor.reset(slide=True)
        elif kind == "scale" and q.construct_scale is not None:
            self.scale_input.reset_scale(
                q.clef,
                slots=len(q.construct_scale),
                caption=q.caption,
                with_steps=q.construct_steps is not None,
                key=q.key,
            )

    def light_answer_notes(self, index: int | None) -> None:
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
        >>> import random
        >>> from alto.exercises.library import ScaleIdentification
        >>> from alto.ui.exercise_page import ExercisePage
        >>> view = ExercisePage(
        ...     ScaleIdentification(),
        ...     rng=random.Random(2),
        ... )
        >>> view.show_progress(view.session.after_attempt(
        ...     True, calendar_review=False, shuffle=False), False)
        >>> view.question_view.light_answer_notes(2)
        >>> list(view.question_view.staff.column_colors)
        [2]
        """
        q = self.interactive_question
        if q is None or not self.progress.answered:
            return
        if isinstance(self.exercise, BeatConstruction):
            column = (
                index
                if index is not None and not q.rhythm[index].endswith("-rest")
                else None
            )
            self.beat_placement.highlight_column(column)
            return
        green = QColor(CORRECT_ANSWER_COLOR)
        if self.fingerboard is not None:
            self.fingerboard.set_sounding(index is not None)
        elif self.keyboard is not None:
            self.keyboard.set_highlight_color(
                green
                if index is not None
                else self.palette().color(QPalette.ColorRole.Highlight),
            )
        else:
            staff = (
                self.note_input
                if q.construct is not None or q.construct_scale is not None
                else self.staff
            )
            if staff is not None:
                staff.column_colors = (
                    {index: green} if index is not None else {}
                )
                staff.update()

    def submit_placement(self) -> None:
        """
        Read the active editor when the learner presses Answer.

        Examples
        --------
        A key fork submits its signed count. A completed scale
        submits its pitches and the steps marked between them.
        """
        if self.interactive_question is None:
            return
        editor = self.editor
        if isinstance(self.exercise, BeatConstruction):
            self.beats_submitted.emit(list(self.beat_placement.marks))
        elif isinstance(editor, KeyFork):
            self.fork_submitted.emit(editor.value)
        elif isinstance(editor, ClefInput):
            editor.place_caret()
        elif isinstance(editor, SignatureInput):
            notes = [n for n in editor.entered_signature() if n is not None]
            self.signature_submitted.emit(notes)
        elif isinstance(editor, ScaleInput) and editor.done:
            self.scale_submitted.emit(list(editor.notes), list(editor.steps))

    def enter_midi_note(self, note: Note) -> None:
        """
        Enter the interpreted MIDI pitch in the active scale editor.

        Parameters
        ----------
        note : Note
            Spelled pitch entered by the learner.

        Examples
        --------
        The last MIDI note submits a scale that needs no marked steps.
        """
        if self.interactive_question is None:
            return
        editor = self.scale_input
        if not editor.complete:
            editor.place_next(note)
            if editor.done:
                self.submit_placement()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: PLR0917
        """
        Handle notation clicks and align the music layout on resize.

        Parameters
        ----------
        watched : QObject
            Object receiving the Qt event.
        event : QEvent
            Pointer or resize event from the displayed music.

        Returns
        -------
        bool
            Whether the event was consumed.

        Examples
        --------
        A narrow viewport leaves room for the horizontal scrollbar.
        """
        if (
            event.type() == QEvent.Type.Resize
            and watched is self._keyboard_interval_row
        ):
            self._align_keyboard_interval()
        if (
            isinstance(event, QMouseEvent)
            and event.type() == QEvent.Type.MouseButtonPress
            and event.button() == Qt.MouseButton.LeftButton
            and isinstance(watched, StaffWidget)
            and watched is self.staff
            and watched.locate_notation
        ):
            self.location_selected.emit(
                watched.hits_notation(event.position().toPoint()),
            )
            return True
        if (
            event.type() == QEvent.Type.Resize
            and hasattr(self, "rhythm_scroll")
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
        return super().eventFilter(watched, event)
