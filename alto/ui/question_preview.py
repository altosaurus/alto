"""
A popup showing a stored question the way the exercise showed it, with its answer.

Examples
--------
>>> question = Question("Name the note.", choices=["C", "D"], answer="C")
>>> QuestionPreview("Note Identification", question=question).windowTitle()
'Note Identification'
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from alto import settings as app_settings
from alto.audio import sounds
from alto.exercises.base import Question
from alto.settings import spell
from alto.ui import icons
from alto.ui.circle import FifthsCircle
from alto.ui.keyboard import KeyboardWidget
from alto.ui.staff import (
    MAX_STEP,
    StaffWidget,
)
from alto.ui.staff_playback import StaffPlayback


class QuestionPreview(QDialog):
    """
    A question as it appeared (the notes on the staff, or the highlighted key), then what the answer is.

    Attributes
    ----------
    question : Question
        The question being shown.

    Examples
    --------
    >>> from alto.theory.pitch import Note
    >>> question = Question("Name the note.", choices=["C", "D"], answer="C", staff=[[Note.parse("C4")]])
    >>> dialog = QuestionPreview("Note Identification", question=question, details=["You answered: D"])
    >>> dialog.question.answer
    'C'
    """

    def __init__(
        self,
        exercise_name: str,
        *,
        question: Question,
        details: list[str] | None = None,
        statistics: Callable[[QWidget], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the popup.

        Parameters
        ----------
        exercise_name : str
            The exercise's name, shown as the title.
        question : Question
            The question to show. Keyword-only.
        details : list of str or None, default None
            Extra lines of HTML, such as what was answered and how long it took. Keyword-only.
        statistics : callable or None, default None
            Opens statistics for the displayed question, with the card as its parent. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns the dialog. Keyword-only.

        Examples
        --------
        >>> from alto.theory.pitch import Note
        >>> question_ = Question("", choices=["C"], answer="C", keyboard=Note.parse("C4"))
        >>> QuestionPreview("Keyboard Note Identification", question=question_).minimumWidth()
        560
        """
        super().__init__(parent)
        self.question = question
        self.setWindowTitle(exercise_name)
        self.setMinimumWidth(560)
        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        title = QLabel(f"<h3>{exercise_name}</h3>")
        header = QHBoxLayout()
        header.addWidget(title, 1)
        if statistics is not None:
            stats_button = QToolButton()
            stats_button.setIcon(icons.svg_icon(icons.BAR_CHART, color=self.palette().color(QPalette.ColorRole.ButtonText)))
            stats_button.setIconSize(QSize(22, 22))
            stats_button.setAccessibleName("Question Statistics")
            stats_button.setToolTip("Question Statistics")
            stats_button.clicked.connect(lambda: statistics(self))
            header.addWidget(stats_button, alignment=Qt.AlignmentFlag.AlignTop)
        lay.addLayout(header)
        if question.prompt and not question.caption:
            prompt = QLabel(question.prompt)
            prompt.setWordWrap(True)
            prompt.setStyleSheet("font-size: 14pt;")
            lay.addWidget(prompt)

        q = question
        scale = [[n] for n in q.construct_scale or []]
        staff = None
        if q.staff or q.show_staff or q.construct is not None or scale:
            staff = StaffWidget(max_step=MAX_STEP)
            if q.construct_steps:  # a scale with its steps shows them above the notes
                staff.wedges = list(q.construct_steps)
            # a "place this note" or "place this scale" question shows the notes that were the answer
            notes = q.staff or ([[q.construct]] if q.construct is not None else scale)
            staff.show_notes(
                notes,
                clef=q.clef,
                key=q.key if q.staff_signature is None else q.staff_signature,
                value=q.value,
                notation_excerpt=q.notation_excerpt,
                notation_target=q.notation_target,
                caption=q.caption,
            )
            lay.addWidget(staff, alignment=Qt.AlignmentFlag.AlignHCenter)
        if q.circle is not None:  # a circle of fifths question shows the circle with its answer in
            circle = FifthsCircle()
            circle.setFixedSize(380, 380)
            circle.show_question(q.circle_kind, place=q.circle, ring=q.circle_ring, key=q.circle_key, title=q.caption)
            circle.reveal(animate=False)
            lay.addWidget(circle, alignment=Qt.AlignmentFlag.AlignHCenter)
        if q.keyboard is not None or q.keyboard_notes:
            if q.key_staff:
                key_staff = StaffWidget(
                    gap=8.0,
                    side=12.0,
                    note_offset=70.0,
                    margin=3.6,
                    compact=True,
                )
                key_staff.setFixedWidth(210)
                key_staff.show_notes([], clef="treble", key=q.key)
                lay.addWidget(key_staff, alignment=Qt.AlignmentFlag.AlignHCenter)
            keyboard = KeyboardWidget()
            keyboard.max_key_width = 30.0 if q.key_staff else 38.0
            if q.keyboard_notes:
                keyboard.show_keys([note.midi for note in q.keyboard_notes], span=q.keyboard_range)
            elif q.keyboard is not None:
                keyboard.show_key(q.keyboard.midi, span=q.keyboard_range)
            lay.addWidget(keyboard)

        lines = [f"<b>Answer:</b> {self._answer_text()}"]
        if q.choices:
            lines.append("<span style='color: gray;'>Choices: " + "  ·  ".join(q.choices) + "</span>")
        if q.octaves:
            lines.append(f"<span style='color: gray;'>{q.second_label}: " + "  ·  ".join(q.octaves) + "</span>")
        lines += details or []
        if q.explanation:
            lines.append(q.explanation)
        info = QLabel("<br>".join(lines))
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(info)

        buttons = QDialogButtonBox()
        notes = q.staff or (
            [q.keyboard_notes]
            if q.keyboard_notes
            else [[q.keyboard]]
            if q.keyboard
            else [[q.construct]]
            if q.construct is not None
            else scale
        )
        # The simple pitch player cannot perform the rhythmic, microtonal, or instrumental markings in these questions.
        if notes and (q.notation_target is None or q.notation_target[0] in ("Notehead", "Stem", "Clef", "Staff line")):
            play = QPushButton("Play")
            if staff is not None and staff.columns == notes:
                playback = StaffPlayback(self, highlight=staff.highlight_column)
                play.clicked.connect(lambda: playback.play(notes))
            else:
                play.clicked.connect(lambda: sounds.play_notes(notes))
            buttons.addButton(play, QDialogButtonBox.ButtonRole.ActionRole)
        buttons.addButton(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        lay.addWidget(buttons)

    def _answer_text(self) -> str:
        """
        Return the answer as it should be shown.

        Returns
        -------
        str
            The right answer; for a "place this note" question, the note's name and octave in the chosen naming.

        Examples
        --------
        >>> QuestionPreview("Intervals", question=Question("?", choices=["M3"], answer="M3"))._answer_text()
        'M3'
        >>> from alto.theory.pitch import Note
        >>> question = Question("Place C4.", choices=[], answer="C4", construct=Note.parse("C4"))
        >>> QuestionPreview("Construction", question=question)._answer_text()
        'C4'
        """
        q = self.question
        if q.construct is not None:
            naming = app_settings.note_names.naming
            if q.notes_only and naming in app_settings.DEGREE_NAMINGS:
                naming = "letters"
            return spell(
                q.construct,
                naming=naming,
                key=q.key,
                octave=not q.any_octave,
                minor=q.minor,
            )
        return q.answer
