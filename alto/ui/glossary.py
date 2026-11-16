"""A searchable glossary of the notation terms used in Alto."""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QKeySequence, QPalette, QShortcut
from PySide6.QtWidgets import (
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
from alto.ui.icons import SEARCH, svg_icon
from alto.ui.staff import StaffWidget
from alto.ui.widgets import SegmentedControl

TERMS: dict[str, tuple[str, tuple[str, str], tuple[str, str]]] = {
    "pitch": (
        (
            "Pitch is how high or low a sound is heard. For a steady musical tone it is closely related to frequency: "
            "a higher frequency generally means a higher pitch. A written note specifies a pitch through its letter, "
            "accidental and octave register."
        ),
        ("Note Identification", "NoteNames"),
        ("Keyboard Identification", "KeyboardNotes"),
    ),
    "octave": (
        (
            "An octave is the interval from a note to the next higher or lower note with the same letter name and "
            "accidental, such as C4 to C5. It spans twelve semitones. The higher tone has twice the frequency of the lower tone."
        ),
        ("Interval Identification", "IntervalNames"),
        ("Note Identification", "NoteNames"),
    ),
    "octave register": (
        (
            "An octave register identifies which octave a note belongs to. Alto uses scientific pitch notation: "
            "middle C is C4. The number changes at C, so B3 is followed by C4. Accidentals do not change the written "
            "octave number: C♭4 is still written in octave 4, though it sounds like B3."
        ),
        ("Note Identification", "NoteNames"),
        ("Keyboard Identification", "KeyboardNotes"),
    ),
    "staff": (
        (
            "A staff is a set of five horizontal lines and the four spaces between them on which notes are written. "
            "Moving from a line to the adjacent space advances one letter name. A clef establishes which pitches "
            "the lines and spaces represent."
        ),
        ("Note Identification", "NoteNames"),
        ("Note Construction", "NoteConstruction"),
    ),
    "ledger lines": (
        (
            "Ledger lines are short extra staff lines used for notes above or below the five-line staff. "
            "Lines and spaces continue in the same alternating pattern. For example, middle C is on the first "
            "ledger line below a treble staff and the first ledger line above a bass staff."
        ),
        ("Note Identification", "NoteNames"),
        ("Note Construction", "NoteConstruction"),
    ),
    "clef": (
        (
            "A clef is a symbol that assigns a reference pitch to a staff line, determining all the other pitches. "
            "The treble clef places G4 on the second line; the bass clef places F3 on the fourth line. "
            "A C clef marks middle C: the third line in alto clef and the fourth in tenor clef. Count lines from the bottom."
        ),
        ("Clef Basics", "ClefBasics"),
        ("Note Identification", "NoteNames"),
    ),
    "grand staff": (
        (
            "A grand staff joins a treble staff and a bass staff, usually with a brace, to show a wide range of pitches. "
            "Middle C lies on a ledger line between them. Piano music commonly uses the upper staff for the right hand "
            "and the lower staff for the left, though either hand can play on either staff."
        ),
        ("Note Identification", "NoteNames"),
        ("Note Construction", "NoteConstruction"),
    ),
}


DETAILS = {
    "pitch": "<p><b>Reading pitch.</b> The staff gives you a letter and register; the key signature and accidentals "
    "complete the pitch. Moving upward on the staff usually moves upward in sound, but an accidental can change "
    "the size of the step.</p><p><b>Hearing pitch.</b> Loudness and tone color are different qualities: a soft flute "
    "and a loud piano can play the same pitch. In standard tuning A4 is 440 Hz. Try the examples below and "
    "listen for the change in height, rather than volume.</p>",
    "octave": "<p><b>Same name, different height.</b> C4 and C5 are distinct pitches, yet sound closely related. "
    "This is why scales repeat their letter names after seven steps. Counting both endpoints gives eight letter "
    "positions: C D E F G A B C.</p><p><b>Reading the interval.</b> On a staff an octave moves from a line to a space, "
    "or a space to a line. The twelve-semitone definition describes a perfect octave; the letter spelling matters "
    "when naming intervals. Listen to the lower and upper C in the example.</p>",
    "octave register": "<p><b>Finding your bearings.</b> Think of each register as a C-to-B band: C4 through B4, "
    "then C5 through B5. Middle C is a useful landmark between the treble and bass staves. A4, the tuning A, "
    "belongs to the same band as middle C.</p><p><b>A common trap.</b> The register changes at C, not A. "
    "An accidental changes the sounding pitch without renaming the written register: B♯3 sounds like C4. "
    "Cycle through B3, C4 and B♯3 below to compare spelling and sound.</p>",
    "staff": "<p><b>A ladder of letters.</b> Number the lines from the bottom. In treble clef they read E G B D F; "
    "the spaces read F A C E. A neighboring line or space is the next letter, but it is not always the same "
    "number of semitones away.</p><p><b>What the staff does not tell you alone.</b> The clef fixes the pitch "
    "reference, the signature and accidentals adjust it, and note shapes indicate duration. Cycle through "
    "E4, F4 and G4 below to follow line–space–line.</p>",
    "ledger lines": "<p><b>The staff continues.</b> A note just above or below the staff may occupy a space "
    "without needing a ledger line. Add a short line only when reaching the next line position; further lines "
    "are spaced exactly like the five staff lines.</p><p><b>Reading strategy.</b> Find a familiar boundary note, "
    "then count alternating spaces and lines. In treble clef, D4 is just below the bottom line, C4 has one "
    "ledger line, and A3 has two. Cycle through those examples below.</p>",
    "clef": "<p><b>A reference, not a transposition.</b> Changing the clef changes the pitch assigned to a given "
    "staff position. To preserve the same written pitch when switching clefs, move the note to its new "
    "position.</p><p><b>Why several clefs?</b> They keep an instrument's usual range near the staff and reduce "
    "ledger lines. Alto and tenor use the same C-clef symbol on different lines. The example keeps middle C "
    "fixed while you cycle through treble, bass, alto and tenor.</p>",
    "grand staff": "<p><b>One pitch space.</b> The two staves are connected rather than independent: the pitch "
    "sequence continues across the gap. The printed distance between staves can change for readability; it "
    "does not represent extra musical steps.</p><p><b>Reading across the join.</b> Treble and bass clefs keep "
    "high and low notes readable. Middle C can be written from either staff, and hand assignment is a performance "
    "choice rather than a rule of the clefs. Compare C3, middle C and C5 below.</p>",
}

EXAMPLES = {
    "pitch": (("C4", "treble"), ("G4", "treble"), ("C5", "treble")),
    "octave": (("C4", "treble"), ("C5", "treble")),
    "octave register": (("B3", "treble"), ("C4", "treble"), ("B#3", "treble")),
    "staff": (("E4", "treble"), ("F4", "treble"), ("G4", "treble")),
    "ledger lines": (("D4", "treble"), ("C4", "treble"), ("A3", "treble")),
    "clef": (("C4", "treble"), ("C4", "bass"), ("C4", "alto"), ("C4", "tenor")),
    "grand staff": (("C3", "grand"), ("C4", "grand"), ("C5", "grand")),
}


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
        sidebar.setMaximumWidth(260)
        sidebar_layout = QVBoxLayout(sidebar)
        self.search = QLineEdit()
        self.search.setProperty("field", True)
        self.search.setPlaceholderText("Search terms…")
        self.search.setAccessibleName("Search glossary terms")
        self.search.setClearButtonEnabled(True)
        self.search.addAction(
            svg_icon(SEARCH, color=self.palette().color(QPalette.ColorRole.WindowText)),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        self.terms = QListWidget()
        self.terms.setObjectName("categories")
        self.terms.setSpacing(2)
        for term in sorted(TERMS):
            row = QListWidgetItem(term)
            row.setSizeHint(QSize(0, 40))
            self.terms.addItem(row)
        sidebar_layout.addWidget(self.search)
        sidebar_layout.addWidget(self.terms)
        layout.addWidget(sidebar)
        self.definition = QTextBrowser()
        self.definition.setOpenLinks(False)
        self.definition.setAccessibleName("Term definition and related activities")
        main = QVBoxLayout()
        main.addWidget(self.definition, 3)
        demo = QHBoxLayout()
        self.example_staff = StaffWidget(gap=7, margin=4, compact=True)
        demo.addWidget(self.example_staff, 1)
        demo_controls = QVBoxLayout()
        self.example_label = QLabel()
        demo_controls.addWidget(self.example_label)
        self.next_example = QPushButton("Next example →")
        self.next_example.clicked.connect(self._next_example)
        demo_controls.addWidget(self.next_example)
        hear = QPushButton("♪ Hear note")
        hear.clicked.connect(self._hear_example)
        demo_controls.addWidget(hear)
        demo.addLayout(demo_controls)
        self.demo = QWidget()
        self.demo.setLayout(demo)
        main.addWidget(self.demo)
        self.activity_switch = SegmentedControl(["Exercises", "Lessons"])
        self.activity_switch.chosen.connect(self._show_activities)
        main.addWidget(self.activity_switch, alignment=Qt.AlignmentFlag.AlignLeft)
        self.activity_body = QWidget()
        self.activity_tiles = QGridLayout(self.activity_body)
        self.activity_tiles.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll = QScrollArea()
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
            self.definition.setHtml("<h2>No matching terms</h2><p>Try a different search.</p>")
            self.demo.hide()

    def _show_term(self, item: QListWidgetItem | None, _previous: QListWidgetItem | None = None) -> None:
        """Show a term's definition and related lesson and exercise links."""
        if item is None:
            self._show_activities(self.activity_switch.current())
            return
        self.definition.setHtml(
            f"<h2>{item.text().capitalize()}</h2><p>{TERMS[item.text()][0]}</p>{DETAILS[item.text()]}",
        )
        self._example_index = 0
        self.demo.show()
        self._update_example()
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
            keys = {key for _title, key in TERMS[item.text()][1:]}
            for column, exercise in enumerate(cls for cls in REGISTRY if cls.__name__ in keys):
                card = ExerciseCard(exercise)
                card.clicked.connect(lambda _checked=False, key=exercise.__name__: self.exercise_requested.emit(key))
                self.activity_tiles.addWidget(card, 0, column)
        else:
            lesson = next(lesson for lesson in LESSONS if lesson.key == "clef-basics")
            card = lesson_card(lesson)
            card.clicked.connect(lambda: self.lesson_requested.emit(lesson.key))
            self.activity_tiles.addWidget(card, 0, 0)

    def _next_example(self) -> None:
        """Cycle through the selected term's notation examples."""
        self._example_index += 1
        self._update_example()

    def _update_example(self) -> None:
        """Draw the current example and identify its pitch and clef."""
        item = self.terms.currentItem()
        if item is None:
            # noinspection PyUnreachableCode
            return
        examples = EXAMPLES[item.text()]
        name, clef = examples[self._example_index % len(examples)]
        note = Note.parse(name)
        self.example_staff.show_notes([[note]], clef=clef)
        self.example_label.setText(f"{note} · {clef.capitalize()}")

    def _hear_example(self) -> None:
        """Play the current notation example with the selected instrument."""
        sounds.preview(sounds.instrument, midis=[self.example_staff.columns[0][0].midi])
