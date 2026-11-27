"""The action buttons beneath a construction exercise's editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from alto.ui import motion
from alto.ui.zoom import px

if TYPE_CHECKING:
    from alto.exercises.base import Question
    from alto.ui.meter_staff import BeatPlacementStaff
    from alto.ui.staff_input import ScaleInput


class PlacementControls(QWidget):
    """
    Show the actions available for editing and submitting a placement.

    Attributes
    ----------
    undo_button : QPushButton
        Removes the last note, step, sign, or beat.
    place_button : QPushButton
        Enters a note, step, or sign at the current position.
    answer_button : QPushButton
        Submits the learner's construction for grading.

    Examples
    --------
    In Scale Construction, Return places notes until the scale is
    complete, then submits the answer.
    """

    def __init__(self) -> None:
        """
        Build the row in the order used for keyboard navigation.

        Examples
        --------
        >>> controls = PlacementControls()
        >>> controls.answer_button.text()
        'Answer'
        """
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        self.undo_button = QPushButton("Undo")
        self.place_button = QPushButton("Place note")
        self.answer_button = QPushButton("Answer")
        for button, shortcut, stretch in (
            (self.undo_button, "Backspace", 0),
            (self.place_button, "Return", 1),
            (self.answer_button, "Return", 1),
        ):
            button.setMinimumHeight(px(40))
            motion.set_shortcut(button, key=shortcut)
            row.addWidget(button, stretch)

    def show_actions(
        self,
        question: Question,
        *,
        live: bool,
        sequence: ScaleInput | None,
        beats: BeatPlacementStaff | None,
    ) -> None:
        """
        Update each action for the question and the learner's progress.

        Parameters
        ----------
        question : Question
            The construction to display.
        live : bool
            Whether the learner can act on the current question.
        sequence : ScaleInput or None
            Active scale or signature editor.
        beats : BeatPlacementStaff or None
            Active beat editor with the learner's marks and feedback.

        Examples
        --------
        An empty beat response offers Undo and Answer and enables both
        once the learner has marked a beat.
        """
        place = question.construct is not None or sequence is not None
        answer = (
            question.build_key
            or bool(question.place_clef)
            or sequence is not None
            or beats is not None
        )
        self.setVisible(place or answer)
        self.place_button.setVisible(place)
        self.answer_button.setVisible(answer)
        self.undo_button.setVisible(sequence is not None or beats is not None)

        label = "Place note"
        if question.place_signature:
            label = "Place sign"
        elif sequence is not None and sequence.placing_steps:
            label = "Mark step"
        if self.place_button.text() != label:
            self.place_button.setText(label)
            motion.set_shortcut(
                self.place_button,
                key="P" if question.place_signature else "Return",
            )

        done = sequence is not None and sequence.done
        self.place_button.setEnabled(live and not done)
        if beats is not None:
            can_undo = bool(beats.marks)
            can_answer = can_undo and beats.feedback is not False
        else:
            can_undo = sequence is not None and bool(sequence.notes)
            can_answer = (
                question.build_key
                or bool(question.place_clef)
                or question.place_signature
                or done
            )
        self.undo_button.setEnabled(live and can_undo)
        self.answer_button.setEnabled(live and can_answer)
