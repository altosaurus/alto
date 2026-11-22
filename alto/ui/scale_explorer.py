"""
Interactive notation and step patterns for learning scales.

Examples
--------
>>> explorer = ScaleExplorer()
>>> len(explorer.notes)
8
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPalette, QWheelEvent
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from alto.theory.pitch import Note
from alto.theory.scales import SCALES, build
from alto.ui.staff import StaffWidget
from alto.ui.staff_playback import StaffPlayback
from alto.ui.zoom import css, px


class ScaleExplorer(QWidget):
    """
    Compare scales on a staff and hear individual steps.

    Examples
    --------
    >>> ScaleExplorer().mode.currentText()
    'Major (Ionian)'
    """

    def __init__(
        self,
        *,
        scale: str = "Major (Ionian)",
        tonic: str = "C4",
        editable: bool = True,
        lesson_layout: bool = False,
    ) -> None:
        """
        Build the scale diagram and its controls.

        Parameters
        ----------
        scale : str
            Initial scale type.
        tonic : str
            Initial tonic with octave.
        editable : bool
            Allow changing the example; false keeps a lesson question fixed.
        lesson_layout : bool
            Use content-sized staff lines in the lesson pane.

        Examples
        --------
        >>> ScaleExplorer(scale="Dorian", tonic="D4").notes[0].name
        'D'
        """
        super().__init__()
        self.notes: list[Note] = []
        self.playback = StaffPlayback(self, highlight=self._highlight_playback)
        self._flash_timer = QTimer(self)
        self._flash_timer.setSingleShot(True)
        self._flash_timer.setInterval(150)
        self._flash_timer.timeout.connect(self._clear_playback_highlight)
        self._playback_notes: list[int] = []
        self._selected_notes: list[int] = []
        layout = QVBoxLayout(self)
        self.tonic = _ScaleComboBox()
        for name in ("C", "D♭", "D", "E♭", "E", "F", "F♯", "G", "A♭", "A", "B♭", "B"):
            self.tonic.addItem(name, name.replace("♭", "b").replace("♯", "#") + "4")
        self.tonic.setCurrentIndex(max(0, self.tonic.findData(tonic)))
        self.tonic.setAccessibleName("Example tonic")
        self.tonic.setProperty("field", True)
        self.mode = _ScaleComboBox()
        self.mode.addItems(list(SCALES))
        self.mode.setCurrentText(scale)
        self.mode.setAccessibleName("Example scale type")
        self.mode.setProperty("field", True)
        controls = QWidget()
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(QLabel("Tonic"))
        controls_layout.addWidget(self.tonic)
        controls_layout.addWidget(QLabel("Scale type"))
        controls_layout.addWidget(self.mode)
        controls.setVisible(editable)
        layout.addWidget(controls)
        self.staff = StaffWidget(gap=9.0, margin=6.0, note_offset=55.0, side=12.0, compact=True, lesson_layout=lesson_layout)
        self.staff.setMinimumWidth(0)
        if lesson_layout:
            layout.addWidget(self.staff, alignment=Qt.AlignmentFlag.AlignLeft)
        else:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFixedHeight(px(180))
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setWidget(self.staff)
            layout.addWidget(scroll)
        self.names = QLabel()
        self.names.setWordWrap(True)
        layout.addWidget(self.names)
        hint = QLabel("Select a gap to highlight and hear its two notes. W = 2 semitones; H = 1; 3H = 3.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        self.steps: list[QPushButton] = []
        gaps = QHBoxLayout()
        gaps.setSpacing(2)
        for index in range(7):
            button = QPushButton()
            button.setMinimumWidth(0)
            button.setStyleSheet(css("QPushButton { padding: 5px 2px; }"))
            button.clicked.connect(lambda _checked=False, gap=index: self.select_gap(gap))
            gaps.addWidget(button)
            self.steps.append(button)
        layout.addLayout(gaps)
        self.detail = QLabel()
        self.detail.setWordWrap(True)
        layout.addWidget(self.detail)
        hear = QPushButton("▶  Hear this scale")
        hear.clicked.connect(self.hear)
        layout.addWidget(hear)
        self.tonic.currentIndexChanged.connect(self.refresh)
        self.mode.currentIndexChanged.connect(self.refresh)
        self.refresh()

    def refresh(self) -> None:
        """
        Rebuild the notation and gap labels for the selected example.

        Examples
        --------
        >>> explorer = ScaleExplorer()
        >>> explorer.mode.setCurrentText("Harmonic minor")
        >>> explorer.steps[5].text()
        '3H'
        """
        self.playback.stop()
        self._flash_timer.stop()
        self._selected_notes = []
        tonic = Note.parse(self.tonic.currentData())
        self.notes = build(tonic, intervals=SCALES[self.mode.currentText()])
        self.notes.append(Note(tonic.octave + 1, letter=tonic.letter, accidental=tonic.accidental))
        self.staff.column_colors = {}
        self.staff.wedge_colors = {}
        self.names.setText(" → ".join(note.name for note in self.notes))
        for index, button in enumerate(self.steps):
            semitones = self.notes[index + 1].midi - self.notes[index].midi
            button.setText({1: "H", 2: "W", 3: "3H"}[semitones])
            button.setAccessibleName(f"Degrees {index + 1} to {index + 2}: {semitones} semitones")
        self.staff.wedges = [button.text() for button in self.steps]
        self.staff.show_notes([[note] for note in self.notes], clef="treble")
        self.detail.setText("The first and last notes are the tonic, an octave apart.")

    def select_gap(self, index: int) -> None:
        """
        Highlight and play the notes around a gap.

        Parameters
        ----------
        index : int
            Gap index, from zero to six.

        Examples
        --------
        >>> explorer = ScaleExplorer()
        >>> explorer.select_gap(2)  # doctest: +SKIP
        """
        first, second = self.notes[index : index + 2]
        self.playback.stop()
        self._flash_timer.stop()
        color = self.palette().color(QPalette.ColorRole.Highlight)
        self._selected_notes = [index, index + 1]
        self.staff.column_colors = dict.fromkeys(self._selected_notes, color)
        self._keep_wedges_unhighlighted()
        self.staff.wedge_colors[index] = color
        self.staff.update()
        self.detail.setText(
            f"Degree {index + 1} → {index + 2}: {first.name} → {second.name}, {second.midi - first.midi} semitone(s).",
        )
        self._playback_notes = [index, index + 1]
        self.playback.play([[first], [second]], gap_ms=450, force=True)

    def hear(self, *, force: bool = True) -> None:
        """
        Play the example using the selected instrument.

        Parameters
        ----------
        force : bool
            Audition the scale while muted. The lesson's main Hear button follows its sound setting.

        Examples
        --------
        >>> ScaleExplorer().hear()  # doctest: +SKIP
        """
        self.playback.stop()
        self._flash_timer.stop()
        self._playback_notes = list(range(len(self.notes)))
        self._selected_notes = []
        self._keep_wedges_unhighlighted()
        self._clear_playback_highlight()
        self.playback.play(self.staff.columns, gap_ms=350, force=force)

    def _keep_wedges_unhighlighted(self) -> None:
        """Keep the W/H labels and their brackets in the staff's normal text color."""
        color = QColor("black")
        self.staff.wedge_colors = {index: color for index in range(len(self.steps))}

    def _highlight_playback(self, index: int | None) -> None:
        """
        Flash the sounding note while retaining the selected scale or gap.

        Parameters
        ----------
        index : int or None
            Note within the sample, or None after playback.
        """
        if index is None:
            self._flash_timer.stop()
            self._clear_playback_highlight()
        else:
            color = self.palette().color(QPalette.ColorRole.Highlight)
            sounding = self._playback_notes[index]
            if sounding not in self._selected_notes:
                self._selected_notes.append(sounding)
            self.staff.column_colors = dict.fromkeys(self._selected_notes, color)
            self.staff.column_colors[sounding] = color.lighter(160)
            self._flash_timer.start()
        self.staff.update()

    def _clear_playback_highlight(self) -> None:
        """End the brief highlight after a note onset."""
        color = self.palette().color(QPalette.ColorRole.Highlight)
        self.staff.column_colors = dict.fromkeys(self._selected_notes, color)
        self.staff.update()


class _ScaleComboBox(QComboBox):
    """A scale selector that lets its containing pane handle wheel scrolling."""

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Ignore wheel turns so the parent scroll area can scroll.

        Parameters
        ----------
        event : QWheelEvent
            The wheel event to pass to the parent.

        Examples
        --------
        >>> _ScaleComboBox().wheelEvent  # doctest: +SKIP
        """
        event.ignore()
