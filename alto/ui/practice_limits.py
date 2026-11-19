"""Daily card allowances in profile and exercise settings."""

from __future__ import annotations

from PySide6.QtCore import QSignalBlocker, Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QSpinBox, QVBoxLayout, QWidget

from alto.learning import Learner
from alto.learning.calendar import DAILY_NEW, DAILY_REVIEWS, UNLIMITED


class DailyLimitsEditor(QWidget):
    """
    Edit a profile's daily limits or an exercise's overrides.

    Examples
    --------
    >>> from alto.learning import Database
    >>> db = Database()
    >>> editor = DailyLimitsEditor(Learner(db, profile=db.add_profile("Ada")))
    >>> editor.fields[0].value()
    10
    """

    changed = Signal()

    def __init__(self, learner: Learner, *, exercise: str = "") -> None:
        """
        Build one number field per limit, with an inheritance choice in exercise settings.

        Parameters
        ----------
        learner : Learner
            Profile whose limits to edit.
        exercise : str
            Exercise class name, or empty for profile defaults.

        Examples
        --------
        The exercise fields initially show the values from Practice settings.
        """
        super().__init__()
        self.learner = learner
        self.exercise = exercise
        self.fields: list[QSpinBox] = []
        self.unlimited: list[QCheckBox] = []
        self.inherit: list[QCheckBox] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for name, default in (("New cards/day", DAILY_NEW), ("Maximum reviews/day", DAILY_REVIEWS)):
            field = QSpinBox()
            field.setAccessibleName(name)
            field.setRange(0, 9999)
            field.setValue(default)
            field.setKeyboardTracking(False)
            label = QLabel(name)
            label.setBuddy(field)
            heading = QHBoxLayout()
            heading.addWidget(label)
            heading.addStretch()
            if exercise:
                inherit = QCheckBox("Use global")
                inherit.setAccessibleName(f"Use global {name.lower()}")
                inherit.toggled.connect(self._save)
                heading.addWidget(inherit)
                self.inherit.append(inherit)
            layout.addLayout(heading)
            row = QHBoxLayout()
            row.addWidget(field)
            self.fields.append(field)
            unlimited = QCheckBox("Unlimited")
            unlimited.setAccessibleName(f"Unlimited {name.lower().removeprefix('maximum ')}")
            unlimited.toggled.connect(self._save)
            row.addWidget(unlimited)
            self.unlimited.append(unlimited)
            row.addStretch()
            layout.addLayout(row)
            field.valueChanged.connect(self._save)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.reload()

    def reload(self) -> None:
        """
        Show current values and disable fields that follow the profile defaults.

        Examples
        --------
        Reopening Daily Limits reflects edits made in the global settings dialog.
        """
        calendar, profile = self.learner.calendar, self.learner.profile.id
        values = calendar.limits(profile, exercise=self.exercise)
        overrides = calendar.overrides(profile, exercise=self.exercise) if self.exercise else values
        for i, field in enumerate(self.fields):
            unlimited = values[i] == UNLIMITED
            inherited = overrides[i] is None
            if not unlimited:
                with QSignalBlocker(field):
                    field.setValue(values[i])
            with QSignalBlocker(self.unlimited[i]):
                self.unlimited[i].setChecked(unlimited)
            self.unlimited[i].setEnabled(not inherited)
            field.setEnabled(not (inherited or unlimited))
            if self.exercise:
                with QSignalBlocker(self.inherit[i]):
                    self.inherit[i].setChecked(inherited)

    def _save(self) -> None:
        """
        Persist edits and notify the exercise or its home tile.

        Examples
        --------
        Checking Use global restores inheritance for that field alone.
        """
        limits: list[int | None] = [
            UNLIMITED if box.isChecked() else field.value() for box, field in zip(self.unlimited, self.fields, strict=True)
        ]
        for i, inherit in enumerate(self.inherit):
            if inherit.isChecked():
                limits[i] = None
        new, reviews = limits
        self.learner.calendar.set_limits(self.learner.profile.id, exercise=self.exercise, new_cards=new, reviews=reviews)
        self.reload()
        self.changed.emit()
