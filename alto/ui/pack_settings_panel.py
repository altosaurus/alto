"""
The settings panels of exercises that plugins add.

A plugin exercise declares the controls it wants (a range, a sound, accidentals ...) and gets a panel built from them, like
the built-in exercises' panels. Its options are saved under the exercise's name.

Examples
--------
>>> COMMIT_DELAY_MS
150
"""

from __future__ import annotations

from collections.abc import (
    Callable,
)

from PySide6.QtCore import (
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QHideEvent,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from alto import settings
from alto.audio import INSTRUMENT_BY_KEY
from alto.exercises.packs import PackExercise
from alto.settings import (
    key_name,
)
from alto.ui.exercise_settings import (
    save_pack_options,
)
from alto.ui.keyboard import KeyboardSpan
from alto.ui.pictures import (
    RangePictures,
)
from alto.ui.settings_menu import (
    ROW_PICTURE_WIDTH,
    ChoiceChecklist,
    ExerciseSettingsPanel,
    MenuRow,
    SlideStack,
    StaffRangePanel,
    ToggleRow,
    arrow_button,
    scrolling,
    subpage,
)
from alto.ui.zoom import (
    px,
)

COMMIT_DELAY_MS = 150  # how long a drag must pause before its range is saved and a new question is asked


def _pack_sound_page(
    exercise: type[PackExercise],
    *,
    title: str,
    chosen: Callable[[str], None],
    back: Callable[[], object],
) -> tuple[QWidget, Callable[[str], str]]:
    """
    Build the page where a learner picks the instrument that sounds in a plugin's exercise.

    The plugin's own instruments are listed first, then other instruments of the same kind, then every other installed
    instrument, each group under its own heading.

    Parameters
    ----------
    exercise : type of PackExercise
        The exercise, which says which instruments to offer and in what order.
    title : str
        The page's title, the plugin's label for the sound setting. Keyword-only.
    chosen : callable
        Called with the key of the instrument the learner picks. Keyword-only.
    back : callable
        Called when the Back button is pressed. Keyword-only.

    Returns
    -------
    tuple of QWidget and callable
        The page, and a function that marks an instrument key as the current choice and returns its label.

    Examples
    --------
    >>> class Demo(PackExercise):
    ...     pack_name = "Demo"
    ...     instruments = {}
    >>> page, show = _pack_sound_page(Demo, title="Sound", chosen=print, back=print)
    >>> show("piano")
    'Piano'
    """
    body = QWidget()
    layout = QVBoxLayout(body)
    layout.setContentsMargins(0, 0, 0, 0)
    group = QButtonGroup(body)
    radios: dict[str, QRadioButton] = {}
    labels: dict[str, str] = {}
    for heading, items in exercise.sound_options():
        layout.addWidget(QLabel(f"<b>{heading}</b>"))
        for key, label in items:
            radio = QRadioButton(label)
            group.addButton(radio)
            radio.toggled.connect(lambda on, picked=key: chosen(picked) if on else None)
            layout.addWidget(radio)
            radios[key], labels[key] = radio, label
    layout.addStretch()

    def show(key: str) -> str:
        """
        Mark an instrument as the one chosen.

        Parameters
        ----------
        key : str
            The instrument's key.

        Returns
        -------
        str
            The instrument's label, or its key when it is not listed.

        Examples
        --------
        Showing the plugin's own sound checks its radio button.
        """
        for name, radio in radios.items():
            radio.blockSignals(True)
            radio.setChecked(name == key)
            radio.blockSignals(False)
        return labels.get(key) or (INSTRUMENT_BY_KEY[key].label if key in INSTRUMENT_BY_KEY else key)

    return subpage(title, body=scrolling(body), back=back, fill=True), show


class PackSettingsPanel(StaffRangePanel):
    """
    The settings a plugin declared for one of its note exercises, drawn from a fixed set of controls.

    The plugin picks which controls appear: a switch for its own sound, a range selector on one clef, and switches for
    accidentals and for the octave. Edits are live: each changes the options, saves them and emits `changed`.

    Attributes
    ----------
    exercise : type of PackExercise
        The exercise whose options are edited.
    cfg : PackExerciseSettings
        The options being edited.
    range_row : MenuRow
        The Range row, present only if the plugin declared a range.
    sound_row : ToggleRow or None
        The plugin sound switch, if declared.
    accidentals_row : ToggleRow or None
        The accidentals switch, if declared.
    octave_row : ToggleRow or None
        The octave switch, if declared.

    Examples
    --------
    >>> class Demo(PackExercise):
    ...     controls = {"octave": True}
    >>> panel = PackSettingsPanel(Demo)
    >>> panel.octave_row is not None and not hasattr(panel, "range_row")
    True
    >>> _ = settings.pack_exercises.pop("Demo")
    """

    range_index = 1

    def __init__(
        self,
        exercise: type[PackExercise],
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the menu and, if the plugin offers a range, its page.

        Parameters
        ----------
        exercise : type of PackExercise
            The exercise to edit.
        parent : QWidget or None, default None
            The widget that owns the panel. Keyword-only.

        Examples
        --------
        >>> class Sounds(PackExercise):
        ...     controls = {"sound": "Demo sound"}
        >>> panel = PackSettingsPanel(Sounds)
        >>> panel.stack.count()
        2
        >>> _ = settings.pack_exercises.pop("Sounds")
        """
        super().__init__(parent)
        self.exercise = exercise
        self.cfg: settings.PackExerciseSettings = exercise.options()
        self.stack = SlideStack()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.stack)
        menu = QWidget()
        layout = QVBoxLayout(menu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("<h3>Settings</h3>"))
        controls = exercise.controls
        self.sound_row: MenuRow | None = None
        self.accidentals_row: ToggleRow | None = None
        self.octave_row: ToggleRow | None = None
        if "sound" in controls:
            self.sound_row = MenuRow(str(controls["sound"]))
            self.sound_row.setToolTip("Choose which instrument sounds in this exercise")
            layout.addWidget(self.sound_row)
        pages = [menu]
        if "range" in controls:
            row = self.range_row = MenuRow("Range", tall=True)
            self.range_pictures = RangePictures(max_width=px(ROW_PICTURE_WIDTH))
            row.attach(self.range_pictures)
            row.clicked.connect(lambda _=False: self._go(self.range_index))
            layout.addWidget(row)
            pages.append(self._range_page())
        if "accidentals" in controls:
            self.accidentals_row = self._switch(
                layout,
                title="Accidentals",
                tip="Also ask the notes between the natural ones, with sharps and flats",
                on=self.cfg.accidentals,
                edit=self._accidentals_toggled,
            )
        if "octave" in controls:
            self.octave_row = self._switch(
                layout,
                title="Octave",
                tip="Also ask which octave the note is in",
                on=self.cfg.require_octave,
                edit=self._octave_toggled,
            )
        if self.sound_row is not None:
            sound_page = len(pages)
            self.sound_row.clicked.connect(lambda _=False, target=sound_page: self._go(target))
            page, self._show_sound = _pack_sound_page(
                exercise,
                title=str(controls["sound"]),
                chosen=self._sound_chosen,
                back=lambda: self._go(0),
            )
            pages.append(page)
        layout.addStretch()
        for page in pages:
            self.stack.addWidget(page)
        self._refresh_summaries()

    def _persist(self) -> None:
        """
        Save the options under the exercise's name.

        Examples
        --------
        >>> from alto.ui.store import store
        >>> class Demo(PackExercise):
        ...     controls = {"sound": "Demo sound"}
        >>> panel = PackSettingsPanel(Demo)
        >>> panel.cfg.sound = "piano"
        >>> panel._persist()
        >>> str(store().value("packExercises/Demo/sound"))
        'piano'
        >>> _ = settings.pack_exercises.pop("Demo")
        >>> store().remove("packExercises/Demo")
        """
        save_pack_options(self.exercise.__name__)

    @staticmethod
    def _switch(
        layout: QVBoxLayout,
        *,
        title: str,
        tip: str,
        on: bool,
        edit: Callable[[bool], None],
    ) -> ToggleRow:
        """
        Add a switch row to the menu.

        Parameters
        ----------
        layout : QVBoxLayout
            The menu's layout. The row goes at the end.
        title : str
            The row's label. Keyword-only.
        tip : str
            What the switch does, as its tooltip. Keyword-only.
        on : bool
            The switch's starting state. Keyword-only.
        edit : callable
            Called with the new state when the switch is clicked. Keyword-only.

        Returns
        -------
        ToggleRow
            The new row.

        Examples
        --------
        >>> layout = QVBoxLayout()
        >>> PackSettingsPanel._switch(layout, title="Octave", tip="", on=True, edit=print).isOn()
        True
        """
        row = ToggleRow(title)
        row.setToolTip(tip)
        row.setOn(on)
        row.switched.connect(edit)
        layout.addWidget(row)
        return row

    def _limits(self, key: str) -> tuple[int, int] | None:
        """
        Keep the range within the notes the plugin lists.

        Parameters
        ----------
        key : str
            The clef.

        Returns
        -------
        tuple of (int, int)
            The lowest and highest staff step among the plugin's notes.

        Examples
        --------
        >>> class Ranged(PackExercise):
        ...     controls = {"range": "alto"}
        ...     span = (21, 30)
        ...     range_clef = "alto"
        >>> PackSettingsPanel(Ranged)._limits("alto")
        (21, 30)
        >>> _ = settings.pack_exercises.pop("Ranged")
        """
        del key
        return self.exercise.span

    def _refresh_summaries(self) -> None:
        """
        Draw the chosen range in the menu row.

        Examples
        --------
        Returning from the Range page refreshes its staff preview.
        """
        if self.sound_row is not None:
            self.sound_row.value.setText(self._show_sound(self.cfg.sound or self._own_sound()))
        if "range" in self.exercise.controls:
            clef = self.exercise.range_clef
            self.range_pictures.set_items([(clef, *self.cfg.range_for(clef))])
            self.range_row.fit()

    def _reset_ranges(self) -> None:
        """
        Go back to every note the plugin lists and show them.

        Examples
        --------
        Reset to defaults on the viola's Range page selects C3 to E5.
        """
        self.cfg.ranges[self.exercise.range_clef] = self.exercise.span
        self._build_range_rows()
        self._save_and_emit()

    def _own_sound(self) -> str:
        """
        Find the key of the instrument the plugin plays by default.

        Returns
        -------
        str
            The key of the exercise's own instrument, or an empty string when it has no recordings.

        Examples
        --------
        The viola exercise's own sound is the plugin's bowed viola.
        """
        model = getattr(self.exercise, "pack_instrument", None)
        own = model.sound if model is not None else None
        return own.key if own is not None else ""

    def _sound_chosen(self, key: str) -> None:
        """
        Take the chosen instrument into the options, save it and say so.

        Parameters
        ----------
        key : str
            The key of the instrument that now sounds in this exercise.

        Examples
        --------
        Choosing the piano makes the viola exercise play the piano.
        """
        self.cfg.sound = None if key == self._own_sound() else key
        self._refresh_summaries()
        self._save_and_emit()

    def _accidentals_toggled(self, on: bool) -> None:
        """
        Take the Accidentals switch into the options, save it and say so.

        Parameters
        ----------
        on : bool
            Whether sharps and flats are asked.

        Examples
        --------
        Switching on adds C sharp to the viola's cards.
        """
        self.cfg.accidentals = on
        self._save_and_emit()

    def _octave_toggled(self, on: bool) -> None:
        """
        Take the Octave switch into the options, save it and say so.

        Parameters
        ----------
        on : bool
            Whether the answer must include the octave.

        Examples
        --------
        Switching on asks for D4 instead of D.
        """
        self.cfg.require_octave = on
        self._save_and_emit()


class PackKeyboardSettingsPanel(ExerciseSettingsPanel):
    """
    The settings a plugin declared for a keyboard interval exercise: its sound, the range of keys, and the intervals.

    The plugin picks which controls appear. Edits are live: each changes the options, saves them and emits `changed`.

    Attributes
    ----------
    exercise : type of PackExercise
        The exercise whose options are edited.
    cfg : PackExerciseSettings
        The options being edited.
    stack : SlideStack
        The settings menu, then the range page and the intervals page, as the plugin offers them.
    sound_row : ToggleRow or None
        The plugin sound switch, if declared.
    range_row : MenuRow or None
        The Range row, if declared.
    span : KeyboardSpan or None
        The draggable range selector, if a range is declared.
    interval_page : ChoiceChecklist or None
        The interval checkboxes, keyed by interval name, if a choice of intervals is declared.
    manual_page : ChoiceChecklist or None
        The keyboard checkboxes, keyed by keyboard name, if a choice of manuals is declared.

    Examples
    --------
    >>> class Demo(PackExercise):
    ...     controls = {"range": True, "intervals": True, "manuals": True}
    ...     spec = {"type": "keyboard-intervals"}
    ...     key_span, key_default = (28, 89), (48, 72)
    ...     interval_names = ("m2", "M2", "m3")
    ...     manual_names = ("Upper manual", "Lower manual")
    >>> panel = PackKeyboardSettingsPanel(Demo)
    >>> panel.stack.count(), panel.low_label.text(), panel.high_label.text()
    (4, 'C3', 'C5')
    >>> _ = settings.pack_exercises.pop("Demo")
    """

    def __init__(
        self,
        exercise: type[PackExercise],
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the menu and the pages the plugin offers.

        Parameters
        ----------
        exercise : type of PackExercise
            The exercise to edit.
        parent : QWidget or None, default None
            The widget that owns the panel. Keyword-only.

        Examples
        --------
        >>> class Sounds(PackExercise):
        ...     controls = {"sound": "Demo sound"}
        ...     spec = {"type": "keyboard-intervals"}
        >>> panel = PackKeyboardSettingsPanel(Sounds)
        >>> panel.stack.count()
        2
        >>> _ = settings.pack_exercises.pop("Sounds")
        """
        super().__init__(parent)
        self.exercise = exercise
        self.cfg: settings.PackExerciseSettings = exercise.options()
        self._commit_timer = QTimer(self)  # saves and asks a new question once a drag pauses, not at every mouse movement
        self._commit_timer.setSingleShot(True)
        self._commit_timer.setInterval(COMMIT_DELAY_MS)
        self._commit_timer.timeout.connect(self.flush)
        self.stack = SlideStack()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.stack)
        menu = QWidget()
        layout = QVBoxLayout(menu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("<h3>Settings</h3>"))
        controls = exercise.controls
        self.sound_row: MenuRow | None = None
        self.range_row: MenuRow | None = None
        self.span: KeyboardSpan | None = None
        self.interval_page: ChoiceChecklist | None = None
        self.manual_page: ChoiceChecklist | None = None
        pages = [menu]
        if "sound" in controls:
            sound = MenuRow(str(controls["sound"]))
            sound.setToolTip("Choose which instrument sounds in this exercise")
            layout.addWidget(sound)
            self.sound_row = sound
        if "range" in controls:
            row = MenuRow("Range", tall=True)
            self.range_keyboard = KeyboardSpan(compact=True, size=(px(ROW_PICTURE_WIDTH), px(36)))
            self.range_keyboard.full = exercise.key_span
            row.attach(self.range_keyboard)
            range_page = len(pages)
            row.clicked.connect(lambda _=False, target=range_page: self._go(target))
            layout.addWidget(row)
            self.range_row = row
            pages.append(self._range_page())
        if "intervals" in controls:
            self.intervals_row = MenuRow("Intervals")
            intervals_page = len(pages)
            self.intervals_row.clicked.connect(lambda _=False, target=intervals_page: self._go(target))
            layout.addWidget(self.intervals_row)
            pages.append(self._intervals_page())
        if "manuals" in controls:
            self.manuals_row = MenuRow("Manuals")
            manuals_page = len(pages)
            self.manuals_row.clicked.connect(lambda _=False, target=manuals_page: self._go(target))
            layout.addWidget(self.manuals_row)
            pages.append(self._manuals_page())
        if self.sound_row is not None:
            sound_page = len(pages)
            self.sound_row.clicked.connect(lambda _=False, target=sound_page: self._go(target))
            page, self._show_sound = _pack_sound_page(
                exercise,
                title=str(controls["sound"]),
                chosen=self._sound_chosen,
                back=lambda: self._go(0),
            )
            pages.append(page)
        layout.addStretch()
        for page in pages:
            self.stack.addWidget(page)
        self._refresh()

    def _persist(self) -> None:
        """
        Save the options under the exercise's name.

        Examples
        --------
        >>> from alto.ui.store import store
        >>> class Demo(PackExercise):
        ...     controls = {"sound": "Demo sound"}
        ...     spec = {"type": "keyboard-intervals"}
        >>> panel = PackKeyboardSettingsPanel(Demo)
        >>> panel.cfg.sound = "piano"
        >>> panel._persist()
        >>> str(store().value("packExercises/Demo/sound"))
        'piano'
        >>> _ = settings.pack_exercises.pop("Demo")
        >>> store().remove("packExercises/Demo")
        """
        save_pack_options(self.exercise.__name__)

    def _range_page(self) -> QWidget:
        """
        Build the page where the keys to practice are chosen.

        Returns
        -------
        QWidget
            The page, with a draggable miniature of the keyboard, steppers for the lowest and highest key, and a reset.

        Examples
        --------
        The harpsichord's page lets the range run from E1 to F6, and starts at C3 to C5.
        """
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        hint = QLabel("Drag to choose the keys to practice. Both highlighted notes must fit within this range.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        span = KeyboardSpan()
        span.full = self.exercise.key_span
        span.dragged.connect(self._set_keys)
        layout.addWidget(span)
        self.span = span
        self.low_label, self.high_label = QLabel(), QLabel()
        self.arrows: dict[str, tuple[QToolButton, QToolButton]] = {}
        for title, label, which in (("Lowest key", self.low_label, "low"), ("Highest key", self.high_label, "high")):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"<b>{title}</b>"), 1)
            down = arrow_button(Qt.ArrowType.LeftArrow, tip=f"{title}: one key down")
            up = arrow_button(Qt.ArrowType.RightArrow, tip=f"{title}: one key up")
            down.clicked.connect(lambda _=False, w=which: self._step(w, delta=-1))
            up.clicked.connect(lambda _=False, w=which: self._step(w, delta=1))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumWidth(px(48))
            row.addWidget(down)
            row.addWidget(label)
            row.addWidget(up)
            layout.addLayout(row)
            self.arrows[which] = (down, up)
        self.entire = QPushButton("Entire keyboard")
        self.entire.clicked.connect(lambda: self._set_keys(*self.exercise.key_span))
        self.default = QPushButton("Reset to default")
        self.default.clicked.connect(lambda: self._set_keys(*self.exercise.key_default))
        layout.addWidget(self.entire)
        layout.addWidget(self.default)
        return subpage("Range", body=body, back=lambda: self._go(0))

    def _intervals_page(self) -> QWidget:
        """
        Build the page where the intervals to ask are chosen.

        Returns
        -------
        QWidget
            The page, with a Select all switch and a checkbox for each interval the plugin lists.

        Examples
        --------
        An interval too wide for the chosen range is shown but cannot be checked.
        """
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        self.select_all = ToggleRow("Select all")
        self.select_all.switched.connect(self._select_all_toggled)
        layout.addWidget(self.select_all)
        names = self.exercise.interval_names
        checklist = ChoiceChecklist(
            [("", [(name, name) for name in names])],
            selected=set(self.exercise.chosen_intervals()),
        )
        checklist.changed.connect(self._intervals_edited)
        layout.addWidget(checklist)
        self.interval_page = checklist
        return subpage("Intervals", body=scrolling(body), back=lambda: self._go(0), fill=True)

    def _manuals_page(self) -> QWidget:
        """
        Build the page where the keyboards the highlighted keys sit on are chosen.

        Returns
        -------
        QWidget
            The page, with a checkbox for each keyboard the exercise uses. At least one stays checked.

        Examples
        --------
        Checking only the upper manual highlights both keys of every question on it.
        """
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        hint = QLabel("Both highlighted keys sit on the checked manuals. Check both to include keys on each.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        checklist = ChoiceChecklist(
            [("", [(name, name) for name in self.exercise.manual_names])],
            selected=set(self.exercise.chosen_manuals()),
        )
        checklist.changed.connect(self._manuals_edited)
        layout.addWidget(checklist)
        layout.addStretch()
        self.manual_page = checklist
        return subpage("Manuals", body=scrolling(body), back=lambda: self._go(0), fill=True)

    def _manuals_edited(self) -> None:
        """
        Take the checked manuals into the options, save them and say so.

        Examples
        --------
        Unchecking the lower manual leaves only questions on the upper manual.
        """
        if self.manual_page is None:
            return
        picked = {str(name) for name in self.manual_page.selected()}
        every = set(self.exercise.manual_names)
        self.cfg.manuals = None if picked >= every or not picked else frozenset(picked)
        self._save_and_emit()

    @staticmethod
    def _distance(name: str) -> int:
        """
        Count the half steps in one of the plugin's intervals.

        Parameters
        ----------
        name : str
            The interval's name, such as ``P5``.

        Returns
        -------
        int
            The number of half steps.

        Examples
        --------
        The distance of a perfect fifth is 7.
        """
        return settings.KEYBOARD_INTERVAL_NAMES.index(name) + 1

    def _refresh(self) -> None:
        """
        Show the chosen range and intervals, and disable the intervals that are too wide for the range.

        Examples
        --------
        Narrowing the range to a fifth disables the sixths and sevenths.
        """
        low, high = self.exercise.chosen_keys()
        names = set(self.exercise.chosen_intervals())
        if self.sound_row is not None:
            self.sound_row.value.setText(self._show_sound(self.cfg.sound or self._own_sound()))
        if self.range_row is not None:
            self.range_keyboard.set_span(low, hi=high)
            self.range_keyboard.setToolTip(f"{key_name(low)} to {key_name(high)}")
            self.range_row.value.setText(f"{key_name(low)} to {key_name(high)}")
            self.range_row.fit()
        if self.span is not None:
            self.low_label.setText(key_name(low))
            self.high_label.setText(key_name(high))
            self.span.set_span(low, hi=high)
            first, last = self.exercise.key_span
            self.arrows["low"][0].setEnabled(low > first)
            self.arrows["low"][1].setEnabled(low < high - 1)
            self.arrows["high"][0].setEnabled(high > low + 1)
            self.arrows["high"][1].setEnabled(high < last)
        if self.manual_page is not None:
            chosen_boards = self.exercise.chosen_manuals()
            self.manual_page.blockSignals(True)
            for name, box in self.manual_page.boxes.items():
                box.setChecked(name in chosen_boards)
            self.manual_page.blockSignals(False)
            every_board = len(chosen_boards) == len(self.exercise.manual_names)
            shown = "Both" if every_board else ", ".join(name.removesuffix(" manual") for name in chosen_boards)
            self.manuals_row.value.setText(shown)
        if self.interval_page is not None:
            self.interval_page.blockSignals(True)
            fitting = {name: self._distance(str(name)) <= high - low for name in self.interval_page.boxes}
            for name, box in self.interval_page.boxes.items():
                box.setChecked(name in names and fitting[name])
            for name, box in self.interval_page.boxes.items():
                box.setEnabled(fitting[name])  # after checking, which can re-enable the last checked box
            self.interval_page.blockSignals(False)
            self.select_all.blockSignals(True)
            self.select_all.setOn(all(box.isChecked() for box in self.interval_page.boxes.values() if box.isEnabled()))
            self.select_all.blockSignals(False)
            self.intervals_row.value.setText(f"{len(names)} of {len(self.exercise.interval_names)}")

    def _step(self, which: str, *, delta: int) -> None:
        """
        Move one end of the range by a key, without letting the two ends meet.

        Parameters
        ----------
        which : str
            The end, ``low`` or ``high``.
        delta : int
            The number of keys to move. Keyword-only.

        Examples
        --------
        Stepping the lowest key up from C3 gives C#3.
        """
        low, high = self.exercise.chosen_keys()
        first, last = self.exercise.key_span
        if which == "low":
            low = min(max(low + delta, first), high - 1)
        else:
            high = max(min(high + delta, last), low + 1)
        self._set_keys(low, high)

    def _set_keys(  # noqa: PLR0917 (a Qt slot: the signal passes positional arguments)
        self,
        low: int,
        high: int,
    ) -> None:
        """
        Take a new range into the options, keep only the intervals that still fit, save it and say so.

        Parameters
        ----------
        low : int
            The lowest key, as a MIDI number.
        high : int
            The highest key. Both are kept inside the keys the plugin has cards for.

        Examples
        --------
        Dragging the range to C4 to G4 leaves intervals up to a perfect fifth.
        """
        first, last = self.exercise.key_span
        low, high = max(low, first), min(high, last)
        if high - low < 1:
            return
        self.cfg.keys = None if (low, high) == self.exercise.key_default else (low, high)
        fitting = {name for name in self.exercise.chosen_intervals() if self._distance(name) <= high - low}
        self._keep(fitting or {name for name in self.exercise.interval_names if self._distance(name) <= high - low})
        self._save_and_emit()

    def _keep(self, names: set[str]) -> None:
        """
        Record the chosen intervals, or none at all when every interval is chosen.

        Parameters
        ----------
        names : set of str
            The names of the intervals to ask.

        Examples
        --------
        Choosing every interval the plugin lists stores no choice.
        """
        every = set(self.exercise.interval_names)
        self.cfg.intervals = None if names >= every else frozenset(names)

    def _select_all_toggled(self, on: bool) -> None:
        """
        Choose every interval that fits the range, or only the smallest one.

        Parameters
        ----------
        on : bool
            True to choose all of them. False keeps the smallest interval, since at least one must be asked.

        Examples
        --------
        Switching Select all off leaves a minor second.
        """
        low, high = self.exercise.chosen_keys()
        fitting = [name for name in self.exercise.interval_names if self._distance(name) <= high - low]
        self._keep(set(fitting) if on else set(fitting[:1]))
        self._save_and_emit()

    def _intervals_edited(self) -> None:
        """
        Take the checked intervals into the options, save them and say so.

        Examples
        --------
        Unchecking the tritone stops it being asked.
        """
        if self.interval_page is None:
            return
        picked = {str(name) for name in self.interval_page.selected()}
        self._keep(picked or set(self.exercise.chosen_intervals()))
        self._save_and_emit()

    def _own_sound(self) -> str:
        """
        Find the key of the instrument the plugin plays by default.

        Returns
        -------
        str
            The key of the exercise's own instrument, or an empty string when it has no recordings.

        Examples
        --------
        The harpsichord exercise's own sound is the plugin's Flemish harpsichord.
        """
        model = getattr(self.exercise, "pack_instrument", None)
        own = model.sound if model is not None else None
        return own.key if own is not None else ""

    def _sound_chosen(self, key: str) -> None:
        """
        Take the chosen instrument into the options, save it and say so.

        Parameters
        ----------
        key : str
            The key of the instrument that now sounds in this exercise.

        Examples
        --------
        Choosing the piano makes the harpsichord exercise play the piano.
        """
        self.cfg.sound = None if key == self._own_sound() else key
        self._save_and_emit()

    def _save_and_emit(self) -> None:
        """
        Show the options as they now are at once, and save them and ask a new question when the edits pause.

        Examples
        --------
        Dragging the range redraws the keyboard at every movement but asks one new question when the drag stops.
        """
        self._refresh()
        self.restyled.emit()  # the keyboards on screen follow the range while it is dragged
        self._commit_timer.start()

    def flush(self) -> None:
        """
        Save the options and ask a new question now, if an edit is waiting.

        Examples
        --------
        >>> class Demo(PackExercise):
        ...     controls = {"sound": "Demo sound"}
        ...     spec = {"type": "keyboard-intervals"}
        >>> panel = PackKeyboardSettingsPanel(Demo)
        >>> panel._sound_chosen("piano")
        >>> panel.flush()
        >>> panel._commit_timer.isActive()
        False
        >>> _ = settings.pack_exercises.pop("Demo")
        """
        if self._commit_timer.isActive():
            self._commit_timer.stop()
            self._persist()
            self.changed.emit()

    def hideEvent(self, event: QHideEvent) -> None:
        """
        Keep an edit that is still waiting when the panel closes.

        Parameters
        ----------
        event : QHideEvent
            The event.

        Examples
        --------
        >>> class Demo(PackExercise):
        ...     controls = {"sound": "Demo sound"}
        ...     spec = {"type": "keyboard-intervals"}
        >>> panel = PackKeyboardSettingsPanel(Demo)
        >>> panel._sound_chosen("piano")
        >>> panel.show()
        >>> panel.hide()
        >>> panel._commit_timer.isActive()
        False
        >>> _ = settings.pack_exercises.pop("Demo")
        """
        self.flush()
        super().hideEvent(event)
