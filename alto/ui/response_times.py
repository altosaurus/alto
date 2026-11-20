"""Profile speed-grading settings and the rolling distribution for each exercise."""

from __future__ import annotations

import math
from bisect import bisect_left
from itertools import pairwise

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QSpinBox, QVBoxLayout, QWidget

from alto.exercises import REGISTRY
from alto.learning import Learner
from alto.learning.response_times import MINIMUM, WINDOW
from alto.ui.charts import HBarChart
from alto.ui.dropdown import FieldComboBox


class ResponseTimeDialog(QDialog):
    """Inspect recent correct first answers and adjust the profile's automatic grading bands."""

    def __init__(self, learner: Learner, *, parent: QWidget, exercise: str | None = None) -> None:
        """Open with the active profile’s saved settings and the selected exercise’s recent timings."""
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.learner = learner
        self.setWindowTitle("Response-time grading")
        self.resize(560, 560)
        layout = QVBoxLayout(self)
        description = QLabel(
            f"Automatic SM-2 and FSRS grades for {learner.profile.name}. Each exercise uses its own last {WINDOW} "
            f"timed, correct first answers. Grading by speed starts after {MINIMUM}.",
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        layout.addLayout(form)
        self.easy = QSpinBox()
        self.hard = QSpinBox()
        self.exercise = FieldComboBox()
        for cls in REGISTRY:
            self.exercise.addItem(cls.name, cls.__name__)
        if exercise is not None:
            self.exercise.setCurrentIndex(self.exercise.findData(exercise))
        sample = learner.response_times(self.exercise.currentData())
        for field, name, value in (
            (self.easy, "Easy · fastest", sample.easy_percent),
            (self.hard, "Hard · slowest", sample.hard_percent),
        ):
            field.setRange(0, 100)
            field.setSuffix("%")
            field.setValue(value)
            field.setKeyboardTracking(False)
            field.setAccessibleName(name)
            form.addRow(name, field)
        self.good = QLabel()
        form.addRow("Good · middle", self.good)
        self.exercise.setAccessibleName("Exercise")
        form.addRow("Exercise", self.exercise)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.chart = HBarChart("Response time in seconds")
        self.chart.setAccessibleName("Distribution of correct first answers")
        layout.addWidget(self.chart, 1)
        close = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close.rejected.connect(self.close)
        layout.addWidget(close)
        self.easy.valueChanged.connect(self._save)
        self.hard.valueChanged.connect(self._save)
        self.exercise.currentIndexChanged.connect(self._refresh)
        self._refresh()

    def _save(self) -> None:
        """Persist the profile-wide percentages and refresh the selected exercise."""
        self.learner.set_speed_thresholds(easy=self.easy.value(), hard=self.hard.value())
        self._refresh()

    def _refresh(self) -> None:
        """Show counts in duration bins and the cutoffs used by the grader."""
        sample = self.learner.response_times(self.exercise.currentData())
        self.easy.setMaximum(100 - sample.hard_percent)
        self.hard.setMaximum(100 - sample.easy_percent)
        self.good.setText(f"{100 - sample.easy_percent - sample.hard_percent}%")
        count = len(sample.times)
        if sample.ready:
            bands = []
            if sample.easy_percent:
                bands.append(f"Easy below {sample.percentile(sample.easy_percent) / 1000:.3f} s")
            if sample.hard_percent:
                bands.append(f"Hard above {sample.percentile(100 - sample.hard_percent) / 1000:.3f} s")
            detail = " · ".join(bands) if bands else "All correct answers earn Good."
        else:
            detail = f"{MINIMUM - count} more needed. Correct answers currently earn Good."
        self.summary.setText(f"{count} timed answers. {detail}")
        rows = []
        if count:
            # Cover the central 90% with readable, equal-width bins. Outliers get their own end bins.
            low, high = sample.percentile(5), sample.percentile(95)
            target = max(1, (high - low) / 7)
            unit = 10 ** math.floor(math.log10(target))
            width = next(step * unit for step in (1, 2, 5, 10) if step * unit >= target)
            start = math.floor(low / width) * width
            stop = max(start + width, math.ceil(high / width) * width)
            edges = list(range(start, stop + 1, width))
            labels = [f"{lo / 1000:g}–<{hi / 1000:g} s" for lo, hi in pairwise(edges)]
            starts = [bisect_left(sample.times, edge) for edge in edges]
            if starts[0]:
                labels.insert(0, f"Under {start / 1000:g} s")
                starts.insert(0, 0)
            if starts[-1] < count:
                labels.append(f"{stop / 1000:g} s or more")
                starts.append(count)
            for label, (left, right) in zip(labels, pairwise(starts), strict=True):
                n = right - left
                rows.append((label, 100 * n / count, str(n)))
        self.chart.set_data(rows)
