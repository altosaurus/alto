"""Passing grades and review intervals for manual self-grading."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fsrs import Rating
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QWidget

if TYPE_CHECKING:
    from alto.learning.calendar import ReviewInterval


class RatingControls(QWidget):
    """
    Display the passing grades and emit the learner's selection.

    Attributes
    ----------
    rating_requested : Signal
        Emits the selected Rating when a grade button is clicked.
    choices : dict
        Interval label and button for each passing grade.

    Examples
    --------
    After a correct answer, the learner can choose Hard, Good, or Easy.
    """

    rating_requested = Signal(object)

    def __init__(self) -> None:
        """
        Build each grade button with its interval label above it.

        Examples
        --------
        The controls stay hidden until the scheduler offers grades.
        """
        super().__init__()
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.choices: dict[Rating, tuple[QLabel, QPushButton]] = {}
        for column, grade in enumerate(
            (Rating.Hard, Rating.Good, Rating.Easy),
        ):
            label = QLabel()
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button = QPushButton(grade.name)
            label.setBuddy(button)
            layout.addWidget(label, 0, column)
            layout.addWidget(button, 1, column)
            button.clicked.connect(
                lambda _checked=False, rating=grade: (
                    self.rating_requested.emit(rating)
                ),
            )
            self.choices[grade] = label, button
        self.hide()

    def show_ratings(self, ratings: dict[Rating, ReviewInterval]) -> None:
        """
        Display the offered review intervals, or hide the row.

        Parameters
        ----------
        ratings : dict[Rating, ReviewInterval]
            Review intervals offered for each passing grade.

        Examples
        --------
        The Good button describes how long until the next review.
        """
        for rating, preview in ratings.items():
            label, button = self.choices[rating]
            label.setText(preview.duration)
            button.setAccessibleDescription(
                f"Next review in {preview.duration}",
            )
        self.setVisible(bool(ratings))
