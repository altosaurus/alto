"""Answer and review controls beneath an exercise question."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from alto.ui import motion
from alto.ui.answer_controls import AnswerControls
from alto.ui.rating_controls import RatingControls
from alto.ui.zoom import px

if TYPE_CHECKING:
    from alto.exercises.base import Exercise, Question


class ControlArea(QWidget):
    """
    Group the controls for answering, rating, and advancing.

    Attributes
    ----------
    answers : AnswerControls
        Choices and placement actions for the current question.
    ratings : RatingControls
        Passing grades and their review intervals.
    next_button : QPushButton
        Advances practice or checks an empty review queue again.

    Examples
    --------
    In calendar practice, a correct answer can reveal the grade buttons
    below the answer choices.
    """

    def __init__(self, exercise: Exercise) -> None:
        """
        Lay out the answer row, ratings, and Next button.

        Parameters
        ----------
        exercise : Exercise
            Exercise whose choices or placement actions to display.

        Examples
        --------
        The ratings row starts hidden while the learner answers.
        """
        super().__init__()
        self.answers = AnswerControls(exercise)
        self.ratings = RatingControls()
        self.next_button = QPushButton("Next")
        self.next_button.setMinimumHeight(px(40))
        motion.set_shortcut(self.next_button, key="Return")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        answer_row = QHBoxLayout()
        answer_row.addStretch(1)
        answer_row.addWidget(self.answers, 100)
        answer_row.addStretch(1)
        layout.addLayout(answer_row)
        layout.addWidget(self.ratings, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(
            self.next_button,
            alignment=Qt.AlignmentFlag.AlignHCenter,
        )

    def show_question(
        self,
        q: Question,
        *,
        named_meter: bool,
        locate_notation: bool,
        empty_queue: bool = False,
    ) -> None:
        """
        Clear the previous feedback and display the new answer controls.

        Parameters
        ----------
        q : Question
            Question to answer.
        named_meter : bool
            Display time signature names on the answer buttons.
        locate_notation : bool
            Ask for the answer on the staff and hide the choice grid.
        empty_queue : bool
            Offer to check for due cards when the queue is empty.

        Examples
        --------
        Starting the next question hides the previous review ratings.
        """
        label = "Check again" if empty_queue else "Next"
        if self.next_button.text() != label:
            self.next_button.setText(label)
            motion.set_shortcut(self.next_button, key="Return")
        self.next_button.setVisible(empty_queue)
        self.ratings.hide()
        self.answers.placement.answer_button.setStyleSheet("")
        self.answers.placement.place_button.setStyleSheet("")
        self.answers.show_question(
            q,
            named_meter=named_meter,
            locate_notation=locate_notation,
        )
