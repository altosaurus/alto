"""A searchable glossary of the notation terms used in Alto."""

from dataclasses import dataclass
from itertools import pairwise
from math import ceil

from PySide6.QtCore import QSize, QSizeF, Qt, Signal
from PySide6.QtGui import QHideEvent, QIcon, QKeySequence, QResizeEvent, QShortcut
from PySide6.QtWidgets import (
    QBoxLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from alto.audio import sounds
from alto.exercises import REGISTRY
from alto.lessons import LESSONS
from alto.theory.pitch import Note
from alto.ui.home import ExerciseCard, lesson_card
from alto.ui.icons import SEARCH, set_svg_icon
from alto.ui.keyboard import KeyboardWidget
from alto.ui.reference import ExplorableCircle
from alto.ui.staff import StaffWidget
from alto.ui.staff_playback import StaffPlayback
from alto.ui.widgets import SegmentedControl

_STEP_LABELS = {1: "H", 2: "W", 3: "3H"}


@dataclass(frozen=True)
class _Example:
    """A caption and the spelled pitches to display and play, in reading order."""

    pitches: str
    caption: str
    clef: str = "treble"
    signature: int = 0


@dataclass(frozen=True, kw_only=True)
class _Term:
    """Keep the explanation, demonstration, and practice material for one concept together."""

    definition: str
    guide: str
    examples: tuple[_Example, ...]
    exercises: tuple[str, ...]
    lesson: str
    keyboard: bool = False
    label_steps: bool = False
    circle: bool = False


TERMS = {
    "pitch": _Term(
        definition="Pitch is how high or low a sound seems. For a steady tone, faster vibrations produce a higher pitch.",
        guide="Play the two notes and follow them from left to right. A higher note on this staff also sounds higher.",
        examples=(
            _Example("C4 G4", "From middle C up to G"),
            _Example("G4 C4", "From G down to middle C"),
        ),
        exercises=("NoteNames", "KeyboardNotes"),
        lesson="pitches-and-notes",
    ),
    "octave": _Term(
        definition="An octave is the interval from one note to the next higher or lower note of the same name. "
        "It spans twelve half steps. The higher pitch has twice the frequency of the lower one.",
        guide="Count the letter names from C up to the next C, including both ends: C, D, E, F, G, A, B, C. "
        "Play the pair to hear how two notes can share a name at different heights.",
        examples=(
            _Example("C4 C5", "Middle C and the C one octave higher"),
            _Example("F4 F5", "F and the F one octave higher"),
        ),
        exercises=("IntervalNames", "KeyboardIntervals"),
        lesson="pitches-and-notes",
    ),
    "octave register": _Term(
        definition="An octave register is a band of notes that share an octave number. "
        "In scientific pitch notation, each band runs from C through the B above it. Middle C is C4.",
        guide="Follow the letters across the boundary. The number increases as B rises to C and stays the same "
        "as C rises to D. Accidentals keep the octave number of their written letter.",
        examples=(
            _Example("B3 C4 D4", "B3 → C4 → D4"),
            _Example("B4 C5 D5", "B4 → C5 → D5"),
        ),
        exercises=("NoteNames", "KeyboardNotes"),
        lesson="pitches-and-notes",
    ),
    "staff": _Term(
        definition="A staff is a set of five horizontal lines. The center of a notehead sits on a line or in a space. "
        "The clef tells you which letter name belongs to each position.",
        guide="Count from the bottom. In treble clef the first line is E, the space above it is F, "
        "and the second line is G. Follow the noteheads up one position at a time.",
        examples=(
            _Example("E4 F4 G4", "E on line 1, F in space 1, G on line 2"),
            _Example("G4 A4 B4", "G on line 2, A in space 2, B on line 3"),
        ),
        exercises=("NoteNames", "NoteConstruction"),
        lesson="clef-basics",
    ),
    "ledger lines": _Term(
        definition="Ledger lines are short lines that extend the staff above or below its five lines. "
        "They keep the same spacing as the staff and are drawn only where a note needs them.",
        guide="Look at the bottom of the treble staff. D fits in the space just below it. Middle C sits on "
        "the first ledger line. The A below middle C needs a second ledger line.",
        examples=(
            _Example("D4 C4 A3", "Below the staff: zero, one, then two ledger lines"),
            _Example("G5 A5 C6", "Above the staff: zero, one, then two ledger lines"),
        ),
        exercises=("NoteNames", "NoteConstruction"),
        lesson="clef-basics",
    ),
    "clef": _Term(
        definition="A clef is a sign that assigns a pitch to a particular staff line. "
        "Once that line is known, the other lines and spaces follow in letter order.",
        guide="Find the line marked by each clef. The treble clef curls around G, the bass clef’s dots straddle F, "
        "and the center of a C clef marks middle C. Count lines from the bottom.",
        examples=(
            _Example("G4", "Treble clef marks G4 on line 2"),
            _Example("F3", "Bass clef marks F3 on line 4", clef="bass"),
            _Example("C4", "Alto clef marks middle C on line 3", clef="alto"),
            _Example("C4", "Tenor clef marks middle C on line 4", clef="tenor"),
        ),
        exercises=("ClefBasics", "NoteNames"),
        lesson="clef-basics",
    ),
    "grand staff": _Term(
        definition="A grand staff is a pair of staves joined by a brace and read together. "
        "Piano scores usually put a treble clef on the upper staff and a bass clef on the lower one.",
        guide="Follow the notes across the gap. Middle C can be written on one ledger line below the treble "
        "staff or one above the bass staff. Here it is written just below the treble staff.",
        examples=(
            _Example("B3 C4 D4", "B below middle C, middle C, then D above it", clef="grand"),
            _Example("C3 C4 C5", "Three Cs, each an octave above the last", clef="grand"),
        ),
        exercises=("NoteNames", "NoteConstruction"),
        lesson="clef-basics",
    ),
    "major scale": _Term(
        definition="A major scale has seven different letter names. Going up from its starting note (the tonic) "
        "to the next tonic, the steps are whole, whole, half, whole, whole, whole, half.",
        guide="Read the marks between the notes. W means a whole step and H means a half step. "
        "In C major the half steps are E–F and B–C. Switch to G major and find them in the same two places.",
        examples=(
            _Example("C4 D4 E4 F4 G4 A4 B4 C5", "C major · half steps at E–F and B–C"),
            _Example("G4 A4 B4 C5 D5 E5 F#5 G5", "G major · half steps at B–C and F♯–G", signature=1),
        ),
        exercises=("ScaleIdentification", "ScaleConstruction"),
        lesson="scale-identification",
        label_steps=True,
    ),
    "half step": _Term(
        definition="A half step, also called a semitone, is the distance from one piano key to its immediate "
        "neighbor in either direction. Count black keys as well as white keys.",
        guide="Look for a key between the two highlighted pitches. E and F touch with no black key between them. "
        "C and C♯ are just as close, even though their keys have different colors.",
        examples=(
            _Example("E4 F4", "E to F · adjacent white keys"),
            _Example("C4 C#4", "C to C♯ · adjacent white and black keys"),
        ),
        exercises=("KeyboardIntervals", "ScaleConstruction"),
        lesson="scale-identification",
        keyboard=True,
    ),
    "whole step": _Term(
        definition="A whole step, also called a whole tone, is an interval of two half steps. "
        "On a piano, exactly one key lies between the two pitches.",
        guide="Trace the two half steps between the highlighted keys. From C to D you pass over C♯. "
        "From E to F♯ you pass over F.",
        examples=(
            _Example("C4 D4", "C to D · C♯ lies between"),
            _Example("E4 F#4", "E to F♯ · F lies between"),
        ),
        exercises=("KeyboardIntervals", "ScaleConstruction"),
        lesson="scale-identification",
        keyboard=True,
    ),
    "tetrachord": _Term(
        definition="A tetrachord is a series of four pitches spanning a perfect fourth (five half steps). "
        "In a major tetrachord the three steps are whole, whole, half.",
        guide="C major contains two major tetrachords. Read C–D–E–F, then switch to G–A–B–C. "
        "Each ends with a half step. A whole step from F to G joins the two groups.",
        examples=(
            _Example("C4 D4 E4 F4", "C–D–E–F · lower tetrachord of C major"),
            _Example("G4 A4 B4 C5", "G–A–B–C · upper tetrachord of C major"),
        ),
        exercises=("ScaleIdentification", "ScaleConstruction"),
        lesson="scale-identification",
        label_steps=True,
    ),
    "accidental": _Term(
        definition="An accidental is a sign before a notehead that raises, lowers, or restores the pitch of that letter. "
        "A sharp raises the letter’s natural pitch by a half step, a flat lowers it by a half step, "
        "and a natural sign calls for the unaltered pitch.",
        guide="Compare the two notes in each example. Their staff position stays the same. "
        "Read the sign before the second note and listen for which way the pitch moves. "
        "An accidental normally carries through the measure for that letter in that octave.",
        examples=(
            _Example("F4 F#4", "F to F♯ · the sharp raises the second note"),
            _Example("B4 Bb4", "B to B♭ · the flat lowers the second note"),
            _Example("F#4 F4", "F♯ to F♮ · the natural cancels the signature’s F♯", signature=1),
        ),
        exercises=("NoteNames", "NoteConstruction"),
        lesson="scale-identification",
    ),
    "key": _Term(
        definition="The key of a passage tells you which note sounds like home (the tonic) and whether the music "
        "is in major or minor. Melodies and chords establish the key by moving away from and returning to the tonic.",
        guide="Both examples have an empty key signature. Listen to the opening chord played one note at a time, "
        "then hear the melody settle back on C in C major or A in A minor.",
        examples=(
            _Example("C4 E4 G4 D4 C4", "C major · hear D settle on C"),
            _Example("A4 C5 E5 B4 A4", "A minor · hear B settle on A"),
        ),
        exercises=("ScaleIdentification", "CircleOfFifths"),
        lesson="circle-of-fifths",
    ),
    "key signature": _Term(
        definition="A key signature is the pattern of sharps or flats written after the clef. It sets the default "
        "pitch for each affected letter in every octave until the signature changes. An accidental can override it locally.",
        guide="Compare the same two Fs with an empty signature and with one sharp. The noteheads stay in place, "
        "but the sharp beside the clef raises both Fs. Then try the flat signature and listen to the two Bs.",
        examples=(
            _Example("F4 F5", "Empty signature · F4 and F5"),
            _Example("F#4 F#5", "One sharp in the signature · F♯4 and F♯5", signature=1),
            _Example("Bb3 Bb4", "One flat in the signature · B♭3 and B♭4", signature=-1),
        ),
        exercises=("KeySignatures", "KeySignatureConstruction"),
        lesson="circle-of-fifths",
    ),
    "enharmonic": _Term(
        definition="Enharmonic describes a change in spelling that keeps the same sounding pitch on an equal-tempered "
        "instrument such as a piano. The spelling can show where a note is heading.",
        guide="Play both phrases. The middle note sounds the same each time. C♯ leads up to D in the first "
        "phrase. D♭ leads down to C in the second.",
        examples=(
            _Example("C4 C#4 D4", "C–C♯–D · a rising line"),
            _Example("D4 Db4 C4", "D–D♭–C · a falling line"),
        ),
        exercises=("NoteNames", "NoteConstruction"),
        lesson="pitches-and-notes",
    ),
    "enharmonically equivalent": _Term(
        definition="Two notes are enharmonically equivalent when they have different written names but sound at "
        "the same pitch in equal temperament.",
        guide="Play each pair. The notehead moves to a different staff position, yet you hear one piano key "
        "struck twice. Even a white key can have two names.",
        examples=(
            _Example("F#4 Gb4", "F♯ and G♭ share a black key"),
            _Example("B#4 C5", "B♯ and C share a white key"),
        ),
        exercises=("NoteNames", "KeyboardNotes"),
        lesson="pitches-and-notes",
    ),
    "transpose": _Term(
        definition="To transpose music is to move every note up or down by the same interval. "
        "The starting pitch changes while the distances between notes and their rhythm stay the same.",
        guide="Play the phrase in C, then switch to D. Each note has moved up a whole step. "
        "The last note moves from E to F♯ so the last step of the melody keeps its sound.",
        examples=(
            _Example("C4 D4 F4 E4", "Original phrase · C–D–F–E"),
            _Example("D4 E4 G4 F#4", "Up a whole step · D–E–G–F♯", signature=2),
        ),
        exercises=("IntervalNames", "NoteConstruction"),
        lesson="intervals",
    ),
    "circle of fifths": _Term(
        definition="The circle of fifths is a diagram of keys arranged by their tonics. Each clockwise step "
        "takes you up a perfect fifth. Starting at C major, the signatures gain one sharp per step clockwise "
        "or one flat per step counterclockwise until the sharp and flat spellings meet.",
        guide="Follow the major keys on the outer ring. Play the two tonics, then switch examples. "
        "Moving clockwise from C to G to D gives one sharp, then two. Moving one place the other way from C gives F.",
        examples=(
            _Example("C4 G4", "C to G clockwise · G major has one sharp", signature=1),
            _Example("G4 D5", "G to D clockwise · D major has two sharps", signature=2),
            _Example("C5 F4", "C to F counterclockwise · F major has one flat", signature=-1),
        ),
        exercises=("CircleOfFifths", "KeySignatures"),
        lesson="circle-of-fifths",
        circle=True,
    ),
    "natural minor scale": _Term(
        definition="A natural minor scale rises from its tonic by whole, half, whole, whole, half, whole, "
        "and whole steps. It uses the notes of the minor key signature.",
        guide="Find the two half steps, marked H. In A minor they fall between B and C and between E and F. "
        "Switch to E minor and hear the same pattern from a different tonic.",
        examples=(
            _Example("A3 B3 C4 D4 E4 F4 G4 A4", "A natural minor · no sharps or flats"),
            _Example("E4 F#4 G4 A4 B4 C5 D5 E5", "E natural minor · one sharp", signature=1),
        ),
        exercises=("ScaleIdentification", "ScaleConstruction"),
        lesson="scale-identification",
        label_steps=True,
    ),
    "harmonic minor scale": _Term(
        definition="Harmonic minor raises the seventh degree of natural minor by a half step. "
        "That seventh degree, the leading tone, is now a half step below the tonic.",
        guide="Listen to the last three notes. The gap marked 3H spans three half steps from degree 6 to "
        "degree 7. The leading tone then rises just one half step to the tonic.",
        examples=(
            _Example("A3 B3 C4 D4 E4 F4 G#4 A4", "A harmonic minor · F to G♯ to A"),
            _Example("E4 F#4 G4 A4 B4 C5 D#5 E5", "E harmonic minor · C to D♯ to E", signature=1),
        ),
        exercises=("ScaleIdentification", "ScaleConstruction"),
        lesson="scale-identification",
        label_steps=True,
    ),
    "melodic minor scale": _Term(
        definition="In the traditional ascending form, melodic minor raises the sixth and seventh degrees of "
        "natural minor by a half step each. The traditional descending form uses natural minor.",
        guide="Follow D minor up, then down. On the way up, B♮ and C♯ lead to D. On the way down, "
        "listen for C♮ and B♭. The key signature stays the same.",
        examples=(
            _Example("D4 E4 F4 G4 A4 B4 C#5 D5", "D melodic minor ascending · B♮ and C♯", signature=-1),
            _Example("D5 C5 Bb4 A4 G4 F4 E4 D4", "D melodic minor descending · C♮ and B♭", signature=-1),
        ),
        exercises=("ScaleIdentification", "ScaleConstruction"),
        lesson="scale-identification",
        label_steps=True,
    ),
    "minor pentachord": _Term(
        definition="A minor pentachord consists of the first five notes of a minor scale. "
        "From the tonic up to the fifth, its steps are whole, half, whole, whole.",
        guide="Find the H between the second and third notes. All three forms of the minor scale begin "
        "with this same five-note pattern.",
        examples=(
            _Example("A4 B4 C5 D5 E5", "Minor pentachord on A · the half step is B–C"),
            _Example("D4 E4 F4 G4 A4", "Minor pentachord on D · the half step is E–F", signature=-1),
        ),
        exercises=("ScaleConstruction", "ScaleIdentification"),
        lesson="scale-identification",
        label_steps=True,
    ),
    "relative keys": _Term(
        definition="Relative keys are a major key and a minor key with the same key signature. The tonic "
        "of the relative minor lies a minor third below the tonic of the relative major.",
        guide="Play both phrases. Each has one sharp, F♯. The first phrase settles on G. "
        "The second settles on E, the tonic of G major’s relative minor.",
        examples=(
            _Example("G4 B4 D5 F#4 G4", "G major · listen for the return to G", signature=1),
            _Example("E4 G4 B4 F#4 E4", "E minor · listen for the return to E", signature=1),
        ),
        exercises=("CircleOfFifths", "KeySignatures"),
        lesson="key-signatures",
    ),
    "parallel keys": _Term(
        definition="Parallel keys are a major key and a minor key with the same tonic. Their key signatures differ.",
        guide="Both phrases start and end on D. Listen to the third note. The F♯ of D major becomes F♮ in D minor, "
        "while D still sounds like home.",
        examples=(
            _Example("D4 E4 F#4 E4 D4", "D major · two sharps", signature=2),
            _Example("D4 E4 F4 E4 D4", "D minor · one flat", signature=-1),
        ),
        exercises=("KeySignatures", "ScaleIdentification"),
        lesson="key-signatures",
    ),
}


class _DefinitionArea(QScrollArea):
    """Lay out the glossary text and its example in a shared scroll area."""

    def __init__(self, *, definition: QTextBrowser, example: QWidget) -> None:
        super().__init__()
        self.definition = definition
        self.example = example
        self.setObjectName("glossaryDefinition")
        self.setWidgetResizable(True)

        definition.setObjectName("glossaryText")
        definition.setFrameShape(QFrame.Shape.NoFrame)
        definition.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        definition.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        definition.document().documentLayout().documentSizeChanged.connect(self._fit_text)

        content = QWidget()
        self.content_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom, content)
        self.content_layout.setContentsMargins(8, 0, 8, 12)
        self.content_layout.setSpacing(12)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.addWidget(definition, 1, Qt.AlignmentFlag.AlignTop)
        self.content_layout.addWidget(example, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setWidget(content)
        self._fit_text(definition.document().size())

    def _fit_text(self, size: QSizeF) -> None:
        """Give the browser enough height for its wrapped document."""
        self.definition.setFixedHeight(ceil(size.height()))

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Place the example alongside the definition when both can fit."""
        super().resizeEvent(event)
        available = self.viewport().width() - 16  # content margins
        self.example.setFixedWidth(max(280, min(available, 380)))
        wide = available >= 700
        direction = QBoxLayout.Direction.LeftToRight if wide else QBoxLayout.Direction.TopToBottom
        self.content_layout.setDirection(direction)


class GlossaryPage(QWidget):
    """Display definitions and links beside a searchable term list."""

    back = Signal()
    lesson_requested = Signal(str)
    exercise_requested = Signal(str)

    def __init__(self) -> None:
        """Build the glossary and select its first term."""
        super().__init__()
        layout = QHBoxLayout(self)
        sidebar = QWidget()
        sidebar.setMaximumWidth(210)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.search = QLineEdit()
        self.search.setObjectName("glossarySearch")
        self.search.setProperty("field", True)
        self.search.setPlaceholderText("Search terms…")
        self.search.setAccessibleName("Search glossary terms")
        self.search.setClearButtonEnabled(True)
        search_action = self.search.addAction(QIcon(), QLineEdit.ActionPosition.LeadingPosition)
        set_svg_icon(search_action, SEARCH)
        self.terms = QListWidget()
        self.terms.setObjectName("categories")
        self.terms.setProperty("glossaryBox", True)
        self.terms.setSpacing(2)
        for term in sorted(TERMS):
            row = QListWidgetItem(term)
            row.setSizeHint(QSize(0, 40))
            self.terms.addItem(row)
        sidebar_layout.addWidget(self.search)
        sidebar_layout.addWidget(self.terms)
        layout.addWidget(sidebar)
        self.definition = QTextBrowser()
        self.definition.document().setDocumentMargin(14)
        self.definition.setOpenLinks(False)
        self.definition.setAccessibleName("Term definition and related activities")
        main = QVBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        demo = QVBoxLayout()
        self.example_circle = ExplorableCircle()
        self.example_circle.set_interactive(False)
        self.example_circle.setFixedHeight(280)
        demo.addWidget(self.example_circle)
        self.example_staff = StaffWidget(gap=10, side=12, note_offset=60, margin=5, compact=True)
        self.example_keyboard = KeyboardWidget()
        self.example_keyboard.max_key_width = 26
        demo.addWidget(self.example_staff)
        demo.addWidget(self.example_keyboard)
        self.playback = StaffPlayback(self, highlight=self.example_staff.highlight_column)
        self._preview_played = False
        demo_controls = QVBoxLayout()
        self.example_label = QLabel()
        self.example_label.setWordWrap(True)
        demo_controls.addWidget(self.example_label)
        self.next_example = QPushButton("Next example →")
        self.next_example.clicked.connect(self._next_example)
        demo_controls.addWidget(self.next_example)
        self.hear = QPushButton("▶  Hear note")
        self.hear.clicked.connect(self._hear_example)
        demo_controls.addWidget(self.hear)
        demo.addLayout(demo_controls)
        self.demo = QWidget()
        demo.setContentsMargins(0, 0, 0, 0)
        self.demo.setLayout(demo)
        self.definition_area = _DefinitionArea(definition=self.definition, example=self.demo)
        main.addWidget(self.definition_area, 3)
        self.activity_switch = SegmentedControl(["Exercises", "Lessons"])
        self.activity_switch.chosen.connect(self._show_activities)
        main.addWidget(self.activity_switch, alignment=Qt.AlignmentFlag.AlignLeft)
        self.activity_body = QWidget()
        self.activity_tiles = QGridLayout(self.activity_body)
        self.activity_tiles.setContentsMargins(14, 14, 14, 14)
        self.activity_tiles.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll = QScrollArea()
        scroll.setObjectName("glossaryActivities")
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.activity_body)
        main.addWidget(scroll, 2)
        layout.addLayout(main, 1)
        self.search.textChanged.connect(self._filter)
        self.terms.currentItemChanged.connect(self._show_term)
        self.terms.setCurrentRow(0)
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.back.emit)

    def _filter(self, text: str) -> None:
        """Filter the term list and select the first visible match."""
        first = None
        for row in range(self.terms.count()):
            item = self.terms.item(row)
            item.setHidden(text.casefold().strip() not in item.text().casefold())
            if first is None and not item.isHidden():
                first = item
        self.terms.setCurrentRow(self.terms.row(first) if first is not None else -1)
        if first is None:
            self._stop_preview()
            self.definition.setHtml("<h2>No matching terms</h2><p>Try a different search.</p>")
            self.demo.hide()

    def _show_term(self, item: QListWidgetItem | None, _previous: QListWidgetItem | None = None) -> None:
        """Show a term's definition and related lesson and exercise links."""
        if item is None:
            self._show_activities(self.activity_switch.current())
            return
        term = TERMS[item.text()]
        self.definition.setHtml(f"<h2>{item.text()}</h2><p>{term.definition}</p><p>{term.guide}</p>")
        self._example_index = 0
        self._update_example()
        self.demo.show()
        self.definition_area.verticalScrollBar().setValue(0)
        self._show_activities(self.activity_switch.current())

    def _show_activities(self, mode: int) -> None:
        """Display related exercise or lesson tiles for the selected term."""
        while self.activity_tiles.count():
            entry = self.activity_tiles.takeAt(0)
            widget = entry.widget() if entry is not None else None
            if widget is not None:
                widget.hide()
                widget.deleteLater()
        item = self.terms.currentItem()
        if item is None:
            # noinspection PyUnreachableCode
            return
        if mode == 0:
            keys = TERMS[item.text()].exercises
            for column, exercise in enumerate(cls for cls in REGISTRY if cls.__name__ in keys):
                card = ExerciseCard(exercise)
                card.clicked.connect(lambda _checked=False, key=exercise.__name__: self.exercise_requested.emit(key))
                self.activity_tiles.addWidget(card, 0, column)
        else:
            lesson = next(lesson for lesson in LESSONS if lesson.key == TERMS[item.text()].lesson)
            card = lesson_card(lesson)
            card.clicked.connect(lambda: self.lesson_requested.emit(lesson.key))
            self.activity_tiles.addWidget(card, 0, 0)

    def _next_example(self) -> None:
        """Cycle through the selected term's notation examples."""
        self._example_index += 1
        self._update_example()

    def _update_example(self) -> None:
        """Render the notation or keyboard diagram from the same pitches used for playback."""
        item = self.terms.currentItem()
        if item is None:
            return
        self._stop_preview()
        term = TERMS[item.text()]
        example = term.examples[self._example_index % len(term.examples)]
        notes = [Note.parse(name) for name in example.pitches.split()]
        self._example_midis = [note.midi for note in notes]
        self.example_circle.setVisible(term.circle)
        if term.circle:
            self.example_circle.select("outer", place=example.signature)
        self.example_keyboard.setVisible(term.keyboard)
        self.example_staff.setVisible(not term.keyboard)
        if term.keyboard:
            self.example_keyboard.show_keys(self._example_midis, span=(60, 72))
        else:
            self.example_staff.wedges = (
                [_STEP_LABELS[abs(right - left)] for left, right in pairwise(self._example_midis)] if term.label_steps else []
            )
            self.example_staff.show_notes([[note] for note in notes], clef=example.clef, key=example.signature)
        self.example_label.setText(example.caption)
        self.hear.setText("▶  Hear note" if len(notes) == 1 else "▶  Hear example")

    def _hear_example(self) -> None:
        """Audition the pitches in the displayed order."""
        if self.example_staff.isHidden():
            sounds.preview(sounds.instrument, midis=self._example_midis, step_ms=450)
            self._preview_played = True
        else:
            self.playback.play(self.example_staff.columns, force=True)

    def _stop_preview(self) -> None:
        """Silence the previous example when the learner changes the display."""
        self.playback.stop()
        if self._preview_played:
            sounds.stop_all()
            self._preview_played = False

    def hideEvent(self, event: QHideEvent) -> None:
        """
        End the example when leaving the glossary.

        Parameters
        ----------
        event : QHideEvent
            The notification that the glossary has been hidden.
        """
        self._stop_preview()
        super().hideEvent(event)
