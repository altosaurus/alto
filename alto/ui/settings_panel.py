"""
The settings panels of the built-in exercises, and `settings_panel_for`,
which picks the panel for any exercise.

Each exercise with settings has a panel: a menu of rows (Clefs, Range,
Key signatures ...) that each lead to a page. Edits
are live: they change the shared settings object, are saved, and a
`changed` signal tells the exercise to ask a new
question. The widgets the panels are built from are in
`alto.ui.settings_menu`, plugin exercises' panels are in
`alto.ui.pack_settings_panel`, and loading and saving the settings is in
`alto.ui.exercise_settings`.

Examples
--------
>>> panel = settings_panel_for(ClefBasics())
>>> type(panel).__name__
'ClefBasicsSettingsPanel'
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSignalBlocker, QSize, Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from alto import settings
from alto.circle_schemes import (
    DEFAULT_SCHEME,
    CustomRecord,
)
from alto.exercises.base import (
    ChoiceExercise,
    Exercise,
)
from alto.exercises.library import (
    ArpeggioNames,
    BeatConstruction,
    BeatIdentification,
    CircleOfFifths,
    ClefBasics,
    IntervalConstruction,
    IntervalNames,
    KeyboardIntervals,
    KeyboardNotes,
    KeySignatureConstruction,
    KeySignatures,
    NotationIdentification,
    NoteConstruction,
    NoteNames,
    OrderOfKeys,
    RythmicEquations,
    ScaleConstruction,
    ScaleIdentification,
)
from alto.exercises.packs import PackExercise
from alto.learning import Learner
from alto.learning.calendar import CALENDAR_SCHEDULERS
from alto.notation_terms import CATALOG
from alto.settings import (
    CLEFS,
    NAMINGS,
    NoteNameSettings,
    key_name,
)
from alto.theory.pitch import ACCIDENTAL_SYMBOLS
from alto.theory.scales import INVERSION_NAMES
from alto.ui.circle_colors import (
    SchemeEditor,
    SchemePage,
)
from alto.ui.degree_text import degree_tooltip
from alto.ui.dropdown import FieldComboBox
from alto.ui.exercise_settings import (
    save_arpeggio,
    save_circle,
    save_clef_basics,
    save_construction,
    save_key_settings,
    save_keyboard,
    save_keyboard_intervals,
    save_note_names,
    saved_notation_terms,
)
from alto.ui.interval_range import IntervalRangeSlider
from alto.ui.keyboard import KeyboardSpan
from alto.ui.pack_settings_panel import (
    PackKeyboardSettingsPanel,
    PackSettingsPanel,
)
from alto.ui.pictures import (
    RHYTHM_SYMBOL_NAMES,
    ClefPictures,
    KeySignaturePicture,
    NamePicture,
    RangePictures,
    ValuePictures,
)
from alto.ui.practice_limits import DailyLimitsEditor
from alto.ui.settings_menu import (
    ROW_PICTURE_WIDTH,
    ChoiceChecklist,
    ClefsPanel,
    ExerciseSettingsPanel,
    KeyboardRangePanel,
    KeyChecklist,
    KeyDiagram,
    KeySignaturePage,
    MenuRow,
    NoteAnswerSettingsPanel,
    ScaleKeyPicker,
    SlideStack,
    StaffRangePanel,
    ToggleRow,
    arrow_button,
    buttons_page,
    clef_choice_page,
    direction_choices,
    guard_last,
    label_with_picture,
    scrolling,
    show_keys,
    subpage,
)
from alto.ui.store import (
    save_bool,
    store,
    text_value,
)
from alto.ui.zoom import (
    css,
    px,
)


def _note_naming_page(
    cfg: NoteNameSettings | settings.KeyboardSettings,
    *,
    preview: NamePicture,
    changed: Callable[[], None],
    back: Callable[[], None],
) -> tuple[dict[str, QRadioButton], QWidget]:
    """
    Build the answer type or keyboard note naming submenu.

    Parameters
    ----------
    cfg : NoteNameSettings or KeyboardSettings
        Exercise whose naming preference is edited.
    preview : NamePicture
        Menu row illustration to update.
    changed : callable
        Saves the exercise settings and refreshes its question.
    back : callable
        Opens the exercise settings menu.

    Returns
    -------
    tuple
        Naming radio buttons and the submenu containing them.

    Examples
    --------
    Keyboard Note Identification can use letters while the staff uses
    scale degrees.
    """
    body = QWidget()
    layout = QVBoxLayout(body)
    layout.setContentsMargins(0, 0, 0, 0)
    degrees = QGroupBox("Scale degrees")
    degree_layout = QVBoxLayout(degrees)
    group = QButtonGroup(body)
    radios = {}

    def select(checked: bool, *, naming: str) -> None:
        """
        Apply the selected naming to this exercise.

        Parameters
        ----------
        checked : bool
            Whether this radio button is now checked.
        naming : str
            Naming system represented by the button.

        Examples
        --------
        Choosing Caret updates the preview to show numbered degrees.
        """
        if checked:
            if isinstance(cfg, NoteNameSettings):
                cfg.scale_answer = naming == "scale"
            if naming != "scale":
                cfg.naming = naming
                preview.set_naming(naming)
            changed()

    selected = (
        "scale"
        if isinstance(cfg, NoteNameSettings) and cfg.scale_answer
        else cfg.naming
    )
    for naming, label in NAMINGS.items():
        radio = radios[naming] = QRadioButton()
        label_with_picture(
            radio,
            picture=NamePicture(naming, scale=1.6),
            name=label,
        )
        radio.setText(label.split(" (")[0])
        radio.setToolTip(degree_tooltip(label))
        group.addButton(radio)
        radio.setChecked(naming == selected)
        radio.toggled.connect(
            lambda checked, n=naming: select(checked, naming=n),
        )
        target = degree_layout if naming in settings.DEGREE_NAMINGS else layout
        target.addWidget(radio)
    if isinstance(cfg, NoteNameSettings):
        scale = radios["scale"] = QRadioButton("Scale")
        label_with_picture(scale, picture=KeySignaturePicture(2), name="Scale")
        scale.setToolTip(
            "Choose the key from the note and its scale degree",
        )
        group.addButton(scale)
        scale.setChecked(selected == "scale")
        scale.toggled.connect(lambda checked: select(checked, naming="scale"))
        layout.addWidget(scale)

    layout.addWidget(degrees)
    layout.addStretch()
    return radios, subpage(
        "Answer Type" if isinstance(cfg, NoteNameSettings) else "Note names",
        body=scrolling(body),
        back=back,
        fill=True,
    )


class NoteNameSettingsPanel(NoteAnswerSettingsPanel):
    """
    The settings of the note identification exercise: a menu leading to
    a page for each group of settings.

    The menu opens pages for Clefs, Range, Staff Key, Scale Key,
    Note values and Answer Type. Accidentals and Octave are switches.
    Each edit saves the settings and emits `changed`.

    Attributes
    ----------
    cfg : NoteNameSettings
        The settings being edited.
    stack : SlideStack
        The menu and its pages.
    boxes : dict of str to QCheckBox
        The clef checkboxes.
    key_boxes : dict of int to QCheckBox
        The key signature checkboxes.
    value_boxes : dict of str to QCheckBox
        The note value checkboxes.
    naming_radios : dict of str to QRadioButton
        The letters and solfège choices, plus caret and function
        notation in the Scale degrees group.
    octave_row : ToggleRow
        Whether the answer must include the written octave.
    range_editors : dict of str to RangeEditor
        The range editor of each clef in use, built when the Range page
        opens.

    Examples
    --------
    >>> panel = NoteNameSettingsPanel(
    ...     NoteNameSettings()
    ... )
    >>> panel.cfg.active_clefs()
    ['treble', 'bass']
    """

    def __init__(
        self,
        cfg: NoteNameSettings,
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the panel for a set of settings.

        Parameters
        ----------
        cfg : NoteNameSettings
            The settings to edit.
        parent : QWidget or None, default None
            The widget that owns the panel. Keyword-only.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(
        ...     NoteNameSettings()
        ... )
        >>> panel.stack.count()  # the menu and six pages
        7
        """
        super().__init__(parent)
        self.cfg: NoteNameSettings = cfg
        menu, mlay = self._build_menu()
        self.clefs_row, self.range_row = (
            MenuRow("Clefs"),
            MenuRow("Range", tall=True),
        )
        self.keys_row, self.values_row, self.names_row = (
            MenuRow("Scale Key"),
            MenuRow("Note values"),
            MenuRow("Answer Type"),
        )
        self.staff_key_row = MenuRow("Staff Key")
        self.staff_key_row.setToolTip(
            "Signatures drawn at the start of the staff",
        )
        self.keys_row.setToolTip(
            "Keys used to choose notes and identify scale degrees",
        )
        self.staff_keys_diagram = KeyDiagram()
        self.staff_key_row.attach(self.staff_keys_diagram)
        self.clef_pictures = ClefPictures()
        self.clefs_row.attach(self.clef_pictures)
        self.range_pictures = RangePictures(max_width=px(ROW_PICTURE_WIDTH))
        self.range_row.attach(self.range_pictures)
        self.value_pictures = ValuePictures()
        self.values_row.attach(self.value_pictures)
        self.name_picture = NamePicture()
        self.names_row.attach(self.name_picture)
        for index, row in enumerate(
            (
                self.clefs_row,
                self.range_row,
                self.staff_key_row,
                self.keys_row,
                self.values_row,
                self.names_row,
            ),
            1,
        ):
            row.clicked.connect(lambda _=False, i=index: self._go(i))
            mlay.addWidget(row)
        self.accidentals_row = ToggleRow("Accidentals")
        self.accidentals_row.setToolTip(
            "Also ask notes with sharps, flats and naturals",
        )
        self.accidentals_row.setOn(cfg.accidentals)
        self.accidentals_row.switched.connect(self._accidentals_toggled)
        mlay.addWidget(self.accidentals_row)
        self.octave_row = ToggleRow("Octave")
        self.octave_row.setToolTip("Also ask which octave the note is in")
        self.octave_row.setOn(cfg.require_octave)
        self.octave_row.switched.connect(self._octave_toggled)
        mlay.addWidget(self.octave_row)
        mlay.addStretch()

        # layer 2: clefs
        self.boxes, clefs_page = clef_choice_page(
            settings.RANGE_KEYS,
            selected=cfg.clefs,
            edited=self._clefs_edited,
            back=lambda: self._go(0),
        )

        # layer 2: range
        range_page = self._range_page()

        # layer 2: key signatures, each drawn as it would be written
        # (flats on the left, sharps on the right)
        self.staff_keys = KeyChecklist(cfg.staff_keys or {0})
        self.staff_keys.changed.connect(self._staff_keys_edited)
        staff_page = subpage(
            "Staff Key",
            body=scrolling(self.staff_keys),
            back=lambda: self._go(0),
            fill=True,
        )
        major, minor = cfg.key_selections()
        self.scale_keys = ScaleKeyPicker(major_keys=major, minor_keys=minor)
        self.scale_keys.major_keys.changed.connect(self._keys_edited)
        self.scale_keys.minor_keys.changed.connect(self._keys_edited)
        self.key_boxes = self.scale_keys.major_keys.boxes
        keys_page = subpage(
            "Scale Key",
            body=scrolling(self.scale_keys),
            back=lambda: self._go(0),
            fill=True,
        )

        values_page = self._values_page("Note values")

        self.naming_radios, names_page = _note_naming_page(
            cfg,
            preview=self.name_picture,
            changed=self._answer_type_changed,
            back=lambda: self._go(0),
        )

        for page in (
            menu,
            clefs_page,
            range_page,
            staff_page,
            keys_page,
            values_page,
            names_page,
        ):
            self.stack.addWidget(page)
        self._refresh_summaries()

    def _answer_type_changed(self) -> None:
        """
        Show the controls and key selection for the new answer type.

        Examples
        --------
        Scale answers use their own key selection.
        """
        major, minor = self.cfg.key_selections()
        for checklist, selected in (
            (self.scale_keys.major_keys, major),
            (self.scale_keys.minor_keys, minor),
        ):
            for key, box in checklist.boxes.items():
                with QSignalBlocker(box):
                    box.setChecked(key in selected)
        self.scale_keys.setCurrentIndex(0 if major else 1)
        self._refresh_summaries()
        self._save_and_emit()

    def _refresh_summaries(self) -> None:
        """
        Update the menu's summaries (the clef, range, key, value and
        naming pictures) from the settings.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(
        ...     NoteNameSettings(
        ...         clefs={"bass", "tenor"}
        ...     )
        ... )
        >>> panel._refresh_summaries()
        >>> panel.clef_pictures.toolTip()
        'Bass, Tenor'
        """
        super()._refresh_summaries()
        show_keys(
            self.staff_key_row,
            diagram=self.staff_keys_diagram,
            enabled=True,
            keys=self.cfg.staff_keys,
        )
        self.scale_keys.update_summary(self.keys_row)
        self.name_picture.set_naming(self.cfg.naming)
        self.name_picture.setVisible(not self.cfg.scale_answer)
        self.names_row.value.setText("Scale" if self.cfg.scale_answer else "")
        self.accidentals_row.setVisible(not self.cfg.scale_answer)
        self.octave_row.setVisible(not self.cfg.scale_answer)

    # key signatures / note values / note names pages

    def _persist(self) -> None:
        """
        Save the note identification settings.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(
        ...     settings.note_names
        ... )
        >>> panel._persist()
        >>> store().contains("noteNames/clefs")
        True
        """
        save_note_names()

    def _staff_keys_edited(self) -> None:
        """
        Save the signatures that can appear beside the clef.

        Examples
        --------
        Checking two sharps adds that signature to the staff selection.
        """
        self.cfg.staff_keys = self.staff_keys.selected()
        self._save_and_emit()

    def _keys_edited(self) -> None:
        """
        Take the checked key signatures into the settings, save them and
        say so.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(
        ...     NoteNameSettings()
        ... )
        >>> panel.key_boxes[2].setChecked(True)
        >>> 2 in panel.cfg.key_signatures
        True
        """
        major = self.scale_keys.major_keys.selected()
        minor = self.scale_keys.minor_keys.selected()
        if self.cfg.scale_answer:
            self.cfg.scale_keys, self.cfg.scale_minor_keys = major, minor
        else:
            self.cfg.key_signatures, self.cfg.minor_keys = major, minor
        self.scale_keys.update_summary(self.keys_row)
        self._save_and_emit()


class KeyboardSettingsPanel(KeyboardRangePanel):
    """
    The settings of the keyboard exercise: a menu with a page for the
    range of keys.

    The menu includes Range, Black keys, Octave number, Key signatures
    and Note names.
    Edits are live: each changes the settings, saves them
    and emits `changed`.

    Attributes
    ----------
    cfg : KeyboardSettings
        The settings being edited.
    stack : SlideStack
        The menu and its pages.
    span : KeyboardSpan
        The miniature piano on the Range page, which can be dragged to
        choose the keys.
    low_label, high_label : QLabel
        The names of the lowest and highest key asked.
    key_page : KeySignaturePage
        The key signature sub-page.

    Examples
    --------
    >>> panel = KeyboardSettingsPanel(
    ...     settings.KeyboardSettings()
    ... )
    >>> (
    ...     panel.low_label.text(),
    ...     panel.high_label.text(),
    ... )
    ('C3', 'C5')
    """

    def __init__(
        self,
        cfg: settings.KeyboardSettings,
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the panel for a set of settings.

        Parameters
        ----------
        cfg : KeyboardSettings
            The settings to edit.
        parent : QWidget or None, default None
            The widget that owns the panel. Keyword-only.

        Examples
        --------
        >>> KeyboardSettingsPanel(
        ...     settings.KeyboardSettings()
        ... ).stack.count()  # the menu, range, keys and note names
        4
        """
        super().__init__(parent)
        self.cfg = cfg
        menu, mlay = self._build_menu()
        self.range_row = MenuRow("Range", tall=True)
        self.range_row.clicked.connect(lambda: self._go(1))
        self.range_keyboard = KeyboardSpan(
            compact=True,
            size=(px(ROW_PICTURE_WIDTH), px(36)),
        )  # the asked span, lit on a miniature piano
        self.range_row.attach(self.range_keyboard)
        self.black_keys_row = ToggleRow("Black keys")
        self.black_keys_row.setToolTip(
            "Also ask the black keys, answered by either of their names",
        )
        self.black_keys_row.setOn(cfg.black_keys)
        self.black_keys_row.switched.connect(self._black_keys_toggled)
        self.octave_row = ToggleRow("Octave number")
        self.octave_row.setToolTip(
            "Answer with the octave as well, for example C4",
        )
        self.octave_row.setOn(cfg.require_octave)
        self.octave_row.switched.connect(self._octave_toggled)
        self.keys_row = MenuRow(
            "Key signatures",
        )  # opens a page: use them or not, and which keys
        self.keys_row.setToolTip(
            (
                "Show a key signature above the keyboard and require the "
                "name that fits it"
            ),
        )
        self.keys_row.clicked.connect(lambda: self._go(2))
        self.keys_diagram = KeyDiagram()
        self.keys_row.attach(self.keys_diagram)
        self.names_row = MenuRow("Note names")
        self.name_picture = NamePicture(cfg.naming)
        self.names_row.attach(self.name_picture)
        self.names_row.clicked.connect(lambda: self._go(3))
        for row in (
            self.range_row,
            self.black_keys_row,
            self.octave_row,
            self.keys_row,
            self.names_row,
        ):
            mlay.addWidget(row)
        mlay.addStretch()

        # layer 2: range
        self.span = KeyboardSpan()
        body = self._range_body(
            self.span,
            changed=self._set_range,
            single_note=True,
        )
        range_page = subpage("Range", body=body, back=lambda: self._go(0))

        # layer 2: key signatures
        self.key_page = KeySignaturePage(cfg.key_signature, selected=cfg.keys)
        self.key_page.changed.connect(self._keys_edited)
        keys_page = subpage(
            "Key signatures",
            body=self.key_page,
            back=lambda: self._go(0),
        )

        self.naming_radios, names_page = _note_naming_page(
            cfg,
            preview=self.name_picture,
            changed=self._save_and_emit,
            back=lambda: self._go(0),
        )

        self.stack.addWidget(menu)
        self.stack.addWidget(range_page)
        self.stack.addWidget(keys_page)
        self.stack.addWidget(names_page)
        self._refresh_range()
        self._show_keys()

    def _refresh_range(self) -> None:
        """
        Show the range everywhere it appears and enable only the arrows
        that can still move.

        Examples
        --------
        >>> cfg_ = settings.KeyboardSettings()
        >>> panel = KeyboardSettingsPanel(cfg_)
        >>> cfg_.low = 50
        >>> panel._refresh_range()
        >>> panel.low_label.text()
        'D3'
        """
        cfg = self.cfg
        self.low_label.setText(key_name(cfg.low))
        self.high_label.setText(key_name(cfg.high))
        self.span.set_span(cfg.low, hi=cfg.high)
        first, last = settings.KEYBOARD_FULL
        self.arrows["low"][0].setEnabled(cfg.low > first)
        self.arrows["low"][1].setEnabled(
            cfg.low < cfg.high,
        )  # the lowest key can't pass the highest
        self.arrows["high"][0].setEnabled(cfg.high > cfg.low)
        self.arrows["high"][1].setEnabled(cfg.high < last)
        self.range_keyboard.set_span(cfg.low, hi=cfg.high)
        self.range_keyboard.setToolTip(
            f"{key_name(cfg.low)} to {key_name(cfg.high)}",
        )

    def _step(
        self,
        which: str,
        *,
        delta: int,
    ) -> None:
        """
        Move one end of the range by some keys, keeping the lowest below
        the highest and both on the piano.

        Parameters
        ----------
        which : str
            "low" or "high".
        delta : int
            How many keys to move; positive is higher. Keyword-only.

        Examples
        --------
        >>> cfg = settings.KeyboardSettings()
        >>> panel = KeyboardSettingsPanel(cfg)
        >>> panel._step("low", delta=2)
        >>> cfg.low
        50
        >>> panel._step(
        ...     "high", delta=-100
        ... )  # the highest key cannot pass the lowest
        >>> cfg.high
        50
        """
        low, high = self.cfg.low, self.cfg.high
        first, last = settings.KEYBOARD_FULL
        if which == "low":
            low = min(max(low + delta, first), high)
        else:
            high = max(min(high + delta, last), low)
        self._set_range(low, high)

    def _set_range(  # noqa: PLR0917  (a Qt slot: the signal passes positional arguments)
        self,
        low: int,
        high: int,
    ) -> None:
        """
        Take a new range into the settings, show it, save it and say so.

        Nothing happens if the range has not changed.

        Parameters
        ----------
        low : int
            The lowest key asked, as a MIDI number.
        high : int
            The highest key asked.

        Examples
        --------
        >>> cfg = settings.KeyboardSettings()
        >>> panel = KeyboardSettingsPanel(cfg)
        >>> panel._set_range(60, 72)
        >>> (cfg.low, cfg.high), panel.low_label.text()
        ((60, 72), 'C4')
        """
        if (low, high) == (self.cfg.low, self.cfg.high):
            return
        self.cfg.low, self.cfg.high = low, high
        self._refresh_range()
        self._save_and_emit()

    def _black_keys_toggled(self, on: bool) -> None:
        """
        Take the Black keys switch into the settings, save it and say
        so.

        Parameters
        ----------
        on : bool
            Whether the black keys are asked.

        Examples
        --------
        >>> cfg = settings.KeyboardSettings()
        >>> KeyboardSettingsPanel(
        ...     cfg
        ... )._black_keys_toggled(False)
        >>> cfg.black_keys
        False
        """
        self.cfg.black_keys = on
        self._save_and_emit()

    def _octave_toggled(self, on: bool) -> None:
        """
        Take the Octave number switch into the settings, save it and say
        so.

        Parameters
        ----------
        on : bool
            Whether the answer must include the octave.

        Examples
        --------
        >>> cfg = settings.KeyboardSettings()
        >>> KeyboardSettingsPanel(cfg)._octave_toggled(
        ...     True
        ... )
        >>> cfg.require_octave
        True
        """
        self.cfg.require_octave = on
        self._save_and_emit()

    def _show_keys(self) -> None:
        """
        Update the menu's key signature summary.

        Examples
        --------
        >>> panel = KeyboardSettingsPanel(
        ...     settings.KeyboardSettings()
        ... )
        >>> panel._show_keys()
        >>> panel.keys_row.value.text()  # key signatures are off
        'Off'
        """
        show_keys(
            self.keys_row,
            diagram=self.keys_diagram,
            enabled=self.cfg.key_signature,
            keys=set(self.cfg.active_keys()),
        )

    def _keys_edited(self) -> None:
        """
        Take the key signature page into the settings, save it and say
        so.

        Examples
        --------
        >>> cfg = settings.KeyboardSettings()
        >>> panel = KeyboardSettingsPanel(cfg)
        >>> panel.key_page.switch_row.setOn(True)
        >>> panel._keys_edited()
        >>> cfg.key_signature
        True
        """
        self.cfg.key_signature = self.key_page.enabled()
        self.cfg.keys = self.key_page.selected()
        self._show_keys()
        self._save_and_emit()

    def _persist(self) -> None:
        """
        Save the keyboard settings.

        Examples
        --------
        >>> panel = KeyboardSettingsPanel(
        ...     settings.keyboard
        ... )
        >>> panel._persist()
        >>> store().contains("keyboard/keys")
        True
        >>> store().remove("keyboard")
        """
        save_keyboard()


class NoteConstructionSettingsPanel(ClefsPanel):
    """
    The settings of the note construction exercise: a menu with a page
    for the staff and one for the keys.

    The menu has Clefs, Staff Key, Question Type, and Octave. Edits are
    live: each changes the settings, saves them and
    emits `changed`.

    Attributes
    ----------
    cfg : ConstructionSettings
        The settings being edited.
    stack : SlideStack
        The menu and its pages.
    boxes : dict of str to QCheckBox
        The clef checkboxes, including the grand staff.
    key_tabs : QTabWidget
        The key signature sub-page.

    Examples
    --------
    >>> panel = NoteConstructionSettingsPanel(
    ...     settings.ConstructionSettings()
    ... )
    >>> sorted(panel.boxes)[:3]
    ['alto', 'baritone', 'bass']
    """

    cfg: settings.ConstructionSettings

    def __init__(
        self,
        cfg: settings.ConstructionSettings,
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the panel for a set of settings.

        Parameters
        ----------
        cfg : ConstructionSettings
            The settings to edit.
        parent : QWidget or None, default None
            The widget that owns the panel. Keyword-only.

        Examples
        --------
        >>> NoteConstructionSettingsPanel(
        ...     settings.ConstructionSettings()
        ... ).stack.count()
        4
        """
        super().__init__(parent)
        self.cfg = cfg
        menu, mlay = self._build_menu()
        self.clefs_row = MenuRow("Clefs")
        self.clefs_row.clicked.connect(lambda: self._go(1))
        self.clef_pictures = ClefPictures()
        self.clefs_row.attach(self.clef_pictures)
        self.staff_key_row = MenuRow("Staff Key")
        self.staff_key_row.clicked.connect(lambda: self._go(3))
        self.staff_keys_diagram = KeyDiagram()
        self.staff_key_row.attach(self.staff_keys_diagram)
        self.keys_row = MenuRow("Question Type")
        self.keys_row.setToolTip("Choose note name or scale key questions")
        self.keys_row.clicked.connect(lambda: self._go(2))
        self.octave_row = ToggleRow("Octave")
        self.octave_row.setToolTip("Show and require a specific octave")
        self.octave_row.setOn(cfg.octave)
        self.octave_row.switched.connect(self._octave_toggled)
        for row in (
            self.clefs_row,
            self.staff_key_row,
            self.keys_row,
            self.octave_row,
        ):
            mlay.addWidget(row)
        mlay.addStretch()

        # layer 2: clefs
        self.boxes, clefs_page = clef_choice_page(
            settings.RANGE_KEYS,
            selected=cfg.clefs,
            edited=self._clefs_edited,
            back=lambda: self._go(0),
        )

        # layer 2: key signatures
        if not cfg.key_signature:
            cfg.key_signature = True
            cfg.keys = {0}
            cfg.minor_keys = {0}
        self.key_tabs = ScaleKeyPicker(
            major_keys=cfg.keys if cfg.major else set(),
            minor_keys=(cfg.minor_keys or cfg.keys) if cfg.minor else set(),
        )
        self.major_keys = self.key_tabs.major_keys
        self.minor_keys = self.key_tabs.minor_keys
        self.minor_keys.changed.connect(self._keys_edited)
        self.major_keys.changed.connect(self._keys_edited)
        question_body = QWidget()
        question_layout = QVBoxLayout(question_body)
        question_layout.setContentsMargins(0, 0, 0, 0)
        notes_only = QRadioButton("Notes Only")
        self.scale_key_choice = QRadioButton("Scale and Degree")
        question_layout.addWidget(notes_only)
        question_layout.addWidget(self.scale_key_choice)
        notes_only.setChecked(cfg.question_type == "notes")
        self.scale_key_choice.setChecked(cfg.question_type == "scale")
        scale_options = QWidget()
        scale_layout = QVBoxLayout(scale_options)
        scale_layout.setContentsMargins(0, 0, 0, 0)
        scale_layout.addWidget(QLabel("Keys"))
        scale_layout.addWidget(self.key_tabs)
        self.degree_choices = ChoiceChecklist(
            [("Degrees", [(degree, f"{degree}̂") for degree in range(1, 8)])],
            selected=cfg.degrees,
        )
        for degree, box in self.degree_choices.boxes.items():
            box.setAccessibleName(f"Degree {degree}")
        self.degree_choices.changed.connect(self._degrees_edited)
        scale_layout.addWidget(self.degree_choices)
        scale_layout.addStretch()
        self.scale_key_scroll = scrolling(scale_options)
        question_layout.addWidget(self.scale_key_scroll, 1)
        self.scale_key_scroll.setVisible(self.scale_key_choice.isChecked())
        question_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scale_key_choice.toggled.connect(self._question_type_changed)
        keys_page = subpage(
            "Question Type",
            body=question_body,
            back=lambda: self._go(0),
            fill=True,
        )

        self.staff_keys = KeyChecklist(cfg.staff_keys or {0})
        self.staff_keys.changed.connect(self._staff_keys_edited)
        staff_page = subpage(
            "Staff Key",
            body=scrolling(self.staff_keys),
            back=lambda: self._go(0),
            fill=True,
        )

        for page in (menu, clefs_page, keys_page, staff_page):
            self.stack.addWidget(page)
        self._refresh_summaries()

    def _refresh_summaries(self) -> None:
        """
        Update the menu's clef and key signature summaries from the
        settings.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(
        ...     settings.ConstructionSettings(
        ...         clefs={"bass"}
        ...     )
        ... )
        >>> panel._refresh_summaries()
        >>> panel.clef_pictures.toolTip()
        'Bass'
        """
        self.clef_pictures.set_clefs(self.cfg.active_clefs())
        self._show_keys()

    def _persist(self) -> None:
        """
        Save the note construction settings.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(
        ...     settings.ConstructionSettings(
        ...         clefs={"alto"}
        ...     )
        ... )
        >>> panel._persist()
        >>> str(store().value("construction/clefs"))
        'alto'
        >>> store().remove("construction")
        """
        save_construction(self.cfg)

    def _degrees_edited(self) -> None:
        """
        Save the scale degrees selected for questions.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(
        ...     settings.ConstructionSettings()
        ... )
        >>> panel._degrees_edited()
        """
        self.cfg.degrees = self.degree_choices.selected()
        self._save_and_emit()

    def _question_type_changed(self, scale_key: bool) -> None:
        """
        Save the question type and show the scale key lists when
        relevant.

        Parameters
        ----------
        scale_key : bool
            Whether to ask for a scale degree.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(
        ...     settings.ConstructionSettings()
        ... )
        >>> panel._question_type_changed(False)
        >>> panel.cfg.question_type
        'notes'
        """
        self.cfg.question_type = "scale" if scale_key else "notes"
        self.scale_key_scroll.setVisible(scale_key)
        self._show_keys()
        self._save_and_emit()

    def _octave_toggled(self, on: bool) -> None:
        """
        Save whether questions require a specific octave.

        Parameters
        ----------
        on : bool
            Whether to require the specified octave.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(
        ...     settings.ConstructionSettings()
        ... )
        >>> panel._octave_toggled(False)
        >>> panel.cfg.octave
        False
        """
        self.cfg.octave = on
        self._save_and_emit()

    def _staff_keys_edited(self) -> None:
        """
        Save the signatures selected for the staff.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(
        ...     settings.ConstructionSettings()
        ... )
        >>> panel._staff_keys_edited()
        """
        self.cfg.staff_keys = self.staff_keys.selected()
        self.staff_keys_diagram.set_keys(self.cfg.staff_keys)
        self._save_and_emit()

    def _show_keys(self) -> None:
        """
        Update the menu's key signature summary.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(
        ...     settings.ConstructionSettings()
        ... )
        >>> panel._show_keys()
        >>> panel.keys_row.value.text()
        'Scale and Degree'
        """
        self.staff_keys_diagram.set_keys(self.cfg.staff_keys or {0})
        guard_last(
            [*self.major_keys.boxes.values(), *self.minor_keys.boxes.values()],
        )
        self.keys_row.value.setText(
            "Notes Only"
            if self.cfg.question_type == "notes"
            else "Scale and Degree",
        )

    def _keys_edited(self) -> None:
        """
        Take the key signature page into the settings, save it and say
        so.

        Examples
        --------
        >>> cfg = settings.ConstructionSettings()
        >>> panel = NoteConstructionSettingsPanel(cfg)
        >>> panel.major_keys.boxes[1].setChecked(True)
        >>> cfg.key_signature
        True
        """
        major_keys = self.major_keys.selected()
        minor_keys = self.minor_keys.selected()
        self.cfg.major = bool(major_keys)
        self.cfg.minor = bool(minor_keys)
        if major_keys:
            self.cfg.keys = major_keys
        if minor_keys:
            self.cfg.minor_keys = minor_keys
        self._show_keys()
        self._save_and_emit()


class IntervalSettingsPanel(StaffRangePanel):
    """
    Choose the notation and answer format for written intervals.

    Examples
    --------
    >>> IntervalSettingsPanel(
    ...     settings.IntervalSettings()
    ... ).stack.count()
    10
    """

    def __init__(
        self,
        cfg: settings.IntervalSettings,
        *,
        prefix: str = "intervals",
    ) -> None:
        """
        Build the interval settings menu with direction choices under
        Melodic.

        Parameters
        ----------
        cfg : IntervalSettings
            The interval exercise settings.
        prefix : str
            Settings-store group for identification or construction.

        Examples
        --------
        >>> IntervalSettingsPanel(
        ...     settings.IntervalSettings()
        ... ).quality_row.value.text()
        'Interval and Quality'
        """
        super().__init__()
        self.prefix = prefix
        self.cfg: settings.IntervalSettings = cfg
        menu, layout = self._build_menu()
        self.stack.addWidget(menu)
        self.clefs_row = MenuRow("Clefs")
        self.clef_pictures = ClefPictures()
        self.clefs_row.attach(self.clef_pictures)
        self.range_row = MenuRow("Range", tall=True)
        self.range_pictures = RangePictures(max_width=px(ROW_PICTURE_WIDTH))
        self.range_row.attach(self.range_pictures)
        self.staff_key_row = MenuRow("Staff Key")
        self.key_diagram = KeyDiagram()
        self.staff_key_row.attach(self.key_diagram)
        self.values_row = MenuRow("Note Value")
        self.value_pictures = ValuePictures()
        self.values_row.attach(self.value_pictures)
        self.display_row = MenuRow("Display Mode")
        self.quality_row = MenuRow("Quality")
        self.accidentals_row = MenuRow("Accidentals")
        self.intervals_row = MenuRow("Intervals")
        self.buttons_row = MenuRow("Buttons")
        for index, row in enumerate(
            (
                self.clefs_row,
                self.range_row,
                self.staff_key_row,
                self.display_row,
                self.quality_row,
                self.intervals_row,
                self.accidentals_row,
                self.values_row,
                self.buttons_row,
            ),
            1,
        ):
            row.clicked.connect(
                lambda _checked=False, page=index: self._go(page),
            )
            layout.addWidget(row)
        self.buttons_row.setVisible(prefix == "intervals")
        if prefix == "intervals":
            self.inversions_row = ToggleRow("Inversions")
            self.inversions_row.setToolTip(
                "Identify the inversion of the interval shown on the staff",
            )
            self.inversions_row.setOn(cfg.inversions)
            self.inversions_row.switched.connect(self._save_and_emit)
            layout.insertWidget(
                layout.indexOf(self.quality_row) + 1,
                self.inversions_row,
            )
            self.consonance_row = ToggleRow("Consonance")
            self.consonance_row.setToolTip(
                "Identify whether the interval is consonant or dissonant",
            )
            self.consonance_row.setOn(cfg.consonance)
            self.consonance_row.switched.connect(self._save_and_emit)
            layout.insertWidget(
                layout.indexOf(self.inversions_row) + 1,
                self.consonance_row,
            )
        layout.addStretch()

        self.boxes, clefs = clef_choice_page(
            settings.RANGE_KEYS,
            selected=cfg.clefs,
            edited=self._save_and_emit,
            back=lambda: self._go(0),
        )
        self.stack.addWidget(clefs)
        self.stack.addWidget(self._range_page())
        self.staff_keys = KeyChecklist(cfg.staff_keys)
        self.display = ChoiceChecklist(
            [("", [(style, style) for style in settings.INTERVAL_DISPLAYS])],
            selected=cfg.displays,
        )
        self.direction_choices = ChoiceChecklist(
            [
                (
                    "",
                    [
                        (direction, direction.title())
                        for direction in settings.MELODIC_DIRECTIONS
                    ],
                ),
            ],
            selected=cfg.directions,
        )
        self.direction_choices.changed.connect(self._save_and_emit)
        self.direction_choices.setAccessibleName("Melodic direction")
        self.direction_choices.setContentsMargins(18, 0, 0, 0)
        display_layout = self.display.layout()
        assert isinstance(display_layout, QVBoxLayout)
        display_layout.insertWidget(
            display_layout.indexOf(self.display.boxes["Melodic"]) + 1,
            self.direction_choices,
        )
        self.interval_list = ChoiceChecklist(
            [
                (
                    title,
                    [
                        (name, name)
                        for name, iv in settings.WRITTEN_INTERVALS.items()
                        if lo <= iv.number <= hi
                    ],
                )
                for title, lo, hi in (
                    ("Simple intervals", 2, 8),
                    ("Compound intervals", 9, 15),
                )
            ],
            selected=cfg.intervals,
            allow_empty=True,
            positions={
                name: (
                    (iv.number - 2) % 7,
                    settings.INTERVAL_QUALITY_ORDER[iv.quality],
                )
                for name, iv in settings.WRITTEN_INTERVALS.items()
            },
        )
        self.stack.addWidget(
            subpage(
                "Staff Key",
                body=scrolling(self.staff_keys),
                back=lambda: self._go(0),
                fill=True,
            ),
        )
        self.stack.addWidget(
            subpage(
                "Display Mode",
                body=scrolling(self.display),
                back=lambda: self._go(0),
                fill=True,
            ),
        )
        self.staff_keys.changed.connect(self._save_and_emit)
        self.display.changed.connect(self._save_and_emit)

        quality_page = QWidget()
        quality_layout = QVBoxLayout(quality_page)
        quality_layout.setContentsMargins(0, 0, 0, 0)
        self.quality_modes: dict[str, QRadioButton] = {}
        for mode, label in settings.INTERVAL_QUALITY_MODES.items():
            radio = QRadioButton(label)
            quality_layout.addWidget(radio)
            radio.setChecked(mode == cfg.quality_mode)
            radio.toggled.connect(
                lambda checked: checked and self._save_and_emit(),
            )
            self.quality_modes[mode] = radio
        self.stack.addWidget(
            subpage("Quality", body=quality_page, back=lambda: self._go(0)),
        )

        intervals = QWidget()
        interval_layout = QVBoxLayout(intervals)
        interval_layout.setContentsMargins(0, 0, 0, 0)
        self.select_all = ToggleRow("Select all")
        self._previous_intervals = set(cfg.intervals)
        self.select_all.switched.connect(self._select_all)
        interval_layout.addWidget(self.select_all)
        self.interval_span = QLabel()
        interval_layout.addWidget(self.interval_span)
        self.slider = IntervalRangeSlider()
        self.slider.edited.connect(self._select_span)
        interval_layout.addWidget(self.slider)
        interval_layout.addWidget(self.interval_list)
        self.interval_list.changed.connect(self._save_and_emit)
        self.stack.addWidget(
            subpage(
                "Intervals",
                body=scrolling(intervals),
                back=lambda: self._go(0),
                fill=True,
            ),
        )
        self.accidental_list = ChoiceChecklist(
            [
                (
                    "",
                    [
                        (sign, ACCIDENTAL_SYMBOLS[sign] or "♮")
                        for sign in settings.INTERVAL_ACCIDENTALS
                    ],
                ),
            ],
            selected=cfg.accidentals,
            positions={
                0: (0, 0),
                -1: (1, 0),
                1: (1, 1),
                -2: (2, 0),
                2: (2, 1),
            },
        )
        self.accidental_list.setStyleSheet(
            css("QCheckBox { font-size: 22pt; }"),
        )
        for sign, name in settings.INTERVAL_ACCIDENTALS.items():
            box = self.accidental_list.boxes[sign]
            box.setAccessibleName(name)
            box.setToolTip(name)
        self.accidental_list.changed.connect(self._save_and_emit)
        self.stack.addWidget(
            subpage(
                "Accidentals",
                body=self.accidental_list,
                back=lambda: self._go(0),
            ),
        )
        self.stack.addWidget(self._values_page("Note Value"))
        if prefix == "intervals":
            self.stack.addWidget(
                buttons_page(
                    cfg,
                    changed=self._save_and_emit,
                    back=lambda: self._go(0),
                ),
            )
        self._refresh_summaries()

    def _select_all(self, on: bool) -> None:
        """
        Temporarily include all spellings or restore the previous
        checks.

        Parameters
        ----------
        on : bool
            Whether all intervals should be selected.

        Examples
        --------
        Switch Select all off again to return to practicing thirds.
        """
        if on:
            self._previous_intervals = set(self.cfg.intervals)
        self._set_intervals(
            set(settings.WRITTEN_INTERVALS)
            if on
            else self._previous_intervals,
            restore=not on,
        )

    def _select_span(self, low: int, high: int) -> None:  # noqa: PLR0917 (Qt passes both endpoints positionally)
        """
        Check every spelling whose written interval number is between
        the handles.

        Parameters
        ----------
        low, high : int
            Inclusive written interval numbers.

        Examples
        --------
        Set both ends to three to check all the thirds.
        """
        self._set_intervals(
            {
                name
                for name, iv in settings.WRITTEN_INTERVALS.items()
                if low <= iv.number <= high
            },
        )

    def _set_intervals(
        self,
        names: set[str],
        *,
        restore: bool = False,
    ) -> None:
        """
        Apply a bulk interval selection in one edit.

        Parameters
        ----------
        names : set of str
            Checked interval spellings.
        restore : bool
            Restore the full selection saved before Select all,
            including hidden choices.

        Examples
        --------
        Moving a slider handle generates one new question.
        """
        for name, box in self.interval_list.boxes.items():
            if box.isHidden() and not restore:
                continue  # Preserve choices outside the current staff ranges.
            box.blockSignals(True)
            box.setChecked(name in names)
            box.blockSignals(False)
        self._save_and_emit()

    def _refresh_summaries(self) -> None:
        """
        Show the selected clefs, ranges, signatures, displays and
        interval count.

        Examples
        --------
        >>> IntervalSettingsPanel(
        ...     settings.IntervalSettings()
        ... ).display_row.value.text()
        'Harmonic'
        """
        super()._refresh_summaries()
        show_keys(
            self.staff_key_row,
            diagram=self.key_diagram,
            enabled=True,
            keys=self.cfg.staff_keys,
        )
        self.display_row.value.setText(
            ", ".join(
                d for d in settings.INTERVAL_DISPLAYS if d in self.cfg.displays
            ),
        )
        self.direction_choices.setVisible("Melodic" in self.cfg.displays)
        self.quality_row.value.setText(
            settings.INTERVAL_QUALITY_MODES[self.cfg.quality_mode],
        )
        if self.prefix == "intervals":
            self.quality_row.setEnabled(not self.cfg.consonance)
        self.accidentals_row.value.setText(
            " ".join(
                ACCIDENTAL_SYMBOLS[sign] or "♮"
                for sign in settings.INTERVAL_ACCIDENTALS
                if sign in self.cfg.accidentals
            ),
        )
        self.buttons_row.value.setText(self.cfg.button_mode.title())
        span = max(
            self.cfg.staff_span(clef) for clef in self.cfg.active_clefs()
        )
        available = {
            name
            for name, iv in settings.WRITTEN_INTERVALS.items()
            if iv.number <= span
        }
        for name, box in self.interval_list.boxes.items():
            box.setVisible(name in available)
            box.setEnabled(name in available)
        self.interval_list.headings["Simple intervals"].setVisible(span >= 2)
        self.interval_list.headings["Compound intervals"].setVisible(span >= 9)
        selected = self.cfg.intervals & available
        numbers = [
            settings.WRITTEN_INTERVALS[name].number for name in selected
        ]
        low, high = min(numbers, default=2), max(numbers, default=2)
        self.slider.set_range(
            low,
            high=high,
            minimum=2,
            maximum=min(span, 15),
            active=bool(numbers),
        )
        self.slider.setVisible(bool(available))
        self.select_all.setEnabled(bool(available))
        self.interval_span.setText(
            f"Interval numbers  {low}–{high}"
            if numbers
            else "No intervals selected",
        )
        if not available:
            self.interval_span.setText(
                "Widen a staff range to practice intervals.",
            )
        if not available or selected != available:
            self.select_all.setOn(False)
        count = len(selected)
        self.intervals_row.value.setText(
            f"{count} selected" if count else "None",
        )

    def _persist(self) -> None:
        """
        Take every control's choices into the settings, save them and
        show them in the menu.

        Examples
        --------
        >>> panel = IntervalSettingsPanel(
        ...     settings.IntervalSettings(),
        ...     prefix="intervals",
        ... )
        >>> panel.boxes["alto"].setChecked(True)
        >>> (
        ...     panel.cfg.active_clefs(),
        ...     str(store().value("intervals/clefs")),
        ... )
        (['treble', 'bass', 'alto'], 'alto,bass,treble')
        >>> store().remove("intervals")
        """
        cfg = self.cfg
        cfg.clefs = {c for c, box in self.boxes.items() if box.isChecked()}
        guard_last(self.boxes.values())
        cfg.staff_keys = self.staff_keys.selected()
        cfg.displays = self.display.selected()
        cfg.directions = self.direction_choices.selected()
        cfg.accidentals = self.accidental_list.selected()
        cfg.quality_mode = next(
            mode
            for mode, radio in self.quality_modes.items()
            if radio.isChecked()
        )
        cfg.intervals = self.interval_list.selected()
        saved = store()
        prefix = self.prefix
        if prefix == "intervals":
            cfg.inversions = self.inversions_row.isOn()
            cfg.consonance = self.consonance_row.isOn()
            saved.setValue(
                f"{prefix}/consonance",
                "true" if cfg.consonance else "false",
            )
            saved.setValue(
                f"{prefix}/inversions",
                "true" if cfg.inversions else "false",
            )
            saved.setValue(f"{prefix}/buttonMode", cfg.button_mode)
            saved.setValue(f"{prefix}/buttonCount", cfg.button_count)
        saved.setValue(f"{prefix}/clefs", ",".join(sorted(cfg.clefs)))
        saved.setValue(
            f"{prefix}/staffKeys",
            ",".join(map(str, sorted(cfg.staff_keys))),
        )
        saved.setValue(f"{prefix}/values", ",".join(cfg.active_values()))
        saved.setValue(f"{prefix}/display", ",".join(sorted(cfg.displays)))
        saved.setValue(
            f"{prefix}/accidentals",
            ",".join(map(str, sorted(cfg.accidentals))),
        )
        saved.setValue(f"{prefix}/direction", ",".join(sorted(cfg.directions)))
        saved.setValue(f"{prefix}/quality", cfg.quality_mode)
        saved.setValue(f"{prefix}/intervals", ",".join(sorted(cfg.intervals)))
        saved.remove(f"{prefix}/range")
        for clef, (low, high) in cfg.ranges.items():
            saved.setValue(f"{prefix}/range/{clef}", f"{low},{high}")
        self._refresh_summaries()


class KeyboardIntervalSettingsPanel(KeyboardRangePanel):
    """
    Range and interval selection pages for keyboard interval
    identification.

    Attributes
    ----------
    cfg : KeyboardIntervalSettings
        The settings being edited.
    stack : SlideStack
        The settings menu, range page, and interval page.
    span : KeyboardSpan
        The draggable range selector.
    interval_range : QWidget
        The interval range controls directly below Select all.
    interval_slider : IntervalRangeSlider
        The two-handle interval selector.
    interval_low_label, interval_high_label : FieldComboBox
        Clickable endpoint notation with scrollable interval lists.
    interval_page : ChoiceChecklist
        The interval checkboxes, keyed by distance in half steps.

    Examples
    --------
    >>> panel = KeyboardIntervalSettingsPanel(
    ...     settings.KeyboardIntervalSettings()
    ... )
    >>> panel.stack.count()
    4
    """

    def __init__(
        self,
        cfg: settings.KeyboardIntervalSettings,
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the range selector and interval checklist.

        Parameters
        ----------
        cfg : KeyboardIntervalSettings
            The settings to edit.
        parent : QWidget or None, default None
            The widget that owns the panel. Keyword-only.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(
        ...     settings.KeyboardIntervalSettings()
        ... )
        >>> (
        ...     panel.low_label.text(),
        ...     panel.high_label.text(),
        ... )
        ('C3', 'C5')
        """
        super().__init__(parent)
        self.cfg = cfg
        cfg.low, cfg.high = cfg.bounds()
        cfg.intervals = set(cfg.active_intervals())
        self._selection_before_all = set(cfg.intervals)
        self._select_all_active = False
        menu, menu_layout = self._build_menu()
        self.range_row = MenuRow("Range", tall=True)
        self.range_row.clicked.connect(lambda: self._go(1))
        self.range_keyboard = KeyboardSpan(
            compact=True,
            size=(px(ROW_PICTURE_WIDTH), px(36)),
        )
        self.range_row.attach(self.range_keyboard)
        self.intervals_row = MenuRow("Intervals")
        self.intervals_row.clicked.connect(lambda: self._go(2))
        menu_layout.addWidget(self.range_row)
        menu_layout.addWidget(self.intervals_row)
        self.buttons_row = MenuRow("Buttons")
        self.buttons_row.clicked.connect(lambda: self._go(3))
        menu_layout.addWidget(self.buttons_row)
        menu_layout.addStretch()
        buttons_body = QWidget()
        buttons_layout = QVBoxLayout(buttons_body)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.button_modes: dict[str, QRadioButton] = {}
        mode_group = QButtonGroup(self)
        for mode, label, tip in (
            (
                "limited",
                "Limited",
                "Show up to the chosen number of answer buttons",
            ),
            ("all", "All", "Show a fixed button for every selected interval"),
            (
                "compact",
                "Compact",
                (
                    "Choose a quality letter and an interval number, in "
                    "either order"
                ),
            ),
        ):
            radio = QRadioButton(label)
            radio.setToolTip(tip)
            mode_group.addButton(radio)
            radio.toggled.connect(
                lambda on, chosen=mode: self._button_mode_chosen(
                    chosen,
                    on=on,
                ),
            )
            buttons_layout.addWidget(radio)
            self.button_modes[mode] = radio
        self.button_count_row = QWidget()
        count_layout = QHBoxLayout(self.button_count_row)
        count_layout.setContentsMargins(0, 0, 0, 0)
        count_layout.addWidget(QLabel("Button count"), 1)
        self.button_count_down = arrow_button(
            Qt.ArrowType.LeftArrow,
            tip="Fewer answer buttons",
        )
        self.button_count_up = arrow_button(
            Qt.ArrowType.RightArrow,
            tip="More answer buttons",
        )
        self.button_count_down.clicked.connect(
            lambda: self._step_button_count(-1),
        )
        self.button_count_up.clicked.connect(
            lambda: self._step_button_count(1),
        )
        self.button_count = QLineEdit()
        self.button_count.setProperty("field", True)
        self.button_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_count.setFixedWidth(px(54))
        self.button_count.setValidator(
            QIntValidator(
                1,
                len(settings.KEYBOARD_INTERVAL_NAMES),
                self.button_count,
            ),
        )
        self.button_count.setAccessibleName("Answer button count")
        self.button_count.setToolTip(
            (
                "Maximum answer buttons in limited mode; fewer are shown "
                "if fewer intervals are selected"
            ),
        )
        self.button_count.editingFinished.connect(self._button_count_edited)
        count_layout.addWidget(self.button_count_down)
        count_layout.addWidget(self.button_count)
        count_layout.addWidget(self.button_count_up)
        buttons_layout.insertWidget(1, self.button_count_row)
        buttons_layout.addStretch()

        self.span = KeyboardSpan()
        body = self._range_body(self.span, changed=self._set_range)
        intervals = QWidget()
        intervals_layout = QVBoxLayout(intervals)
        intervals_layout.setContentsMargins(0, 0, 0, 0)
        self.select_all = ToggleRow("Select all")
        self.select_all.switched.connect(self._select_all_toggled)
        intervals_layout.addWidget(self.select_all)
        self.interval_range = QWidget()
        range_layout = QVBoxLayout(self.interval_range)
        range_layout.setContentsMargins(0, 0, 0, 0)
        self.interval_slider = IntervalRangeSlider()
        self.interval_slider.edited.connect(self._interval_range_edited)
        range_layout.addWidget(self.interval_slider)
        endpoints = QGridLayout()
        endpoints.setColumnStretch(2, 1)
        self.interval_low_label, self.interval_high_label = (
            FieldComboBox(),
            FieldComboBox(),
        )
        self.interval_arrows: dict[str, tuple[QToolButton, QToolButton]] = {}
        for row, (title, label, which) in enumerate(
            (
                ("From", self.interval_low_label, "low"),
                ("To", self.interval_high_label, "high"),
            ),
        ):
            endpoints.addWidget(QLabel(title), row, 0)
            down = arrow_button(
                Qt.ArrowType.LeftArrow,
                tip=f"{title}: smaller interval",
            )
            up = arrow_button(
                Qt.ArrowType.RightArrow,
                tip=f"{title}: larger interval",
            )
            down.clicked.connect(
                lambda _=False, w=which: self.interval_slider.move_endpoint(
                    w,
                    delta=-1,
                ),
            )
            up.clicked.connect(
                lambda _=False, w=which: self.interval_slider.move_endpoint(
                    w,
                    delta=1,
                ),
            )
            label.setProperty("field", True)
            label.setMinimumWidth(px(48))
            label.setMaxVisibleItems(12)
            label.setPlaceholderText("—")
            label.setAccessibleName(
                "Lowest interval" if which == "low" else "Highest interval",
            )
            label.setToolTip(
                "Choose the "
                f"{('lowest' if which == 'low' else 'highest')}"
                " interval",
            )
            label.activated.connect(
                lambda index, w=which: self._interval_endpoint_picked(
                    w,
                    index=index,
                ),
            )
            endpoints.addWidget(down, row, 1)
            endpoints.addWidget(label, row, 2)
            endpoints.addWidget(up, row, 3)
            self.interval_arrows[which] = (down, up)
        range_layout.addLayout(endpoints)
        intervals_layout.addWidget(self.interval_range)
        self.interval_page = ChoiceChecklist(
            [
                (
                    "Simple intervals",
                    [
                        (distance, settings.keyboard_interval_name(distance))
                        for distance in range(1, 13)
                    ],
                ),
                (
                    "Compound intervals",
                    [
                        (distance, settings.keyboard_interval_name(distance))
                        for distance in range(
                            13,
                            len(settings.KEYBOARD_INTERVAL_NAMES) + 1,
                        )
                    ],
                ),
            ],
            selected=cfg.intervals,
            allow_empty=True,
        )
        self.interval_page.changed.connect(self._intervals_edited)
        intervals_layout.addWidget(self.interval_page)
        self.stack.addWidget(menu)
        self.stack.addWidget(
            subpage("Range", body=body, back=lambda: self._go(0)),
        )
        self.stack.addWidget(
            subpage(
                "Intervals",
                body=scrolling(intervals),
                back=lambda: self._go(0),
                fill=True,
            ),
        )
        self.stack.addWidget(
            subpage("Buttons", body=buttons_body, back=lambda: self._go(0)),
        )
        self._refresh()

    def _refresh(self) -> None:
        """
        Update range labels and disable interval choices that cannot be
        used.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(
        ...     settings.KeyboardIntervalSettings(
        ...         low=60, high=64
        ...     )
        ... )
        >>> panel.interval_page.boxes[12].isEnabled()
        False
        """
        cfg = self.cfg
        mode = (
            "compact"
            if cfg.compact_buttons
            else "all"
            if cfg.all_interval_buttons
            else "limited"
        )
        for key, radio in self.button_modes.items():
            radio.blockSignals(True)
            radio.setChecked(key == mode)
            radio.blockSignals(False)
        self.buttons_row.value.setText(self.button_modes[mode].text())
        self.button_count.setText(str(cfg.answer_button_limit()))
        self.button_count_row.setEnabled(
            not (cfg.all_interval_buttons or cfg.compact_buttons),
        )
        self.button_count_down.setEnabled(cfg.answer_button_limit() > 1)
        self.button_count_up.setEnabled(
            cfg.answer_button_limit() < len(settings.KEYBOARD_INTERVAL_NAMES),
        )
        self.low_label.setText(key_name(cfg.low))
        self.high_label.setText(key_name(cfg.high))
        self.span.set_span(cfg.low, hi=cfg.high)
        available = cfg.high - cfg.low
        low = min(cfg.intervals) if cfg.intervals else 1
        high = max(cfg.intervals) if cfg.intervals else 1
        active = bool(cfg.intervals)
        self.interval_slider.set_range(
            low,
            high=high,
            maximum=available,
            active=active,
        )
        for picker, value in (
            (self.interval_low_label, low),
            (self.interval_high_label, high),
        ):
            picker.blockSignals(True)
            if picker.count() != available:
                picker.clear()
                picker.addItems(
                    list(settings.KEYBOARD_INTERVAL_NAMES[:available]),
                )
            picker.setCurrentIndex(value - 1 if active else -1)
            picker.blockSignals(False)
        self.interval_arrows["low"][0].setEnabled(not active or low > 1)
        self.interval_arrows["low"][1].setEnabled(not active or low < high)
        self.interval_arrows["high"][0].setEnabled(not active or high > low)
        self.interval_arrows["high"][1].setEnabled(
            not active or high < available,
        )
        self.range_keyboard.set_span(cfg.low, hi=cfg.high)
        self.range_keyboard.setToolTip(
            f"{key_name(cfg.low)} to {key_name(cfg.high)}",
        )
        first, last = settings.KEYBOARD_FULL
        self.arrows["low"][0].setEnabled(cfg.low > first)
        self.arrows["low"][1].setEnabled(cfg.low + 1 < cfg.high)
        self.arrows["high"][0].setEnabled(cfg.high - 1 > cfg.low)
        self.arrows["high"][1].setEnabled(cfg.high < last)
        names = [
            settings.KEYBOARD_INTERVAL_NAMES[distance - 1]
            for distance in sorted(cfg.intervals)
        ]
        all_selected = len(names) == cfg.high - cfg.low
        self.select_all.setOn(self._select_all_active)
        self.intervals_row.value.setText(
            "All" if all_selected else ", ".join(names) if names else "None",
        )
        self.intervals_row.setToolTip(", ".join(names))
        for distance in range(1, len(settings.KEYBOARD_INTERVAL_NAMES) + 1):
            box = self.interval_page.boxes[distance]
            box.setVisible(distance <= cfg.high - cfg.low)
            box.blockSignals(True)
            box.setChecked(distance in cfg.intervals)
            box.setEnabled(distance <= cfg.high - cfg.low)
            box.blockSignals(False)

    def _step(self, which: str, *, delta: int) -> None:
        """
        Adjust one endpoint without collapsing the range to a single
        key.

        Parameters
        ----------
        which : str
            The endpoint, "low" or "high".
        delta : int
            The number of keys to move. Keyword-only.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(
        ...     settings.KeyboardIntervalSettings()
        ... )
        >>> panel._step("low", delta=1)
        >>> panel.cfg.low
        49
        >>> panel._step("high", delta=-1)
        >>> (
        ...     panel.cfg.high
        ...     == settings.KeyboardIntervalSettings().high - 1
        ... )
        True
        """
        low, high = self.cfg.low, self.cfg.high
        first, last = settings.KEYBOARD_FULL
        if which == "low":
            low = min(max(low + delta, first), high - 1)
        else:
            high = max(min(high + delta, last), low + 1)
        self._set_range(low, high)

    def _set_range(  # noqa: PLR0917 (the Qt signal supplies two positional arguments)
        self,
        low: int,
        high: int,
    ) -> None:
        """
        Save a dragged range and retain only intervals that fit.

        Parameters
        ----------
        low : int
            The lowest selected MIDI key.
        high : int
            The highest selected MIDI key.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(
        ...     settings.KeyboardIntervalSettings()
        ... )
        >>> panel._set_range(60, 64)
        >>> panel.cfg.active_intervals()
        [1, 2, 3, 4]
        """
        self.cfg.low, self.cfg.high = low, high
        self.cfg.low, self.cfg.high = self.cfg.bounds()
        if self._select_all_active:
            self.cfg.intervals = set(
                range(1, self.cfg.high - self.cfg.low + 1),
            )
        else:
            self.cfg.intervals = set(self.cfg.active_intervals())
        self._save_and_emit()

    def _interval_endpoint_picked(self, which: str, *, index: int) -> None:
        """
        Select an endpoint from its dropdown and keep the interval
        bounds ordered.

        Parameters
        ----------
        which : str
            The endpoint, "low" or "high".
        index : int
            The selected interval's zero-based index. Keyword-only.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(
        ...     settings.KeyboardIntervalSettings()
        ... )
        >>> panel._interval_endpoint_picked(
        ...     "low", index=2
        ... )
        >>> (
        ...     min(panel.cfg.intervals),
        ...     max(panel.cfg.intervals),
        ... )
        (3, 12)
        """
        if not 0 <= index < self.cfg.high - self.cfg.low:
            return
        value = index + 1
        selected = self.cfg.intervals
        low = min(selected) if selected else value
        high = max(selected) if selected else value
        if which == "low":
            low, high = value, max(high, value)
        else:
            low, high = min(low, value), value
        self._interval_range_edited(low, high)

    def _interval_range_edited(  # noqa: PLR0917 (the Qt signal supplies two positional arguments)
        self,
        low: int,
        high: int,
    ) -> None:
        """
        Select the interval span chosen with the slider or endpoint
        buttons.

        Parameters
        ----------
        low : int
            The lowest interval distance, in half steps.
        high : int
            The highest interval distance, in half steps.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(
        ...     settings.KeyboardIntervalSettings()
        ... )
        >>> panel.interval_slider.move_endpoint(
        ...     "low", delta=2
        ... )
        >>> panel.cfg.intervals
        {3, 4, 5, 6, 7, 8, 9, 10, 11, 12}
        >>> panel.cfg.bounds()
        (48, 72)
        """
        self._select_all_active = False
        self.cfg.intervals = set(range(low, high + 1))
        self._save_and_emit()

    def _step_button_count(self, delta: int) -> None:
        """
        Adjust the limited answer-button count with an arrow button.

        Parameters
        ----------
        delta : int
            The number of buttons to add or remove.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(
        ...     settings.KeyboardIntervalSettings()
        ... )
        >>> panel._step_button_count(1)
        >>> panel.cfg.button_count
        7
        """
        self.cfg.button_count = max(
            1,
            min(
                len(settings.KEYBOARD_INTERVAL_NAMES),
                self.cfg.answer_button_limit() + delta,
            ),
        )
        self._save_and_emit()

    def _button_count_edited(self) -> None:
        """
        Commit a typed answer-button count, restoring the current value
        if the input is invalid.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(
        ...     settings.KeyboardIntervalSettings()
        ... )
        >>> panel.button_count.setText("8")
        >>> panel._button_count_edited()
        >>> panel.cfg.button_count
        8
        >>> panel.button_count.setText(
        ...     ""
        ... )  # not a number: the field shows the saved count again
        >>> panel._button_count_edited()
        >>> (
        ...     panel.button_count.text(),
        ...     panel.cfg.button_count,
        ... )
        ('8', 8)
        """
        try:
            count = int(self.button_count.text())
        except ValueError:
            self._refresh()
            return
        self.cfg.button_count = max(
            1,
            min(len(settings.KEYBOARD_INTERVAL_NAMES), count),
        )
        self._save_and_emit()

    def _button_mode_chosen(self, mode: str, *, on: bool) -> None:
        """
        Save the selected answer mode while preserving the limited
        button count.

        Parameters
        ----------
        mode : str
            The selected mode: "limited", "all", or "compact".
        on : bool
            Whether this radio button is selected. Keyword-only.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(
        ...     settings.KeyboardIntervalSettings()
        ... )
        >>> panel.button_modes["compact"].click()
        >>> (
        ...     panel.cfg.compact_buttons,
        ...     panel.cfg.all_interval_buttons,
        ... )
        (True, False)
        """
        if not on:
            return
        self.cfg.compact_buttons = mode == "compact"
        self.cfg.all_interval_buttons = mode == "all"
        self._save_and_emit()

    def _select_all_toggled(self, on: bool) -> None:
        """
        Temporarily select every interval, or restore the selection from
        before the toggle was enabled.

        Parameters
        ----------
        on : bool
            True to select all available intervals; False to restore the
            previous selection.

        Examples
        --------
        >>> cfg = settings.KeyboardIntervalSettings(
        ...     low=60, high=64, intervals={3}
        ... )
        >>> panel = KeyboardIntervalSettingsPanel(cfg)
        >>> panel._select_all_toggled(True)
        >>> cfg.intervals
        {1, 2, 3, 4}
        >>> panel._select_all_toggled(False)
        >>> cfg.intervals
        {3}
        """
        if on:
            self._selection_before_all = set(self.cfg.intervals)
            self.cfg.intervals = set(
                range(1, self.cfg.high - self.cfg.low + 1),
            )
        else:
            self.cfg.intervals = set(self._selection_before_all)
            self.cfg.intervals = set(self.cfg.active_intervals())
        self._select_all_active = on
        self._save_and_emit()

    def _intervals_edited(self) -> None:
        """
        Save the interval selection and ask a new question.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(
        ...     settings.KeyboardIntervalSettings()
        ... )
        >>> panel.interval_page.boxes[12].setChecked(
        ...     False
        ... )
        >>> 12 in panel.cfg.intervals
        False
        """
        self._select_all_active = False
        selected = self.interval_page.selected()
        self.cfg.intervals = {
            distance
            for distance in range(1, len(settings.KEYBOARD_INTERVAL_NAMES) + 1)
            if distance in selected
        }
        self.cfg.intervals = set(self.cfg.active_intervals())
        self._save_and_emit()

    def _persist(self) -> None:
        """
        Bring the controls up to date with the settings, and save them.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(
        ...     settings.KeyboardIntervalSettings()
        ... )
        >>> panel._persist()
        >>> int(
        ...     store().value("keyboardIntervals/low")
        ... ) == panel.cfg.low
        True
        """
        self._refresh()
        save_keyboard_intervals(self.cfg)


_INVERSION_SHORT = (
    "Root",
    "1st",
    "2nd",
    "3rd",
)


class ArpeggioSettingsPanel(ClefsPanel):
    """
    The settings of the arpeggio exercise: a menu with a page for each
    group of settings.

    The menu has Clefs, Arpeggio types, Inversions and Key signatures.
    Edits are live: each changes the settings, saves them
    and emits `changed`.

    Attributes
    ----------
    cfg : ArpeggioSettings
        The settings being edited.
    stack : SlideStack
        The menu and its pages.
    boxes : dict of str to QCheckBox
        The clef checkboxes.
    types : ChoiceChecklist
        The chord types.
    inversions : ChoiceChecklist
        The inversions.
    key_page : KeySignaturePage
        The key signature sub-page.

    Examples
    --------
    >>> panel = ArpeggioSettingsPanel(
    ...     settings.ArpeggioSettings()
    ... )
    >>> panel.types_row.value.text()
    '4 of 9'
    """

    cfg: settings.ArpeggioSettings

    def __init__(
        self,
        cfg: settings.ArpeggioSettings,
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the panel for a set of settings.

        Parameters
        ----------
        cfg : ArpeggioSettings
            The settings to edit.
        parent : QWidget or None, default None
            The widget that owns the panel. Keyword-only.

        Examples
        --------
        >>> ArpeggioSettingsPanel(
        ...     settings.ArpeggioSettings()
        ... ).stack.count()  # the menu and four pages
        5
        """
        super().__init__(parent)
        self.cfg = cfg
        menu, mlay = self._build_menu()
        self.clefs_row = MenuRow("Clefs")
        self.clefs_row.clicked.connect(lambda: self._go(1))
        self.clef_pictures = ClefPictures()
        self.clefs_row.attach(self.clef_pictures)
        self.types_row = MenuRow("Arpeggio types")
        self.types_row.clicked.connect(lambda: self._go(2))
        self.inversions_row = MenuRow("Inversions")
        self.inversions_row.clicked.connect(lambda: self._go(3))
        self.keys_row = MenuRow("Key signatures")
        self.keys_row.setToolTip(
            (
                "Draw a key signature; the arpeggio then only gets signs "
                "where it differs from it"
            ),
        )
        self.keys_row.clicked.connect(lambda: self._go(4))
        self.keys_diagram = KeyDiagram()
        self.keys_row.attach(self.keys_diagram)
        for row in (
            self.clefs_row,
            self.types_row,
            self.inversions_row,
            self.keys_row,
        ):
            mlay.addWidget(row)
        mlay.addStretch()

        # layer 2: clefs (the ones with a single staff)
        self.boxes, clefs_page = clef_choice_page(
            CLEFS,
            selected=cfg.clefs,
            edited=self._clefs_edited,
            back=lambda: self._go(0),
        )

        # layer 2: arpeggio types, and inversions
        self.types = ChoiceChecklist(
            [
                (
                    "Triads",
                    [(t, t.capitalize()) for t in settings.ARPEGGIO_TRIADS],
                ),
                (
                    "Seventh chords",
                    [(t, t.capitalize()) for t in settings.ARPEGGIO_SEVENTHS],
                ),
            ],
            selected=cfg.types,
        )
        self.types.changed.connect(self._types_edited)
        types_page = subpage(
            "Arpeggio types",
            body=self.types,
            back=lambda: self._go(0),
        )
        names = settings_inversion_names()
        self.inversions = ChoiceChecklist(
            [("", [(i, names[i]) for i in settings.INVERSIONS])],
            selected=cfg.inversions,
        )
        self.inversions.changed.connect(self._inversions_edited)
        note = QLabel(
            (
                "A triad has no 3rd inversion, so that choice only applies"
                " to seventh chords."
            ),
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: gray;")
        inv_body = QWidget()
        inv_lay = QVBoxLayout(inv_body)
        inv_lay.setContentsMargins(0, 0, 0, 0)
        inv_lay.addWidget(self.inversions)
        inv_lay.addWidget(note)
        inversions_page = subpage(
            "Inversions",
            body=inv_body,
            back=lambda: self._go(0),
        )

        # layer 2: key signatures
        self.key_page = KeySignaturePage(cfg.key_signature, selected=cfg.keys)
        self.key_page.changed.connect(self._keys_edited)
        keys_page = subpage(
            "Key signatures",
            body=self.key_page,
            back=lambda: self._go(0),
        )

        for page in (
            menu,
            clefs_page,
            types_page,
            inversions_page,
            keys_page,
        ):
            self.stack.addWidget(page)
        self._refresh_summaries()

    def _refresh_summaries(self) -> None:
        """
        Update the menu's summaries: the clefs, how many types, which
        inversions and the keys.

        Examples
        --------
        >>> panel = ArpeggioSettingsPanel(
        ...     settings.ArpeggioSettings(
        ...         inversions={0, 2}
        ...     )
        ... )
        >>> panel._refresh_summaries()
        >>> panel.inversions_row.value.text()
        'Root, 2nd'
        """
        cfg = self.cfg
        self.clef_pictures.set_clefs(cfg.active_clefs())
        types = cfg.active_types()
        self.types_row.value.setText(
            f"{len(types)} of {len(settings.ARPEGGIO_TYPES)}",
        )
        inversions = cfg.active_inversions()
        self.inversions_row.value.setText(
            "All"
            if len(inversions) == len(settings.INVERSIONS)
            else ", ".join(_INVERSION_SHORT[i] for i in inversions),
        )
        show_keys(
            self.keys_row,
            diagram=self.keys_diagram,
            enabled=cfg.key_signature,
            keys=set(cfg.active_keys()),
        )

    def _persist(self) -> None:
        """
        Save the arpeggio settings.

        Examples
        --------
        >>> cfg_ = settings.ArpeggioSettings(
        ...     clefs={"tenor"}
        ... )
        >>> panel = ArpeggioSettingsPanel(cfg_)
        >>> panel._persist()
        >>> str(store().value("arpeggio/clefs"))
        'tenor'
        >>> store().setValue(
        ...     "arpeggio/clefs", "treble,bass"
        ... )
        """
        save_arpeggio(self.cfg)

    def _types_edited(self) -> None:
        """
        Take the checked chord types into the settings, save them and
        say so.

        Examples
        --------
        >>> cfg = settings.ArpeggioSettings()
        >>> panel = ArpeggioSettingsPanel(cfg)
        >>> panel.types.boxes["minor 7th"].setChecked(
        ...     True
        ... )
        >>> "minor 7th" in cfg.types
        True
        """
        self.cfg.types = self.types.selected()
        self._save_and_emit()

    def _inversions_edited(self) -> None:
        """
        Take the checked inversions into the settings, save them and say
        so.

        Examples
        --------
        >>> cfg = settings.ArpeggioSettings()
        >>> panel = ArpeggioSettingsPanel(cfg)
        >>> panel.inversions.boxes[3].setChecked(False)
        >>> 3 in cfg.inversions
        False
        """
        self.cfg.inversions = self.inversions.selected()
        self._save_and_emit()

    def _keys_edited(self) -> None:
        """
        Take the key signature page into the settings, update the menu,
        save and say so.

        Examples
        --------
        >>> cfg = settings.ArpeggioSettings()
        >>> panel = ArpeggioSettingsPanel(cfg)
        >>> panel.key_page.switch_row.setOn(True)
        >>> panel._keys_edited()
        >>> cfg.key_signature
        True
        """
        self.cfg.key_signature = self.key_page.enabled()
        self.cfg.keys = self.key_page.selected()
        show_keys(
            self.keys_row,
            diagram=self.keys_diagram,
            enabled=self.cfg.key_signature,
            keys=set(self.cfg.active_keys()),
        )
        self._save_and_emit()


class KeySignatureSettingsPanel(ClefsPanel):
    """
    The settings of a key signature exercise: a menu with a page for
    each group of settings.

    The same panel serves key signature identification, key signature
    construction and both scale exercises, each saving
    under its own name.

    The menu has Clefs, Scales and Key signatures. Both scale exercises
    have independent staff and scale key choices;
    construction also has Octave and Steps switches. Edits are live:
    each changes the settings, saves them and emits `changed`.

    Attributes
    ----------
    cfg : KeySignatureSettings
        The settings being edited.
    prefix : str
        What the settings are saved under, such as "keySignatures".
    stack : SlideStack
        The menu and its pages.
    boxes : dict of str to QCheckBox
        The clef checkboxes.
    modes : ChoiceChecklist
        The scales (major, minor and the modes).
    key_list : KeyChecklist
        The key signatures (of the scales, in scale construction).
    staff_key_list : KeyChecklist or None
        The key signatures that may be drawn on the staff; only scale
        construction has it.

    Examples
    --------
    >>> panel = KeySignatureSettingsPanel(
    ...     settings.KeySignatureSettings()
    ... )
    >>> panel.modes_row.value.text()
    '2 of 7'
    """

    cfg: settings.KeySignatureSettings

    def __init__(
        self,
        cfg: settings.KeySignatureSettings,
        *,
        prefix: str = "keySignatures",
        keys_title: str = "Key signatures",
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the panel for a set of settings.

        Parameters
        ----------
        cfg : KeySignatureSettings
            The settings to edit.
        prefix : str, default "keySignatures"
            What the settings are saved under. Keyword-only.
        keys_title : str, default "Key signatures"
            Title for the signature checklist when the exercise uses a
            single list. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns the panel. Keyword-only.

        Examples
        --------
        >>> KeySignatureSettingsPanel(
        ...     settings.KeySignatureSettings()
        ... ).stack.count()  # the menu and three pages
        4
        """
        super().__init__(parent)
        self.cfg = cfg
        self.prefix = prefix
        menu, mlay = self._build_menu()
        scales = isinstance(
            cfg,
            (
                settings.ScaleConstructionSettings,
                settings.ScaleIdentificationSettings,
            ),
        )  # these have a signature for the staff and one for the scale
        self.clefs_row = MenuRow("Clefs")
        self.modes_row = MenuRow("Scales")
        self.keys_row = MenuRow("Scale Key" if scales else keys_title)
        self.staff_keys_row: MenuRow | None = (
            MenuRow("Staff Key") if scales else None
        )
        self.clef_pictures = ClefPictures()
        self.clefs_row.attach(self.clef_pictures)
        self.keys_diagram = KeyDiagram()
        if not scales:
            self.keys_row.attach(self.keys_diagram)
        self.staff_keys_diagram = KeyDiagram()
        if self.staff_keys_row is not None:
            self.staff_keys_row.attach(self.staff_keys_diagram)
        menu_rows = [self.clefs_row, self.modes_row]
        if self.staff_keys_row is not None:
            menu_rows.append(
                self.staff_keys_row,
            )  # the staff's key and the scale's are next to each other
        menu_rows.append(self.keys_row)
        if isinstance(cfg, settings.OrderOfKeysSettings):
            self.starts_row = MenuRow("Starting Accidentals")
            menu_rows.append(self.starts_row)
        if scales:
            self.motion_row = MenuRow("Motion")
            menu_rows.append(self.motion_row)
        if isinstance(cfg, settings.ScaleIdentificationSettings):
            self.buttons_row = MenuRow("Buttons")
            menu_rows.append(self.buttons_row)
            self.question_type_row = MenuRow("Question Type")
            menu_rows.append(self.question_type_row)
        for index, row in enumerate(menu_rows, 1):
            row.clicked.connect(lambda _=False, i=index: self._go(i))
            mlay.addWidget(row)
        self.steps_row: ToggleRow | None = (
            # only scale construction has steps to mark, and an octave
            # to start in
            None
        )
        self.octave_row: ToggleRow | None = None
        if isinstance(cfg, settings.ScaleConstructionSettings):
            octave_row = ToggleRow("Octave")
            octave_row.setToolTip(
                (
                    "Name the octave of the first note, such as G2 Major, "
                    "and require the scale to start there"
                ),
            )
            octave_row.setOn(cfg.octave)
            octave_row.switched.connect(self._octave_toggled)
            mlay.addWidget(octave_row)
            self.octave_row = octave_row
            steps_row = ToggleRow("Steps")
            steps_row.setToolTip(
                (
                    "Also mark the whole and half steps between the notes,"
                    " once they are placed"
                ),
            )
            steps_row.setOn(cfg.steps)
            steps_row.switched.connect(self._steps_toggled)
            mlay.addWidget(steps_row)
            self.steps_row = steps_row
        mlay.addStretch()

        # layer 2: the clefs the signature is drawn on
        self.boxes, clefs_page = clef_choice_page(
            CLEFS,
            selected=cfg.clefs,
            edited=self._clefs_edited,
            back=lambda: self._go(0),
        )

        # layer 2: the scales, so the key can be a major or minor key or
        # a mode
        self.modes = ChoiceChecklist(
            [("", [(m, settings.MODE_LABELS[m]) for m in settings.KEY_MODES])],
            selected=cfg.modes,
        )
        self.modes.changed.connect(self._modes_edited)
        modes_note = QLabel(
            "A mode has the key signature of a major key and starts from "
            "another note of it: D Dorian has "
            "the signature of C major.",
        )
        modes_note.setWordWrap(True)
        modes_note.setStyleSheet("color: gray;")
        modes_body = QWidget()
        mlay2 = QVBoxLayout(modes_body)
        mlay2.setContentsMargins(0, 0, 0, 0)
        mlay2.addWidget(self.modes)
        mlay2.addWidget(modes_note)
        modes_page = subpage(
            "Scales",
            body=modes_body,
            back=lambda: self._go(0),
        )

        # layer 2: the key signatures asked
        if isinstance(
            cfg,
            (
                settings.ScaleConstructionSettings,
                settings.ScaleIdentificationSettings,
            ),
        ):
            self.scale_keys = ScaleKeyPicker(
                major_keys=set(cfg.active_keys())
                if cfg.minor_keys is None
                else cfg.keys,
                minor_keys=set(cfg.active_keys())
                if cfg.minor_keys is None
                else cfg.minor_keys,
            )
            self.key_list = self.scale_keys.major_keys
            self.scale_keys.minor_keys.changed.connect(self._keys_edited)
        else:
            self.key_list = KeyChecklist(cfg.keys)
        self.key_list.changed.connect(self._keys_edited)
        pages = [menu, clefs_page, modes_page]
        self.staff_key_list: KeyChecklist | None = None
        if isinstance(
            cfg,
            (
                settings.ScaleConstructionSettings,
                settings.ScaleIdentificationSettings,
            ),
        ):
            # layer 2: the signature drawn on the staff, which need not
            # be the scale's own
            staff_key_list = KeyChecklist(cfg.staff_keys)
            staff_key_list.changed.connect(self._staff_keys_edited)
            self.staff_key_list = staff_key_list
            staff_note = QLabel(
                "The key signature drawn at the start of the staff. It need"
                " not be the scale's: with two flats on the "
                "staff, a C major scale needs a natural on its B and E.",
            )
            staff_note.setWordWrap(True)
            staff_note.setStyleSheet("color: gray;")
            staff_body = QWidget()
            staff_lay = QVBoxLayout(staff_body)
            staff_lay.setContentsMargins(0, 0, 0, 0)
            staff_lay.addWidget(staff_key_list)
            staff_lay.addWidget(staff_note)
            pages.append(
                subpage(
                    "Staff Key",
                    body=staff_body,
                    back=lambda: self._go(0),
                ),
            )
            pages.append(
                subpage(
                    "Scale Key",
                    body=scrolling(self.scale_keys),
                    back=lambda: self._go(0),
                    fill=True,
                ),
            )
            pages.append(
                subpage(
                    "Motion",
                    body=direction_choices(cfg, edited=self._save_and_emit),
                    back=lambda: self._go(0),
                ),
            )
        else:
            pages.append(
                subpage(
                    keys_title,
                    body=self.key_list,
                    back=lambda: self._go(0),
                ),
            )

        if isinstance(cfg, settings.OrderOfKeysSettings):
            self.starts_list = KeyChecklist(
                cfg.starting_accidentals,
                counts_only=True,
            )

            def save_starts() -> None:
                """
                Apply the counts checked in Starting Accidentals.

                Examples
                --------
                Checking two flats allows signatures to begin with two
                printed flats.
                """
                cfg.starting_accidentals = self.starts_list.selected()
                self._refresh_summaries()
                self._save_and_emit()

            self.starts_list.changed.connect(save_starts)
            pages.append(
                subpage(
                    "Starting Accidentals",
                    body=scrolling(self.starts_list),
                    back=lambda: self._go(0),
                    fill=True,
                ),
            )

        if isinstance(cfg, settings.ScaleIdentificationSettings):
            pages.append(
                buttons_page(
                    cfg,
                    changed=self._save_and_emit,
                    back=lambda: self._go(0),
                ),
            )

            question_types = ChoiceChecklist(
                [("", [("key", "Key"), ("mode", "Mode")])],
                selected={"key", "mode"}
                if cfg.question_type == "combined"
                else {cfg.question_type},
            )

            def save_question_type() -> None:
                """
                Save the selected parts of the scale question.

                Examples
                --------
                Clear Key on the Question Type page to save Mode alone.
                """
                selected = question_types.selected()
                cfg.question_type = (
                    "combined"
                    if len(selected) == 2
                    else next(iter(selected), "combined")
                )
                self._save_and_emit()

            question_types.changed.connect(save_question_type)
            pages.append(
                subpage(
                    "Question Type",
                    body=question_types,
                    back=lambda: self._go(0),
                ),
            )

        for page in pages:
            self.stack.addWidget(page)
        self._refresh_summaries()

    def _refresh_summaries(self) -> None:
        """
        Update the menu's summaries: the clefs, how many scales and the
        keys.

        Examples
        --------
        >>> panel = KeySignatureSettingsPanel(
        ...     settings.KeySignatureSettings(
        ...         modes={"Dorian"}
        ...     )
        ... )
        >>> panel._refresh_summaries()
        >>> panel.modes_row.value.text()
        '1 of 7'
        """
        cfg = self.cfg
        self.clef_pictures.set_clefs(cfg.active_clefs())
        if isinstance(cfg, settings.ScaleIdentificationSettings):
            self.buttons_row.value.setText(cfg.button_mode.title())
        modes = cfg.active_modes()
        self.modes_row.value.setText(
            f"{len(modes)} of {len(settings.KEY_MODES)}",
        )
        if isinstance(
            cfg,
            (
                settings.ScaleConstructionSettings,
                settings.ScaleIdentificationSettings,
            ),
        ):
            self.scale_keys.update_summary(self.keys_row)
        else:
            show_keys(
                self.keys_row,
                diagram=self.keys_diagram,
                enabled=True,
                keys=set(cfg.active_keys()),
            )
        if isinstance(cfg, settings.OrderOfKeysSettings):
            allowed = cfg.available_starts()
            selected = cfg.starting_accidentals.intersection(allowed) or {0}
            cfg.starting_accidentals = selected
            for count, box in self.starts_list.boxes.items():
                box.blockSignals(True)
                box.setChecked(count in selected)
                box.blockSignals(False)
                box.setEnabled(count in allowed and selected != {count})
            summary = (
                self.starts_list.boxes[next(iter(selected))].text()
                if len(selected) == 1
                else f"{len(selected)} of 15"
            )
            self.starts_row.value.setText(summary)
        if self.staff_keys_row is not None and isinstance(
            cfg,
            (
                settings.ScaleConstructionSettings,
                settings.ScaleIdentificationSettings,
            ),
        ):
            show_keys(
                self.staff_keys_row,
                diagram=self.staff_keys_diagram,
                enabled=True,
                keys=set(cfg.active_staff_keys()),
            )

    def _persist(self) -> None:
        """
        Save the key signature settings, under the exercise's own name.

        Examples
        --------
        >>> panel = KeySignatureSettingsPanel(
        ...     settings.KeySignatureSettings(
        ...         clefs={"alto"}
        ...     )
        ... )
        >>> panel._persist()
        >>> str(store().value("keySignatures/clefs"))
        'alto'
        >>> store().setValue(
        ...     "keySignatures/clefs", "treble,bass"
        ... )
        """
        save_key_settings(self.cfg, prefix=self.prefix)

    def _modes_edited(self) -> None:
        """
        Take the checked scales into the settings, save them and say so.

        Examples
        --------
        >>> cfg = settings.KeySignatureSettings()
        >>> panel = KeySignatureSettingsPanel(cfg)
        >>> panel.modes.boxes["Dorian"].setChecked(True)
        >>> "Dorian" in cfg.modes
        True
        """
        self.cfg.modes = self.modes.selected()
        self._save_and_emit()

    def _staff_keys_edited(self) -> None:
        """
        Take the checked staff key signatures into the settings, save
        them and say so.

        Examples
        --------
        >>> cfg = settings.ScaleConstructionSettings()
        >>> panel = KeySignatureSettingsPanel(
        ...     cfg, prefix="doctestScales"
        ... )
        >>> # noinspection PyUnresolvedReferences
        >>> panel.staff_key_list.boxes[-2].setChecked(
        ...     True
        ... )
        >>> cfg.staff_keys == {0, -2}
        True
        >>> store().remove("doctestScales")
        """
        if (
            isinstance(
                self.cfg,
                (
                    settings.ScaleConstructionSettings,
                    settings.ScaleIdentificationSettings,
                ),
            )
            and self.staff_key_list is not None
        ):
            self.cfg.staff_keys = self.staff_key_list.selected()
            self._save_and_emit()

    def _octave_toggled(self, on: bool) -> None:
        """
        Switch naming the octave of the first note on or off, save it
        and say so.

        Parameters
        ----------
        on : bool
            Whether the scale has to start in the octave named.

        Examples
        --------
        >>> cfg = settings.ScaleConstructionSettings()
        >>> panel = KeySignatureSettingsPanel(
        ...     cfg, prefix="doctestScales"
        ... )
        >>> panel._octave_toggled(True)
        >>> cfg.octave
        True
        >>> store().remove("doctestScales")
        """
        if isinstance(self.cfg, settings.ScaleConstructionSettings):
            self.cfg.octave = on
            self._save_and_emit()

    def _steps_toggled(self, on: bool) -> None:
        """
        Switch marking the steps between the notes on or off, save it
        and say so.

        Parameters
        ----------
        on : bool
            Whether the steps are asked for.

        Examples
        --------
        >>> cfg = settings.ScaleConstructionSettings()
        >>> panel = KeySignatureSettingsPanel(
        ...     cfg, prefix="doctestScales"
        ... )
        >>> panel._steps_toggled(True)
        >>> cfg.steps
        True
        >>> store().remove("doctestScales")
        """
        if isinstance(self.cfg, settings.ScaleConstructionSettings):
            self.cfg.steps = on
            self._save_and_emit()

    def _keys_edited(self) -> None:
        """
        Take the checked key signatures into the settings, save them and
        say so.

        Examples
        --------
        >>> cfg = settings.KeySignatureSettings()
        >>> panel = KeySignatureSettingsPanel(cfg)
        >>> panel.key_list.boxes[2].setChecked(False)
        >>> 2 in cfg.keys
        False
        """
        self.cfg.keys = self.key_list.selected()
        if isinstance(
            self.cfg,
            (
                settings.ScaleConstructionSettings,
                settings.ScaleIdentificationSettings,
            ),
        ):
            self.cfg.minor_keys = self.scale_keys.minor_keys.selected()
        self._refresh_summaries()
        self._save_and_emit()


class NotationSettingsPanel(ExerciseSettingsPanel):
    """
    Choose the question type and the notation terms to practice.

    Examples
    --------
    >>> "Trill" in NotationSettingsPanel().terms.boxes
    True
    """

    def __init__(self) -> None:
        """
        Build the settings menu and its Question Type and Terms pages.

        Examples
        --------
        >>> len(
        ...     NotationSettingsPanel().terms.boxes
        ... ) == len(settings.NOTATION_TERMS)
        True
        """
        super().__init__()
        menu, menu_layout = self._build_menu()
        self.type_row = MenuRow("Question Type")
        self.type_row.clicked.connect(lambda: self.stack.slide_to(1))
        menu_layout.addWidget(self.type_row)
        self.terms_row = MenuRow("Terms")
        self.terms_row.clicked.connect(lambda: self.stack.slide_to(2))
        menu_layout.addWidget(self.terms_row)
        menu_layout.addStretch()
        self.stack.addWidget(menu)

        question_types = QWidget()
        type_layout = QVBoxLayout(question_types)
        type_layout.setContentsMargins(0, 0, 0, 0)
        self.types: dict[str, QRadioButton] = {}
        for key, label in settings.NOTATION_QUESTION_TYPES.items():
            radio = QRadioButton(label)
            type_layout.addWidget(radio)
            radio.setChecked(key == settings.notation.question_type)
            radio.toggled.connect(lambda checked: checked and self._save())
            self.types[key] = radio
        self.stack.addWidget(
            subpage(
                "Question Type",
                body=question_types,
                back=lambda: self.stack.slide_to(0),
            ),
        )

        terms_body = QWidget()
        terms_layout = QVBoxLayout(terms_body)
        terms_layout.setContentsMargins(0, 0, 0, 0)
        self.select_none = ToggleRow("Select none")
        self.select_none.switched.connect(
            lambda on: self._set_terms(
                set() if on else saved_notation_terms(),
            ),
        )
        terms_layout.addWidget(self.select_none)
        self.group_picker = FieldComboBox()
        self.group_picker.setAccessibleName("Notation term group")
        self.group_picker.setPlaceholderText("Select a group…")
        self.group_picker.addItems(["All terms", *CATALOG])
        self.group_picker.setCurrentIndex(-1)
        terms_layout.addWidget(self.group_picker)
        self.terms = ChoiceChecklist(
            [
                (group, [(term, term) for term in terms])
                for group, terms in CATALOG.items()
            ],
            selected=settings.notation.terms,
            allow_empty=True,
        )
        terms_layout.addWidget(scrolling(self.terms), 1)
        self.stack.addWidget(
            subpage(
                "Terms",
                body=terms_body,
                back=lambda: self.stack.slide_to(0),
                fill=True,
            ),
        )
        self.terms.changed.connect(self._save)
        self.group_picker.textActivated.connect(self._select_group)
        self._refresh_summaries()

    def _refresh_summaries(self) -> None:
        """
        Show the selected question type and term count on the settings
        menu.

        Examples
        --------
        >>> row = NotationSettingsPanel().type_row
        >>> label = settings.NOTATION_QUESTION_TYPES
        >>> row.value.text() == label[settings.notation.question_type]
        True
        """
        self.type_row.value.setText(
            settings.NOTATION_QUESTION_TYPES[settings.notation.question_type],
        )
        count = len(settings.notation.terms)
        self.select_none.setOn(count == 0)
        summary = (
            "All"
            if count == len(settings.NOTATION_TERMS)
            else f"{count} selected"
        )
        self.terms_row.value.setText(summary if count else "None")

    def _select_group(self, group: str) -> None:
        """
        Select all terms or only the terms of one group and apply the
        edit once.

        Parameters
        ----------
        group : str
            The group chosen in the picker.

        Examples
        --------
        >>> "Ornaments" in CATALOG
        True
        """
        selected = (
            settings.NOTATION_TERMS if group == "All terms" else CATALOG[group]
        )
        self.group_picker.setCurrentIndex(-1)
        self._set_terms(set(selected))

    def _set_terms(self, selected: set[str]) -> None:
        """
        Apply a bulk edit and request one new question.

        Parameters
        ----------
        selected : set of str
            The terms to check.

        Examples
        --------
        Select none clears every box in one edit.
        """
        for term, box in self.terms.boxes.items():
            box.blockSignals(True)
            box.setChecked(term in selected)
            box.blockSignals(False)
        self._save()

    def _save(self) -> None:
        """
        Save the question type and checked terms, then request a
        matching question.

        Examples
        --------
        >>> callable(NotationSettingsPanel()._save)
        True
        """
        settings.notation.question_type = next(
            key for key, radio in self.types.items() if radio.isChecked()
        )
        store().setValue(
            "notationIdentification/questionType",
            settings.notation.question_type,
        )
        selected = self.terms.selected()
        if remembered := selected or settings.notation.terms:
            store().setValue(
                "notationIdentification/terms",
                ",".join(sorted(remembered)),
            )
        store().setValue(
            "notationIdentification/selectNone",
            "false" if selected else "true",
        )
        settings.notation.terms = selected
        self._refresh_summaries()
        self.changed.emit()


class ClefBasicsSettingsPanel(ClefsPanel):
    """
    The settings of the clef basics exercise: a menu with two pages,
    Question Type and Clefs.

    Question Type chooses between Clef Construction (put a named clef on
    a blank staff) and Clef Identification (name the clef on
    a staff). Clefs lists the clefs in the same groups as the other
    exercises, with the French violin and subbass clefs, which
    only this exercise has, at the bottom. Edits are live: each changes
    the settings, saves them and emits `changed`.

    Attributes
    ----------
    cfg : ClefBasicsSettings
        The settings being edited.
    stack : SlideStack
        The menu and its two pages.
    types : dict of str to QRadioButton
        The choice of question, by key of `CLEF_QUESTION_TYPES`.
    boxes : dict of str to QCheckBox
        The checkbox of each clef.

    Examples
    --------
    >>> panel = ClefBasicsSettingsPanel(
    ...     settings.ClefBasicsSettings()
    ... )
    >>> panel.stack.count()  # the menu and two pages
    3
    """

    cfg: settings.ClefBasicsSettings

    def __init__(
        self,
        cfg: settings.ClefBasicsSettings,
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the panel for a set of settings.

        Parameters
        ----------
        cfg : ClefBasicsSettings
            The settings to edit.
        parent : QWidget or None, default None
            The widget that owns the panel. Keyword-only.

        Examples
        --------
        >>> panel = ClefBasicsSettingsPanel(
        ...     settings.ClefBasicsSettings(
        ...         clefs={"subbass"}
        ...     )
        ... )
        >>> (
        ...     panel.boxes["subbass"].isChecked(),
        ...     list(panel.boxes)[-2:],
        ... )
        (True, ['french', 'subbass'])
        """
        super().__init__(parent)
        self.cfg = cfg
        menu, mlay = self._build_menu()
        self.type_row = MenuRow("Question Type")
        self.type_row.clicked.connect(lambda _=False: self._go(1))
        mlay.addWidget(self.type_row)
        self.clefs_row = MenuRow("Clefs")
        self.clef_pictures = ClefPictures()
        self.clefs_row.attach(self.clef_pictures)
        self.clefs_row.clicked.connect(lambda _=False: self._go(2))
        mlay.addWidget(self.clefs_row)
        mlay.addStretch()
        self.types: dict[str, QRadioButton] = {}
        type_body = QWidget()
        type_lay = QVBoxLayout(type_body)
        type_lay.setContentsMargins(0, 0, 0, 0)
        type_group = QButtonGroup(self)
        for key, label in settings.CLEF_QUESTION_TYPES.items():
            radio = QRadioButton(label)
            radio.setChecked(key == cfg.active_type())
            radio.toggled.connect(
                lambda on, chosen=key: self._type_chosen(chosen, on=on),
            )
            type_group.addButton(radio)
            type_lay.addWidget(radio)
            self.types[key] = radio
        type_page = subpage(
            "Question Type",
            body=type_body,
            back=lambda: self._go(0),
        )
        self.boxes, clefs_page = clef_choice_page(
            settings.CLEF_BASICS_CLEFS,
            selected=cfg.clefs,
            edited=self._clefs_edited,
            back=lambda: self._go(0),
        )
        for page in (menu, type_page, clefs_page):
            self.stack.addWidget(page)
        self._refresh_summaries()

    def _refresh_summaries(self) -> None:
        """
        Show the kind of question and the clefs that are asked for in
        the menu's rows.

        Examples
        --------
        >>> panel = ClefBasicsSettingsPanel(
        ...     settings.ClefBasicsSettings(
        ...         clefs={"alto"}
        ...     )
        ... )
        >>> (
        ...     panel.clef_pictures.clefs,
        ...     panel.type_row.value.text(),
        ... )
        (['alto'], 'Construction')
        """
        self.clef_pictures.set_clefs(self.cfg.active_clefs())
        self.type_row.value.setText(
            settings.CLEF_QUESTION_TYPES[self.cfg.active_type()].removeprefix(
                "Clef ",
            ),
        )

    def _type_chosen(self, key: str, *, on: bool) -> None:
        """
        Take the kind of question chosen into the settings, save it and
        say so.

        Parameters
        ----------
        key : str
            A key of `CLEF_QUESTION_TYPES`.
        on : bool
            Whether its button was just switched on; the one switched
            off is ignored.

        Examples
        --------
        >>> cfg = settings.ClefBasicsSettings()
        >>> panel = ClefBasicsSettingsPanel(cfg)
        >>> panel.types["identification"].setChecked(
        ...     True
        ... )
        >>> (
        ...     cfg.question_type,
        ...     str(store().value("clefBasics/type")),
        ... )
        ('identification', 'identification')
        >>> store().remove("clefBasics")
        """
        if not on:
            return
        self.cfg.question_type = key
        self._save_and_emit()

    def _persist(self) -> None:
        """
        Save the clef basics settings.

        Examples
        --------
        >>> panel = ClefBasicsSettingsPanel(
        ...     settings.ClefBasicsSettings(
        ...         clefs={"alto"}
        ...     )
        ... )
        >>> panel._persist()
        >>> str(store().value("clefBasics/clefs"))
        'alto'
        >>> store().remove("clefBasics")
        """
        save_clef_basics(self.cfg)


def settings_inversion_names() -> tuple[str, ...]:
    """
    Return the inversions as they are written in the settings.

    Returns
    -------
    tuple of str
        'Root position', '1st inversion', '2nd inversion' and '3rd
        inversion'.

    Examples
    --------
    >>> settings_inversion_names()
    ('Root position', '1st inversion', '2nd inversion', '3rd inversion')
    """
    return tuple(n.capitalize() for n in INVERSION_NAMES)


class CircleSettingsPanel(ExerciseSettingsPanel):
    """
    The settings of the circle of fifths exercise: which kinds of
    question to ask, and the colors of the circle.

    The menu has two rows. Questions opens a page of switches. Colors
    opens a page of color schemes to choose from, with a
    button to make one of your own, which opens an editor. Edits are
    live: each changes the settings and saves them. A new kind
    of question emits `changed`, and a new color scheme emits
    `restyled`, which keeps the question.

    Attributes
    ----------
    cfg : CircleSettings
        The settings being edited.
    stack : SlideStack
        The menu and its pages: the menu, the questions, the color
        schemes and the editor of a scheme.
    questions_row : MenuRow
        The menu row for the questions.
    colors_row : MenuRow
        The menu row for the colors; its value is the name of the chosen
        scheme.
    questions : ChoiceChecklist
        The kinds of question: relative major, relative minor and Roman
        numerals.
    schemes : SchemePage
        The color schemes.
    editor : SchemeEditor
        The editor of a scheme of your own.

    Examples
    --------
    >>> panel = CircleSettingsPanel(
    ...     settings.CircleSettings()
    ... )
    >>> (
    ...     panel.questions_row.value.text(),
    ...     panel.colors_row.value.text(),
    ... )
    ('3 of 3', 'Cyan to indigo')
    """

    def __init__(
        self,
        cfg: settings.CircleSettings,
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the panel for a set of settings.

        Parameters
        ----------
        cfg : CircleSettings
            The settings to edit.
        parent : QWidget or None, default None
            The widget that owns the panel. Keyword-only.

        Examples
        --------
        >>> CircleSettingsPanel(
        ...     settings.CircleSettings()
        ... # the menu, the questions, the colors and the editor
        ... ).stack.count()
        4
        """
        super().__init__(parent)
        self.cfg = cfg
        menu, mlay = self._build_menu()
        self.questions_row = MenuRow("Questions")
        self.questions_row.clicked.connect(lambda: self._go(1))
        mlay.addWidget(self.questions_row)
        self.colors_row = MenuRow("Colors")
        self.colors_row.clicked.connect(lambda: self._go(2))
        mlay.addWidget(self.colors_row)
        mlay.addStretch()
        self.questions = ChoiceChecklist(
            [("", list(settings.CIRCLE_QUESTIONS.items()))],
            selected=cfg.questions,
        )
        self.questions.changed.connect(self._questions_edited)
        note = QLabel(
            "Relative major: a minor key is shown, and you name its major. "
            "Relative minor: the other way around. Roman "
            "numerals: a key is shown with its six chords lit, and you give"
            " the numeral of one. One of the checked kinds is "
            "asked at random.",
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: gray;")
        body = QWidget()
        blay = QVBoxLayout(body)
        blay.setContentsMargins(0, 0, 0, 0)
        blay.addWidget(self.questions)
        blay.addWidget(note)
        self.schemes = SchemePage()
        self.schemes.chosen.connect(self._scheme_chosen)
        self.schemes.new.connect(self._new_scheme)
        self.schemes.edit_asked.connect(self._edit_scheme)
        self.editor = SchemeEditor()
        self.editor.saved.connect(self._scheme_saved)
        self.editor.deleted.connect(self._scheme_deleted)
        self.editor.canceled.connect(lambda: self._go(2))
        pages = (
            menu,
            subpage("Questions", body=body, back=lambda: self._go(0)),
            subpage(
                "Colors",
                body=scrolling(self.schemes),
                back=lambda: self._go(0),
                fill=True,
            ),
            subpage(
                "Your colors",
                body=scrolling(self.editor),
                back=lambda: self._go(2),
                fill=True,
            ),
        )
        for page in pages:
            self.stack.addWidget(page)
        self.schemes.load(current=cfg.scheme, customs=cfg.customs)
        self._refresh_summaries()

    def _refresh_summaries(self) -> None:
        """
        Update the menu's summaries: how many kinds of question are on,
        and the name of the color scheme.

        Examples
        --------
        >>> panel = CircleSettingsPanel(
        ...     settings.CircleSettings(
        ...         questions={"minor"},
        ...         scheme="midnight",
        ...     )
        ... )
        >>> panel._refresh_summaries()
        >>> (
        ...     panel.questions_row.value.text(),
        ...     panel.colors_row.value.text(),
        ... )
        ('1 of 3', 'Midnight')
        """
        self.questions_row.value.setText(
            f"{len(self.cfg.active_questions())}"
            " of "
            f"{len(settings.CIRCLE_QUESTIONS)}",
        )
        self.colors_row.value.setText(self.cfg.active_scheme().name)

    def _questions_edited(self) -> None:
        """
        Take the checked kinds of question into the settings, save them
        and say so.

        Examples
        --------
        >>> cfg = settings.CircleSettings()
        >>> panel = CircleSettingsPanel(cfg)
        >>> panel.questions.boxes["numeral"].setChecked(
        ...     False
        ... )
        >>> sorted(cfg.questions)
        ['major', 'minor']
        >>> store().remove("circle")
        """
        self.cfg.questions = self.questions.selected()
        save_circle(self.cfg)
        self.changed.emit()

    def _scheme_chosen(self, key: str) -> None:
        """
        Use a color scheme: take it into the settings, save it and say
        so.

        Parameters
        ----------
        key : str
            The key of the scheme that was clicked.

        Examples
        --------
        >>> cfg = settings.CircleSettings()
        >>> panel = CircleSettingsPanel(cfg)
        >>> panel._scheme_chosen("ember")
        >>> (
        ...     cfg.scheme,
        ...     panel.schemes.thumbs[
        ...         "ember"
        ...     ].isChecked(),
        ...     panel.colors_row.value.text(),
        ... )
        ('ember', True, 'Ember')
        >>> store().remove("circle")
        """
        self.cfg.scheme = key
        save_circle(self.cfg)
        self.schemes.load(current=key, customs=self.cfg.customs)
        self._refresh_summaries()
        self.restyled.emit()

    def _new_scheme(self) -> None:
        """
        Open the editor on a new scheme of your own.

        Examples
        --------
        >>> panel = CircleSettingsPanel(
        ...     settings.CircleSettings()
        ... )
        >>> panel._new_scheme()
        >>> (
        ...     panel.editor.record()["id"],
        ...     panel.editor.delete_button.isHidden(),
        ... )
        ('custom-1', True)
        """
        self.editor.load(None, taken=self.cfg.customs)
        self._go(3)

    def _edit_scheme(self, key: str) -> None:
        """
        Open the editor on one of your schemes.

        Parameters
        ----------
        key : str
            Its key.

        Examples
        --------
        >>> from alto.circle_schemes import record_of
        >>> mine = record_of(
        ...     "custom-1",
        ...     name="Mine",
        ...     mode="single",
        ...     colors=["#2f6bd0"],
        ... )
        >>> panel = CircleSettingsPanel(
        ...     settings.CircleSettings(customs=[mine])
        ... )
        >>> panel._edit_scheme("custom-1")
        >>> (
        ...     panel.editor.name.text(),
        ...     panel.editor.delete_button.isHidden(),
        ... )
        ('Mine', False)
        """
        for record in self.cfg.customs:
            if record["id"] == key:
                self.editor.load(record, taken=self.cfg.customs)
                self._go(3)
                return

    def _scheme_saved(self, record: CustomRecord) -> None:
        """
        Keep a scheme of your own, use it, save it and go back to the
        list.

        Parameters
        ----------
        record : CustomRecord
            The scheme from the editor: a new one is added, one that has
            the same key is replaced.

        Examples
        --------
        >>> cfg = settings.CircleSettings()
        >>> panel = CircleSettingsPanel(cfg)
        >>> panel._new_scheme()
        >>> panel._scheme_saved(panel.editor.record())
        >>> (
        ...     cfg.scheme,
        ...     [r["name"] for r in cfg.customs],
        ...     "custom-1" in panel.schemes.thumbs,
        ... )
        ('custom-1', ['My colors'], True)
        >>> store().remove("circle")
        """
        others = [
            existing
            for existing in self.cfg.customs
            if existing["id"] != record["id"]
        ]
        self.cfg.customs = sorted(
            [*others, record],
            key=lambda item: item["id"],
        )
        self.cfg.scheme = record["id"]
        save_circle(self.cfg)
        self.schemes.load(current=record["id"], customs=self.cfg.customs)
        self._refresh_summaries()
        self.restyled.emit()
        self.stack.setCurrentIndex(3)
        self._go(2)

    def _scheme_deleted(self, key: str) -> None:
        """
        Delete a scheme of your own; if it was the one in use, go back
        to the default.

        Parameters
        ----------
        key : str
            Its key.

        Examples
        --------
        >>> from alto.circle_schemes import record_of
        >>> mine = record_of(
        ...     "custom-1",
        ...     name="Mine",
        ...     mode="single",
        ...     colors=["#2f6bd0"],
        ... )
        >>> cfg = settings.CircleSettings(
        ...     customs=[mine], scheme="custom-1"
        ... )
        >>> panel = CircleSettingsPanel(cfg)
        >>> panel._scheme_deleted("custom-1")
        >>> cfg.customs, cfg.scheme
        ([], 'cyan-indigo')
        >>> store().remove("circle")
        """
        self.cfg.customs = [
            record for record in self.cfg.customs if record["id"] != key
        ]
        if self.cfg.scheme == key:
            self.cfg.scheme = DEFAULT_SCHEME
        save_circle(self.cfg)
        self.schemes.load(current=self.cfg.scheme, customs=self.cfg.customs)
        self._refresh_summaries()
        self.restyled.emit()
        self._go(2)


def settings_panel_for(
    exercise: Exercise,
    *,
    learner: Learner | None = None,
) -> ExerciseSettingsPanel:
    """
    Return the settings panel for an exercise.

    Parameters
    ----------
    exercise : Exercise
        The exercise.
    learner : Learner or None
        Profile whose calendar limits can be overridden.

    Returns
    -------
    ExerciseSettingsPanel
        A panel with the exercise options and the shared Next Question
        setting.

    Examples
    --------
    >>> from alto.exercises.library import (
    ...     IntervalNames,
    ...     NoteNames,
    ... )
    >>> type(
    ...     settings_panel_for(NoteNames())
    ... ).__name__
    'NoteNameSettingsPanel'
    >>> type(
    ...     settings_panel_for(IntervalNames())
    ... ).__name__
    'IntervalSettingsPanel'
    """
    panel = _exercise_panel(exercise)

    if panel is None:
        panel = ExerciseSettingsPanel()
        stack = panel.stack = SlideStack()
        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(stack)
        menu = QWidget()
        layout = QVBoxLayout(menu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("<h3>Settings</h3>"))
        layout.addStretch()
        stack.addWidget(menu)
    else:
        stack = panel.stack
        menu = stack.widget(0)
        assert menu is not None
        layout = menu.layout()
        assert isinstance(layout, QVBoxLayout)
    if isinstance(exercise, BeatIdentification):

        def save_component(value: str) -> None:
            """
            Apply the rhythm component to practice and future sessions.

            Parameters
            ----------
            value : str
                Selected answer format.

            Examples
            --------
            Choosing Beat and meter opens a classification question.
            """
            settings.beat_rhythm_component = value
            store().setValue("beatIdentification/rhythmComponent", value)
            panel.changed.emit()

        _add_radio_option(
            panel,
            layout=layout,
            title="Rhythm Component",
            choices=settings.BEAT_RHYTHM_COMPONENTS,
            selected=settings.beat_rhythm_component,
            changed=save_component,
        )
    if isinstance(exercise, RythmicEquations):
        _add_rhythm_options(panel, layout=layout)
    if isinstance(exercise, (BeatIdentification, BeatConstruction)):
        prefix = (
            "beatIdentification"
            if isinstance(exercise, BeatIdentification)
            else "beatConstruction"
        )
        _add_beat_note_types(panel, layout=layout, prefix=prefix)
        tuplets = ToggleRow("Tuplets")
        tuplets.setOn(settings.beat_tuplets[prefix])
        tuplets.setToolTip(
            "Occasionally include numbered groups, most often triplets"
            if prefix == "beatIdentification"
            else "Include simple-meter triplets and compound-meter duplets",
        )
        layout.insertWidget(layout.count() - 1, tuplets)

        def save_tuplets(on: bool) -> None:
            """
            Save this exercise's tuplet switch and refresh its rhythm.

            Parameters
            ----------
            on : bool
                Whether numbered tuplet groups can appear.

            Examples
            --------
            Turning Tuplets on allows three eighths in one quarter beat.
            """
            settings.beat_tuplets[prefix] = on
            save_bool(store(), key=f"{prefix}/tuplets", value=on)
            panel.changed.emit()

        tuplets.switched.connect(save_tuplets)
    if isinstance(exercise, ChoiceExercise):
        _add_choice_buttons(panel, exercise=exercise, layout=layout)

    key = f"nextQuestion/{type(exercise).__name__}"
    modes = ("Immediately", "Wait", "After Animation")
    saved_mode = text_value(store(), key=key, default=panel.next_question_mode)
    if saved_mode in modes:
        panel.next_question_mode = saved_mode

    def select(mode: str) -> None:
        """
        Save how this exercise proceeds after a correct answer.

        Parameters
        ----------
        mode : str
            The selected radio button's label.

        Examples
        --------
        Choosing Wait keeps the next correct answer on screen for
        review.
        """
        panel.next_question_mode = mode
        store().setValue(key, mode)

    panel.next_question_row, panel.next_question_choices = _add_radio_option(
        panel,
        layout=layout,
        title="Next Question",
        choices=modes,
        selected=panel.next_question_mode,
        changed=select,
    )
    if learner is not None:
        panel.limits_editor = DailyLimitsEditor(
            learner,
            exercise=type(exercise).__name__,
        )
        panel.limits_row = MenuRow("Daily Limits")
        layout.insertWidget(layout.count() - 1, panel.limits_row)
        panel.limits_page = stack.addWidget(
            subpage(
                "Daily Limits",
                body=panel.limits_editor,
                back=lambda: stack.slide_to(0),
            ),
        )
        panel.limits_row.clicked.connect(
            lambda: stack.slide_to(panel.limits_page),
        )
        panel.limits_editor.changed.connect(panel.changed)
        panel.refresh_limits(
            learner.mode,
            self_grading=learner.mode in CALENDAR_SCHEDULERS
            and learner.self_grading,
        )
    stack.removeWidget(menu)
    stack.insertWidget(0, scrolling(menu))
    stack.setCurrentIndex(0)
    return panel


def _add_beat_note_types(
    panel: ExerciseSettingsPanel,
    *,
    layout: QVBoxLayout,
    prefix: str,
) -> None:
    """
    Add an illustrated checklist of durations used in written rhythms.

    Parameters
    ----------
    panel : ExerciseSettingsPanel
        Settings panel for the exercise.
    layout : QVBoxLayout
        Main settings menu.
    prefix : str
        Preference key for the exercise.

    Examples
    --------
    Selecting only Whole gives one whole note or rest per measure.
    """
    row = MenuRow("Note Type", tall=True)
    selected = settings.beat_note_types[prefix]
    types = settings.BEAT_NOTE_TYPES
    choices = ChoiceChecklist(
        [("", [(v, RHYTHM_SYMBOL_NAMES[v]) for v in types])],
        selected=selected,
    )
    preview = ValuePictures([v for v in types if v in selected])
    row.attach(preview)
    for value in types:
        ValuePictures([value], scale=1.25, center_stemless=True).label_button(
            choices.boxes[value],
        )
    row.value.setText(f"{len(selected)} selected")
    layout.insertWidget(layout.count() - 1, row)
    page = panel.stack.addWidget(
        subpage(
            "Note Type",
            body=scrolling(choices),
            back=lambda: panel.stack.slide_to(0),
            fill=True,
        ),
    )
    row.clicked.connect(lambda: panel.stack.slide_to(page))

    def save() -> None:
        """
        Apply the checked durations and remember them for next time.

        Examples
        --------
        Checking Half makes half notes available in this exercise.
        """
        values = choices.selected()
        settings.beat_note_types[prefix] = values
        preview.set_values([v for v in types if v in values])
        store().setValue(f"{prefix}/noteTypes", ",".join(sorted(values)))
        row.value.setText(f"{len(values)} selected")
        panel.changed.emit()

    choices.changed.connect(save)


def _add_radio_option(
    panel: ExerciseSettingsPanel,
    *,
    layout: QVBoxLayout,
    title: str,
    choices: tuple[str, ...],
    selected: str,
    changed: Callable[[str], None],
) -> tuple[MenuRow, QWidget]:
    """
    Add a settings row and a submenu of mutually exclusive choices.

    Parameters
    ----------
    panel : ExerciseSettingsPanel
        Panel that owns the submenu.
    layout : QVBoxLayout
        Main settings menu.
    title : str
        Label for the row and submenu.
    choices : tuple of str
        Radio button labels in display order.
    selected : str
        Current choice shown on the row.
    changed : callable
        Apply the newly selected choice.

    Returns
    -------
    tuple of MenuRow and QWidget
        The menu row and the group of radio buttons.

    Examples
    --------
    Next Question uses this submenu to choose the pace of practice.
    """
    stack = panel.stack
    row = MenuRow(title)
    row.value.setText(selected)
    layout.insertWidget(layout.count() - 1, row)
    body = QWidget()
    options = QVBoxLayout(body)
    options.setContentsMargins(0, 0, 0, 0)

    def select(value: str) -> None:
        """
        Update the summary and apply the selected option.

        Parameters
        ----------
        value : str
            Selected radio button label.

        Examples
        --------
        Choosing Wait also displays Wait on the Next Question row.
        """
        row.value.setText(value)
        changed(value)

    for choice in choices:
        radio = QRadioButton(choice)
        options.addWidget(radio)
        radio.setChecked(choice == selected)
        radio.toggled.connect(
            lambda on, value=choice: on and select(value),
        )
    page = stack.addWidget(
        subpage(title, body=body, back=lambda: stack.slide_to(0)),
    )
    row.clicked.connect(lambda: stack.slide_to(page))
    return row, body


def _rhythm_operator_summary() -> str:
    """
    Describe the selected signs and operator counts.

    Returns
    -------
    str
        The value shown on the Operators menu row.

    Examples
    --------
    >>> "1 left" in _rhythm_operator_summary()
    True
    """
    lines = []
    for side in ("left", "right"):
        count = getattr(settings, f"rhythm_{side}_operators")
        selected = getattr(settings, f"rhythm_{side}_signs")
        signs = " ".join(
            op for op in settings.RHYTHM_OPERATORS if op in selected
        )
        lines.append(f"{count} {side} · {signs}")
    return "\n".join(lines)


def _rhythm_selection_summary(title: str, *, selected: set[str]) -> str:
    """
    Format the current selection on a rhythm settings row.

    Parameters
    ----------
    title : str
        The option shown on the row.
    selected : set of str
        Enabled choices.

    Returns
    -------
    str
        Summary for this option.

    Examples
    --------
    >>> _rhythm_selection_summary("Answer Type", selected={"symbol"})
    'Symbol'
    """
    if title == "Answer Type":
        return ", ".join(
            label
            for key, label in settings.RHYTHM_ANSWER_TYPES.items()
            if key in selected
        )
    return str(len(selected))


def _operator_options(
    panel: ExerciseSettingsPanel,
    *,
    menu: MenuRow,
) -> QWidget:
    """
    Build a count field and a sign checklist for each side.

    Parameters
    ----------
    panel : ExerciseSettingsPanel
        Panel that refreshes the exercise when a setting changes.
    menu : MenuRow
        Row whose summary includes the counts.

    Returns
    -------
    QWidget
        Operator settings grouped by side of the equals sign.

    Examples
    --------
    A right count of two puts two signs after the equals sign.
    """
    body = QWidget()
    grid = QGridLayout(body)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setColumnStretch(0, 1)

    for index, side in enumerate(("left", "right")):
        title = f"{side.title()} operators"
        label = QLabel(title)
        field = QSpinBox()
        field.setAccessibleName(title)
        field.setRange(0, settings.MAX_RHYTHM_OPERATORS)
        field.setValue(getattr(settings, f"rhythm_{side}_operators"))
        field.setKeyboardTracking(False)
        label.setBuddy(field)
        grid.addWidget(label, 2 * index, 0)
        grid.addWidget(field, 2 * index, 1)
        choices = ChoiceChecklist(
            [("", list(settings.RHYTHM_OPERATORS.items()))],
            selected=getattr(settings, f"rhythm_{side}_signs"),
        )
        choices.setAccessibleName(title)
        for box in choices.boxes.values():
            box.setAccessibleName(f"{side.title()} {box.text()}")
        grid.addWidget(choices, 2 * index + 1, 0, 1, 2)

        def save(
            *,
            side: str = side,
            field: QSpinBox = field,
            choices: ChoiceChecklist = choices,
        ) -> None:
            """
            Apply this side's count and signs to the next question.

            Parameters
            ----------
            side : str
                Side of the equals sign.
            field : QSpinBox
                Operator count for this side.
            choices : ChoiceChecklist
                Signs allowed on this side.

            Examples
            --------
            Checking Division on the right updates the right selection.
            """
            count = field.value()
            signs = choices.selected()
            setattr(settings, f"rhythm_{side}_operators", count)
            setattr(settings, f"rhythm_{side}_signs", signs)
            saved = store()
            saved.setValue(f"rythmicEquations/{side}Operators", count)
            saved.setValue(
                f"rythmicEquations/{side}Signs",
                ",".join(sorted(signs)),
            )
            menu.value.setText(_rhythm_operator_summary())
            panel.changed.emit()

        field.valueChanged.connect(save)
        choices.changed.connect(save)
    return body


def _add_rhythm_options(
    panel: ExerciseSettingsPanel,
    *,
    layout: QVBoxLayout,
) -> None:
    """
    Add checklists for the operations and note symbols used in rhythm
    equations.

    Parameters
    ----------
    panel : ExerciseSettingsPanel
        The pane to extend.
    layout : QVBoxLayout
        The main settings menu. Keyword-only.

    Examples
    --------
    Rythmic Equations offers Operators and Symbols alongside the shared
    Buttons page.
    """
    stack = panel.stack

    def save_switch(on: bool, *, key: str) -> None:
        """
        Save a rhythm switch and refresh the question.

        Parameters
        ----------
        on : bool
            Whether to enable the option.
        key : str
            Rhythm setting controlled by this switch.

        Examples
        --------
        Enabling Ties can show two notes connected by a curved line.
        """
        setattr(settings, f"rhythm_{key}", on)
        store().setValue(f"rythmicEquations/{key}", "true" if on else "false")
        panel.changed.emit()

    for key, tip in (
        ("ties", "Show two tied notes as one duration"),
        ("beams", "Show two beamed notes as one duration"),
        (
            "parentheses",
            "Group operations on sides with two or more operators",
        ),
    ):
        switch = ToggleRow(key.title())
        switch.setOn(getattr(settings, f"rhythm_{key}"))
        switch.setToolTip(tip)
        switch.switched.connect(lambda on, key=key: save_switch(on, key=key))
        layout.insertWidget(layout.count() - 1, switch)
    operators = MenuRow("Operators")
    operators.value.setText(_rhythm_operator_summary())
    layout.insertWidget(layout.count() - 1, operators)
    operator_page = stack.addWidget(
        subpage(
            "Operators",
            body=scrolling(_operator_options(panel, menu=operators)),
            back=lambda: stack.slide_to(0),
            fill=True,
        ),
    )
    operators.clicked.connect(lambda: stack.slide_to(operator_page))
    for title, attribute, key, labels in (
        (
            "Answer Type",
            "rhythm_answer_types",
            "answerTypes",
            settings.RHYTHM_ANSWER_TYPES,
        ),
        ("Symbols", "rhythm_symbols", "symbols", RHYTHM_SYMBOL_NAMES),
    ):
        row = MenuRow(title)
        selected = getattr(settings, attribute)
        positions: dict[object, tuple[int, int]] | None = None
        if title == "Symbols":
            notes = [name for name in labels if f"{name}-rest" in labels]
            positions = {
                symbol: (row_index, column)
                for row_index, name in enumerate(notes)
                for column, symbol in enumerate((name, f"{name}-rest"))
            }
            dotted = [name for name in labels if name.startswith("dotted-")]
            positions.update(
                {
                    name: (len(notes) + index, 0)
                    for index, name in enumerate(dotted)
                },
            )
        choices = ChoiceChecklist(
            [("", list(labels.items()))],
            selected=selected,
            positions=positions,
        )
        if title == "Symbols":
            for name, label in labels.items():
                box = choices.boxes[name]
                box.setAccessibleName(label)
                box.setText("")
                box.setIcon(ValuePictures.icon(name, scale=1.0))
                box.setIconSize(QSize(px(18), px(40)))
        row.value.setText(_rhythm_selection_summary(title, selected=selected))
        layout.insertWidget(layout.count() - 1, row)
        page = stack.addWidget(
            subpage(
                title,
                body=scrolling(choices),
                back=lambda: stack.slide_to(0),
                fill=True,
            ),
        )
        row.clicked.connect(
            lambda _checked=False, index=page: stack.slide_to(index),
        )

        def save(
            *,
            choices: ChoiceChecklist = choices,
            row: MenuRow = row,
            attribute: str = attribute,
            title: str = title,
            key: str = key,
        ) -> None:
            """
            Save the edited checklist and ask a new question.

            Parameters
            ----------
            choices : ChoiceChecklist
                The edited checklist.
            row : MenuRow
                The corresponding menu entry.
            attribute : str
                The settings attribute to update.
            title : str
                The settings page name.
            key : str
                Storage key for this option.

            Examples
            --------
            Checking Number adds questions with numeric answers.
            """
            selected = choices.selected()
            setattr(settings, attribute, selected)
            store().setValue(
                f"rythmicEquations/{key}",
                ",".join(sorted(selected)),
            )
            row.value.setText(
                _rhythm_selection_summary(title, selected=selected),
            )
            panel.changed.emit()

        choices.changed.connect(save)


def _add_choice_buttons(
    panel: ExerciseSettingsPanel,
    *,
    exercise: ChoiceExercise,
    layout: QVBoxLayout,
) -> None:
    """
    Append the Buttons row and its page to a multiple-choice exercise.

    Parameters
    ----------
    panel : ExerciseSettingsPanel
        The exercise settings panel.
    exercise : ChoiceExercise
        The exercise that owns the button preferences.
    layout : QVBoxLayout
        The settings menu containing the row.

    Examples
    --------
    Chord Quality uses this row to limit the number of answers.
    """
    stack = panel.stack
    cfg = exercise.button_settings()
    row = panel.choice_buttons_row = MenuRow("Buttons")
    row.value.setText(cfg.button_mode.title())
    layout.insertWidget(layout.count() - 1, row)

    def save() -> None:
        """
        Save this exercise's selection and apply it to the next
        question.

        Examples
        --------
        Editing the count in Note Identification leaves the keyboard
        exercise's count alone.
        """
        saved = store()
        prefix = f"answerButtons/{type(exercise).__name__}"
        saved.setValue(f"{prefix}/mode", cfg.button_mode)
        saved.setValue(f"{prefix}/count", cfg.button_count)
        row.value.setText(cfg.button_mode.title())
        panel.changed.emit()

    page = stack.addWidget(
        buttons_page(cfg, changed=save, back=lambda: stack.slide_to(0)),
    )
    row.clicked.connect(lambda: stack.slide_to(page))


# The panel of each built-in exercise, by its class. A subclass of one
# of these gets the same panel.
PANELS: dict[type[Exercise], Callable[[], ExerciseSettingsPanel]] = {
    NotationIdentification: NotationSettingsPanel,
    NoteNames: lambda: NoteNameSettingsPanel(settings.note_names),
    IntervalConstruction: lambda: IntervalSettingsPanel(
        settings.interval_construction,
        prefix="intervalConstruction",
    ),
    IntervalNames: lambda: IntervalSettingsPanel(settings.intervals),
    KeyboardIntervals: lambda: KeyboardIntervalSettingsPanel(
        settings.keyboard_intervals,
    ),
    KeyboardNotes: lambda: KeyboardSettingsPanel(settings.keyboard),
    NoteConstruction: lambda: NoteConstructionSettingsPanel(
        settings.construction,
    ),
    ArpeggioNames: lambda: ArpeggioSettingsPanel(settings.arpeggio),
    KeySignatures: lambda: KeySignatureSettingsPanel(settings.key_signatures),
    OrderOfKeys: lambda: KeySignatureSettingsPanel(
        settings.order_of_keys,
        prefix="orderOfKeys",
        keys_title="Key Signatures",
    ),
    KeySignatureConstruction: lambda: KeySignatureSettingsPanel(
        settings.key_construction,
        prefix="keyConstruction",
    ),
    ScaleIdentification: lambda: KeySignatureSettingsPanel(
        settings.scale_identification,
        prefix="scaleIdentification",
    ),
    ScaleConstruction: lambda: KeySignatureSettingsPanel(
        settings.scale_construction,
        prefix="scaleConstruction",
    ),
    ClefBasics: lambda: ClefBasicsSettingsPanel(settings.clef_basics),
    CircleOfFifths: lambda: CircleSettingsPanel(settings.circle),
}


def _exercise_panel(exercise: Exercise) -> ExerciseSettingsPanel | None:
    """
    Build the exercise-specific settings pages.

    A plugin exercise gets a panel made from the controls it declares; a
    built-in one gets its entry in `PANELS`, or the entry of
    the nearest class it is a subclass of.

    Parameters
    ----------
    exercise : Exercise
        The exercise being opened.

    Returns
    -------
    ExerciseSettingsPanel or None
        Its specialized panel, if it has one.

    Examples
    --------
    >>> type(_exercise_panel(NoteNames())).__name__
    'NoteNameSettingsPanel'
    >>> class Drill(KeyboardNotes):
    ...     name = "Drill"
    >>> type(_exercise_panel(Drill())).__name__
    'KeyboardSettingsPanel'
    >>> from alto.exercises.library import (
    ...     ChordQualities,
    ... )
    >>> _exercise_panel(ChordQualities()) is None
    True
    """
    if isinstance(exercise, PackExercise) and exercise.controls:
        return (
            PackKeyboardSettingsPanel(type(exercise))
            if exercise.is_keyboard
            else PackSettingsPanel(type(exercise))
        )
    build = next(
        (PANELS[cls] for cls in type(exercise).__mro__ if cls in PANELS),
        None,
    )
    return None if build is None else build()
