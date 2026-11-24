"""
Modeless Anki deck exporter using Alto's exercise controls and music
engraving.
"""

from __future__ import annotations

import atexit
import hashlib
import multiprocessing
import os
from concurrent.futures import Future
from contextlib import closing
from html import escape
from multiprocessing.connection import Connection
from multiprocessing.process import BaseProcess
from pathlib import Path
from tempfile import TemporaryDirectory

from PySide6.QtCore import (
    QBuffer,
    QByteArray,
    QCoreApplication,
    QEvent,
    QIODevice,
    QSignalBlocker,
    QSize,
    Qt,
    QThread,
    QTimeLine,
    QTimer,
    QUrl,
    Signal,
    Slot,
)
from PySide6.QtGui import QColor, QIcon, QImage, QTextDocument
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextBrowser,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from alto.anki_export import (
    DeckSelection,
    ExportControl,
    PlannedDeck,
    Review,
    deck_candidates,
    plan_deck,
    profile_reviews,
    write_decks,
)
from alto.exercises import REGISTRY, Exercise, Question
from alto.exercises.library import (
    IntervalConstruction,
    RythmicEquations,
)
from alto.exercises.packs import load_packs
from alto.learning import Database, Learner
from alto.learning.calendar import CALENDAR_SCHEDULERS
from alto.location import database_path, desktop_name
from alto.notation_excerpts import excerpts
from alto.ui import icons
from alto.ui.circle import question_circle
from alto.ui.colors import CORRECT_ANSWER_COLOR
from alto.ui.dropdown import style_combo_popup
from alto.ui.exercise_settings import load_exercise_settings
from alto.ui.fingerboard import FingerboardWidget
from alto.ui.home import category_tree, exercise_icon
from alto.ui.keyboard import KeyboardWidget
from alto.ui.keyboard_styles import load_style as load_keyboard_style
from alto.ui.notation import load_style as load_notation_style
from alto.ui.pictures import RHYTHM_SYMBOL_NAMES, rhythm_picture
from alto.ui.settings_menu import ExerciseSettingsPanel
from alto.ui.settings_panel import settings_panel_for
from alto.ui.staff import MAX_STEP, StaffWidget
from alto.ui.staff_input import SignatureInput
from alto.ui.store import export_settings, import_settings, store, text_value
from alto.ui.style import navigation_heading_style
from alto.ui.theme import apply_theme, saved_theme
from alto.ui.widgets import SegmentedControl
from alto.ui.zoom import px


def _picture(widget: QWidget, *, folder: Path, label: str) -> str:
    """
    Store one illustration under a content-based filename for safe media
    reuse in Anki.

    Returns
    -------
    str
        The HTML image tag for the note.

    Raises
    ------
    OSError
        If Qt cannot encode the image.
    """
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not widget.grab().save(buffer, "PNG"):
        raise OSError("Could not render the card illustration.")
    image = data.data()
    name = f"alto-{hashlib.sha256(image).hexdigest()[:24]}.png"
    (folder / name).write_bytes(image)
    return f'<img src="{name}" alt="{escape(label, quote=True)}">'


def card_fields(
    question: Question,
    *,
    folder: Path,
    exercise: Exercise,
) -> list[str]:
    """
    Render an exercise as a reveal-and-grade card.

    Returns
    -------
    list of str
        The prompt, illustrations, answer, and explanation fields as
        HTML.
    """
    q = question
    front, back = [], []
    key = q.key if q.staff_signature is None else q.staff_signature
    locate = q.notation_target is not None and not q.choices
    if (
        q.staff
        or q.show_staff
        or q.construct
        or q.construct_scale
        or q.key_staff
    ):
        staff = StaffWidget(max_step=MAX_STEP)
        staff.interval_voices = exercise.interval_voices
        staff.clef_hidden = bool(q.place_clef)
        staff.show_notes(
            q.placement_columns(None) if q.construct else q.staff,
            clef=q.clef,
            key=0 if q.build_key or q.place_signature else key,
            value=q.value,
            notation_target=q.notation_target,
            notation_excerpt=q.notation_excerpt,
            locate_notation=locate,
            caption=q.caption if q.caption != q.prompt else "",
        )
        staff.resize(staff.sizeHint())
        if q.place_signature:
            incomplete = SignatureInput()
            incomplete.reset_signature(
                q.clef,
                key=q.key,
                caption="",
                starting_slots=q.starting_slots,
            )
            incomplete.resize(650, incomplete.minimumHeight())
            front.append(
                _picture(
                    incomplete,
                    folder=folder,
                    label="Incomplete key signature",
                ),
            )
        else:
            front.append(
                _picture(staff, folder=folder, label="Question staff"),
            )
        if (
            q.construct
            or q.construct_scale
            or q.build_key
            or q.place_signature
            or q.place_clef
            or locate
        ):
            staff.clef_hidden = False
            staff.wedges = q.construct_steps or []
            solution = (
                q.placement_columns(q.construct)
                if q.construct
                else [[note] for note in q.construct_scale or []]
            )
            staff.show_notes(
                solution or q.staff,
                clef=q.place_clef or q.clef,
                key=key,
                value=q.value,
                notation_target=q.notation_target,
                notation_excerpt=q.notation_excerpt,
            )
            staff.resize(staff.sizeHint())
            back.append(
                _picture(staff, folder=folder, label="Completed staff"),
            )
    position = q.fingerboard or q.picture
    if position is not None:
        board = FingerboardWidget()
        board.show_position(position)
        board.resize(board.sizeHint())
        label = (
            "Marked fingerboard position"
            if q.fingerboard
            else "Marked instrument picture"
        )
        front.append(_picture(board, folder=folder, label=label))
    if q.keyboard is not None or q.keyboard_notes:
        keyboard = KeyboardWidget()
        keyboard.resize(720, keyboard.height())
        keyboard.show_keys(
            [note.midi for note in q.keyboard_notes]
            if q.keyboard is None
            else [q.keyboard.midi],
            span=q.keyboard_range,
        )
        front.append(
            _picture(keyboard, folder=folder, label="Highlighted piano keys"),
        )
    if q.circle is not None:
        circle = question_circle(q)
        front.append(_picture(circle, folder=folder, label="Circle of fifths"))
        circle.reveal(animate=False)
        back.append(
            _picture(
                circle,
                folder=folder,
                label="Completed circle of fifths",
            ),
        )
    solution_text = " and ".join(q.required) if q.required else q.answer
    if isinstance(exercise, RythmicEquations):
        terms = []
        for term in q.prompt.split():
            picture = rhythm_picture(term)
            label = "□" if term == "_" else term
            terms.append(
                _picture(picture, folder=folder, label=label)
                if picture is not None
                else escape(label),
            )
        front.append(" ".join(terms))
        solution_text = " / ".join(
            RHYTHM_SYMBOL_NAMES[name] for name in (q.answer, *q.accept)
        )
    if (
        q.keyboard is not None or isinstance(exercise, IntervalConstruction)
    ) and q.accept:
        solution_text = " / ".join((q.answer, *q.accept))
    answer = "<br>".join([escape(solution_text), *back])
    explanation = escape(q.explanation)
    if q.notation_excerpt:
        explanation += "<br>" + escape(excerpts()[q.notation_excerpt].credit)
    return [
        escape(exercise.card_prompt(q)),
        "<br>".join(front),
        answer,
        explanation,
    ]


class _PlanJob(QThread):
    """
    Collect eligible cards without blocking the destination picker.
    """

    def __init__(
        self,
        selections: list[DeckSelection],
        *,
        parent: QWidget,
    ) -> None:
        """Capture the selection when the confirmation dialog opens."""
        super().__init__(parent)
        self.selections = selections
        self.plans: list[PlannedDeck] = []
        self.error = ""

    def run(self) -> None:
        """
        Prepare the same questions that the package writer will receive.
        """
        try:
            self.plans = [
                plan_deck(selection) for selection in self.selections
            ]
        except Exception as error:
            self.error = f"Could not count cards. {error}"


class _ExportJob(QThread):
    """
    Generate the package on a worker thread and send widget rendering to
    its owning GUI thread.
    """

    progress = Signal(str, int, int)
    deck_progress = Signal(int, bool)
    render_requested = Signal(object, object, object, object)

    def __init__(
        self,
        path: Path,
        *,
        plans: list[PlannedDeck],
        parent: QWidget,
    ) -> None:
        """Capture the export settings before the worker starts."""
        super().__init__(parent)
        self.path = path
        self.control = ExportControl()
        self.plans = plans
        self.count = 0
        self.error = ""
        self.render_requested.connect(
            self._paint_card,
            Qt.ConnectionType.QueuedConnection,
        )

    def run(self) -> None:
        """
        Write all decks and retain the outcome until the finished signal
        reaches the window.
        """
        try:
            self.count = write_decks(
                self.path,
                plans=self.plans,
                render=self._render,
                progress=self.progress.emit,
                control=self.control,
                deck_progress=self.deck_progress.emit,
            )
        except Exception as error:
            if not self.control.canceled.is_set():
                self.error = f"Export failed. {error}"

    def _render(  # noqa: PLR0917 (render callback)
        self,
        q: Question,
        folder: Path,
        exercise: Exercise,
    ) -> list[str]:
        """
        Request the fields for one card and wait for Qt to finish
        drawing it.

        Returns
        -------
        list of str
            The card fields, with its illustrations saved in the package
            directory.
        """
        fields = Future[list[str]]()
        self.render_requested.emit(q, folder, exercise, fields)
        return fields.result()

    @Slot(object, object, object, object)
    def _paint_card(  # noqa: PLR0917 (queued signal arguments)
        self,
        q: Question,
        folder: Path,
        exercise: Exercise,
        fields: Future[list[str]],
    ) -> None:
        """
        Render widgets on the GUI thread and release the worker on
        either success or failure.
        """
        try:
            fields.set_result(card_fields(q, folder=folder, exercise=exercise))
        except Exception as error:
            fields.set_exception(error)


class _ExportDialog(QDialog):
    """
    Choose the package destination, review card counts, and monitor the
    export.
    """

    def __init__(
        self,
        selections: list[DeckSelection],
        *,
        parent: QWidget,
    ) -> None:
        """
        Start counting eligible questions while the user chooses a
        destination.
        """
        super().__init__(parent)
        self.setWindowTitle("Export Anki decks")
        self.resize(480, 360)
        layout = QVBoxLayout(self)
        self.destination = QWidget()
        row = QHBoxLayout(self.destination)
        row.setContentsMargins(0, 0, 0, 0)
        name = (
            f"alto - {selections[0].exercise.name}"
            if len(selections) == 1
            else "alto"
        )
        self.filename = QLineEdit(str(Path.home() / f"{name}.apkg"))
        self.filename.setProperty("field", True)
        self.filename.setAccessibleName("File name")
        label = QLabel("File name")
        label.setBuddy(self.filename)
        row.addWidget(label)
        row.addWidget(self.filename, 1)
        self.browse = QPushButton("Browse…")
        self.browse.clicked.connect(self._browse)
        row.addWidget(self.browse)
        layout.addWidget(self.destination)
        self.summary = QTreeWidget()
        self.summary.setObjectName("detailPane")
        self.summary.setAlternatingRowColors(True)
        self.summary.setAccessibleName("Cards by deck")
        self.summary.setHeaderLabels(["Deck", "Cards", "Status"])
        self.summary.header().setStretchLastSection(False)
        self.summary.header().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )
        self.summary.header().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.summary.header().setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        # Reveal the existing check stroke from its short downstroke to
        # the tip, keeping the green box still.
        self._check_frames = [
            icons.svg_icon(
                f'<g stroke-dasharray="{length} 24">{icons.CHECKED_BOX}</g>',
                color=QColor(CORRECT_ANSWER_COLOR),
                size=16,
            )
            for length in range(1, 20, 2)
        ]
        self._spinner = QTimer(self)
        self._spinner.setInterval(80)
        self._spinner.timeout.connect(self._advance_spinner)
        self._spinner_angle = 0
        self._active_row: QTreeWidgetItem
        groups: dict[str, QTreeWidgetItem] = {}
        heading_font, _ = navigation_heading_style(self.summary.palette())
        self.rows: list[QTreeWidgetItem] = []
        for selection in selections:
            exercise = selection.exercise
            if exercise.category not in groups:
                group = groups[exercise.category] = QTreeWidgetItem(
                    self.summary,
                    [exercise.category],
                )
                group.setFont(0, heading_font)
            self.rows.append(
                QTreeWidgetItem(
                    groups[exercise.category],
                    [exercise.name, "…"],
                ),
            )
        self.summary.expandAll()
        self._check_animations = []
        for row in self.rows:
            animation = QTimeLine(280, self)
            animation.setFrameRange(0, len(self._check_frames) - 1)
            animation.setUpdateInterval(20)
            animation.frameChanged.connect(
                lambda frame, item=row: item.setIcon(
                    2,
                    self._check_frames[frame],
                ),
            )
            self._check_animations.append(animation)
        layout.addWidget(self.summary)
        self.total = QLabel("Counting cards…")
        layout.addWidget(self.total)
        self.progress = QProgressBar()
        self.progress.setAccessibleName("Anki export progress")
        self.progress.hide()
        layout.addWidget(self.progress)
        self.status = QLabel()
        self.status.setTextFormat(Qt.TextFormat.PlainText)
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        footer = QHBoxLayout()
        layout.addLayout(footer)
        footer.addStretch()
        self.dismiss = QPushButton("Cancel")
        self.dismiss.clicked.connect(self.reject)
        footer.addWidget(self.dismiss)
        self.save = QPushButton("Export")
        self.save.setProperty("primary", True)
        self.save.setDefault(True)
        self.save.setEnabled(False)
        self.save.clicked.connect(self._start_export)
        footer.addWidget(self.save)
        self._close_when_ready = False
        self.plans: list[PlannedDeck] = []
        self._job: _ExportJob | None = None
        self._counter: _PlanJob | None = _PlanJob(selections, parent=self)
        self._counter.finished.connect(self._counted)
        self._counter.start()

    @Slot()
    def _counted(self) -> None:
        """
        Show exact filtered counts and enable writing when at least one
        card matches.
        """
        counter = self._counter
        assert counter is not None
        self._counter = None
        counter.deleteLater()
        if self._close_when_ready:
            self.reject()
            return
        if counter.error:
            self.total.setText(counter.error)
            return
        self.plans = counter.plans
        for row, plan in zip(self.rows, self.plans, strict=True):
            row.setText(1, str(len(plan.cards)))
            row.setText(2, "Pending" if plan.cards else "No cards")
        count = sum(len(plan.cards) for plan in self.plans)
        self.total.setText(
            f"Total: {count} {'card' if count == 1 else 'cards'}",
        )
        self.save.setEnabled(count > 0)
        if not count:
            self.status.setText("No cards match these settings.")

    def _browse(self) -> None:
        """
        Choose a package path and leave overwrite confirmation to the
        Export button.
        """
        picker = QFileDialog(self)
        picker.setOption(QFileDialog.Option.DontUseNativeDialog)
        picker.setOption(QFileDialog.Option.DontConfirmOverwrite)
        picker.setWindowTitle("Export Anki decks")
        picker.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        picker.setNameFilter("Anki decks (*.apkg)")
        picker.selectFile(
            str(
                Path.home() / os.path.expanduser(self.filename.text().strip()),
            ),
        )
        for combo in picker.findChildren(QComboBox):
            style_combo_popup(combo)
        if picker.exec():
            self.filename.setText(picker.selectedFiles()[0])
        picker.deleteLater()

    def _start_export(self) -> None:
        """
        Validate the package path and start writing the summarized
        cards.
        """
        value = os.path.expanduser(self.filename.text().strip())
        if os.path.basename(value) in {"", ".", ".."}:
            self.status.setText("Enter a file name.")
            self.filename.setFocus()
            return
        path = Path.home() / value
        if not path.parent.is_dir():
            self.status.setText("Choose an existing directory.")
            self.filename.setFocus()
            return
        if not path.name.lower().endswith(".apkg") and not path.is_dir():
            path = path.with_name(path.name + ".apkg")
        self.filename.setText(str(path))
        if path.is_dir():
            self.status.setText("A directory already has that file name.")
            return
        if path.exists() and not self._confirm_replace(path):
            return
        self.destination.setEnabled(False)
        self.save.setEnabled(False)
        self.dismiss.setText("Cancel")
        for row, plan in zip(self.rows, self.plans, strict=True):
            if plan.cards:
                row.setText(2, "Pending")
                row.setIcon(2, QIcon())
        self.progress.reset()
        self.progress.show()
        self.status.setText("Starting export…")
        job = self._job = _ExportJob(path, plans=self.plans, parent=self)
        job.progress.connect(self._show_progress)
        job.deck_progress.connect(self._deck_progress)
        job.finished.connect(self._export_finished)
        job.start()

    def _confirm_replace(self, path: Path) -> bool:
        """
        Ask whether to overwrite the selected package.

        Returns
        -------
        bool
            True if the user approves replacing the file.
        """
        warning = QMessageBox(self)
        warning.setWindowTitle("Replace file?")
        warning.setIcon(QMessageBox.Icon.Question)
        warning.setTextFormat(Qt.TextFormat.PlainText)
        warning.setText(f"Replace the existing file “{path.name}”?")
        warning.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        # QMessageBox sizes itself from its contents. Reserve room for
        # the window title even for short file names.
        layout = warning.layout()
        assert isinstance(layout, QGridLayout)
        layout.addItem(
            QSpacerItem(360, 0),
            layout.rowCount(),
            0,
            1,
            layout.columnCount(),
        )
        answer = warning.exec()
        warning.deleteLater()
        return answer == QMessageBox.StandardButton.Yes

    @Slot(int, bool)
    def _deck_progress(self, index: int, complete: bool) -> None:  # noqa: PLR0917 (queued signal)
        """
        Mark the deck being prepared and give finished decks a read-only
        green check.
        """
        row = self.rows[index]
        row.setText(2, "Complete" if complete else "In progress")
        if complete:
            self._spinner.stop()
            row.setIcon(2, self._check_frames[0])
            self._check_animations[index].start()
        else:
            self._active_row = row
            self._advance_spinner()
            self._spinner.start()

    def _advance_spinner(self) -> None:
        """
        Rotate the active deck's status icon in the current theme
        accent.
        """
        arc = (
            '<path transform="rotate('
            f"{self._spinner_angle}"
            ' 12 12)" d="M12 3a9 9 0 1 1-9 9" '
            'fill="none" stroke="COLOR" stroke-width="3" '
            'stroke-linecap="round"/>'
        )
        self._active_row.setIcon(
            2,
            icons.svg_icon(
                arc,
                color=self.palette().highlight().color(),
                size=16,
            ),
        )
        self._spinner_angle = (self._spinner_angle + 30) % 360

    @Slot(str, int, int)
    def _show_progress(self, message: str, completed: int, total: int) -> None:  # noqa: PLR0917 (queued signal)
        """
        Show cumulative progress across the decks and the final package
        write.
        """
        if self._job is not None and self._job.control.canceled.is_set():
            return
        self.status.setText(message)
        self.progress.setRange(0, total)
        self.progress.setValue(completed)

    @Slot()
    def _export_finished(self) -> None:
        """
        Keep the outcome visible and allow a failed export to be
        retried.
        """
        job = self._job
        assert job is not None
        self._job = None
        job.deleteLater()
        self._spinner.stop()
        if job.control.canceled.is_set():
            super().reject()
            return
        self.dismiss.setEnabled(True)
        self.dismiss.setText("Close")
        if job.error:
            for animation in self._check_animations:
                animation.stop()
            for row, plan in zip(self.rows, self.plans, strict=True):
                if plan.cards:
                    row.setIcon(2, QIcon())
                    row.setText(
                        2,
                        "Failed"
                        if row.text(2) == "In progress"
                        else "Not exported",
                    )
            self.progress.hide()
            self.status.setText(job.error)
            self.destination.setEnabled(True)
            self.save.setEnabled(True)
        else:
            noun = "card" if job.count == 1 else "cards"
            self.status.setText(
                "Export successful. Saved "
                f"{job.count}"
                " "
                f"{noun}"
                " to "
                f"{job.path.name}"
                ".",
            )
            self.browse.hide()
            self.save.hide()
            self.dismiss.setDefault(True)
            self.dismiss.setFocus()
        if self._close_when_ready:
            self.reject()

    def reject(self) -> None:
        """
        Confirm cancellation of an active write before closing its
        dialog.
        """
        job = self._job
        if job is None:
            self.finish_then_close()
        elif self.dismiss.isEnabled():
            self.dismiss.setEnabled(False)
            canceled = job.control.confirm_cancel(self._confirm_cancel)
            if self._job is job:
                if canceled:
                    self.status.setText("Canceling export…")
                else:
                    self.dismiss.setEnabled(True)

    def finish_then_close(self) -> None:
        """
        Defer window teardown until both worker threads have finished.
        """
        if self._job is None and self._counter is None:
            super().reject()
        else:
            self._close_when_ready = True

    def _confirm_cancel(self) -> bool:
        """
        Ask before discarding the package being prepared.

        Returns
        -------
        bool
            True when the user chooses to cancel the export.
        """
        answer = QMessageBox.warning(
            self,
            "Cancel export?",
            "Cancel this export and discard the unfinished package?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes


class AnkiExporter(QDialog):
    """
    Select exercise decks, preview cards, and export an Anki package.
    """

    def __init__(
        self,
        learner: Learner | None,
        *,
        reviews: dict[str, list[Review]],
        selected: str = "",
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the deck navigation, card preview, and private exercise
        settings.
        """
        super().__init__(parent, Qt.WindowType.Window)
        self.reviews = reviews
        self.export_dialog: _ExportDialog | None = None
        self._close_after_export = False
        self.learner = learner
        self.setWindowTitle("Anki Exporter")
        self.resize(1080, 640)
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        layout.addLayout(toolbar)
        self.nav_toggle = QToolButton()
        self.nav_toggle.setAutoRaise(True)
        self.nav_toggle.setIconSize(QSize(px(18), px(18)))
        self.nav_toggle.setCheckable(True)
        self.nav_toggle.setChecked(True)
        self.nav_toggle.setToolTip("Show or hide exercise decks")
        self.nav_toggle.setAccessibleName("Exercise decks")
        toolbar.addWidget(self.nav_toggle)
        self.heading = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.heading.setObjectName("activityTitle")
        toolbar.addWidget(self.heading, 1)
        self.gear = QToolButton()
        self.gear.setAutoRaise(True)
        self.gear.setIconSize(QSize(px(24), px(24)))
        self.gear.setAccessibleName("Exercise settings")
        self.gear.setToolTip("Show or hide exercise settings")
        self.gear.setCheckable(True)
        toolbar.addWidget(self.gear)
        body = QHBoxLayout()
        layout.addLayout(body, 1)
        self.tree = category_tree("Exercise decks")
        body.addWidget(self.tree)
        self.nav_toggle.toggled.connect(self.tree.setVisible)
        self.nav_toggle.toggled.connect(self._style_nav_toggle)
        self.items: dict[type[Exercise], QTreeWidgetItem] = {}
        self.exercises = {cls: cls() for cls in REGISTRY}
        root = QTreeWidgetItem(self.tree, ["All exercises"])
        root.setFlags(root.flags() | Qt.ItemFlag.ItemIsAutoTristate)
        groups: dict[str, QTreeWidgetItem] = {}
        initial = next(
            (cls for cls in REGISTRY if cls.__name__ == selected),
            REGISTRY[0],
        )
        for index, cls in enumerate(REGISTRY):
            if cls.category not in groups:
                group = groups[cls.category] = QTreeWidgetItem(
                    root,
                    [cls.category],
                )
                group.setFlags(group.flags() | Qt.ItemFlag.ItemIsAutoTristate)
            leaf = self.items[cls] = QTreeWidgetItem(
                groups[cls.category],
                [cls.name],
            )
            leaf.setData(0, Qt.ItemDataRole.UserRole, index)
            leaf.setToolTip(0, cls.description)
            leaf.setCheckState(
                0,
                Qt.CheckState.Checked
                if cls is initial
                else Qt.CheckState.Unchecked,
            )
        self.group_items = [root, *groups.values()]
        self._style_navigation()
        self.tree.expandAll()
        # Leave room for nested labels, the branch column, and the
        # scrollbar at short window heights.
        self.tree.setFixedWidth(
            self.tree.sizeHintForColumn(0)
            + self.tree.columnWidth(1)
            + 3 * self.tree.indentation()
            + self.tree.verticalScrollBar().sizeHint().width()
            + 2 * self.tree.frameWidth(),
        )
        for item in (root, *groups.values(), *self.items.values()):
            item.setSizeHint(0, QSize(0, px(30)))
        center = QVBoxLayout()
        body.addLayout(center, 1)
        self.side = SegmentedControl(["Front", "Back"])
        center.addWidget(self.side, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.preview = QTextBrowser()
        self.preview.setObjectName("detailPane")
        self.preview.setAccessibleName("Sample card")
        center.addWidget(self.preview, 1)
        self.fields: list[str] = []
        self.pane = QFrame()
        self.pane.setObjectName("settingsPane")
        self.pane.setFixedWidth(px(290))
        self.pane_layout = QVBoxLayout(self.pane)
        self.pane.hide()
        body.addWidget(self.pane)
        self.gear.toggled.connect(self.pane.setVisible)
        self.matching = QLabel()
        self.pane_layout.addWidget(self.matching)
        self.panel: ExerciseSettingsPanel | None = None
        footer = QHBoxLayout()
        layout.addLayout(footer)
        self.scheduling = QCheckBox("Include scheduling")
        self.scheduling.setEnabled(
            learner is not None and learner.mode in CALENDAR_SCHEDULERS,
        )
        self.scheduling.setToolTip(
            (
                "Include existing SM-2 or FSRS review dates and intervals "
                "from the active profile."
            ),
        )
        footer.addWidget(self.scheduling)
        self.status = QLabel()
        self.status.setWordWrap(True)
        footer.addWidget(self.status, 1)
        self.save = QPushButton("Export…")
        self.save.setProperty("primary", True)
        footer.addWidget(self.save)
        self.tree.currentItemChanged.connect(self._focus_item)
        self.tree.itemChanged.connect(self._update_selection)
        self.scheduling.toggled.connect(self._refresh_catalog)
        self.side.chosen.connect(self._show_side)
        self.save.clicked.connect(self._save)
        self.tree.setCurrentItem(self.items[initial])

    def _style_nav_toggle(self, expanded: bool) -> None:
        """
        Match the main navigation button's arrow and active accent.
        """
        palette = self.palette()
        self.nav_toggle.setIcon(
            icons.svg_icon(
                icons.NAVIGATION_CLOSE if expanded else icons.NAVIGATION_OPEN,
                color=(
                    palette.highlight() if expanded else palette.windowText()
                ).color(),
            ),
        )

    def _style_navigation(self) -> None:
        """
        Color the navigation icons and section headings with the current
        palette.
        """
        palette = self.palette()
        ink = palette.windowText().color()
        self._style_nav_toggle(self.nav_toggle.isChecked())
        self.gear.setIcon(icons.svg_icon(icons.SLIDERS, color=ink))
        with QSignalBlocker(self.tree):
            for cls, leaf in self.items.items():
                leaf.setIcon(
                    0,
                    icons.svg_icon(
                        exercise_icon(cls.__name__),
                        color=ink,
                        size=icons.ACTIVITY_ICON_SIZE,
                    ),
                )
            font, muted = navigation_heading_style(palette)
            for group in self.group_items:
                group.setFont(0, font)
                group.setForeground(0, muted)

    def changeEvent(self, event: QEvent) -> None:
        """
        Refresh palette-dependent artwork when Qt applies a new theme.
        """
        super().changeEvent(event)
        if event.type() == QEvent.Type.PaletteChange and hasattr(self, "side"):
            self._style_navigation()
            QTimer.singleShot(0, self.side, self.side.restyle)

    def _focus_item(self, item: QTreeWidgetItem) -> None:
        """
        Show the highlighted exercise independently of its export
        checkbox.
        """
        index = item.data(0, Qt.ItemDataRole.UserRole)
        if index is None:
            return
        self.exercise = self.exercises[REGISTRY[index]]
        if self.panel is not None:
            self.pane_layout.removeWidget(self.panel)
            self.panel.hide()
            self.panel.deleteLater()
        self.panel = settings_panel_for(self.exercise, learner=self.learner)
        self.panel.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Ignored,
        )
        self.pane_layout.addWidget(self.panel, 1)
        self.panel.changed.connect(self._refresh_catalog)
        self.heading.setText(self.exercise.name)
        self._refresh_catalog()

    def _selection(self, exercise: Exercise) -> DeckSelection:
        """
        Read the current export options for one deck.

        Returns
        -------
        DeckSelection
            Exercise and eligible review records.
        """
        reviews = (
            self.reviews.get(type(exercise).__name__, [])
            if self.scheduling.isChecked()
            else []
        )
        return DeckSelection(exercise, reviews)

    def _checked(self) -> list[Exercise]:
        """
        Read the exercise checkboxes.

        Returns
        -------
        list of Exercise
            Checked exercises in navigation order.
        """
        return [
            self.exercises[cls]
            for cls, item in self.items.items()
            if item.checkState(0) == Qt.CheckState.Checked
        ]

    def _update_selection(self) -> None:
        """
        Update the export button without changing the active preview.
        """
        checked = self._checked()
        self.save.setEnabled(any(ex.card_count() != 0 for ex in checked))
        self.status.setText(
            f"{len(checked)}"
            " "
            f"{('deck' if len(checked) == 1 else 'decks')}"
            " selected",
        )

    def _refresh_catalog(self) -> None:
        """
        Update the matching card count and preview for the highlighted
        deck.
        """
        count = self.exercise.card_count()
        self.matching.setVisible(count is not None)
        self.matching.setText(f"Matching cards: {count}")
        self._update_selection()
        sample = next(
            deck_candidates(
                self.exercise,
                reviews=self._selection(self.exercise).reviews,
            ),
            None,
        )
        self.side.setEnabled(sample is not None)
        self.fields = []
        doc = QTextDocument(self.preview)
        self.preview.setDocument(doc)
        if sample is not None:
            with TemporaryDirectory() as folder:
                work = Path(folder)
                self.fields = card_fields(
                    sample[0],
                    folder=work,
                    exercise=self.exercise,
                )
                for image in work.glob("*.png"):
                    doc.addResource(
                        QTextDocument.ResourceType.ImageResource,
                        QUrl(image.name),
                        QImage(str(image)),
                    )
        self._show_side()

    def _show_side(self) -> None:
        """
        Display either face using the fields and illustrations prepared
        for the same sample.
        """
        if not self.fields:
            self.preview.setPlainText("No cards match these settings.")
            return
        prompt, illustration, answer, explanation = self.fields
        html = f"<p>{prompt}</p><p>{illustration}</p>"
        if self.side.current() == 1:
            html += f"<hr><p>{answer}</p><p>{explanation}</p>"
        html = html.replace("<img ", '<img style="max-width:100%" ')
        self.preview.setHtml(
            f'<div align="center" style="font-size: 20px">{html}</div>',
        )

    def _save(self) -> None:
        """
        Open the destination and summary for the checked exercises.
        """
        dialog = self.export_dialog = _ExportDialog(
            [self._selection(ex) for ex in self._checked()],
            parent=self,
        )
        dialog.finished.connect(self._dialog_closed)
        dialog.open()

    def _dialog_closed(self) -> None:
        """
        Release the completed dialog and honor a pending window close.
        """
        assert self.export_dialog is not None
        self.export_dialog.deleteLater()
        self.export_dialog = None
        if self._close_after_export:
            super().reject()

    def reject(self) -> None:
        """
        Keep the export process alive until the destination dialog can
        close.
        """
        if self.export_dialog is None:
            super().reject()
        else:
            self._close_after_export = True
            self.export_dialog.finish_then_close()


class ExporterSession:
    """
    Manage a modeless Qt window with its own exercise settings and Qt
    settings store.
    """

    def __init__(self) -> None:
        """Start with no exporter open."""
        self.process: BaseProcess | None = None
        self.commands: Connection | None = None

    def open(self, learner: Learner | None, *, selected: str) -> None:
        """
        Raise the existing exporter or spawn a window for the active
        profile.

        Parameters
        ----------
        learner : Learner or None
            Active profile whose review dates and practice limits are
            available.
        selected : str
            Class name of the exercise to select when opening.

        Raises
        ------
        OSError
            If the system cannot start the exporter.
        """
        if (
            self.process is not None
            and self.process.is_alive()
            and self.commands is not None
        ):
            try:
                self.commands.send("raise")
            except (BrokenPipeError, EOFError, ConnectionResetError):
                pass
            else:
                return
        self.close()
        ctx = multiprocessing.get_context("spawn")
        receiver, sender = ctx.Pipe(duplex=False)
        mode = learner.mode if learner is not None else None
        limits = []
        if learner is not None:
            limits = [
                tuple(row)
                for row in learner.db.conn.execute(
                    (
                        "SELECT exercise, new_cards, reviews FROM "
                        "practice_limits WHERE profile_id=?"
                    ),
                    (learner.profile.id,),
                )
            ]
        process = ctx.Process(
            target=_run_exporter,
            args=(receiver,),
            kwargs={
                "plugins": database_path().parent / "plugins",
                "desktop_id": QApplication.desktopFileName() or desktop_name(),
                "preferences": export_settings(),
                "selected": selected,
                "mode": mode,
                "self_grading": learner.self_grading
                if learner is not None
                else False,
                "limits": limits,
                "reviews": profile_reviews(learner)
                if learner is not None
                else {},
            },
        )
        try:
            process.start()
        except OSError:
            sender.close()
            raise
        finally:
            receiver.close()
        self.process, self.commands = process, sender
        atexit.register(self.close)

    def sync_theme(self, key: str) -> None:
        """
        Forward the selected palette and any custom colors to an open
        exporter.
        """
        if self.commands is not None:
            try:
                self.commands.send(
                    (
                        "theme",
                        key,
                        text_value(store(), key="ui/userThemes", default="[]"),
                    ),
                )
            except (BrokenPipeError, EOFError, ConnectionResetError):
                self.close()

    def close(self) -> None:
        """
        Close the command pipe so the exporter can finish its current
        write and exit normally.
        """
        if self.commands is not None:
            atexit.unregister(self.close)
            self.commands.close()
        self.commands = None
        self.process = None


def _run_exporter(
    commands: Connection,
    *,
    desktop_id: str,
    preferences: dict[str, object],
    mode: str | None,
    self_grading: bool,
    limits: list[tuple[str, int | None, int | None]],
    reviews: dict[str, list[Review]],
    selected: str,
    plugins: Path,
) -> None:
    """
    Run the exercise controls in isolation from the practice window's
    mutable settings.
    """
    with (
        commands,
        TemporaryDirectory(prefix="alto-export-") as folder,
        closing(Database()) as db,
    ):
        os.environ["ALTO_HOME"] = folder
        QCoreApplication.setAttribute(
            Qt.ApplicationAttribute.AA_DontUseNativeDialogs,
        )
        app = QApplication([desktop_id])
        app.setApplicationName("Alto")
        app.setDesktopFileName(desktop_id)
        import_settings(preferences)
        apply_theme(saved_theme())
        load_packs(plugins)
        load_exercise_settings()
        load_notation_style()
        load_keyboard_style()
        app.setWindowIcon(
            QIcon(
                str(
                    Path(__file__).resolve().parents[1]
                    / "assets"
                    / "icon.svg",
                ),
            ),
        )
        learner = None
        if mode is not None:
            learner = Learner(db, profile=db.add_profile("Export"))
            learner.set_mode(mode)
            learner.set_self_grading(self_grading)
            for name, new, daily in limits:
                learner.calendar.set_limits(
                    learner.profile.id,
                    exercise=name,
                    new_cards=new,
                    reviews=daily,
                )
        window = AnkiExporter(learner, reviews=reviews, selected=selected)

        def receive() -> None:
            """
            Raise the window on a repeat menu click and exit when its
            parent closes the pipe.
            """
            if commands.poll():
                try:
                    command = commands.recv()
                except EOFError:
                    timer.stop()
                    window.close()
                    return
                if command == "raise":
                    window.showNormal()
                    window.raise_()
                    window.activateWindow()
                else:
                    _, theme, user_themes = command
                    saved = store()
                    saved.setValue("ui/userThemes", user_themes)
                    saved.setValue("ui/theme", theme)
                    apply_theme(theme)

        timer = QTimer(window)
        timer.timeout.connect(receive)
        timer.start(150)
        window.show()
        app.exec()
