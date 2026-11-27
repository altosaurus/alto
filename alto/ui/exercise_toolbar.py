"""The toolbar above the music in an exercise."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from alto.ui.icons import (
    BOOK,
    SLIDERS,
    SPEAKER_MUTED,
    SPEAKER_ON,
    set_svg_icon,
)
from alto.ui.midi_input import MidiInput
from alto.ui.widgets import HelpButton, PracticeCounts
from alto.ui.zoom import px

if TYPE_CHECKING:
    from alto.learning.practice_session import PracticeSession


class ExerciseToolbar(QWidget):
    """
    Show practice progress and the controls available for an exercise.

    Attributes
    ----------
    book_btn : QToolButton or None
        Toggles the reference pane for exercises that have a reference.

    Examples
    --------
    >>> toolbar = ExerciseToolbar(
    ...     lambda: "Identify the note.",
    ...     has_reference=True,
    ...     has_midi=False,
    ... )
    >>> toolbar.gear.toolTip()
    'Exercise settings'
    """

    def __init__(
        self,
        instructions: Callable[[], str],
        *,
        has_reference: bool,
        has_midi: bool,
    ) -> None:
        """
        Arrange the exercise controls in one horizontal row.

        Parameters
        ----------
        instructions : callable
            Provide the current exercise instructions when help opens.
        has_reference : bool
            Whether to show the reference pane toggle.
        has_midi : bool
            Whether to offer the MIDI input selector.

        Examples
        --------
        The Back to lesson button starts hidden until a lesson opens
        the exercise.
        """
        super().__init__()
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        self.lesson_back_button = QPushButton("← Back to lesson")
        self.lesson_back_button.hide()
        row.addWidget(self.lesson_back_button)
        row.addStretch()
        self.queue_counts = PracticeCounts()
        self.queue_counts.hide()
        row.addWidget(self.queue_counts)
        self.score = QLabel()
        row.addWidget(self.score)
        self.help_btn = HelpButton(instructions)
        row.addWidget(self.help_btn)
        self.book_btn = (
            self._tool_button(BOOK, label="Reference")
            if has_reference
            else None
        )
        if self.book_btn is not None:
            row.addWidget(self.book_btn)
        self.midi_input = MidiInput() if has_midi else None
        if self.midi_input is not None:
            row.addWidget(self.midi_input)
        self.sound_btn = QToolButton()
        self.sound_btn.setAutoRaise(True)
        self.sound_btn.setIconSize(QSize(px(24), px(24)))
        row.addWidget(self.sound_btn)
        self.gear = self._tool_button(SLIDERS, label="Exercise settings")
        row.addWidget(self.gear)

    @staticmethod
    def _tool_button(icon: str, *, label: str) -> QToolButton:
        """
        Create the toggle for a side pane.

        Parameters
        ----------
        icon : str
            SVG artwork for the button.
        label : str
            Tooltip and accessible name.

        Returns
        -------
        QToolButton
            A checkable button with the toolbar's icon size.

        Examples
        --------
        Both the settings and reference buttons stay checked while open.
        """
        button = QToolButton()
        set_svg_icon(button, icon)
        button.setIconSize(QSize(px(24), px(24)))
        button.setCheckable(True)
        button.setAutoRaise(True)
        button.setToolTip(label)
        button.setAccessibleName(label)
        return button

    def show_score(self, session: PracticeSession) -> None:
        """
        Display the session's first-attempt score and current streak.

        Parameters
        ----------
        session : PracticeSession
            Current progress in this exercise.

        Examples
        --------
        A fresh session displays a dash until the first graded answer.
        """
        correct, total = session.correct, session.total
        percent = f"{100 * correct / total:.0f}%" if total else "–"
        self.score.setText(
            f"{correct}/{total} ({percent})   streak {session.streak}",
        )

    def set_sound_enabled(self, enabled: bool) -> None:
        """
        Show the current sound state on the speaker button.

        Parameters
        ----------
        enabled : bool
            Whether application sound is on.

        Examples
        --------
        A muted speaker offers to turn sound back on.
        """
        set_svg_icon(self.sound_btn, SPEAKER_ON if enabled else SPEAKER_MUTED)
        self.sound_btn.setToolTip(
            "Sound on (click to mute)"
            if enabled
            else "Muted (click to unmute)",
        )
        self.sound_btn.setAccessibleName(
            "Sound on" if enabled else "Sound muted",
        )
