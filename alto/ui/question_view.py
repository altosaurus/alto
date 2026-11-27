"""Music displays and placement controls for an exercise question."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from alto import settings
from alto.exercises.base import Question
from alto.ui.circle import FifthsCircle
from alto.ui.fingerboard import FingerboardWidget
from alto.ui.key_fork import MAX_ACCIDENTALS, KeyFork
from alto.ui.keyboard import KeyboardWidget
from alto.ui.staff import MAX_STEP, StaffWidget, keyboard_key_staff
from alto.ui.staff_input import (
    ClefInput,
    ScaleInput,
    SignatureInput,
    StaffInput,
)
from alto.ui.zoom import px

_Widget = TypeVar("_Widget", bound=QWidget)


class QuestionView(QWidget):
    """
    Present a question's music and the editor used to answer it.

    A question can use several displays together, such as a keyboard
    with a key signature above it. It has at most one placement editor.

    Examples
    --------
    >>> view = QuestionView()
    >>> q = Question("", choices=[], answer="C", show_staff=True)
    >>> view.show_question(q, interval_voices=False)
    >>> isinstance(view.staff, StaffWidget) and view.editor is None
    True
    """

    widget_created = Signal(QWidget)

    def __init__(self, *, center_controls: bool = False) -> None:
        """
        Make room for the question and its placement controls.

        Parameters
        ----------
        center_controls : bool
            Center the editor and controls together for Order of Keys.

        Examples
        --------
        >>> QuestionView().keyboard is None
        True
        """
        super().__init__()
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )
        self.rows = QVBoxLayout(self)
        self.rows.setContentsMargins(0, 0, 0, 0)
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
        self.staff: StaffWidget | None = None
        self.keyboard: KeyboardWidget | None = None
        self.key_staff: StaffWidget | None = None
        self.circle: FifthsCircle | None = None
        self.fingerboard: FingerboardWidget | None = None
        self.editor: StaffInput | ClefInput | KeyFork | None = None

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

    def show_question(self, q: Question, *, interval_voices: bool) -> None:
        """
        Render the displays and editor requested by a question.

        Parameters
        ----------
        q : Question
            Music to display and input required.
        interval_voices : bool
            Separate the voices of an interval on the display staff.

        Examples
        --------
        Key Signature Construction shows both the staff and a key fork.
        """
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
            self.grid.removeWidget(self.editor)
            self.editor.hide()
            self.editor.deleteLater()
            self.editor = None
        if kind is not None and self.editor is None:
            self.editor = kind()
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
