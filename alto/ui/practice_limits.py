"""Daily card allowances in profile and exercise settings."""

from __future__ import annotations

from PySide6.QtCore import QSignalBlocker, Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QSpinBox, QVBoxLayout, QWidget

from alto.learning import Learner


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
        self.inherit: list[QCheckBox] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for name in ("New cards/day", "Maximum reviews/day"):
            field = QSpinBox()
            field.setAccessibleName(name)
            field.setRange(0, 9999)
            field.setKeyboardTracking(False)
            label = QLabel(name)
            label.setBuddy(field)
            layout.addWidget(label)
            row = QHBoxLayout()
            row.addWidget(field)
            self.fields.append(field)
            if exercise:
                inherit = QCheckBox("Use global")
                inherit.setAccessibleName(f"Use global {name.lower()}")
                inherit.toggled.connect(self._save)
                row.addWidget(inherit)
                self.inherit.append(inherit)
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
            with QSignalBlocker(field):
                field.setValue(values[i])
            if self.exercise:
                with QSignalBlocker(self.inherit[i]):
                    self.inherit[i].setChecked(overrides[i] is None)
                field.setEnabled(overrides[i] is not None)

    def _save(self) -> None:
        """
        Persist edits and notify the exercise or its home tile.

        Examples
        --------
        Checking Use global restores inheritance for that field alone.
        """
        new, reviews = [None if self.exercise and self.inherit[i].isChecked() else f.value() for i, f in enumerate(self.fields)]
        self.learner.calendar.set_limits(self.learner.profile.id, exercise=self.exercise, new_cards=new, reviews=reviews)
        self.reload()
        self.changed.emit()
