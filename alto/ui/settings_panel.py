"""
The settings panels that slide in beside an exercise, and the small widgets they are built from.

Each exercise with settings has a panel: a menu of rows (Clefs, Range, Key signatures ...) that each lead to a page. Edits
are live: they change the shared settings object, are saved, and a `changed` signal tells the exercise to ask a new
question. This module also loads and saves each exercise's settings.

Examples
--------
>>> _key_label(2)
'D  ·  2♯'
>>> row = _Row("Clefs")
>>> row.title.text()
'<b>Clefs</b>'
"""

from __future__ import annotations

from collections.abc import (
    Callable,
    Iterable,
)

from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPointF,
    QPropertyAnimation,
    QSize,
    Qt,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QIntValidator,
    QPainter,
    QPaintEvent,
    QPalette,
    QPen,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QBoxLayout,
    QButtonGroup,
    QCheckBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QStackedWidget,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from alto import settings
from alto.circle_schemes import (
    DEFAULT_SCHEME,
    PRESETS,
    CustomRecord,
    dump_customs,
    load_customs,
)
from alto.exercises.base import Exercise
from alto.exercises.library import (
    ArpeggioNames,
    CircleOfFifths,
    ClefBasics,
    IntervalNames,
    KeyboardIntervals,
    KeyboardNotes,
    KeySignatureConstruction,
    KeySignatures,
    NotationIdentification,
    NoteConstruction,
    NoteNames,
    ScaleConstruction,
    ScaleIdentification,
)
from alto.notation_terms import CATALOG
from alto.settings import (
    CLEFS,
    DEFAULT_RANGES,
    MAX_DIATONIC,
    MIN_DIATONIC,
    NAMINGS,
    NOTE_VALUES,
    RANGE_LIMITS,
    NoteNameSettings,
    diatonic_name,
    key_name,
)
from alto.theory.pitch import (
    MAJOR_KEYS,
    Note,
)
from alto.theory.scales import INVERSION_NAMES, mode_tonic
from alto.ui.circle_colors import (
    SchemeEditor,
    SchemePage,
)
from alto.ui.colors import blend
from alto.ui.degree_text import DegreeCheckBox, degree_tooltip
from alto.ui.dropdown import FieldComboBox
from alto.ui.interval_range import IntervalRangeSlider
from alto.ui.keyboard import KeyboardSpan
from alto.ui.pictures import (
    CLEF_NAMES,
    VALUE_NAMES,
    ClefPictures,
    KeySignaturePicture,
    NamePicture,
    RangePictures,
    ValuePictures,
    _Picture,
)
from alto.ui.staff import StaffWidget
from alto.ui.store import (
    int_value,
    store,
    text_value,
)


def load_note_names() -> None:
    """
    Load the saved note identification settings into the shared settings object.

    Settings saved by an older version, which had a switch between the grand staff and single clefs, are converted. Anything
    in the saved data that is not valid is ignored.

    Examples
    --------
    >>> cfg_ = settings.note_names
    >>> cfg_.clefs = {"alto"}
    >>> save_note_names()
    >>> cfg_.clefs = {"treble"}
    >>> load_note_names()
    >>> cfg_.clefs
    {'alto'}
    >>> cfg_.clefs = {"treble", "bass"}
    >>> save_note_names()
    """
    s = store()
    cfg = settings.note_names
    saved = s.value("noteNames/clefs")
    if saved is not None:
        text = saved if isinstance(saved, str) else ",".join(saved)
        cfg.clefs = {c for c in text.split(",") if c in settings.RANGE_KEYS}
    if s.value("noteNames/mode") == "grand":  # an older version had a switch between the grand staff and single clefs
        cfg.clefs = {"grand"}
    s.remove("noteNames/mode")
    keys = text_value(s, key="noteNames/keys", default="")
    if keys:
        cfg.key_signatures = {int(k) for k in keys.split(",") if k.lstrip("-").isdigit() and abs(int(k)) <= 7} or {0}
    values = text_value(s, key="noteNames/values", default="")
    if values:
        cfg.note_values = {v for v in values.split(",") if v in NOTE_VALUES} or {"whole"}
    naming = text_value(s, key="noteNames/naming", default=cfg.naming)
    cfg.naming = naming if naming in NAMINGS else "letters"
    cfg.accidentals = text_value(s, key="noteNames/accidentals", default="false").lower() == "true"
    cfg.require_octave = text_value(s, key="noteNames/requireOctave", default="false").lower() == "true"
    cfg.ranges = {}
    for item in text_value(s, key="noteNames/ranges", default="").split(","):  # e.g. "treble:31-33,bass:14-28"
        try:
            key, span = item.split(":")
            lo, hi = (int(x) for x in span.split("-"))
        except ValueError:
            continue
        if key in DEFAULT_RANGES and MIN_DIATONIC <= lo <= hi <= MAX_DIATONIC:
            cfg.ranges[key] = (lo, hi)


def save_note_names() -> None:
    """
    Save the note identification settings.

    Examples
    --------
    >>> cfg_ = settings.note_names
    >>> cfg_.naming = "solfege"
    >>> save_note_names()
    >>> str(store().value("noteNames/naming"))
    'solfege'
    >>> cfg_.naming = "letters"
    >>> save_note_names()
    """
    s = store()
    cfg = settings.note_names
    s.setValue("noteNames/clefs", ",".join(c for c in settings.RANGE_KEYS if c in cfg.clefs))
    s.setValue("noteNames/keys", ",".join(str(k) for k in cfg.active_keys()))
    s.setValue("noteNames/values", ",".join(cfg.active_values()))
    s.setValue("noteNames/naming", cfg.naming)
    s.setValue("noteNames/accidentals", "true" if cfg.accidentals else "false")
    s.setValue("noteNames/requireOctave", "true" if cfg.require_octave else "false")
    s.setValue("noteNames/ranges", ",".join(f"{k}:{lo}-{hi}" for k, (lo, hi) in cfg.ranges.items()))


def _guard_last(
    boxes: Iterable[QAbstractButton],
    *,
    enabled: bool = True,
) -> None:
    """
    Disable the only checked box, so that at least one choice always stays selected.

    Parameters
    ----------
    boxes : iterable of QAbstractButton
        The checkboxes of one choice.
    enabled : bool, default True
        False disables them all (for when the whole choice is switched off). Keyword-only.

    Examples
    --------
    >>> first, second = QCheckBox(), QCheckBox()
    >>> first.setChecked(True)
    >>> _guard_last([first, second])
    >>> first.isEnabled(), second.isEnabled()
    (False, True)
    >>> second.setChecked(True)
    >>> _guard_last([first, second])
    >>> first.isEnabled()
    True
    """
    checked = [b for b in boxes if b.isChecked()]
    for box in boxes:
        box.setEnabled(enabled and not (len(checked) == 1 and box.isChecked()))


def _key_label(count: int) -> str:
    """
    Label a key signature with its key and its accidentals.

    Parameters
    ----------
    count : int
        Sharps if positive, flats if negative.

    Returns
    -------
    str
        For example 'D  ·  2♯', 'E♭  ·  3♭' or 'C  ·  none'.

    Examples
    --------
    >>> _key_label(0), _key_label(2), _key_label(-3)
    ('C  ·  none', 'D  ·  2♯', 'E♭  ·  3♭')
    """
    return f"{MAJOR_KEYS[count]}  ·  " + ("none" if count == 0 else f"{abs(count)}{'♯' if count > 0 else '♭'}")


def _arrow(
    kind: Qt.ArrowType,
    *,
    tip: str,
) -> QToolButton:
    """
    Make a small arrow button that repeats while it is held.

    Parameters
    ----------
    kind : Qt.ArrowType
        Which way the arrow points.
    tip : str
        The tooltip. Keyword-only.

    Returns
    -------
    QToolButton
        The button.

    Examples
    --------
    >>> button = _arrow(Qt.ArrowType.UpArrow, tip="Raise the lowest note")
    >>> button.toolTip(), button.autoRepeat()
    ('Raise the lowest note', True)
    """
    btn = QToolButton()
    btn.setArrowType(kind)
    btn.setProperty("arrowButton", True)  # styled with a visible border (see style.py)
    btn.setToolTip(tip)
    btn.setAccessibleName(tip)
    btn.setAutoRepeat(True)
    btn.setAutoRepeatDelay(350)
    btn.setAutoRepeatInterval(90)
    return btn


class RangeEditor(QWidget):
    """
    A staff showing the lowest and highest note asked for a clef.

    Arrows on the left move the lower bound, arrows on the right move the upper bound.

    Attributes
    ----------
    edited : Signal
        Emitted with the clef key, the lowest note and the highest note (as staff steps) after a change.
    key : str
        The clef.
    low : int
        The lowest note asked, as a staff step (`Note.diatonic`).
    high : int
        The highest note asked.
    limits : tuple of (int, int)
        The furthest the bounds may go.
    staff : StaffWidget
        Shows the two notes.

    Examples
    --------
    >>> editor = RangeEditor("treble", low=28, high=34)
    >>> editor.caption_text.text()
    '<b>C4 – B4</b>'
    """

    edited = Signal(str, int, int)  # clef key, low, high (diatonic)

    def __init__(
        self,
        key: str,
        *,
        low: int,
        high: int,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the editor for a clef's range.

        Parameters
        ----------
        key : str
            The clef, a key of `RANGE_LIMITS`.
        low : int
            The lowest note asked, as a staff step. Keyword-only.
        high : int
            The highest note asked. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns the editor. Keyword-only.

        Examples
        --------
        >>> RangeEditor("bass", low=14, high=28).limits == settings.RANGE_LIMITS["bass"]
        True
        """
        super().__init__(parent)
        self.key, self.low, self.high = key, low, high
        self.limits = RANGE_LIMITS[key]
        self.caption_text = QLabel()
        self.caption_text.setStyleSheet("font-size: 12pt;")
        self.caption = QWidget()  # the clef as a picture, then the lowest and highest note
        caption_row = QHBoxLayout(self.caption)
        caption_row.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        caption_row.addWidget(ClefPictures([key], scale=0.9))
        caption_row.addWidget(self.caption_text)
        caption_row.addStretch()
        self.staff = StaffWidget(
            gap=9.0,
            side=18.0,
            note_offset=62.0,
            margin=8.0,
            compact=True,
        )
        self.staff.setFixedWidth(168)
        self.low_up = _arrow(Qt.ArrowType.UpArrow, tip="Raise the lowest note")
        self.low_down = _arrow(Qt.ArrowType.DownArrow, tip="Lower the lowest note")
        self.high_up = _arrow(Qt.ArrowType.UpArrow, tip="Raise the highest note")
        self.high_down = _arrow(Qt.ArrowType.DownArrow, tip="Lower the highest note")
        self.low_up.clicked.connect(lambda: self._move(low=1))
        self.low_down.clicked.connect(lambda: self._move(low=-1))
        self.high_up.clicked.connect(lambda: self._move(high=1))
        self.high_down.clicked.connect(lambda: self._move(high=-1))

        row = QHBoxLayout()
        row.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        row.addStretch()  # keep the staff and its arrows together, centered in the pane
        for column, buttons in ((0, (self.low_up, self.low_down)), (2, (self.high_up, self.high_down))):
            col = QVBoxLayout()
            col.setSpacing(2)
            col.addStretch()  # center the pair on the staff's midline
            col.addWidget(buttons[0])
            col.addWidget(buttons[1])
            col.addStretch()
            if column == 0:
                row.addLayout(col)
                row.addWidget(self.staff)
            else:
                row.addLayout(col)
        row.addStretch()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            0,
            8,
            0,
            16,
        )  # space between one clef's block and the next
        lay.setSpacing(8)
        lay.addWidget(self.caption)
        lay.addLayout(row)
        self._refresh()

    def _move(
        self,
        low: int = 0,
        *,
        high: int = 0,
    ) -> None:
        """
        Move the bounds by steps, keeping the lower below the upper and both within the limits.

        Parameters
        ----------
        low : int, default 0
            How many staff steps to move the lower bound; positive is higher.
        high : int, default 0
            How many steps to move the upper bound. Keyword-only.

        Examples
        --------
        >>> editor = RangeEditor("treble", low=28, high=34)
        >>> got = []
        >>> _ = editor.edited.connect(lambda key, lo, hi: got.append((key, lo, hi)))
        >>> editor._move(low=1)
        >>> got
        [('treble', 29, 34)]
        >>> editor._move(low=100)  # the lower bound cannot pass the upper
        >>> editor.low
        34
        """
        self.low = min(max(self.low + low, self.limits[0]), self.high)  # the lower bound can't pass the upper
        self.high = max(min(self.high + high, self.limits[1]), self.low)
        self._refresh()
        self.edited.emit(self.key, self.low, self.high)

    def _refresh(self) -> None:
        """
        Show the bounds on the staff and in the caption, and enable only the arrows that can still move.

        Examples
        --------
        >>> editor = RangeEditor("treble", low=22, high=30)  # 22 is the lowest the treble range goes
        >>> editor._refresh()
        >>> editor.low_down.isEnabled(), editor.low_up.isEnabled()
        (False, True)
        """
        self.caption_text.setText(f"<b>{diatonic_name(self.low)} – {diatonic_name(self.high)}</b>")
        self.staff.show_notes([[Note.from_diatonic(self.low)], [Note.from_diatonic(self.high)]], clef=self.key)
        self.low_up.setEnabled(self.low < self.high)
        self.low_down.setEnabled(self.low > self.limits[0])
        self.high_up.setEnabled(self.high < self.limits[1])
        self.high_down.setEnabled(self.high > self.low)


class KeyDiagram(QWidget):
    """
    A small fork showing which key signatures are selected.

    C major is on the left, then two rows of seven dots: 1 to 7 sharps on the top row and 1 to 7 flats on the bottom.
    Selected keys are filled, the rest are hollow.

    Attributes
    ----------
    DOT, PITCH, ROW_GAP, PAD : float
        The dot radius and the spacing, in pixels.
    keys : set of int
        The selected key signatures: sharps if positive, flats if negative.

    Examples
    --------
    >>> KeyDiagram({0, 2}).toolTip()
    'C, D'
    """

    DOT, PITCH, ROW_GAP, PAD = 4.4, 12.6, 13.0, 1.5  # dot radius and spacing, in pixels

    def __init__(
        self,
        keys: set[int] | None = None,
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Create the diagram.

        Parameters
        ----------
        keys : set of int or None, default None
            The key signatures to show as selected.
        parent : QWidget or None, default None
            The widget that owns it. Keyword-only.

        Examples
        --------
        >>> KeyDiagram().keys
        set()
        """
        super().__init__(parent)
        self.keys: set[int] = set(keys or ())
        self.first_column = self.PAD + 2 * self.DOT + 7 + self.DOT  # x of the 1-sharp / 1-flat dots
        self.setFixedSize(
            int(self.first_column + 6 * self.PITCH + self.DOT + self.PAD) + 1,
            int(self.ROW_GAP + 2 * self.DOT + 2 * self.PAD) + 3,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # the row underneath is the click target
        self._update_tip()

    def set_keys(self, keys: set[int]) -> None:
        """
        Choose which key signatures are shown as selected.

        Parameters
        ----------
        keys : set of int
            Sharps if positive, flats if negative.

        Examples
        --------
        >>> diagram = KeyDiagram()
        >>> diagram.set_keys({2, -1, 0})
        >>> diagram.toolTip()
        'C, D, F'
        """
        self.keys = set(keys)
        self._update_tip()
        self.update()

    def _update_tip(self) -> None:
        """
        Set the tooltip to the names of the selected keys, sharp keys first.

        Examples
        --------
        >>> diagram = KeyDiagram({3, 1})
        >>> diagram._update_tip()
        >>> diagram.toolTip()
        'G, A'
        """
        names = [MAJOR_KEYS[k] for k in sorted(self.keys, key=lambda k: (k < 0, abs(k)))]
        self.setToolTip(", ".join(names))

    def paintEvent(self, _: QPaintEvent) -> None:
        """
        Draw a dot for each key signature, filled when selected.

        Parameters
        ----------
        _ : QPaintEvent
            The paint request; the whole widget is always redrawn.

        Examples
        --------
        >>> KeyDiagram({0, 1, -1}).grab().isNull()
        False
        """
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pal = self.palette()
        text = pal.color(QPalette.ColorRole.Text)
        base = pal.color(QPalette.ColorRole.Base)  # the row is filled with the base color

        def shade(t: float) -> QColor:  # t of the way from the row's background to the text color
            """
            Return a color a fraction of the way from the row's background to the text color.

            Parameters
            ----------
            t : float
                0 for the background, 1 for the text color.

            Returns
            -------
            QColor
                The blended color.

            Examples
            --------
            >>> shade(0.5)  # doctest: +SKIP
            """
            return blend(base, b=text, t=t)

        filled, outline = shade(0.85), shade(0.5)  # both stand out from the background, in a light or a dark theme
        mid, top = self.height() / 2, self.height() / 2 - self.ROW_GAP / 2
        spots = [(0, self.PAD + self.DOT, mid)]  # C major, between the two rows
        for n in range(1, 8):
            x = self.first_column + (n - 1) * self.PITCH
            spots += [(n, x, top), (-n, x, top + self.ROW_GAP)]
        for count, x, y in spots:
            selected = count in self.keys
            p.setPen(QPen(filled if selected else outline, 1.2))
            p.setBrush(filled if selected else base)
            p.drawEllipse(QPointF(x, y), self.DOT, self.DOT)


ROW_PICTURE_WIDTH = 238  # room for a picture on its own line in a menu row (pane width less margins)


def _label_with_picture(
    button: QAbstractButton,
    *,
    picture: _Picture,
    name: str,
) -> None:
    """
    Label a checkbox or radio button with a picture instead of text.

    The name stays as the tooltip and the accessible name.

    Parameters
    ----------
    button : QAbstractButton
        The button to label.
    picture : _Picture
        The picture (a clef, a note value ...). Keyword-only.
    name : str
        What it is called. Keyword-only.

    Examples
    --------
    >>> box = QCheckBox()
    >>> _label_with_picture(box, picture=ClefPictures(["treble"]), name="Treble")
    >>> box.toolTip(), box.accessibleName()
    ('Treble', 'Treble')
    """
    button.setIcon(picture.to_icon())
    button.setIconSize(picture.size())
    button.setToolTip(name)
    button.setAccessibleName(name)


def _label_with_clef(
    button: QAbstractButton,
    *,
    clef: str,
    scale: float = 1.4,
) -> None:
    """
    Label a button with a clef's picture and its name beside it.

    Parameters
    ----------
    button : QAbstractButton
        The button to label.
    clef : str
        A key of `CLEF_NAMES`. Keyword-only.
    scale : float, default 1.4
        How much to enlarge the picture. Keyword-only.

    Examples
    --------
    >>> box = QCheckBox()
    >>> _label_with_clef(box, clef="mezzo")
    >>> box.text()
    'Mezzo-soprano'
    """
    _label_with_picture(button, picture=ClefPictures([clef], scale=scale), name=CLEF_NAMES[clef])
    button.setText(CLEF_NAMES[clef])


def _clef_box(
    clef: str,
    *,
    scale: float = 1.4,
) -> QCheckBox:
    """
    Make a checkbox for a clef, with its picture and name.

    Parameters
    ----------
    clef : str
        A key of `CLEF_NAMES`.
    scale : float, default 1.4
        How much to enlarge the picture. Keyword-only.

    Returns
    -------
    QCheckBox
        The checkbox.

    Examples
    --------
    >>> _clef_box("alto").text()
    'Alto'
    """
    box = QCheckBox()
    _label_with_clef(box, clef=clef, scale=scale)
    return box


def _clef_list(boxes: dict[str, QCheckBox]) -> QWidget:
    """
    Lay the clef checkboxes out one under another, in three groups divided by a line.

    The groups are the grand staff; the treble, bass, alto and tenor clefs; and the soprano, mezzo-soprano and baritone
    clefs. A group none of the boxes belong to is left out. The list is indented under its heading.

    Parameters
    ----------
    boxes : dict of str to QCheckBox
        The checkbox of each clef.

    Returns
    -------
    QWidget
        The list.

    Examples
    --------
    >>> boxes_ = {clef: _clef_box(clef) for clef in ("treble", "bass", "soprano")}
    >>> widget_ = _clef_list(boxes_)
    >>> # noinspection PyUnresolvedReferences
    >>> widget_.layout().count()  # two boxes_, a dividing line, and one box
    4
    """
    widget = QWidget()
    lay = QVBoxLayout(widget)
    lay.setContentsMargins(
        24,
        0,
        0,
        0,
    )
    lay.setSpacing(8)
    groups = [[boxes[c] for c in group if c in boxes] for group in settings.CLEF_GROUPS]
    for i, group in enumerate([g for g in groups if g]):
        if i:
            rule = QFrame()
            rule.setFrameShape(QFrame.Shape.HLine)
            rule.setFrameShadow(QFrame.Shadow.Plain)
            rule.setStyleSheet("color: palette(mid);")
            lay.addWidget(rule)
        for box in group:
            lay.addWidget(box, 0, Qt.AlignmentFlag.AlignLeft)
    return widget


def _clefs_page(
    choices: Iterable[str],
    *,
    selected: set[str],
    edited: Callable[[], object],
    back: Callable[[], object],
    title: str = "Clefs",
    hint: str = "One of the checked clefs is picked at random.",
) -> tuple[dict[str, QCheckBox], QWidget]:
    """
    Build the "Clefs" page that every exercise with a choice of clefs shares.

    Parameters
    ----------
    choices : iterable of str
        The clefs to offer, from `settings.RANGE_KEYS`; "grand" is left out of exercises that cannot use the grand staff.
    selected : set of str
        The clefs that start checked. Keyword-only.
    edited : callable
        Called whenever a box is checked or unchecked. Keyword-only.
    back : callable
        Called when the Back button is clicked. Keyword-only.
    title : str, default "Clefs"
        The page's title. Keyword-only.
    hint : str, default "One of the checked clefs is picked at random."
        The gray line above the list. Keyword-only.

    Returns
    -------
    dict of str to QCheckBox
        The checkbox of each clef offered.
    QWidget
        The page, with its title. The last checked clef cannot be unchecked.

    Examples
    --------
    >>> checked = []
    >>> boxes_, page_ = _clefs_page(("treble", "bass"), selected={"bass"}, edited=lambda: checked.append(1), back=lambda: None)
    >>> boxes_["bass"].isEnabled()  # it is the only one checked, so it stays checked
    False
    >>> boxes_["treble"].setChecked(True)
    >>> sorted(c for c, ticked_box in boxes_.items() if ticked_box.isChecked()), checked
    (['bass', 'treble'], [1])
    """
    boxes = {c: _clef_box(c) for c in choices}
    body = QWidget()
    lay = QVBoxLayout(body)
    lay.setContentsMargins(
        0,
        0,
        0,
        0,
    )
    note = QLabel(hint)
    note.setWordWrap(True)
    note.setStyleSheet("color: gray;")
    lay.addWidget(note)
    for c, box in boxes.items():
        box.setChecked(c in selected)
    lay.addWidget(_clef_list(boxes))
    _guard_last(list(boxes.values()))  # the last checked clef can't be unchecked
    for box in boxes.values():
        box.toggled.connect(edited)
    return boxes, _subpage(title, body=body, back=back)


def _show_keys(
    row: _Row,
    *,
    diagram: KeyDiagram,
    enabled: bool,
    keys: set[int],
) -> None:
    """
    Show the selected keys as a diagram in a menu row, or "Off" when key signatures are switched off.

    Parameters
    ----------
    row : _Row
        The menu row.
    diagram : KeyDiagram
        The diagram to update. Keyword-only.
    enabled : bool
        Whether key signatures are on. Keyword-only.
    keys : set of int
        The selected key signatures. Keyword-only.

    Examples
    --------
    >>> row_, diagram_ = _Row("Key signatures"), KeyDiagram()
    >>> _show_keys(row_, diagram=diagram_, enabled=False, keys={0})
    >>> row_.value.text(), diagram_.isHidden()
    ('Off', True)
    """
    diagram.set_keys(keys)
    diagram.setVisible(enabled)
    row.value.setText("" if enabled else "Off")


class _ValueLabel(QLabel):
    """
    The value shown on the right of a menu row, which a screen reader is also given as the row's description.

    Examples
    --------
    >>> row = QPushButton()
    >>> label = _ValueLabel(row)
    >>> label.setText("2 of 7")
    >>> row.accessibleDescription()
    '2 of 7'
    """

    def __init__(self, row: QPushButton) -> None:
        """
        Make the label for a row.

        Parameters
        ----------
        row : QPushButton
            The row that this is the value of.

        Examples
        --------
        >>> _ValueLabel(QPushButton()).text()
        ''
        """
        super().__init__()
        self._row = row

    def setText(self, text: str) -> None:
        """
        Show a value, and describe the row with it.

        Parameters
        ----------
        text : str
            The value.

        Examples
        --------
        >>> row = QPushButton()
        >>> _ValueLabel(row).setText("On")
        >>> row.accessibleDescription()
        'On'
        """
        super().setText(text)
        self._row.setAccessibleDescription(text)


class _Row(QPushButton):
    """
    A menu row: title on the left, current value and a chevron on the right.

    A `tall` row puts a picture on a second line of its own, using the full width, for summaries that need room to be
    readable.

    Attributes
    ----------
    tall : bool
        Whether the row has a second line.
    title : QLabel
        The title.
    value : QLabel
        The current value, shown on the right.

    Examples
    --------
    >>> row = _Row("Range", tall=True)
    >>> row.tall, row.title.text()
    (True, '<b>Range</b>')
    """

    def __init__(
        self,
        title: str,
        *,
        chevron: bool = True,
        tall: bool = False,
    ) -> None:
        """
        Build the row.

        Parameters
        ----------
        title : str
            The row's title.
        chevron : bool, default True
            Show a chevron on the right, to say it opens a page. Keyword-only.
        tall : bool, default False
            Give the row a second line for a picture. Keyword-only.

        Examples
        --------
        >>> _Row("Clefs").minimumHeight()
        48
        """
        super().__init__()
        self.tall = tall
        self._contents: QBoxLayout  # the layout inside the row
        self.title = QLabel(f"<b>{title}</b>")
        self.setAccessibleName(title)  # the text is in labels on the button, which a screen reader would not read as its name
        self.value = _ValueLabel(self)
        self.value.setStyleSheet("color: gray;")
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        for label in (self.title, self.value):
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        arrow = QLabel("›")
        arrow.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        if tall:
            outer = QVBoxLayout(self)
            outer.setContentsMargins(
                11,
                8,
                11,
                8,
            )
            outer.setSpacing(4)
            top = QHBoxLayout()
            top.addWidget(self.title)
            top.addWidget(self.value, 1)
            if chevron:
                top.addWidget(arrow)
            outer.addLayout(top)
            self._below = QHBoxLayout()
            outer.addLayout(self._below)
            self._contents = outer
            return
        self.setMinimumHeight(48)
        lay = QHBoxLayout(self)
        self._contents = lay
        lay.setContentsMargins(
            11,
            4,
            11,
            4,
        )  # leaves room for a small diagram in the row
        lay.addWidget(self.title)
        lay.addWidget(self.value, 1)
        if chevron:
            lay.addWidget(arrow)

    def attach(self, widget: QWidget) -> None:
        """
        Put a widget in the row.

        Just after the value text, or (in a tall row) centered on its own line below.

        Parameters
        ----------
        widget : QWidget
            The widget, usually a small picture of the current choice.

        Examples
        --------
        >>> row = _Row("Clefs")
        >>> picture = ClefPictures(["treble"])
        >>> row.attach(picture)
        >>> # noinspection PyUnresolvedReferences
        >>> row.layout().indexOf(picture)
        2
        """
        if self.tall:
            self._below.addStretch()
            self._below.addWidget(widget)
            self._below.addStretch()
            self.fit()
        else:
            self._contents.insertWidget(2, widget)

    def fit(self) -> None:
        """
        Make a tall row as high as its contents need.

        A button does not size itself to a layout inside it.

        Examples
        --------
        >>> row = _Row("Range", tall=True)
        >>> row.attach(QLabel("a picture"))
        >>> row.minimumHeight() > 0
        True
        """
        if self.tall:
            self.setMinimumHeight(self._contents.minimumSize().height())


class Switch(QAbstractButton):
    """
    A pill-shaped on/off switch whose knob slides across when toggled.

    Attributes
    ----------
    W, H : int
        The switch's size, in pixels.

    Examples
    --------
    >>> switch = Switch()
    >>> switch.setChecked(True)
    >>> switch.isChecked()
    True
    """

    W, H = 42, 24

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Create a switch that is off.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns it.

        Examples
        --------
        >>> Switch().isChecked()
        False
        """
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(self.W, self.H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._pos = 0.0  # knob position, 0 (off) .. 1 (on)
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._set_pos)
        self.toggled.connect(self._slide)

    def _set_pos(self, value: float) -> None:
        """
        Move the knob.

        Parameters
        ----------
        value : float
            0 for off up to 1 for on, with values between while it slides.

        Examples
        --------
        >>> switch = Switch()
        >>> switch._set_pos(0.5)
        >>> switch._pos
        0.5
        """
        self._pos = float(value)
        self.update()

    def _slide(self, on: bool) -> None:
        """
        Slide the knob to on or off.

        Parameters
        ----------
        on : bool
            Where the knob is going.

        Examples
        --------
        >>> switch = Switch()
        >>> switch._slide(True)
        >>> switch._anim.endValue()
        1.0
        """
        self._anim.stop()
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(1.0 if on else 0.0)
        self._anim.start()

    def setChecked(self, on: bool) -> None:  # no animation when set programmatically
        """
        Turn the switch on or off without animating, as when a setting is loaded.

        Parameters
        ----------
        on : bool
            The new state.

        Examples
        --------
        >>> switch = Switch()
        >>> switch.setChecked(True)
        >>> switch._pos
        1.0
        """
        super().setChecked(on)
        self._anim.stop()
        self._set_pos(1.0 if on else 0.0)

    def paintEvent(self, _: QPaintEvent) -> None:
        """
        Draw the track, tinted between off and on, and the knob.

        Parameters
        ----------
        _ : QPaintEvent
            The paint request; the whole widget is always redrawn.

        Examples
        --------
        >>> Switch().grab().isNull()
        False
        """
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pal = self.palette()
        off, on = pal.color(QPalette.ColorRole.Mid), pal.color(QPalette.ColorRole.Highlight)
        track = blend(off, b=on, t=self._pos)
        if not self.isEnabled():
            track.setAlpha(110)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(track)
        p.drawRoundedRect(self.rect(), self.H / 2, self.H / 2)
        r, margin = self.H / 2 - 3, 3
        x = margin + r + self._pos * (self.W - 2 * (margin + r))
        p.setBrush(QColor("white"))
        p.drawEllipse(QPointF(x, self.H / 2), r, r)

    def sizeHint(self) -> QSize:
        """
        Return the switch's fixed size.

        Returns
        -------
        QSize
            `W` by `H`.

        Examples
        --------
        >>> Switch().sizeHint()
        PySide6.QtCore.QSize(42, 24)
        """
        return QSize(self.W, self.H)


class _ToggleRow(_Row):
    """
    A menu row with a switch that changes a setting in place instead of opening a page.

    Attributes
    ----------
    switched : Signal
        Emitted with the new state when the row is clicked.
    switch : Switch
        The switch.

    Examples
    --------
    >>> row = _ToggleRow("Accidentals")
    >>> changes = []
    >>> _ = row.switched.connect(changes.append)
    >>> row.click()
    >>> changes, row.isOn()
    ([True], True)
    """

    switched = Signal(bool)

    def __init__(self, title: str) -> None:
        """
        Build the row with its switch off.

        Parameters
        ----------
        title : str
            The row's title.

        Examples
        --------
        >>> _ToggleRow("Accidentals").isOn()
        False
        """
        super().__init__(title, chevron=False)
        self.value.hide()
        self.switch = Switch()
        self.switch.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # the whole row is the click target
        self.switch.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # the row is what the keyboard reaches, not its picture of a switch
        self.switch.setAccessibleName(title)
        self._contents.addWidget(self.switch)
        self.clicked.connect(lambda: self._set(not self.switch.isChecked()))

    def _set(self, on: bool) -> None:
        """
        Set the switch and tell whoever is listening.

        Parameters
        ----------
        on : bool
            The new state.

        Examples
        --------
        >>> row = _ToggleRow("Accidentals")
        >>> changes = []
        >>> _ = row.switched.connect(changes.append)
        >>> row._set(True)
        >>> changes
        [True]
        """
        self.switch.setChecked(on)
        self.switch.update()
        self.switched.emit(on)

    # noinspection PyPep8Naming
    def isOn(self) -> bool:
        """
        Report whether the switch is on.

        Returns
        -------
        bool
            True if on.

        Examples
        --------
        >>> _ToggleRow("Accidentals").isOn()
        False
        """
        return self.switch.isChecked()

    # noinspection PyPep8Naming
    def setOn(self, on: bool) -> None:
        """
        Set the switch without announcing it, as when a setting is loaded.

        Parameters
        ----------
        on : bool
            The new state.

        Examples
        --------
        >>> row = _ToggleRow("Accidentals")
        >>> row.setOn(True)
        >>> row.isOn()
        True
        """
        self.switch.setChecked(on)


def _subpage(
    title: str,
    *,
    body: QWidget,
    back: Callable[[], object],
    fill: bool = False,
) -> QWidget:
    """
    Build a second-layer page: a Back button and title above a body.

    Parameters
    ----------
    title : str
        The page's title.
    body : QWidget
        What the page shows. Keyword-only.
    back : callable
        Called when Back is clicked. Keyword-only.
    fill : bool, default False
        Let the body take all the room (so a long page can scroll) instead of leaving space below it. Keyword-only.

    Returns
    -------
    QWidget
        The page.

    Examples
    --------
    >>> calls = []
    >>> page_ = _subpage("Clefs", body=QWidget(), back=lambda: calls.append("back"))
    >>> next(b for b in page_.findChildren(QToolButton) if b.text() == "‹ Back").click()
    >>> calls
    ['back']
    """
    page = QWidget()
    lay = QVBoxLayout(page)
    lay.setContentsMargins(
        0,
        0,
        0,
        0,
    )
    head = QHBoxLayout()
    btn = QToolButton()
    btn.setText("‹ Back")
    btn.setAutoRaise(True)
    btn.clicked.connect(back)
    head.addWidget(btn)
    head.addWidget(QLabel(f"<b>{title}</b>"))
    head.addStretch()
    lay.addLayout(head)
    lay.addWidget(body, 1 if fill else 0)
    if not fill:
        lay.addStretch()
    return page


class SlideStack(QStackedWidget):
    """
    A stacked widget whose pages slide in from the right (going deeper) or the left (going back).

    Examples
    --------
    >>> stack = SlideStack()
    >>> _ = stack.addWidget(QWidget())
    >>> _ = stack.addWidget(QWidget())
    >>> stack.sliding
    False
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Create an empty stack.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns it.

        Examples
        --------
        >>> SlideStack().count()
        0
        """
        super().__init__(parent)
        self._slide: QParallelAnimationGroup | None = None

    @property
    def sliding(self) -> bool:
        """
        Report whether a page is sliding in.

        Returns
        -------
        bool
            True from the start of a slide until it finishes.

        Examples
        --------
        >>> SlideStack().sliding
        False
        """
        return self._slide is not None

    def slide_to(self, index: int) -> None:
        """
        Slide to another page.

        Going to a later page slides it in from the right and going back slides it in from the left. A request made during a
        slide, or for the page already showing, is ignored.

        Parameters
        ----------
        index : int
            The page to go to.

        Examples
        --------
        >>> stack = SlideStack()
        >>> _ = stack.addWidget(QWidget())
        >>> _ = stack.addWidget(QWidget())
        >>> stack.slide_to(1)
        >>> stack.sliding
        True
        """
        if self.sliding or index == self.currentIndex():
            return  # ignore requests mid-transition
        old, new = self.currentWidget(), self.widget(index)
        assert old is not None and new is not None
        w = self.width()
        sign = 1 if index > self.currentIndex() else -1
        new.setGeometry(
            0,
            0,
            w,
            self.height(),
        )
        new.move(sign * w, 0)
        new.show()
        new.raise_()
        group = QParallelAnimationGroup(self)
        for widget, start, end in ((old, 0, -sign * w), (new, sign * w, 0)):
            anim = QPropertyAnimation(widget, b"pos", group)
            anim.setDuration(220)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setStartValue(QPoint(start, 0))
            anim.setEndValue(QPoint(end, 0))
            group.addAnimation(anim)

        def done() -> None:
            """
            Finish the slide: show the new page and put both pages back in place.

            Examples
            --------
            >>> done()  # doctest: +SKIP
            """
            self.setCurrentIndex(index)
            # noinspection PyUnresolvedReferences
            old.move(0, 0)
            # noinspection PyUnresolvedReferences
            new.move(0, 0)
            self._slide = None

        group.finished.connect(done)
        self._slide = group
        group.start()


class ExerciseSettingsPanel(QWidget):
    """
    What every exercise's settings pane has in common: it says when a setting has been edited.

    Attributes
    ----------
    changed : Signal
        Emitted after any setting is edited that changes what is asked, so the exercise asks a new question.
    restyled : Signal
        Emitted after a setting is edited that changes only how the exercise looks, so the question stays and the picture is
        drawn again.

    Examples
    --------
    >>> panel = ExerciseSettingsPanel()
    >>> got = []
    >>> _ = panel.changed.connect(lambda: got.append(1))
    >>> panel.changed.emit()
    True
    >>> got
    [1]
    """

    changed = Signal()
    restyled = Signal()


class _StaffRangePanel(ExerciseSettingsPanel):
    """
    Shared navigation and per-clef pitch range editors.

    Examples
    --------
    Note and interval identification both open Range on page two.
    """

    cfg: settings.StaffRangeSettings
    stack: SlideStack

    _persist: Callable[[], None]
    clef_pictures: ClefPictures
    range_pictures: RangePictures
    range_row: _Row

    def _refresh_summaries(self) -> None:
        """
        Refresh the exercise-specific main menu previews.

        Examples
        --------
        Returning from Range refreshes its staff preview.
        """
        clefs = self.cfg.active_clefs()
        self.clef_pictures.set_clefs(clefs)
        self.range_pictures.set_items([(c, *self.cfg.range_for(c)) for c in clefs])
        self.range_row.fit()

    def _save_and_emit(self) -> None:
        """
        Persist changes for this exercise and request a new question.

        Examples
        --------
        Editing the bass range saves it under the current exercise.
        """
        self._persist()
        self.changed.emit()

    def _range_page(self) -> QWidget:
        """
        Build the scrollable page used to edit pitch limits.

        Returns
        -------
        QWidget
            The titled Range submenu.

        Examples
        --------
        Each checked clef gets its own range editor when the page opens.
        """
        self.range_body = QWidget()
        self.range_lay = QVBoxLayout(self.range_body)
        self.range_lay.setContentsMargins(
            6,
            4,
            10,
            8,
        )
        self.range_editors: dict[str, RangeEditor] = {}
        # Restoring a pane after a theme change selects its page directly.
        self.stack.currentChanged.connect(
            lambda index: self._build_range_rows() if index == 2 and not self.range_editors else None,
        )
        scroll = QScrollArea()
        scroll.setWidget(self.range_body)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        return _subpage(
            "Range",
            body=scroll,
            back=lambda: self._go(0),
            fill=True,
        )

    # navigation
    def _go(self, index: int) -> None:
        """
        Slide to a page, refreshing it first.

        Going back to the menu refreshes its summaries; going to the Range page builds its rows. A request made during a slide is
        ignored.

        Parameters
        ----------
        index : int
            0 for the menu, 1 for Clefs, 2 for Range, or an exercise-specific page.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(NoteNameSettings())
        >>> panel._go(2)
        >>> sorted(panel.range_editors), panel.stack.sliding
        (['bass', 'treble'], True)
        """
        if self.stack.sliding or index == self.stack.currentIndex():
            return  # ignore clicks mid-transition
        if index == 0:
            self._refresh_summaries()
        elif index == 2:
            self._build_range_rows()
        self.stack.slide_to(index)

    def _active_keys(self) -> list[str]:
        """
        Return the clefs in use.

        Returns
        -------
        list of str
            The chosen clefs, which the range editors and summaries are for.

        Examples
        --------
        >>> NoteNameSettingsPanel(NoteNameSettings(clefs={"alto"}))._active_keys()
        ['alto']
        """
        return self.cfg.active_clefs()

    # range page
    def _build_range_rows(self) -> None:
        """
        Build a range editor for each clef in use, and a button to reset them to the defaults.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(NoteNameSettings(clefs={"treble"}))
        >>> panel._build_range_rows()
        >>> list(panel.range_editors)
        ['treble']
        """
        while self.range_lay.count():
            item = self.range_lay.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        self.range_editors = {}
        for key in self._active_keys():
            low, high = self.cfg.range_for(key)
            editor = RangeEditor(key, low=low, high=high)
            editor.edited.connect(self._range_edited)
            self.range_editors[key] = editor
            self.range_lay.addWidget(editor)
        reset = QPushButton("Reset to defaults")
        reset.clicked.connect(self._reset_ranges)
        self.range_lay.addWidget(reset)
        self.range_lay.addStretch()

    def _range_edited(  # noqa: PLR0917  (a Qt slot: the signal passes positional arguments)
        self,
        key: str,
        low: int,
        high: int,
    ) -> None:
        """
        Take a changed range into the settings, save it and say so.

        Parameters
        ----------
        key : str
            The clef.
        low : int
            The lowest note, as a staff step.
        high : int
            The highest note.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(NoteNameSettings())
        >>> panel._range_edited("treble", 30, 40)
        >>> panel.cfg.ranges
        {'treble': (30, 40)}
        """
        self.cfg.ranges[key] = (low, high)
        self._save_and_emit()

    def _reset_ranges(self) -> None:
        """
        Go back to the default ranges and show them.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(NoteNameSettings(ranges={"treble": (30, 40)}))
        >>> panel._reset_ranges()
        >>> panel.cfg.ranges
        {}
        """
        self.cfg.ranges.clear()
        self._build_range_rows()
        self._save_and_emit()


class NoteNameSettingsPanel(_StaffRangePanel):
    """
    The settings of the note identification exercise: a menu leading to a page for each group of settings.

    Two layers: the menu (Clefs, Range, Key signatures, Note values, Note names, Accidentals and Octave) and a page for
    each. Edits are live: each changes the settings, saves them and emits `changed`.

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
        The letters and solfège choices, plus caret and function notation in the Scale degrees group.
    octave_row : _ToggleRow
        Whether the answer must include the written octave.
    range_editors : dict of str to RangeEditor
        The range editor of each clef in use, built when the Range page opens.

    Examples
    --------
    >>> panel = NoteNameSettingsPanel(NoteNameSettings())
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
        >>> panel = NoteNameSettingsPanel(NoteNameSettings())
        >>> panel.stack.count()  # the menu and five pages
        6
        """
        super().__init__(parent)
        self._persist = save_note_names
        self.cfg: NoteNameSettings = cfg
        self.stack = SlideStack()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        outer.addWidget(self.stack)

        # layer 1: menu
        menu = QWidget()
        mlay = QVBoxLayout(menu)
        mlay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        mlay.addWidget(QLabel("<h3>Settings</h3>"))
        self.clefs_row, self.range_row = _Row("Clefs"), _Row("Range", tall=True)
        self.keys_row, self.values_row, self.names_row = _Row("Key signatures"), _Row("Note values"), _Row("Note names")
        self.keys_diagram = KeyDiagram()
        self.keys_row.attach(self.keys_diagram)
        self.clef_pictures = ClefPictures()
        self.clefs_row.attach(self.clef_pictures)
        self.range_pictures = RangePictures(max_width=ROW_PICTURE_WIDTH)
        self.range_row.attach(self.range_pictures)
        self.value_pictures = ValuePictures()
        self.values_row.attach(self.value_pictures)
        self.name_picture = NamePicture()
        self.names_row.attach(self.name_picture)
        for index, row in enumerate(
            (
                self.clefs_row,
                self.range_row,
                self.keys_row,
                self.values_row,
                self.names_row,
            ),
            1,
        ):
            row.clicked.connect(lambda _=False, i=index: self._go(i))
            mlay.addWidget(row)
        self.accidentals_row = _ToggleRow("Accidentals")
        self.accidentals_row.setToolTip("Also ask notes with sharps, flats and naturals")
        self.accidentals_row.setOn(cfg.accidentals)
        self.accidentals_row.switched.connect(self._accidentals_toggled)
        mlay.addWidget(self.accidentals_row)
        self.octave_row = _ToggleRow("Octave")
        self.octave_row.setToolTip("Also ask which octave the note is in")
        self.octave_row.setOn(cfg.require_octave)
        self.octave_row.switched.connect(self._octave_toggled)
        mlay.addWidget(self.octave_row)
        mlay.addStretch()

        # layer 2: clefs
        self.boxes, clefs_page = _clefs_page(
            settings.RANGE_KEYS,
            selected=cfg.clefs,
            edited=self._clefs_edited,
            back=lambda: self._go(0),
        )

        # layer 2: range
        range_page = self._range_page()

        # layer 2: key signatures, each drawn as it would be written (flats on the left, sharps on the right)
        self.key_list = KeyChecklist(cfg.key_signatures)
        self.key_list.changed.connect(self._keys_edited)
        self.key_boxes = self.key_list.boxes
        keys_page = _subpage("Key signatures", body=self.key_list, back=lambda: self._go(0))

        # layer 2: note values, a vertical list: the engraved symbol, then its name
        self.value_boxes = {v: QCheckBox(VALUE_NAMES[v]) for v in NOTE_VALUES}
        values_body = QWidget()
        vlay = QVBoxLayout(values_body)
        vlay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        vlay.setSpacing(2)
        values_hint = QLabel("One of the checked values is picked at random.")
        values_hint.setWordWrap(True)
        vlay.addWidget(values_hint)
        for v, box in self.value_boxes.items():
            picture = ValuePictures([v], scale=1.25, center_stemless=True)
            box.setIcon(picture.to_icon())
            box.setIconSize(picture.size())
            box.setStyleSheet("QCheckBox { font-size: 11pt; }")
            box.setChecked(v in cfg.note_values)
            box.toggled.connect(self._values_edited)
            vlay.addWidget(box)
        vlay.addStretch()
        values_page = _subpage("Note values", body=values_body, back=lambda: self._go(0))

        # layer 2: note names
        self.naming_radios = {k: QRadioButton() for k in NAMINGS}
        for k, radio in self.naming_radios.items():
            _label_with_picture(radio, picture=NamePicture(k, scale=1.6), name=NAMINGS[k])
            radio.setText(NAMINGS[k].split(" (")[0])
            radio.setToolTip(degree_tooltip(NAMINGS[k]))
        names_body = QWidget()
        nlay = QVBoxLayout(names_body)
        nlay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        degree_group = QGroupBox("Scale degrees")
        degree_layout = QVBoxLayout(degree_group)
        naming_group = QButtonGroup(self)
        for k, radio in self.naming_radios.items():
            naming_group.addButton(radio)
            radio.setChecked(k == cfg.naming)
            radio.toggled.connect(self._names_edited)
            if k in settings.DEGREE_NAMINGS:
                degree_layout.addWidget(radio)
            else:
                nlay.addWidget(radio)
        nlay.addWidget(degree_group)
        names_page = _subpage("Note names", body=names_body, back=lambda: self._go(0))

        for page in (
            menu,
            clefs_page,
            range_page,
            keys_page,
            values_page,
            names_page,
        ):
            self.stack.addWidget(page)
        _guard_last(list(self.key_boxes.values()))
        _guard_last(list(self.value_boxes.values()))
        self._refresh_summaries()

    def _refresh_summaries(self) -> None:
        """
        Update the menu's summaries (the clef, range, key, value and naming pictures) from the settings.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(NoteNameSettings(clefs={"bass", "tenor"}))
        >>> panel._refresh_summaries()
        >>> panel.clef_pictures.toolTip()
        'Bass, Tenor'
        """
        super()._refresh_summaries()
        _show_keys(
            self.keys_row,
            diagram=self.keys_diagram,
            enabled=True,
            keys=set(self.cfg.active_keys()),
        )
        self.value_pictures.set_values(self.cfg.active_values())
        self.name_picture.set_naming(self.cfg.naming)

    # clefs page
    def _clefs_edited(self) -> None:
        """
        Take the checked clefs into the settings, save them and say so.

        The last checked clef cannot be unchecked.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(NoteNameSettings())
        >>> got = []
        >>> _ = panel.changed.connect(lambda: got.append(1))
        >>> panel.boxes["alto"].setChecked(True)
        >>> "alto" in panel.cfg.clefs, got
        (True, [1])
        """
        self.cfg.clefs = {c for c, b in self.boxes.items() if b.isChecked()}
        _guard_last(list(self.boxes.values()))  # the last checked clef can't be unchecked
        save_note_names()
        self.changed.emit()

    # key signatures / note values / note names pages
    def _keys_edited(self) -> None:
        """
        Take the checked key signatures into the settings, save them and say so.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(NoteNameSettings())
        >>> panel.key_boxes[2].setChecked(True)
        >>> 2 in panel.cfg.key_signatures
        True
        """
        self.cfg.key_signatures = {k for k, b in self.key_boxes.items() if b.isChecked()}
        _guard_last(list(self.key_boxes.values()))
        self._save_and_emit()

    def _values_edited(self) -> None:
        """
        Take the checked note values into the settings, save them and say so.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(NoteNameSettings())
        >>> panel.value_boxes["half"].setChecked(True)
        >>> "half" in panel.cfg.note_values
        True
        """
        self.cfg.note_values = {v for v, b in self.value_boxes.items() if b.isChecked()}
        _guard_last(list(self.value_boxes.values()))
        self._save_and_emit()

    def _names_edited(self) -> None:
        """
        Take the chosen naming (letters, solfège or scale degrees) into the settings, save it and say so.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(NoteNameSettings())
        >>> panel.naming_radios["solfege"].setChecked(True)
        >>> panel.cfg.naming
        'solfege'
        """
        self.cfg.naming = next(k for k, r in self.naming_radios.items() if r.isChecked())
        self._save_and_emit()

    def _accidentals_toggled(self, on: bool) -> None:
        """
        Take the Accidentals switch into the settings, save it and say so.

        Parameters
        ----------
        on : bool
            Whether sharps, flats and naturals are asked.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(NoteNameSettings())
        >>> panel._accidentals_toggled(True)
        >>> panel.cfg.accidentals
        True
        """
        self.cfg.accidentals = on
        self._save_and_emit()

    def _octave_toggled(self, on: bool) -> None:
        """
        Take the Octave switch into the settings, save it and say so.

        Parameters
        ----------
        on : bool
            Whether the answer must include the note's octave.

        Examples
        --------
        >>> panel = NoteNameSettingsPanel(NoteNameSettings())
        >>> panel._octave_toggled(True)
        >>> panel.cfg.require_octave
        True
        """
        self.cfg.require_octave = on
        self._save_and_emit()


def load_keyboard() -> None:
    """
    Load the saved keyboard exercise settings into the shared settings object.

    A saved range that is not a valid span of keys, or a key list with nothing usable in it, is ignored.

    Examples
    --------
    >>> cfg_ = settings.keyboard
    >>> cfg_.require_octave = True
    >>> save_keyboard()
    >>> cfg_.require_octave = False
    >>> load_keyboard()
    >>> cfg_.require_octave
    True
    >>> cfg_.require_octave = False
    >>> save_keyboard()
    """
    saved_settings = store()
    cfg = settings.keyboard
    cfg.black_keys = text_value(saved_settings, key="keyboard/blackKeys", default="true").lower() != "false"
    cfg.require_octave = text_value(saved_settings, key="keyboard/requireOctave", default="false").lower() == "true"
    try:
        low = int_value(saved_settings, key="keyboard/low", default=cfg.low)
        high = int_value(saved_settings, key="keyboard/high", default=cfg.high)
    except (TypeError, ValueError):
        return
    first, last = settings.KEYBOARD_FULL
    if first <= low <= high <= last:
        cfg.low, cfg.high = low, high
    cfg.key_signature = text_value(saved_settings, key="keyboard/keySignature", default="false").lower() == "true"
    keys = text_value(saved_settings, key="keyboard/keys", default="")
    if keys:
        cfg.keys = {int(k) for k in keys.split(",") if k.lstrip("-").isdigit() and abs(int(k)) <= 7} or cfg.keys


def save_keyboard() -> None:
    """
    Save the keyboard exercise settings.

    Examples
    --------
    >>> cfg_ = settings.keyboard
    >>> save_keyboard()
    >>> int(store().value("keyboard/low")) == cfg_.low
    True
    """
    saved_settings = store()
    cfg = settings.keyboard
    saved_settings.setValue("keyboard/blackKeys", "true" if cfg.black_keys else "false")
    saved_settings.setValue("keyboard/requireOctave", "true" if cfg.require_octave else "false")
    saved_settings.setValue("keyboard/low", cfg.low)
    saved_settings.setValue("keyboard/high", cfg.high)
    saved_settings.setValue("keyboard/keySignature", "true" if cfg.key_signature else "false")
    saved_settings.setValue("keyboard/keys", ",".join(str(k) for k in cfg.active_keys()))


def load_keyboard_intervals() -> None:
    """
    Load keyboard interval settings, ignoring invalid values and intervals that cannot fit.

    Examples
    --------
    >>> load_keyboard_intervals()
    >>> settings.keyboard_intervals.bounds()[0] < settings.keyboard_intervals.bounds()[1]
    True
    """
    saved = store()
    cfg = settings.keyboard_intervals
    defaults = settings.KeyboardIntervalSettings()
    try:
        low = int_value(saved, key="keyboardIntervals/low", default=defaults.low)
        high = int_value(saved, key="keyboardIntervals/high", default=defaults.high)
    except (TypeError, ValueError):
        low, high = defaults.bounds()
    first, last = settings.KEYBOARD_FULL
    cfg.low, cfg.high = (low, high) if first <= low < high <= last else defaults.bounds()
    selected = text_value(saved, key="keyboardIntervals/intervals", default=",".join(str(n) for n in range(1, 13)))
    cfg.intervals = {int(value) for value in selected.split(",") if value.isdecimal() and 1 <= int(value) <= last - first}
    if not cfg.intervals and selected.strip():
        cfg.intervals = {1}
    cfg.intervals = set(cfg.active_intervals())
    cfg.compact_buttons = text_value(saved, key="keyboardIntervals/compactButtons", default="false").lower() == "true"
    cfg.all_interval_buttons = text_value(saved, key="keyboardIntervals/allButtons", default="false").lower() == "true"
    try:
        cfg.button_count = int_value(saved, key="keyboardIntervals/buttonCount", default=6)
    except (TypeError, ValueError):
        cfg.button_count = 6
    cfg.button_count = cfg.answer_button_limit()


def save_keyboard_intervals(cfg: settings.KeyboardIntervalSettings) -> None:
    """
    Save the keyboard interval range and selected distances.

    Parameters
    ----------
    cfg : KeyboardIntervalSettings
        The settings to save.

    Examples
    --------
    >>> save_keyboard_intervals(settings.KeyboardIntervalSettings())
    >>> int(store().value("keyboardIntervals/low"))
    48
    """
    saved = store()
    low, high = cfg.bounds()
    saved.setValue("keyboardIntervals/low", low)
    saved.setValue("keyboardIntervals/high", high)
    saved.setValue("keyboardIntervals/intervals", ",".join(str(n) for n in cfg.active_intervals()))
    saved.setValue("keyboardIntervals/compactButtons", "true" if cfg.compact_buttons else "false")
    saved.setValue("keyboardIntervals/allButtons", "true" if cfg.all_interval_buttons else "false")
    saved.setValue("keyboardIntervals/buttonCount", cfg.answer_button_limit())


class _LabeledKeyCheckBox(QCheckBox):
    """
    Keep the signature and its separate label in the same click target.

    Examples
    --------
    >>> _LabeledKeyCheckBox().isCheckable()
    True
    """

    def hitButton(self, pos: QPoint) -> bool:
        """
        Accept clicks anywhere inside the labeled checkbox.

        Parameters
        ----------
        pos : QPoint
            The click position in widget coordinates.

        Returns
        -------
        bool
            Whether the click is inside the widget.

        Examples
        --------
        >>> _LabeledKeyCheckBox().hitButton(QPoint(-1, -1))
        False
        """
        return self.rect().contains(pos)


class KeyChecklist(QWidget):
    """
    Checkboxes for the 15 major keys, flats on the left and sharps on the right.

    At least one stays checked. Each is labeled with a picture of its signature.

    Attributes
    ----------
    changed : Signal
        Emitted after a box is checked or unchecked.
    boxes : dict of int to QCheckBox
        The checkbox of each key signature, from -7 (seven flats) to 7 (seven sharps).

    Examples
    --------
    >>> KeyChecklist({0, 2}).selected() == {0, 2}
    True
    """

    changed = Signal()

    def __init__(
        self,
        selected: set[int],
        *,
        allow_empty: bool = False,
        key_names: dict[int, str] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the checklist.

        Parameters
        ----------
        selected : set of int
            The key signatures to check initially.
        allow_empty : bool, default False
            Allow every key to be unchecked. Keyword-only.
        key_names : dict of int to str or None, default None
            Key names to display beside the signature diagrams. With None, show only diagrams. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns it. Keyword-only.

        Examples
        --------
        >>> len(KeyChecklist({0}).boxes)
        15
        """
        super().__init__(parent)
        self.allow_empty = allow_empty
        checkbox = _LabeledKeyCheckBox if key_names is not None else QCheckBox
        self.boxes = {k: checkbox() for k in range(-7, 8)}
        if key_names is not None:
            grid = QGridLayout(self)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(6)
            for count, box in self.boxes.items():
                name = key_names[count]
                signature = _key_label(count).split("·")[1].strip()
                description = f"{name}, {signature}" if count else f"{name}, no sharps or flats"
                box.setText(name)
                box.setToolTip(description)
                box.setAccessibleName(description)
                picture = KeySignaturePicture(count, scale=0.9)
                picture.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                label_width = box.sizeHint().width()
                contents = QHBoxLayout(box)
                contents.setContentsMargins(label_width + 4, 0, 0, 0)
                contents.addWidget(picture, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                box.setMinimumWidth(label_width + 4 + picture.width())
                box.setMinimumHeight(picture.height())
                if count:
                    grid.addWidget(box, abs(count), int(count > 0))
                else:
                    grid.addWidget(box, 0, 0, 1, 2)
            for column in range(2):
                grid.setColumnStretch(column, 1)
        else:
            for k, box in self.boxes.items():  # each key is labeled with its signature, as written after a treble clef
                description = f"{MAJOR_KEYS[k]} major, {_key_label(k).split('·')[1].strip()}"
                _label_with_picture(box, picture=KeySignaturePicture(k, scale=1.15), name=description)
            # Two framed groups: C major on its own, and the keys with sharps or flats (flats left, sharps right).
            outer = QVBoxLayout(self)
            outer.setContentsMargins(
                0,
                0,
                0,
                0,
            )
            outer.setSpacing(10)
            natural = QFrame()
            natural.setObjectName("keyGroup")  # styled in style.py
            natural_lay = QVBoxLayout(natural)
            natural_lay.addWidget(self.boxes[0])
            outer.addWidget(natural)
            marked = QFrame()
            marked.setObjectName("keyGroup")
            grid = QGridLayout(marked)
            for n in range(1, 8):
                grid.addWidget(self.boxes[-n], n - 1, 0)
                grid.addWidget(self.boxes[n], n - 1, 1)
            outer.addWidget(marked)
        for k, box in self.boxes.items():
            box.setChecked(k in selected)
            box.toggled.connect(self._toggled)
        if not self.allow_empty:
            _guard_last(list(self.boxes.values()))

    def selected(self) -> set[int]:
        """
        Return the checked key signatures.

        Returns
        -------
        set of int
            Sharps if positive, flats if negative.

        Examples
        --------
        >>> KeyChecklist({-3, 1}).selected() == {-3, 1}
        True
        """
        return {k for k, box in self.boxes.items() if box.isChecked()}

    def _toggled(self) -> None:
        """
        Keep one box checked, and say that something changed.

        Examples
        --------
        >>> checklist = KeyChecklist({0})
        >>> got = []
        >>> _ = checklist.changed.connect(lambda: got.append(1))
        >>> checklist.boxes[3].setChecked(True)
        >>> got
        [1]
        """
        if not self.allow_empty:
            _guard_last(list(self.boxes.values()))
        self.changed.emit()


class KeySignaturePage(QWidget):
    """
    The key signature sub-page: a switch for using key signatures at all, and the keys to draw from.

    Attributes
    ----------
    changed : Signal
        Emitted after the switch or a key is changed.
    switch_row : _ToggleRow
        The "Use key signatures" switch.
    checklist : KeyChecklist
        The keys; only enabled while the switch is on.

    Examples
    --------
    >>> page = KeySignaturePage(True, selected={0, 1})
    >>> page.enabled(), page.selected() == {0, 1}
    (True, True)
    """

    changed = Signal()

    def __init__(
        self,
        enabled: bool,
        *,
        selected: set[int],
        allow_empty: bool = False,
        key_names: dict[int, str] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the page.

        Parameters
        ----------
        enabled : bool
            Whether key signatures are on.
        selected : set of int
            The key signatures to check initially. Keyword-only.
        allow_empty : bool, default False
            Allow every key to be unchecked. Keyword-only.
        key_names : dict of int to str or None, default None
            Key names to display beside the signature diagrams. With None, show only diagrams. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns it. Keyword-only.

        Examples
        --------
        >>> page = KeySignaturePage(False, selected={0})
        >>> page.checklist.isEnabled()
        False
        """
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        lay.setSpacing(10)
        self.switch_row = _ToggleRow("Use key signatures")
        self.switch_row.setOn(enabled)
        self.switch_row.switched.connect(self._switched)
        self.checklist = KeyChecklist(selected, allow_empty=allow_empty, key_names=key_names)
        self.checklist.changed.connect(self.changed)
        self.checklist.setEnabled(enabled)  # the keys only matter while key signatures are on
        lay.addWidget(self.switch_row)
        self.keys_label = QLabel("Draw from these keys:")
        lay.addWidget(self.keys_label)
        lay.addWidget(self.checklist)

    def enabled(self) -> bool:
        """
        Report whether key signatures are switched on.

        Returns
        -------
        bool
            True if the switch is on.

        Examples
        --------
        >>> KeySignaturePage(True, selected={0}).enabled()
        True
        """
        return self.switch_row.isOn()

    def selected(self) -> set[int]:
        """
        Return the checked key signatures.

        Returns
        -------
        set of int
            Sharps if positive, flats if negative.

        Examples
        --------
        >>> KeySignaturePage(True, selected={-2, 0}).selected() == {-2, 0}
        True
        """
        return self.checklist.selected()

    def _switched(self, on: bool) -> None:
        """
        Enable the keys only while key signatures are on, and say that something changed.

        Parameters
        ----------
        on : bool
            The switch's new state.

        Examples
        --------
        >>> page = KeySignaturePage(True, selected={0})
        >>> got = []
        >>> _ = page.changed.connect(lambda: got.append(1))
        >>> page._switched(False)
        >>> page.checklist.isEnabled(), got
        (False, [1])
        """
        self.checklist.setEnabled(on)
        self.changed.emit()


class KeyboardSettingsPanel(ExerciseSettingsPanel):
    """
    The settings of the keyboard exercise: a menu with a page for the range of keys.

    The menu has Range, Black keys, Octave number and Key signatures. Edits are live: each changes the settings, saves them
    and emits `changed`.

    Attributes
    ----------
    cfg : KeyboardSettings
        The settings being edited.
    stack : SlideStack
        The menu and its pages.
    span : KeyboardSpan
        The miniature piano on the Range page, which can be dragged to choose the keys.
    low_label, high_label : QLabel
        The names of the lowest and highest key asked.
    key_page : KeySignaturePage
        The key signature sub-page.

    Examples
    --------
    >>> panel = KeyboardSettingsPanel(settings.KeyboardSettings())
    >>> panel.low_label.text(), panel.high_label.text()
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
        >>> KeyboardSettingsPanel(settings.KeyboardSettings()).stack.count()  # the menu, the range and the keys
        3
        """
        super().__init__(parent)
        self.cfg = cfg
        self.stack = SlideStack()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        outer.addWidget(self.stack)

        # layer 1: menu
        menu = QWidget()
        mlay = QVBoxLayout(menu)
        mlay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        mlay.addWidget(QLabel("<h3>Settings</h3>"))
        self.range_row = _Row("Range", tall=True)
        self.range_row.clicked.connect(lambda: self._go(1))
        self.range_keyboard = KeyboardSpan(compact=True, size=(ROW_PICTURE_WIDTH, 36))  # the asked span, lit on a miniature piano
        self.range_row.attach(self.range_keyboard)
        self.black_keys_row = _ToggleRow("Black keys")
        self.black_keys_row.setToolTip("Also ask the black keys, answered by either of their names")
        self.black_keys_row.setOn(cfg.black_keys)
        self.black_keys_row.switched.connect(self._black_keys_toggled)
        self.octave_row = _ToggleRow("Octave number")
        self.octave_row.setToolTip("Answer with the octave as well, for example C4")
        self.octave_row.setOn(cfg.require_octave)
        self.octave_row.switched.connect(self._octave_toggled)
        self.keys_row = _Row("Key signatures")  # opens a page: use them or not, and which keys
        self.keys_row.setToolTip("Show a key signature above the keyboard and require the name that fits it")
        self.keys_row.clicked.connect(lambda: self._go(2))
        self.keys_diagram = KeyDiagram()
        self.keys_row.attach(self.keys_diagram)
        for row in (
            self.range_row,
            self.black_keys_row,
            self.octave_row,
            self.keys_row,
        ):
            mlay.addWidget(row)
        mlay.addStretch()

        # layer 2: range
        body = QWidget()
        blay = QVBoxLayout(body)
        blay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        blay.setSpacing(10)
        blay.addWidget(QLabel("Keys that will be asked: click and drag on the keyboard to choose them."))
        self.span = KeyboardSpan()
        self.span.dragged.connect(self._set_range)
        blay.addWidget(self.span)
        self.low_label, self.high_label = QLabel(), QLabel()
        self.arrows = {}
        for title, label, which in (("Lowest key", self.low_label, "low"), ("Highest key", self.high_label, "high")):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"<b>{title}</b>"), 1)
            down = _arrow(Qt.ArrowType.LeftArrow, tip=f"{title}: one key down")
            up = _arrow(Qt.ArrowType.RightArrow, tip=f"{title}: one key up")
            down.clicked.connect(lambda _=False, w=which: self._step(w, delta=-1))
            up.clicked.connect(lambda _=False, w=which: self._step(w, delta=1))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumWidth(48)
            row.addWidget(down)
            row.addWidget(label)
            row.addWidget(up)
            blay.addLayout(row)
            self.arrows[which] = (down, up)
        self.entire = QPushButton("Entire keyboard")
        self.entire.clicked.connect(lambda: self._set_range(*settings.KEYBOARD_FULL))
        self.default = QPushButton("Reset to default")
        self.default.clicked.connect(lambda: self._set_range(*settings.KEYBOARD_DEFAULT))
        blay.addWidget(self.entire)
        blay.addWidget(self.default)
        range_page = _subpage("Range", body=body, back=lambda: self._go(0))

        # layer 2: key signatures
        self.key_page = KeySignaturePage(cfg.key_signature, selected=cfg.keys)
        self.key_page.changed.connect(self._keys_edited)
        keys_page = _subpage("Key signatures", body=self.key_page, back=lambda: self._go(0))

        self.stack.addWidget(menu)
        self.stack.addWidget(range_page)
        self.stack.addWidget(keys_page)
        self._refresh_range()
        self._show_keys()

    def _go(self, index: int) -> None:
        """
        Slide to a page, refreshing the menu's summaries when going back to it.

        Parameters
        ----------
        index : int
            0 for the menu, 1 for the Range page, 2 for the key signatures.

        Examples
        --------
        >>> panel = KeyboardSettingsPanel(settings.KeyboardSettings())
        >>> panel._go(1)
        >>> panel.stack.sliding
        True
        """
        if self.stack.sliding or index == self.stack.currentIndex():
            return
        self.stack.slide_to(index)

    def _refresh_range(self) -> None:
        """
        Show the range everywhere it appears and enable only the arrows that can still move.

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
        self.arrows["low"][1].setEnabled(cfg.low < cfg.high)  # the lowest key can't pass the highest
        self.arrows["high"][0].setEnabled(cfg.high > cfg.low)
        self.arrows["high"][1].setEnabled(cfg.high < last)
        self.range_keyboard.set_span(cfg.low, hi=cfg.high)
        self.range_keyboard.setToolTip(f"{key_name(cfg.low)} to {key_name(cfg.high)}")

    def _step(
        self,
        which: str,
        *,
        delta: int,
    ) -> None:
        """
        Move one end of the range by some keys, keeping the lowest below the highest and both on the piano.

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
        >>> panel._step("high", delta=-100)  # the highest key cannot pass the lowest
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
        Take the Black keys switch into the settings, save it and say so.

        Parameters
        ----------
        on : bool
            Whether the black keys are asked.

        Examples
        --------
        >>> cfg = settings.KeyboardSettings()
        >>> KeyboardSettingsPanel(cfg)._black_keys_toggled(False)
        >>> cfg.black_keys
        False
        """
        self.cfg.black_keys = on
        self._save_and_emit()

    def _octave_toggled(self, on: bool) -> None:
        """
        Take the Octave number switch into the settings, save it and say so.

        Parameters
        ----------
        on : bool
            Whether the answer must include the octave.

        Examples
        --------
        >>> cfg = settings.KeyboardSettings()
        >>> KeyboardSettingsPanel(cfg)._octave_toggled(True)
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
        >>> panel = KeyboardSettingsPanel(settings.KeyboardSettings())
        >>> panel._show_keys()
        >>> panel.keys_row.value.text()  # key signatures are off
        'Off'
        """
        _show_keys(
            self.keys_row,
            diagram=self.keys_diagram,
            enabled=self.cfg.key_signature,
            keys=set(self.cfg.active_keys()),
        )

    def _keys_edited(self) -> None:
        """
        Take the key signature page into the settings, save it and say so.

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

    def _save_and_emit(self) -> None:
        """
        Save the keyboard settings and emit `changed`.

        Examples
        --------
        >>> panel = KeyboardSettingsPanel(settings.KeyboardSettings())
        >>> got = []
        >>> _ = panel.changed.connect(lambda: got.append(1))
        >>> panel._save_and_emit()
        >>> got
        [1]
        """
        save_keyboard()
        self.changed.emit()


def load_construction() -> None:
    """
    Load the saved note construction settings into the shared settings object.

    Examples
    --------
    >>> store().setValue("construction/accidentals", "true")
    >>> load_construction()
    >>> settings.construction.accidentals
    False
    """
    saved_settings = store()
    cfg = settings.construction
    saved = saved_settings.value("construction/clefs")
    if saved is not None:
        text = saved if isinstance(saved, str) else ",".join(saved)
        cfg.clefs = {c for c in text.split(",") if c in settings.RANGE_KEYS} or cfg.clefs
    cfg.question_type = (
        "notes" if text_value(saved_settings, key="construction/questionType", default="scale") == "notes" else "scale"
    )
    degrees = text_value(saved_settings, key="construction/degrees", default="")
    cfg.degrees = {n for n in range(1, 8) if str(n) in degrees.split(",")} or set(range(1, 8))
    cfg.octave = text_value(saved_settings, key="construction/octave", default="true").lower() == "true"
    cfg.accidentals = False  # ignore the retired setting in existing profiles
    mode = text_value(saved_settings, key="construction/keyMode", default="major")
    cfg.major = mode != "minor"
    cfg.minor = mode in {"minor", "both"}
    staff_keys = text_value(saved_settings, key="construction/staffKeys", default="0")
    cfg.staff_keys = {int(k) for k in staff_keys.split(",") if k.lstrip("-").isdigit() and abs(int(k)) <= 7} or {0}
    cfg.key_signature = True
    used_signatures = text_value(saved_settings, key="construction/keySignature", default="false").lower() == "true"
    keys = text_value(saved_settings, key="construction/keys", default="")
    if keys:
        cfg.keys = {int(k) for k in keys.split(",") if k.lstrip("-").isdigit() and abs(int(k)) <= 7} or cfg.keys
    minor_keys = text_value(saved_settings, key="construction/minorKeys", default="")
    cfg.minor_keys = {int(k) for k in minor_keys.split(",") if k.lstrip("-").isdigit() and abs(int(k)) <= 7} or None
    if not used_signatures:
        cfg.keys = {0}
        cfg.minor_keys = {0}


class _ScaleKeyPicker(QTabWidget):
    """
    Select major and minor keys independently.

    Examples
    --------
    >>> _ScaleKeyPicker(major_keys={0}, minor_keys={-2}).count()
    2
    """

    def __init__(self, *, major_keys: set[int], minor_keys: set[int]) -> None:
        """
        Build one checklist per mode.

        Parameters
        ----------
        major_keys : set of int
            Selected major signatures. Keyword-only.
        minor_keys : set of int
            Selected minor signatures. Keyword-only.

        Examples
        --------
        >>> _ScaleKeyPicker(major_keys=set(), minor_keys={0}).currentIndex()
        1
        """
        super().__init__()
        major_names = {count: f"{name}M" for count, name in MAJOR_KEYS.items()}
        self.major_keys = KeyChecklist(major_keys, allow_empty=True, key_names=major_names)
        minor_names = {count: f"{mode_tonic(count, mode='Natural minor (Aeolian)').name}m" for count in range(-7, 8)}
        self.minor_keys = KeyChecklist(
            minor_keys,
            allow_empty=True,
            key_names=minor_names,
        )
        self.setObjectName("settingsTabs")
        self.setAccessibleName("Key lists")
        for label, checklist in (
            ("Major", self.major_keys),
            ("Minor", self.minor_keys),
        ):
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.addWidget(checklist)
            tab_layout.addStretch()
            self.addTab(tab, label)
        self.setCurrentIndex(0 if major_keys else 1)


class NoteConstructionSettingsPanel(ExerciseSettingsPanel):
    """
    The settings of the note construction exercise: a menu with a page for the staff and one for the keys.

    The menu has Clefs, Staff Key, Question Type, and Octave. Edits are live: each changes the settings, saves them and
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
    >>> panel = NoteConstructionSettingsPanel(settings.ConstructionSettings())
    >>> sorted(panel.boxes)[:3]
    ['alto', 'baritone', 'bass']
    """

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
        >>> NoteConstructionSettingsPanel(settings.ConstructionSettings()).stack.count()
        4
        """
        super().__init__(parent)
        self.cfg = cfg
        self.stack = SlideStack()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        outer.addWidget(self.stack)

        # layer 1: menu
        menu = QWidget()
        mlay = QVBoxLayout(menu)
        mlay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        mlay.addWidget(QLabel("<h3>Settings</h3>"))
        self.clefs_row = _Row("Clefs")
        self.clefs_row.clicked.connect(lambda: self._go(1))
        self.clef_pictures = ClefPictures()
        self.clefs_row.attach(self.clef_pictures)
        self.staff_key_row = _Row("Staff Key")
        self.staff_key_row.clicked.connect(lambda: self._go(3))
        self.staff_keys_diagram = KeyDiagram()
        self.staff_key_row.attach(self.staff_keys_diagram)
        self.keys_row = _Row("Question Type")
        self.keys_row.setToolTip("Choose note name or scale key questions")
        self.keys_row.clicked.connect(lambda: self._go(2))
        self.octave_row = _ToggleRow("Octave")
        self.octave_row.setToolTip("Show and require a specific octave")
        self.octave_row.setOn(cfg.octave)
        self.octave_row.switched.connect(self._octave_toggled)
        for row in (self.clefs_row, self.staff_key_row, self.keys_row, self.octave_row):
            mlay.addWidget(row)
        mlay.addStretch()

        # layer 2: clefs
        self.boxes, clefs_page = _clefs_page(
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
        self.key_tabs = _ScaleKeyPicker(
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
        self.scale_key_scroll = _scrolling(scale_options)
        question_layout.addWidget(self.scale_key_scroll, 1)
        self.scale_key_scroll.setVisible(self.scale_key_choice.isChecked())
        question_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scale_key_choice.toggled.connect(self._question_type_changed)
        keys_page = _subpage("Question Type", body=question_body, back=lambda: self._go(0), fill=True)

        self.staff_keys = KeyChecklist(cfg.staff_keys or {0})
        self.staff_keys.changed.connect(self._staff_keys_edited)
        staff_page = _subpage("Staff Key", body=_scrolling(self.staff_keys), back=lambda: self._go(0), fill=True)

        for page in (menu, clefs_page, keys_page, staff_page):
            self.stack.addWidget(page)
        self._refresh_summaries()

    def _go(self, index: int) -> None:
        """
        Slide to a page, refreshing the menu's summaries when going back to it.

        Parameters
        ----------
        index : int
            0 for the menu, 1 for the Staff page, 2 for Question Type, and 3 for Staff Key.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(settings.ConstructionSettings())
        >>> panel._go(1)
        >>> panel.stack.sliding
        True
        """
        if self.stack.sliding or index == self.stack.currentIndex():
            return
        if index == 0:
            self._refresh_summaries()
        self.stack.slide_to(index)

    def _refresh_summaries(self) -> None:
        """
        Update the menu's clef and key signature summaries from the settings.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(settings.ConstructionSettings(clefs={"bass"}))
        >>> panel._refresh_summaries()
        >>> panel.clef_pictures.toolTip()
        'Bass'
        """
        self.clef_pictures.set_clefs(self.cfg.active_clefs())
        self._show_keys()

    def _save_and_emit(self) -> None:
        """
        Save the note construction settings and emit `changed`.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(settings.ConstructionSettings())
        >>> panel._save_and_emit()
        """
        saved_settings = store()
        cfg = self.cfg
        saved_settings.setValue("construction/clefs", ",".join(c for c in settings.RANGE_KEYS if c in cfg.clefs))
        saved_settings.setValue("construction/keySignature", "true")
        saved_settings.setValue("construction/questionType", cfg.question_type)
        saved_settings.setValue("construction/degrees", ",".join(str(n) for n in sorted(cfg.degrees)))
        saved_settings.setValue("construction/octave", "true" if cfg.octave else "false")
        saved_settings.setValue("construction/staffKeys", ",".join(str(k) for k in sorted(cfg.staff_keys or {0})))
        saved_settings.setValue("construction/keyMode", ("both" if cfg.major else "minor") if cfg.minor else "major")
        saved_settings.setValue("construction/keys", ",".join(str(k) for k in cfg.active_keys()))
        saved_settings.setValue("construction/minorKeys", ",".join(str(k) for k in sorted(cfg.minor_keys or cfg.keys)))
        self.changed.emit()

    def _degrees_edited(self) -> None:
        """
        Save the scale degrees selected for questions.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(settings.ConstructionSettings())
        >>> panel._degrees_edited()
        """
        self.cfg.degrees = self.degree_choices.selected()
        self._save_and_emit()

    def _question_type_changed(self, scale_key: bool) -> None:
        """
        Save the question type and show the scale key lists when relevant.

        Parameters
        ----------
        scale_key : bool
            Whether to ask for a scale degree.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(settings.ConstructionSettings())
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
        >>> panel = NoteConstructionSettingsPanel(settings.ConstructionSettings())
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
        >>> panel = NoteConstructionSettingsPanel(settings.ConstructionSettings())
        >>> panel._staff_keys_edited()
        """
        self.cfg.staff_keys = self.staff_keys.selected()
        self.staff_keys_diagram.set_keys(self.cfg.staff_keys)
        self._save_and_emit()

    def _clefs_edited(self) -> None:
        """
        Take the checked clefs into the settings, save them and say so.

        The last checked clef cannot be unchecked.

        Examples
        --------
        >>> cfg = settings.ConstructionSettings()
        >>> panel = NoteConstructionSettingsPanel(cfg)
        >>> panel.boxes["grand"].setChecked(True)
        >>> "grand" in cfg.clefs
        True
        """
        self.cfg.clefs = {c for c, b in self.boxes.items() if b.isChecked()}
        _guard_last(list(self.boxes.values()))  # the last checked choice can't be unchecked
        self._save_and_emit()

    def _show_keys(self) -> None:
        """
        Update the menu's key signature summary.

        Examples
        --------
        >>> panel = NoteConstructionSettingsPanel(settings.ConstructionSettings())
        >>> panel._show_keys()
        >>> panel.keys_row.value.text()
        'Scale and Degree'
        """
        self.staff_keys_diagram.set_keys(self.cfg.staff_keys or {0})
        _guard_last([*self.major_keys.boxes.values(), *self.minor_keys.boxes.values()])
        self.keys_row.value.setText("Notes Only" if self.cfg.question_type == "notes" else "Scale and Degree")

    def _keys_edited(self) -> None:
        """
        Take the key signature page into the settings, save it and say so.

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


def load_arpeggio() -> None:
    """
    Load the saved arpeggio settings into the shared settings object.

    Anything in the saved data that is not valid is ignored, and a list with nothing valid in it leaves the setting as it was.

    Examples
    --------
    >>> store().setValue("arpeggio/types", "major")
    >>> load_arpeggio()
    >>> settings.arpeggio.types
    {'major'}
    >>> settings.arpeggio.types = {"major", "minor", "dominant 7th", "diminished 7th"}
    >>> store().setValue("arpeggio/types", ",".join(settings.arpeggio.active_types()))
    """
    saved_settings = store()
    cfg = settings.arpeggio
    clefs = text_value(saved_settings, key="arpeggio/clefs", default="")
    if clefs:
        cfg.clefs = {c for c in clefs.split(",") if c in CLEFS} or cfg.clefs
    types = text_value(saved_settings, key="arpeggio/types", default="")
    if types:
        cfg.types = {t for t in types.split(",") if t in settings.ARPEGGIO_TYPES} or cfg.types
    inversions = text_value(saved_settings, key="arpeggio/inversions", default="")
    if inversions:
        found = {int(i) for i in inversions.split(",") if i.isdigit() and int(i) in settings.INVERSIONS}
        cfg.inversions = found or cfg.inversions
    cfg.key_signature = text_value(saved_settings, key="arpeggio/keySignature", default="false").lower() == "true"
    keys = text_value(saved_settings, key="arpeggio/keys", default="")
    if keys:
        cfg.keys = {int(k) for k in keys.split(",") if k.lstrip("-").isdigit() and abs(int(k)) <= 7} or cfg.keys


class ChoiceChecklist(QWidget):
    """
    Checkboxes for a list of choices, optionally under headings and allowing an empty selection.

    Attributes
    ----------
    changed : Signal
        Emitted after a box is checked or unchecked.
    allow_empty : bool
        Whether all choices may be unchecked.
    boxes : dict
        The checkbox of each choice, by its key.

    Examples
    --------
    >>> groups = [("Triads", [("major", "Major"), ("minor", "Minor")]), ("", [("x", "Other")])]
    >>> checklist = ChoiceChecklist(groups, selected={"major"})
    >>> checklist.selected()
    {'major'}
    """

    changed = Signal()

    def __init__(
        self,
        groups: list[tuple[str, list[tuple[object, str]]]],
        *,
        selected: set,
        allow_empty: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the checklist.

        Parameters
        ----------
        groups : list of tuple of (str, list of tuple of (object, str))
            The headings and, under each, the choices as (key, label); an empty heading shows none.
        selected : set
            The keys to check initially. Keyword-only.
        allow_empty : bool, default False
            Allow all choices to be unchecked. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns it. Keyword-only.

        Examples
        --------
        >>> checklist = ChoiceChecklist([("", [(0, "Root"), (1, "1st")])], selected={0})
        >>> # noinspection PyTypeChecker
        >>> sorted(checklist.boxes)
        [0, 1]
        """
        super().__init__(parent)
        self.allow_empty = allow_empty
        self.boxes: dict[object, QCheckBox] = {}
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        lay.setSpacing(6)
        for title, items in groups:
            if title:
                heading = QLabel(title)
                heading.setStyleSheet("color: gray;")
                lay.addWidget(heading)
            for key, label in items:
                box = DegreeCheckBox(label) if "̂" in label else QCheckBox(label)
                box.setChecked(key in selected)
                box.toggled.connect(self._toggled)
                self.boxes[key] = box
                lay.addWidget(box)
        if not self.allow_empty:
            _guard_last(list(self.boxes.values()))

    def selected(self) -> set:
        """
        Return the checked choices.

        Returns
        -------
        set
            The keys of the checked boxes.

        Examples
        --------
        >>> ChoiceChecklist([("", [(0, "Root"), (1, "1st")])], selected={0, 1}).selected()
        {0, 1}
        """
        return {k for k, box in self.boxes.items() if box.isChecked()}

    def _toggled(self) -> None:
        """
        Keep one box checked, and say that something changed.

        Examples
        --------
        >>> checklist = ChoiceChecklist([("", [(0, "Root"), (1, "1st")])], selected={0})
        >>> got = []
        >>> _ = checklist.changed.connect(lambda: got.append(1))
        >>> checklist.boxes[1].setChecked(True)
        >>> got
        [1]
        """
        if not self.allow_empty:
            _guard_last(list(self.boxes.values()))
        self.changed.emit()


def _buttons_page(
    cfg: settings.IntervalSettings,
    *,
    changed: Callable[[], None],
    back: Callable[[], None],
) -> QWidget:
    """
    Build the shared Limited and All answer-button submenu.

    Parameters
    ----------
    cfg : IntervalSettings
        The exercise that owns the button mode and count.
    changed : callable
        Save and apply an edit.
    back : callable
        Return to the exercise settings menu.

    Returns
    -------
    QWidget
        The Buttons page with the count picker below Limited.

    Examples
    --------
    Choosing All hides the count picker and retains its last value.
    """
    body = QWidget()
    layout = QVBoxLayout(body)
    layout.setContentsMargins(0, 0, 0, 0)
    limited = QRadioButton("Limited")
    all_buttons = QRadioButton("All")
    layout.addWidget(limited)
    count_row = QWidget()
    count_layout = QHBoxLayout(count_row)
    count_layout.setContentsMargins(0, 0, 0, 0)
    count_label = QLabel("Button count")
    count = FieldComboBox()
    count.setAccessibleName("Button count")
    count_label.setBuddy(count)
    for value in range(2, 11):
        count.addItem(str(value), value)
    count.setCurrentIndex(count.findData(cfg.button_count))
    count_layout.addWidget(count_label)
    count_layout.addWidget(count, 1)
    layout.addWidget(count_row)
    layout.addWidget(all_buttons)
    limited.setChecked(cfg.button_mode == "limited")
    all_buttons.setChecked(cfg.button_mode == "all")
    count_row.setVisible(limited.isChecked())

    def save_buttons() -> None:
        """
        Save the button mode and count when their controls change.

        Examples
        --------
        Open the Buttons page and choose All to save that mode.
        """
        cfg.button_mode = "limited" if limited.isChecked() else "all"
        cfg.button_count = count.currentData()
        count_row.setVisible(limited.isChecked())
        changed()

    limited.toggled.connect(save_buttons)
    count.currentIndexChanged.connect(save_buttons)
    return _subpage("Buttons", body=body, back=back)


def load_intervals() -> None:
    """
    Restore the saved staff interval options, keeping valid choices and per-clef ranges.

    Examples
    --------
    >>> load_intervals()
    >>> bool(settings.intervals.active_clefs())
    True
    """
    saved = store()
    cfg = settings.intervals
    defaults = settings.IntervalSettings()
    cfg.clefs = (
        set(text_value(saved, key="intervals/clefs", default="treble,bass").split(",")) & set(settings.RANGE_KEYS)
        or defaults.clefs
    )
    cfg.displays = (
        set(text_value(saved, key="intervals/display", default="Melodic").split(",")) & set(settings.INTERVAL_DISPLAYS)
        or defaults.displays
    )
    cfg.quality = text_value(saved, key="intervals/quality", default="true") != "false"
    cfg.button_mode = "all" if text_value(saved, key="intervals/buttonMode", default="limited") == "all" else "limited"
    try:
        cfg.button_count = max(2, min(10, int_value(saved, key="intervals/buttonCount", default=6)))
    except ValueError:
        cfg.button_count = defaults.button_count
    keys = text_value(saved, key="intervals/staffKeys", default="0").split(",")
    cfg.staff_keys = {key for key in range(-7, 8) if str(key) in keys} or {0}
    names = text_value(saved, key="intervals/intervals", default=",".join(defaults.intervals))
    cfg.intervals = set(names.split(",")) & settings.WRITTEN_INTERVALS.keys()
    cfg.ranges = {}
    for clef, (minimum, maximum) in RANGE_LIMITS.items():
        bounds = text_value(saved, key=f"intervals/range/{clef}", default="").split(",")
        if len(bounds) == 2 and all(value.isdecimal() for value in bounds):
            low, high = map(int, bounds)
            if minimum <= low <= high <= maximum:
                cfg.ranges[clef] = (low, high)


class IntervalSettingsPanel(_StaffRangePanel):
    """
    Choose the notation and answer format for written intervals.

    Examples
    --------
    >>> IntervalSettingsPanel(settings.IntervalSettings()).stack.count()
    7
    """

    def __init__(self, cfg: settings.IntervalSettings) -> None:
        """
        Build the menu and its six submenus.

        Parameters
        ----------
        cfg : IntervalSettings
            The interval exercise settings.

        Examples
        --------
        >>> IntervalSettingsPanel(settings.IntervalSettings()).quality_row.isOn()
        True
        """
        super().__init__()
        self.cfg: settings.IntervalSettings = cfg
        self._persist = self._save
        self.stack = SlideStack()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.stack)
        menu = QWidget()
        layout = QVBoxLayout(menu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("<h3>Settings</h3>"))
        self.stack.addWidget(menu)
        self.clefs_row = _Row("Clefs")
        self.clef_pictures = ClefPictures()
        self.clefs_row.attach(self.clef_pictures)
        self.range_row = _Row("Range", tall=True)
        self.range_pictures = RangePictures(max_width=ROW_PICTURE_WIDTH)
        self.range_row.attach(self.range_pictures)
        self.staff_key_row = _Row("Staff Key")
        self.key_diagram = KeyDiagram()
        self.staff_key_row.attach(self.key_diagram)
        self.display_row = _Row("Display")
        self.quality_row = _ToggleRow("Quality")
        self.quality_row.setToolTip("Require the interval’s quality as well as its number")
        self.quality_row.setOn(cfg.quality)
        self.intervals_row = _Row("Intervals")
        self.buttons_row = _Row("Buttons")
        for index, row in enumerate(
            (self.clefs_row, self.range_row, self.staff_key_row, self.display_row, self.intervals_row, self.buttons_row),
            1,
        ):
            if row is self.intervals_row:
                layout.addWidget(self.quality_row)
            row.clicked.connect(lambda _checked=False, page=index: self._go(page))
            layout.addWidget(row)
        layout.addStretch()

        self.boxes, clefs = _clefs_page(
            settings.RANGE_KEYS,
            selected=cfg.clefs,
            edited=self._save_and_emit,
            back=lambda: self._go(0),
        )
        self.stack.addWidget(clefs)
        self.stack.addWidget(self._range_page())
        self.staff_keys = KeyChecklist(cfg.staff_keys)
        self.display = ChoiceChecklist([("", [(style, style) for style in settings.INTERVAL_DISPLAYS])], selected=cfg.displays)
        self.interval_list = ChoiceChecklist(
            [
                (title, [(name, name) for name, iv in settings.WRITTEN_INTERVALS.items() if lo <= iv.number <= hi])
                for title, lo, hi in (("Simple intervals", 1, 8), ("Compound intervals", 9, 15))
            ],
            selected=cfg.intervals,
            allow_empty=True,
        )
        for title, picker in (("Staff Key", self.staff_keys), ("Display", self.display)):
            self.stack.addWidget(_subpage(title, body=_scrolling(picker), back=lambda: self._go(0), fill=True))
            picker.changed.connect(self._save_and_emit)

        intervals = QWidget()
        interval_layout = QVBoxLayout(intervals)
        interval_layout.setContentsMargins(0, 0, 0, 0)
        self.select_all = _ToggleRow("Select all")
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
        self.stack.addWidget(_subpage("Intervals", body=_scrolling(intervals), back=lambda: self._go(0), fill=True))
        self.stack.addWidget(_buttons_page(cfg, changed=self._save_and_emit, back=lambda: self._go(0)))
        self.quality_row.switched.connect(self._save_and_emit)
        self._refresh_summaries()

    def _select_all(self, on: bool) -> None:
        """
        Temporarily include all spellings or restore the previous checks.

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
        self._set_intervals(set(settings.WRITTEN_INTERVALS) if on else self._previous_intervals)

    def _select_span(self, low: int, high: int) -> None:  # noqa: PLR0917 (Qt passes both endpoints positionally)
        """
        Check every spelling whose written interval number is between the handles.

        Parameters
        ----------
        low, high : int
            Inclusive written interval numbers.

        Examples
        --------
        Set both ends to three to check all the thirds.
        """
        self._set_intervals({name for name, iv in settings.WRITTEN_INTERVALS.items() if low <= iv.number <= high})

    def _set_intervals(self, names: set[str]) -> None:
        """
        Apply a bulk interval selection in one edit.

        Parameters
        ----------
        names : set of str
            Checked interval spellings.

        Examples
        --------
        Moving a slider handle generates one new question.
        """
        for name, box in self.interval_list.boxes.items():
            box.blockSignals(True)
            box.setChecked(name in names)
            box.blockSignals(False)
        self._save_and_emit()

    def _refresh_summaries(self) -> None:
        """
        Show the selected clefs, ranges, signatures, displays and interval count.

        Examples
        --------
        >>> IntervalSettingsPanel(settings.IntervalSettings()).display_row.value.text()
        'Melodic'
        """
        super()._refresh_summaries()
        _show_keys(self.staff_key_row, diagram=self.key_diagram, enabled=True, keys=self.cfg.staff_keys)
        self.display_row.value.setText(", ".join(d for d in settings.INTERVAL_DISPLAYS if d in self.cfg.displays))
        self.buttons_row.value.setText(self.cfg.button_mode.title())
        numbers = [settings.WRITTEN_INTERVALS[name].number for name in self.cfg.intervals]
        low, high = min(numbers, default=1), max(numbers, default=1)
        self.slider.set_range(low, high=high, maximum=15, active=bool(numbers))
        self.interval_span.setText(f"Interval numbers  {low}–{high}" if numbers else "No intervals selected")
        if self.cfg.intervals != set(settings.WRITTEN_INTERVALS):
            self.select_all.setOn(False)
        count = len(self.cfg.intervals)
        self.intervals_row.value.setText(f"{count} selected" if count else "None")

    def _save(self) -> None:
        """
        Save the current selection and update its menu previews.

        Examples
        --------
        Editing a pitch limit saves it for its own clef.
        """
        cfg = self.cfg
        cfg.clefs = {c for c, box in self.boxes.items() if box.isChecked()}
        _guard_last(self.boxes.values())
        cfg.staff_keys = self.staff_keys.selected()
        cfg.displays = self.display.selected()
        cfg.quality = self.quality_row.isOn()
        cfg.intervals = self.interval_list.selected()
        saved = store()
        saved.setValue("intervals/buttonMode", cfg.button_mode)
        saved.setValue("intervals/buttonCount", cfg.button_count)
        saved.setValue("intervals/clefs", ",".join(sorted(cfg.clefs)))
        saved.setValue("intervals/staffKeys", ",".join(map(str, sorted(cfg.staff_keys))))
        saved.setValue("intervals/display", ",".join(sorted(cfg.displays)))
        saved.setValue("intervals/quality", "true" if cfg.quality else "false")
        saved.setValue("intervals/intervals", ",".join(sorted(cfg.intervals)))
        saved.remove("intervals/range")
        for clef, (low, high) in cfg.ranges.items():
            saved.setValue(f"intervals/range/{clef}", f"{low},{high}")
        self._refresh_summaries()


class KeyboardIntervalSettingsPanel(ExerciseSettingsPanel):
    """
    Range and interval selection pages for keyboard interval identification.

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
    >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
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
        >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
        >>> panel.low_label.text(), panel.high_label.text()
        ('C3', 'C5')
        """
        super().__init__(parent)
        self.cfg = cfg
        cfg.low, cfg.high = cfg.bounds()
        cfg.intervals = set(cfg.active_intervals())
        self._selection_before_all = set(cfg.intervals)
        self._select_all_active = False
        self.stack = SlideStack()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.stack)
        menu = QWidget()
        menu_layout = QVBoxLayout(menu)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.addWidget(QLabel("<h3>Settings</h3>"))
        self.range_row = _Row("Range", tall=True)
        self.range_row.clicked.connect(lambda: self._go(1))
        self.range_keyboard = KeyboardSpan(compact=True, size=(ROW_PICTURE_WIDTH, 36))
        self.range_row.attach(self.range_keyboard)
        self.intervals_row = _Row("Intervals")
        self.intervals_row.clicked.connect(lambda: self._go(2))
        menu_layout.addWidget(self.range_row)
        menu_layout.addWidget(self.intervals_row)
        self.buttons_row = _Row("Buttons")
        self.buttons_row.clicked.connect(lambda: self._go(3))
        menu_layout.addWidget(self.buttons_row)
        menu_layout.addStretch()
        buttons_body = QWidget()
        buttons_layout = QVBoxLayout(buttons_body)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.button_modes: dict[str, QRadioButton] = {}
        mode_group = QButtonGroup(self)
        for mode, label, tip in (
            ("limited", "Limited", "Show up to the chosen number of answer buttons"),
            ("all", "All", "Show a fixed button for every selected interval"),
            ("compact", "Compact", "Choose a quality letter and an interval number, in either order"),
        ):
            radio = QRadioButton(label)
            radio.setToolTip(tip)
            mode_group.addButton(radio)
            radio.toggled.connect(lambda on, chosen=mode: self._button_mode_chosen(chosen, on=on))
            buttons_layout.addWidget(radio)
            self.button_modes[mode] = radio
        self.button_count_row = QWidget()
        count_layout = QHBoxLayout(self.button_count_row)
        count_layout.setContentsMargins(0, 0, 0, 0)
        count_layout.addWidget(QLabel("Button count"), 1)
        self.button_count_down = _arrow(Qt.ArrowType.LeftArrow, tip="Fewer answer buttons")
        self.button_count_up = _arrow(Qt.ArrowType.RightArrow, tip="More answer buttons")
        self.button_count_down.clicked.connect(lambda: self._step_button_count(-1))
        self.button_count_up.clicked.connect(lambda: self._step_button_count(1))
        self.button_count = QLineEdit()
        self.button_count.setProperty("field", True)
        self.button_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.button_count.setFixedWidth(54)
        self.button_count.setValidator(QIntValidator(1, len(settings.KEYBOARD_INTERVAL_NAMES), self.button_count))
        self.button_count.setAccessibleName("Answer button count")
        self.button_count.setToolTip("Maximum answer buttons in limited mode; fewer are shown if fewer intervals are selected")
        self.button_count.editingFinished.connect(self._button_count_edited)
        count_layout.addWidget(self.button_count_down)
        count_layout.addWidget(self.button_count)
        count_layout.addWidget(self.button_count_up)
        buttons_layout.insertWidget(1, self.button_count_row)
        buttons_layout.addStretch()

        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        hint = QLabel("Drag to choose the keys to practice. Both highlighted notes must fit within this range.")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        self.span = KeyboardSpan()
        self.span.dragged.connect(self._set_range)
        layout.addWidget(self.span)
        self.low_label, self.high_label = QLabel(), QLabel()
        self.arrows: dict[str, tuple[QToolButton, QToolButton]] = {}
        for title, label, which in (("Lowest key", self.low_label, "low"), ("Highest key", self.high_label, "high")):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"<b>{title}</b>"), 1)
            down = _arrow(Qt.ArrowType.LeftArrow, tip=f"{title}: one key down")
            up = _arrow(Qt.ArrowType.RightArrow, tip=f"{title}: one key up")
            down.clicked.connect(lambda _=False, w=which: self._step(w, delta=-1))
            up.clicked.connect(lambda _=False, w=which: self._step(w, delta=1))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumWidth(48)
            row.addWidget(down)
            row.addWidget(label)
            row.addWidget(up)
            layout.addLayout(row)
            self.arrows[which] = (down, up)
        self.entire = QPushButton("Entire keyboard")
        self.entire.clicked.connect(lambda: self._set_range(*settings.KEYBOARD_FULL))
        self.default = QPushButton("Reset to default")
        self.default.clicked.connect(lambda: self._set_range(*settings.KEYBOARD_DEFAULT))
        layout.addWidget(self.entire)
        layout.addWidget(self.default)

        intervals = QWidget()
        intervals_layout = QVBoxLayout(intervals)
        intervals_layout.setContentsMargins(0, 0, 0, 0)
        self.select_all = _ToggleRow("Select all")
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
        self.interval_low_label, self.interval_high_label = FieldComboBox(), FieldComboBox()
        self.interval_arrows: dict[str, tuple[QToolButton, QToolButton]] = {}
        for row, (title, label, which) in enumerate(
            (("From", self.interval_low_label, "low"), ("To", self.interval_high_label, "high")),
        ):
            endpoints.addWidget(QLabel(title), row, 0)
            down = _arrow(Qt.ArrowType.LeftArrow, tip=f"{title}: smaller interval")
            up = _arrow(Qt.ArrowType.RightArrow, tip=f"{title}: larger interval")
            down.clicked.connect(lambda _=False, w=which: self.interval_slider.move_endpoint(w, delta=-1))
            up.clicked.connect(lambda _=False, w=which: self.interval_slider.move_endpoint(w, delta=1))
            label.setProperty("field", True)
            label.setMinimumWidth(48)
            label.setMaxVisibleItems(12)
            label.setPlaceholderText("—")
            label.setAccessibleName("Lowest interval" if which == "low" else "Highest interval")
            label.setToolTip(f"Choose the {'lowest' if which == 'low' else 'highest'} interval")
            label.activated.connect(lambda index, w=which: self._interval_endpoint_picked(w, index=index))
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
                    [(distance, settings.keyboard_interval_name(distance)) for distance in range(1, 13)],
                ),
                (
                    "Compound intervals",
                    [
                        (distance, settings.keyboard_interval_name(distance))
                        for distance in range(13, len(settings.KEYBOARD_INTERVAL_NAMES) + 1)
                    ],
                ),
            ],
            selected=cfg.intervals,
            allow_empty=True,
        )
        self.interval_page.changed.connect(self._intervals_edited)
        intervals_layout.addWidget(self.interval_page)
        self.stack.addWidget(menu)
        self.stack.addWidget(_subpage("Range", body=body, back=lambda: self._go(0)))
        self.stack.addWidget(_subpage("Intervals", body=_scrolling(intervals), back=lambda: self._go(0), fill=True))
        self.stack.addWidget(_subpage("Buttons", body=buttons_body, back=lambda: self._go(0)))
        self._refresh()

    def _go(self, index: int) -> None:
        """
        Open a settings page.

        Parameters
        ----------
        index : int
            The menu at 0, range at 1, intervals at 2, or answer buttons at 3.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
        >>> panel._go(1)
        >>> panel.stack.sliding
        True
        """
        if not self.stack.sliding and index != self.stack.currentIndex():
            self.stack.slide_to(index)

    def _refresh(self) -> None:
        """
        Update range labels and disable interval choices that cannot be used.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings(low=60, high=64))
        >>> panel.interval_page.boxes[12].isEnabled()
        False
        """
        cfg = self.cfg
        mode = "compact" if cfg.compact_buttons else "all" if cfg.all_interval_buttons else "limited"
        for key, radio in self.button_modes.items():
            radio.blockSignals(True)
            radio.setChecked(key == mode)
            radio.blockSignals(False)
        self.buttons_row.value.setText(self.button_modes[mode].text())
        self.button_count.setText(str(cfg.answer_button_limit()))
        self.button_count_row.setEnabled(not (cfg.all_interval_buttons or cfg.compact_buttons))
        self.button_count_down.setEnabled(cfg.answer_button_limit() > 1)
        self.button_count_up.setEnabled(cfg.answer_button_limit() < len(settings.KEYBOARD_INTERVAL_NAMES))
        self.low_label.setText(key_name(cfg.low))
        self.high_label.setText(key_name(cfg.high))
        self.span.set_span(cfg.low, hi=cfg.high)
        available = cfg.high - cfg.low
        low = min(cfg.intervals) if cfg.intervals else 1
        high = max(cfg.intervals) if cfg.intervals else 1
        active = bool(cfg.intervals)
        self.interval_slider.set_range(low, high=high, maximum=available, active=active)
        for picker, value in ((self.interval_low_label, low), (self.interval_high_label, high)):
            picker.blockSignals(True)
            if picker.count() != available:
                picker.clear()
                picker.addItems(list(settings.KEYBOARD_INTERVAL_NAMES[:available]))
            picker.setCurrentIndex(value - 1 if active else -1)
            picker.blockSignals(False)
        self.interval_arrows["low"][0].setEnabled(not active or low > 1)
        self.interval_arrows["low"][1].setEnabled(not active or low < high)
        self.interval_arrows["high"][0].setEnabled(not active or high > low)
        self.interval_arrows["high"][1].setEnabled(not active or high < available)
        self.range_keyboard.set_span(cfg.low, hi=cfg.high)
        self.range_keyboard.setToolTip(f"{key_name(cfg.low)} to {key_name(cfg.high)}")
        first, last = settings.KEYBOARD_FULL
        self.arrows["low"][0].setEnabled(cfg.low > first)
        self.arrows["low"][1].setEnabled(cfg.low + 1 < cfg.high)
        self.arrows["high"][0].setEnabled(cfg.high - 1 > cfg.low)
        self.arrows["high"][1].setEnabled(cfg.high < last)
        names = [settings.KEYBOARD_INTERVAL_NAMES[distance - 1] for distance in sorted(cfg.intervals)]
        all_selected = len(names) == cfg.high - cfg.low
        self.select_all.setOn(self._select_all_active)
        self.intervals_row.value.setText("All" if all_selected else ", ".join(names) if names else "None")
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
        Adjust one endpoint without collapsing the range to a single key.

        Parameters
        ----------
        which : str
            The endpoint, "low" or "high".
        delta : int
            The number of keys to move. Keyword-only.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
        >>> panel._step("low", delta=1)
        >>> panel.cfg.low
        49
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
        >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
        >>> panel._set_range(60, 64)
        >>> panel.cfg.active_intervals()
        [1, 2, 3, 4]
        """
        self.cfg.low, self.cfg.high = low, high
        self.cfg.low, self.cfg.high = self.cfg.bounds()
        if self._select_all_active:
            self.cfg.intervals = set(range(1, self.cfg.high - self.cfg.low + 1))
        else:
            self.cfg.intervals = set(self.cfg.active_intervals())
        self._save_and_emit()

    def _interval_endpoint_picked(self, which: str, *, index: int) -> None:
        """
        Select an endpoint from its dropdown and keep the interval bounds ordered.

        Parameters
        ----------
        which : str
            The endpoint, "low" or "high".
        index : int
            The selected interval's zero-based index. Keyword-only.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
        >>> panel._interval_endpoint_picked("low", index=2)
        >>> min(panel.cfg.intervals), max(panel.cfg.intervals)
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
        Select the interval span chosen with the slider or endpoint buttons.

        Parameters
        ----------
        low : int
            The lowest interval distance, in half steps.
        high : int
            The highest interval distance, in half steps.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
        >>> panel.interval_slider.move_endpoint("low", delta=2)
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
        >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
        >>> panel._step_button_count(1)
        >>> panel.cfg.button_count
        7
        """
        self.cfg.button_count = max(1, min(len(settings.KEYBOARD_INTERVAL_NAMES), self.cfg.answer_button_limit() + delta))
        self._save_and_emit()

    def _button_count_edited(self) -> None:
        """
        Commit a typed answer-button count, restoring the current value if the input is invalid.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
        >>> panel.button_count.setText("8")
        >>> panel._button_count_edited()
        >>> panel.cfg.button_count
        8
        """
        try:
            count = int(self.button_count.text())
        except ValueError:
            self._refresh()
            return
        self.cfg.button_count = max(1, min(len(settings.KEYBOARD_INTERVAL_NAMES), count))
        self._save_and_emit()

    def _button_mode_chosen(self, mode: str, *, on: bool) -> None:
        """
        Save the selected answer mode while preserving the limited button count.

        Parameters
        ----------
        mode : str
            The selected mode: "limited", "all", or "compact".
        on : bool
            Whether this radio button is selected. Keyword-only.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
        >>> panel.button_modes["compact"].click()
        >>> panel.cfg.compact_buttons, panel.cfg.all_interval_buttons
        (True, False)
        """
        if not on:
            return
        self.cfg.compact_buttons = mode == "compact"
        self.cfg.all_interval_buttons = mode == "all"
        self._save_and_emit()

    def _select_all_toggled(self, on: bool) -> None:
        """
        Temporarily select every interval, or restore the selection from before the toggle was enabled.

        Parameters
        ----------
        on : bool
            True to select all available intervals; False to restore the previous selection.

        Examples
        --------
        >>> cfg = settings.KeyboardIntervalSettings(low=60, high=64, intervals={3})
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
            self.cfg.intervals = set(range(1, self.cfg.high - self.cfg.low + 1))
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
        >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
        >>> panel.interval_page.boxes[12].setChecked(False)
        >>> 12 in panel.cfg.intervals
        False
        """
        self._select_all_active = False
        selected = self.interval_page.selected()
        self.cfg.intervals = {
            distance for distance in range(1, len(settings.KEYBOARD_INTERVAL_NAMES) + 1) if distance in selected
        }
        self.cfg.intervals = set(self.cfg.active_intervals())
        self._save_and_emit()

    def _save_and_emit(self) -> None:
        """
        Refresh the controls, persist the settings, and notify the exercise.

        Examples
        --------
        >>> panel = KeyboardIntervalSettingsPanel(settings.KeyboardIntervalSettings())
        >>> panel._save_and_emit()
        >>> int(store().value("keyboardIntervals/low")) == panel.cfg.low
        True
        """
        self._refresh()
        save_keyboard_intervals(self.cfg)
        self.changed.emit()


_INVERSION_SHORT = (
    "Root",
    "1st",
    "2nd",
    "3rd",
)


class ArpeggioSettingsPanel(ExerciseSettingsPanel):
    """
    The settings of the arpeggio exercise: a menu with a page for each group of settings.

    The menu has Clefs, Arpeggio types, Inversions and Key signatures. Edits are live: each changes the settings, saves them
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
    >>> panel = ArpeggioSettingsPanel(settings.ArpeggioSettings())
    >>> panel.types_row.value.text()
    '4 of 9'
    """

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
        >>> ArpeggioSettingsPanel(settings.ArpeggioSettings()).stack.count()  # the menu and four pages
        5
        """
        super().__init__(parent)
        self.cfg = cfg
        self.stack = SlideStack()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        outer.addWidget(self.stack)

        # layer 1: menu
        menu = QWidget()
        mlay = QVBoxLayout(menu)
        mlay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        mlay.addWidget(QLabel("<h3>Settings</h3>"))
        self.clefs_row = _Row("Clefs")
        self.clefs_row.clicked.connect(lambda: self._go(1))
        self.clef_pictures = ClefPictures()
        self.clefs_row.attach(self.clef_pictures)
        self.types_row = _Row("Arpeggio types")
        self.types_row.clicked.connect(lambda: self._go(2))
        self.inversions_row = _Row("Inversions")
        self.inversions_row.clicked.connect(lambda: self._go(3))
        self.keys_row = _Row("Key signatures")
        self.keys_row.setToolTip("Draw a key signature; the arpeggio then only gets signs where it differs from it")
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
        self.boxes, clefs_page = _clefs_page(
            CLEFS,
            selected=cfg.clefs,
            edited=self._clefs_edited,
            back=lambda: self._go(0),
        )

        # layer 2: arpeggio types, and inversions
        self.types = ChoiceChecklist(
            [
                ("Triads", [(t, t.capitalize()) for t in settings.ARPEGGIO_TRIADS]),
                ("Seventh chords", [(t, t.capitalize()) for t in settings.ARPEGGIO_SEVENTHS]),
            ],
            selected=cfg.types,
        )
        self.types.changed.connect(self._types_edited)
        types_page = _subpage("Arpeggio types", body=self.types, back=lambda: self._go(0))
        names = settings_inversion_names()
        self.inversions = ChoiceChecklist([("", [(i, names[i]) for i in settings.INVERSIONS])], selected=cfg.inversions)
        self.inversions.changed.connect(self._inversions_edited)
        note = QLabel("A triad has no 3rd inversion, so that choice only applies to seventh chords.")
        note.setWordWrap(True)
        note.setStyleSheet("color: gray;")
        inv_body = QWidget()
        inv_lay = QVBoxLayout(inv_body)
        inv_lay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        inv_lay.addWidget(self.inversions)
        inv_lay.addWidget(note)
        inversions_page = _subpage("Inversions", body=inv_body, back=lambda: self._go(0))

        # layer 2: key signatures
        self.key_page = KeySignaturePage(cfg.key_signature, selected=cfg.keys)
        self.key_page.changed.connect(self._keys_edited)
        keys_page = _subpage("Key signatures", body=self.key_page, back=lambda: self._go(0))

        for page in (
            menu,
            clefs_page,
            types_page,
            inversions_page,
            keys_page,
        ):
            self.stack.addWidget(page)
        self._refresh_summaries()

    def _go(self, index: int) -> None:
        """
        Slide to a page, refreshing the menu's summaries when going back to it.

        Parameters
        ----------
        index : int
            0 for the menu, then the pages in the order of the menu.

        Examples
        --------
        >>> panel = ArpeggioSettingsPanel(settings.ArpeggioSettings())
        >>> panel._go(2)
        >>> panel.stack.sliding
        True
        """
        if self.stack.sliding or index == self.stack.currentIndex():
            return
        if index == 0:
            self._refresh_summaries()
        self.stack.slide_to(index)

    def _refresh_summaries(self) -> None:
        """
        Update the menu's summaries: the clefs, how many types, which inversions and the keys.

        Examples
        --------
        >>> panel = ArpeggioSettingsPanel(settings.ArpeggioSettings(inversions={0, 2}))
        >>> panel._refresh_summaries()
        >>> panel.inversions_row.value.text()
        'Root, 2nd'
        """
        cfg = self.cfg
        self.clef_pictures.set_clefs(cfg.active_clefs())
        types = cfg.active_types()
        self.types_row.value.setText(f"{len(types)} of {len(settings.ARPEGGIO_TYPES)}")
        inversions = cfg.active_inversions()
        self.inversions_row.value.setText(
            "All" if len(inversions) == len(settings.INVERSIONS) else ", ".join(_INVERSION_SHORT[i] for i in inversions),
        )
        _show_keys(
            self.keys_row,
            diagram=self.keys_diagram,
            enabled=cfg.key_signature,
            keys=set(cfg.active_keys()),
        )

    def _save_and_emit(self) -> None:
        """
        Save the arpeggio settings and emit `changed`.

        Examples
        --------
        >>> cfg_ = settings.ArpeggioSettings(clefs={"tenor"})
        >>> panel = ArpeggioSettingsPanel(cfg_)
        >>> panel._save_and_emit()
        >>> str(store().value("arpeggio/clefs"))
        'tenor'
        >>> store().setValue("arpeggio/clefs", "treble,bass")
        """
        saved_settings = store()
        cfg = self.cfg
        saved_settings.setValue("arpeggio/clefs", ",".join(cfg.active_clefs()))
        saved_settings.setValue("arpeggio/types", ",".join(cfg.active_types()))
        saved_settings.setValue("arpeggio/inversions", ",".join(str(i) for i in cfg.active_inversions()))
        saved_settings.setValue("arpeggio/keySignature", "true" if cfg.key_signature else "false")
        saved_settings.setValue("arpeggio/keys", ",".join(str(k) for k in cfg.active_keys()))
        self.changed.emit()

    def _clefs_edited(self) -> None:
        """
        Take the checked clefs into the settings, save them and say so.

        The last checked clef cannot be unchecked.

        Examples
        --------
        >>> cfg = settings.ArpeggioSettings()
        >>> panel = ArpeggioSettingsPanel(cfg)
        >>> panel.boxes["alto"].setChecked(True)
        >>> "alto" in cfg.clefs
        True
        """
        self.cfg.clefs = {c for c, b in self.boxes.items() if b.isChecked()}
        _guard_last(list(self.boxes.values()))
        self._save_and_emit()

    def _types_edited(self) -> None:
        """
        Take the checked chord types into the settings, save them and say so.

        Examples
        --------
        >>> cfg = settings.ArpeggioSettings()
        >>> panel = ArpeggioSettingsPanel(cfg)
        >>> panel.types.boxes["minor 7th"].setChecked(True)
        >>> "minor 7th" in cfg.types
        True
        """
        self.cfg.types = self.types.selected()
        self._save_and_emit()

    def _inversions_edited(self) -> None:
        """
        Take the checked inversions into the settings, save them and say so.

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
        Take the key signature page into the settings, update the menu, save and say so.

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
        _show_keys(
            self.keys_row,
            diagram=self.keys_diagram,
            enabled=self.cfg.key_signature,
            keys=set(self.cfg.active_keys()),
        )
        self._save_and_emit()


def _load_key_settings(
    cfg: settings.KeySignatureSettings,
    *,
    prefix: str,
) -> None:
    """
    Load the saved clefs, scales and key signatures of a key exercise into its settings.

    Anything in the saved data that is not valid is ignored, and a list with nothing valid in it leaves the setting as it was.

    Parameters
    ----------
    cfg : KeySignatureSettings
        The settings to fill.
    prefix : str
        What the exercise's saved settings are filed under, such as "keySignatures". Keyword-only.

    Examples
    --------
    >>> loaded = settings.KeySignatureSettings()
    >>> store().setValue("doctestKeys/keys", "-2,5,99")
    >>> _load_key_settings(loaded, prefix="doctestKeys")
    >>> sorted(loaded.keys)
    [-2, 5]
    >>> store().remove("doctestKeys")
    """
    saved_settings = store()
    clefs = text_value(saved_settings, key=f"{prefix}/clefs", default="")
    if clefs:
        cfg.clefs = {c for c in clefs.split(",") if c in CLEFS} or cfg.clefs
    modes = text_value(saved_settings, key=f"{prefix}/modes", default="")
    if modes:
        cfg.modes = {m for m in modes.split("|") if m in settings.KEY_MODES} or cfg.modes
    keys = text_value(saved_settings, key=f"{prefix}/keys", default="")
    if keys:
        cfg.keys = {int(k) for k in keys.split(",") if k.lstrip("-").isdigit() and abs(int(k)) <= 7} or cfg.keys
    if isinstance(cfg, (settings.ScaleConstructionSettings, settings.ScaleIdentificationSettings)):
        minor_key = f"{prefix}/minorKeys"
        if saved_settings.contains(minor_key):
            cfg.minor_keys = {
                int(k)
                for k in text_value(saved_settings, key=minor_key, default="").split(",")
                if k.lstrip("-").isdigit() and abs(int(k)) <= 7
            }
            if saved_settings.contains(f"{prefix}/keys") and not keys and cfg.minor_keys:
                cfg.keys = set()
        else:
            cfg.minor_keys = None
    if isinstance(cfg, settings.ScaleConstructionSettings):
        cfg.steps = text_value(saved_settings, key=f"{prefix}/steps", default="false").lower() == "true"
        cfg.octave = text_value(saved_settings, key=f"{prefix}/octave", default="false").lower() == "true"
    if isinstance(cfg, (settings.ScaleConstructionSettings, settings.ScaleIdentificationSettings)):
        if isinstance(cfg, settings.ScaleIdentificationSettings):
            question_type = text_value(saved_settings, key=f"{prefix}/questionType", default="combined")
            cfg.question_type = question_type if question_type in {"mode", "key"} else "combined"
            cfg.button_mode = (
                "all" if text_value(saved_settings, key=f"{prefix}/buttonMode", default="limited") == "all" else "limited"
            )
            cfg.button_count = max(2, min(10, int_value(saved_settings, key=f"{prefix}/buttonCount", default=6)))
        motion = text_value(saved_settings, key=f"{prefix}/motion", default="ascending")
        cfg.motion = motion if motion in {"ascending", "descending"} else "ascending"
        staff_keys = text_value(saved_settings, key=f"{prefix}/staffKeys", default="")
        if staff_keys:
            cfg.staff_keys = {
                int(k) for k in staff_keys.split(",") if k.lstrip("-").isdigit() and abs(int(k)) <= 7
            } or cfg.staff_keys


def load_key_signatures() -> None:
    """
    Load the saved key signature identification settings into the shared settings object.

    Anything in the saved data that is not valid is ignored, and a list with nothing valid in it leaves the setting as it was.

    Examples
    --------
    >>> store().setValue("keySignatures/clefs", "alto")
    >>> load_key_signatures()
    >>> settings.key_signatures.clefs
    {'alto'}
    >>> settings.key_signatures.clefs = {"treble", "bass"}
    >>> store().setValue("keySignatures/clefs", "treble,bass")
    """
    _load_key_settings(settings.key_signatures, prefix="keySignatures")


def load_key_construction() -> None:
    """
    Load the saved key signature construction settings into the shared settings object.

    Anything in the saved data that is not valid is ignored, and a list with nothing valid in it leaves the setting as it was.

    Examples
    --------
    >>> store().setValue("keyConstruction/keys", "-3,4")
    >>> load_key_construction()
    >>> settings.key_construction.active_keys()
    [-3, 4]
    >>> settings.key_construction.keys = set(range(-7, 8))
    >>> store().remove("keyConstruction")
    """
    _load_key_settings(settings.key_construction, prefix="keyConstruction")


def load_scale_identification() -> None:
    """
    Load the saved scale identification options independently of scale construction.

    Examples
    --------
    >>> load_scale_identification()
    >>> settings.scale_identification.active_staff_keys()
    [0]
    """
    _load_key_settings(settings.scale_identification, prefix="scaleIdentification")


def load_scale_construction() -> None:
    """
    Load the saved scale construction settings into the shared settings object.

    Anything in the saved data that is not valid is ignored, and a list with nothing valid in it leaves the setting as it was.

    Examples
    --------
    >>> store().setValue("scaleConstruction/keys", "1,-1")
    >>> store().setValue("scaleConstruction/steps", "true")
    >>> store().setValue("scaleConstruction/octave", "true")
    >>> load_scale_construction()
    >>> settings.scale_construction.active_keys(), settings.scale_construction.steps, settings.scale_construction.octave
    ([-1, 1], True, True)
    >>> settings.scale_construction.keys, settings.scale_construction.steps = set(range(-7, 8)), False
    >>> settings.scale_construction.octave = False
    >>> store().remove("scaleConstruction")
    """
    _load_key_settings(settings.scale_construction, prefix="scaleConstruction")


class KeySignatureSettingsPanel(ExerciseSettingsPanel):
    """
    The settings of a key signature exercise: a menu with a page for each group of settings.

    The same panel serves key signature identification, key signature construction and both scale exercises, each saving
    under its own name.

    The menu has Clefs, Scales and Key signatures. Both scale exercises have independent staff and scale key choices;
    construction also has Octave and Steps switches. Edits are live: each changes the settings, saves them and emits `changed`.

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
        The key signatures that may be drawn on the staff; only scale construction has it.

    Examples
    --------
    >>> panel = KeySignatureSettingsPanel(settings.KeySignatureSettings())
    >>> panel.modes_row.value.text()
    '2 of 7'
    """

    def __init__(
        self,
        cfg: settings.KeySignatureSettings,
        *,
        prefix: str = "keySignatures",
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
        parent : QWidget or None, default None
            The widget that owns the panel. Keyword-only.

        Examples
        --------
        >>> KeySignatureSettingsPanel(settings.KeySignatureSettings()).stack.count()  # the menu and three pages
        4
        """
        super().__init__(parent)
        self.cfg = cfg
        self.prefix = prefix
        self.stack = SlideStack()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        outer.addWidget(self.stack)

        # layer 1: menu
        menu = QWidget()
        mlay = QVBoxLayout(menu)
        mlay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        mlay.addWidget(QLabel("<h3>Settings</h3>"))
        scales = isinstance(
            cfg,
            (settings.ScaleConstructionSettings, settings.ScaleIdentificationSettings),
        )  # these have a signature for the staff and one for the scale
        self.clefs_row = _Row("Clefs")
        self.modes_row = _Row("Scales")
        self.keys_row = _Row("Scale Key" if scales else "Key signatures")
        self.staff_keys_row: _Row | None = _Row("Staff Key") if scales else None
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
            menu_rows.append(self.staff_keys_row)  # the staff's key and the scale's are next to each other
        menu_rows.append(self.keys_row)
        if scales:
            self.motion_row = _Row("Motion")
            menu_rows.append(self.motion_row)
        if isinstance(cfg, settings.ScaleIdentificationSettings):
            self.buttons_row = _Row("Buttons")
            menu_rows.append(self.buttons_row)
            self.question_type_row = _Row("Question Type")
            menu_rows.append(self.question_type_row)
        for index, row in enumerate(menu_rows, 1):
            row.clicked.connect(lambda _=False, i=index: self._go(i))
            mlay.addWidget(row)
        self.steps_row: _ToggleRow | None = None  # only scale construction has steps to mark, and an octave to start in
        self.octave_row: _ToggleRow | None = None
        if isinstance(cfg, settings.ScaleConstructionSettings):
            octave_row = _ToggleRow("Octave")
            octave_row.setToolTip("Name the octave of the first note, such as G2 Major, and require the scale to start there")
            octave_row.setOn(cfg.octave)
            octave_row.switched.connect(self._octave_toggled)
            mlay.addWidget(octave_row)
            self.octave_row = octave_row
            steps_row = _ToggleRow("Steps")
            steps_row.setToolTip("Also mark the whole and half steps between the notes, once they are placed")
            steps_row.setOn(cfg.steps)
            steps_row.switched.connect(self._steps_toggled)
            mlay.addWidget(steps_row)
            self.steps_row = steps_row
        mlay.addStretch()

        # layer 2: the clefs the signature is drawn on
        self.boxes, clefs_page = _clefs_page(
            CLEFS,
            selected=cfg.clefs,
            edited=self._clefs_edited,
            back=lambda: self._go(0),
        )

        # layer 2: the scales, so the key can be a major or minor key or a mode
        self.modes = ChoiceChecklist([("", [(m, settings.MODE_LABELS[m]) for m in settings.KEY_MODES])], selected=cfg.modes)
        self.modes.changed.connect(self._modes_edited)
        modes_note = QLabel(
            "A mode has the key signature of a major key and starts from another note of it: D Dorian has "
            "the signature of C major.",
        )
        modes_note.setWordWrap(True)
        modes_note.setStyleSheet("color: gray;")
        modes_body = QWidget()
        mlay2 = QVBoxLayout(modes_body)
        mlay2.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        mlay2.addWidget(self.modes)
        mlay2.addWidget(modes_note)
        modes_page = _subpage("Scales", body=modes_body, back=lambda: self._go(0))

        # layer 2: the key signatures asked
        if isinstance(cfg, (settings.ScaleConstructionSettings, settings.ScaleIdentificationSettings)):
            self.scale_keys = _ScaleKeyPicker(
                major_keys=set(cfg.active_keys()) if cfg.minor_keys is None else cfg.keys,
                minor_keys=set(cfg.active_keys()) if cfg.minor_keys is None else cfg.minor_keys,
            )
            self.key_list = self.scale_keys.major_keys
            self.scale_keys.minor_keys.changed.connect(self._keys_edited)
        else:
            self.key_list = KeyChecklist(cfg.keys)
        self.key_list.changed.connect(self._keys_edited)
        pages = [menu, clefs_page, modes_page]
        self.staff_key_list: KeyChecklist | None = None
        if isinstance(cfg, (settings.ScaleConstructionSettings, settings.ScaleIdentificationSettings)):
            # layer 2: the signature drawn on the staff, which need not be the scale's own
            staff_key_list = KeyChecklist(cfg.staff_keys)
            staff_key_list.changed.connect(self._staff_keys_edited)
            self.staff_key_list = staff_key_list
            staff_note = QLabel(
                "The key signature drawn at the start of the staff. It need not be the scale's: with two flats on the "
                "staff, a C major scale needs a natural on its B and E.",
            )
            staff_note.setWordWrap(True)
            staff_note.setStyleSheet("color: gray;")
            staff_body = QWidget()
            staff_lay = QVBoxLayout(staff_body)
            staff_lay.setContentsMargins(
                0,
                0,
                0,
                0,
            )
            staff_lay.addWidget(staff_key_list)
            staff_lay.addWidget(staff_note)
            pages.append(_subpage("Staff Key", body=staff_body, back=lambda: self._go(0)))
            pages.append(_subpage("Scale Key", body=_scrolling(self.scale_keys), back=lambda: self._go(0), fill=True))
            motion_body = QWidget()
            motion_layout = QVBoxLayout(motion_body)
            motion_layout.setContentsMargins(0, 0, 0, 0)
            for direction in ("ascending", "descending"):
                radio = QRadioButton(direction.title())
                motion_layout.addWidget(radio)
                radio.setChecked(cfg.motion == direction)
                radio.toggled.connect(lambda checked, value=direction: self._motion_edited(value, checked=checked))
            pages.append(_subpage("Motion", body=motion_body, back=lambda: self._go(0)))
        else:
            pages.append(_subpage("Key signatures", body=self.key_list, back=lambda: self._go(0)))

        if isinstance(cfg, settings.ScaleIdentificationSettings):
            body = QWidget()
            layout = QVBoxLayout(body)
            layout.setContentsMargins(0, 0, 0, 0)
            limited = QRadioButton("Limited")
            all_buttons = QRadioButton("All")
            layout.addWidget(limited)
            count_row = QWidget()
            count_layout = QHBoxLayout(count_row)
            count_layout.setContentsMargins(0, 0, 0, 0)
            count_label = QLabel("Button count")
            count = FieldComboBox()
            count.setAccessibleName("Button count")
            count_label.setBuddy(count)
            for value in range(2, 11):
                count.addItem(str(value), value)
            count.setCurrentIndex(count.findData(cfg.button_count))
            count_layout.addWidget(count_label)
            count_layout.addWidget(count, 1)
            layout.addWidget(count_row)
            layout.addWidget(all_buttons)
            limited.setChecked(cfg.button_mode == "limited")
            all_buttons.setChecked(cfg.button_mode == "all")
            count_row.setVisible(limited.isChecked())

            def save_buttons() -> None:
                """
                Save the button mode and count when their controls change.

                Examples
                --------
                Open the Buttons page and choose All to save that mode.
                """
                cfg.button_mode = "limited" if limited.isChecked() else "all"
                cfg.button_count = count.currentData()
                count_row.setVisible(limited.isChecked())
                self._save_and_emit()

            limited.toggled.connect(save_buttons)
            count.currentIndexChanged.connect(save_buttons)
            pages.append(_subpage("Buttons", body=body, back=lambda: self._go(0)))

            question_types = ChoiceChecklist(
                [("", [("key", "Key"), ("mode", "Mode")])],
                selected={"key", "mode"} if cfg.question_type == "combined" else {cfg.question_type},
            )

            def save_question_type() -> None:
                """
                Save the selected parts of the scale question.

                Examples
                --------
                Clear Key on the Question Type page to save Mode alone.
                """
                selected = question_types.selected()
                cfg.question_type = "combined" if len(selected) == 2 else next(iter(selected), "combined")
                self._save_and_emit()

            question_types.changed.connect(save_question_type)
            pages.append(_subpage("Question Type", body=question_types, back=lambda: self._go(0)))

        for page in pages:
            self.stack.addWidget(page)
        self._refresh_summaries()

    def _go(self, index: int) -> None:
        """
        Slide to a page, refreshing the menu's summaries when going back to it.

        Parameters
        ----------
        index : int
            0 for the menu, then the pages in the order of the menu.

        Examples
        --------
        >>> panel = KeySignatureSettingsPanel(settings.KeySignatureSettings())
        >>> panel._go(1)
        >>> panel.stack.sliding
        True
        """
        if self.stack.sliding or index == self.stack.currentIndex():
            return
        if index == 0:
            self._refresh_summaries()
        self.stack.slide_to(index)

    def _refresh_summaries(self) -> None:
        """
        Update the menu's summaries: the clefs, how many scales and the keys.

        Examples
        --------
        >>> panel = KeySignatureSettingsPanel(settings.KeySignatureSettings(modes={"Dorian"}))
        >>> panel._refresh_summaries()
        >>> panel.modes_row.value.text()
        '1 of 7'
        """
        cfg = self.cfg
        self.clef_pictures.set_clefs(cfg.active_clefs())
        modes = cfg.active_modes()
        self.modes_row.value.setText(f"{len(modes)} of {len(settings.KEY_MODES)}")
        if isinstance(cfg, (settings.ScaleConstructionSettings, settings.ScaleIdentificationSettings)):
            minor_keys = self.scale_keys.minor_keys
            _guard_last([*self.key_list.boxes.values(), *minor_keys.boxes.values()])
            self.keys_row.value.setText(f"{len(self.key_list.selected())} major · {len(minor_keys.selected())} minor")
        else:
            _show_keys(self.keys_row, diagram=self.keys_diagram, enabled=True, keys=set(cfg.active_keys()))
        if self.staff_keys_row is not None and isinstance(
            cfg,
            (settings.ScaleConstructionSettings, settings.ScaleIdentificationSettings),
        ):
            _show_keys(
                self.staff_keys_row,
                diagram=self.staff_keys_diagram,
                enabled=True,
                keys=set(cfg.active_staff_keys()),
            )

    def _save_and_emit(self) -> None:
        """
        Save the key signature settings and emit `changed`.

        Examples
        --------
        >>> panel = KeySignatureSettingsPanel(settings.KeySignatureSettings(clefs={"alto"}))
        >>> panel._save_and_emit()
        >>> str(store().value("keySignatures/clefs"))
        'alto'
        >>> store().setValue("keySignatures/clefs", "treble,bass")
        """
        saved_settings = store()
        cfg = self.cfg
        saved_settings.setValue(f"{self.prefix}/clefs", ",".join(cfg.active_clefs()))
        saved_settings.setValue(f"{self.prefix}/modes", "|".join(cfg.active_modes()))
        keys = cfg.active_keys()
        if (
            isinstance(cfg, (settings.ScaleConstructionSettings, settings.ScaleIdentificationSettings))
            and cfg.minor_keys is not None
        ):
            keys = sorted(cfg.keys)
            saved_settings.setValue(f"{self.prefix}/minorKeys", ",".join(str(k) for k in sorted(cfg.minor_keys)))
        saved_settings.setValue(f"{self.prefix}/keys", ",".join(str(k) for k in keys))
        if isinstance(cfg, settings.ScaleConstructionSettings):
            saved_settings.setValue(f"{self.prefix}/steps", "true" if cfg.steps else "false")
            saved_settings.setValue(f"{self.prefix}/octave", "true" if cfg.octave else "false")
        if isinstance(cfg, (settings.ScaleConstructionSettings, settings.ScaleIdentificationSettings)):
            saved_settings.setValue(f"{self.prefix}/motion", cfg.motion)
            saved_settings.setValue(f"{self.prefix}/staffKeys", ",".join(str(k) for k in cfg.active_staff_keys()))
        if isinstance(cfg, settings.ScaleIdentificationSettings):
            saved_settings.setValue(f"{self.prefix}/questionType", cfg.question_type)
            saved_settings.setValue(f"{self.prefix}/buttonMode", cfg.button_mode)
            saved_settings.setValue(f"{self.prefix}/buttonCount", cfg.button_count)
        self.changed.emit()

    def _motion_edited(self, direction: str, *, checked: bool) -> None:
        """
        Save the selected direction for this scale exercise.

        Parameters
        ----------
        direction : str
            The scale direction to save.
        checked : bool
            Whether the direction was selected. Keyword-only.

        Examples
        --------
        >>> cfg = settings.ScaleIdentificationSettings()
        >>> panel = KeySignatureSettingsPanel(cfg)
        >>> panel._motion_edited("descending", checked=True)
        >>> cfg.motion
        'descending'
        """
        if checked and isinstance(self.cfg, (settings.ScaleConstructionSettings, settings.ScaleIdentificationSettings)):
            self.cfg.motion = direction
            self._save_and_emit()

    def _clefs_edited(self) -> None:
        """
        Take the checked clefs into the settings, save them and say so.

        The last checked clef cannot be unchecked.

        Examples
        --------
        >>> cfg = settings.KeySignatureSettings()
        >>> panel = KeySignatureSettingsPanel(cfg)
        >>> panel.boxes["alto"].setChecked(True)
        >>> "alto" in cfg.clefs
        True
        """
        self.cfg.clefs = {c for c, b in self.boxes.items() if b.isChecked()}
        _guard_last(list(self.boxes.values()))
        self._save_and_emit()

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
        Take the checked staff key signatures into the settings, save them and say so.

        Examples
        --------
        >>> cfg = settings.ScaleConstructionSettings()
        >>> panel = KeySignatureSettingsPanel(cfg, prefix="doctestScales")
        >>> # noinspection PyUnresolvedReferences
        >>> panel.staff_key_list.boxes[-2].setChecked(True)
        >>> cfg.staff_keys == {0, -2}
        True
        >>> store().remove("doctestScales")
        """
        if (
            isinstance(self.cfg, (settings.ScaleConstructionSettings, settings.ScaleIdentificationSettings))
            and self.staff_key_list is not None
        ):
            self.cfg.staff_keys = self.staff_key_list.selected()
            self._save_and_emit()

    def _octave_toggled(self, on: bool) -> None:
        """
        Switch naming the octave of the first note on or off, save it and say so.

        Parameters
        ----------
        on : bool
            Whether the scale has to start in the octave named.

        Examples
        --------
        >>> cfg = settings.ScaleConstructionSettings()
        >>> panel = KeySignatureSettingsPanel(cfg, prefix="doctestScales")
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
        Switch marking the steps between the notes on or off, save it and say so.

        Parameters
        ----------
        on : bool
            Whether the steps are asked for.

        Examples
        --------
        >>> cfg = settings.ScaleConstructionSettings()
        >>> panel = KeySignatureSettingsPanel(cfg, prefix="doctestScales")
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
        Take the checked key signatures into the settings, save them and say so.

        Examples
        --------
        >>> cfg = settings.KeySignatureSettings()
        >>> panel = KeySignatureSettingsPanel(cfg)
        >>> panel.key_list.boxes[2].setChecked(False)
        >>> 2 in cfg.keys
        False
        """
        self.cfg.keys = self.key_list.selected()
        if isinstance(self.cfg, (settings.ScaleConstructionSettings, settings.ScaleIdentificationSettings)):
            self.cfg.minor_keys = self.scale_keys.minor_keys.selected()
            self._refresh_summaries()
        self._save_and_emit()


def load_notation_terms() -> None:
    """
    Restore the question type and term selection, defaulting to Answer Button and all terms.

    Examples
    --------
    >>> load_notation_terms()
    >>> bool(settings.notation.terms)
    True
    """
    kind = text_value(store(), key="notationIdentification/questionType", default="button")
    settings.notation.question_type = kind if kind in settings.NOTATION_QUESTION_TYPES else "button"
    saved = text_value(store(), key="notationIdentification/terms", default="")
    settings.notation.terms = set(settings.NOTATION_TERMS).intersection(saved.split(",")) or set(settings.NOTATION_TERMS)


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
        >>> len(NotationSettingsPanel().terms.boxes) == len(settings.NOTATION_TERMS)
        True
        """
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.stack = SlideStack()
        layout.addWidget(self.stack)
        menu = QWidget()
        menu_layout = QVBoxLayout(menu)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.addWidget(QLabel("<h3>Settings</h3>"))
        self.type_row = _Row("Question Type")
        self.type_row.clicked.connect(lambda: self.stack.slide_to(1))
        menu_layout.addWidget(self.type_row)
        self.terms_row = _Row("Terms")
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
        self.stack.addWidget(_subpage("Question Type", body=question_types, back=lambda: self.stack.slide_to(0)))

        terms_body = QWidget()
        terms_layout = QVBoxLayout(terms_body)
        terms_layout.setContentsMargins(0, 0, 0, 0)
        self.group_picker = FieldComboBox()
        self.group_picker.setAccessibleName("Notation term group")
        self.group_picker.setPlaceholderText("Select a group…")
        self.group_picker.addItems(["All terms", *CATALOG])
        self.group_picker.setCurrentIndex(-1)
        terms_layout.addWidget(self.group_picker)
        self.terms = ChoiceChecklist(
            [(group, [(term, term) for term in terms]) for group, terms in CATALOG.items()],
            selected=settings.notation.terms,
        )
        terms_layout.addWidget(_scrolling(self.terms), 1)
        self.stack.addWidget(_subpage("Terms", body=terms_body, back=lambda: self.stack.slide_to(0), fill=True))
        self.terms.changed.connect(self._save)
        self.group_picker.textActivated.connect(self._select_group)
        self._refresh_summaries()

    def _refresh_summaries(self) -> None:
        """
        Show the selected question type and term count on the settings menu.

        Examples
        --------
        >>> NotationSettingsPanel().type_row.value.text() == settings.NOTATION_QUESTION_TYPES[settings.notation.question_type]
        True
        """
        self.type_row.value.setText(settings.NOTATION_QUESTION_TYPES[settings.notation.question_type])
        count = len(settings.notation.terms)
        self.terms_row.value.setText("All" if count == len(settings.NOTATION_TERMS) else f"{count} selected")

    def _select_group(self, group: str) -> None:
        """
        Select all terms or only the terms of one group and apply the edit once.

        Parameters
        ----------
        group : str
            The group chosen in the picker.

        Examples
        --------
        >>> "Ornaments" in CATALOG
        True
        """
        selected = settings.NOTATION_TERMS if group == "All terms" else CATALOG[group]
        for term, box in self.terms.boxes.items():
            box.blockSignals(True)
            box.setChecked(term in selected)
            box.blockSignals(False)
        _guard_last(self.terms.boxes.values())
        self.group_picker.setCurrentIndex(-1)
        self._save()

    def _save(self) -> None:
        """
        Save the question type and checked terms, then request a matching question.

        Examples
        --------
        >>> callable(NotationSettingsPanel()._save)
        True
        """
        settings.notation.question_type = next(key for key, radio in self.types.items() if radio.isChecked())
        store().setValue("notationIdentification/questionType", settings.notation.question_type)
        settings.notation.terms = self.terms.selected()
        store().setValue("notationIdentification/terms", ",".join(sorted(settings.notation.terms)))
        self._refresh_summaries()
        self.changed.emit()


def load_clef_basics() -> None:
    """
    Load the saved clef basics settings into the shared settings object.

    Anything in the saved data that is not a clef or a kind of question is ignored, and a list with no clef in it leaves the
    setting as it was.

    Examples
    --------
    >>> store().setValue("clefBasics/clefs", "alto,subbass,flute")
    >>> store().setValue("clefBasics/type", "identification")
    >>> load_clef_basics()
    >>> settings.clef_basics.active_clefs(), settings.clef_basics.question_type
    (['alto', 'subbass'], 'identification')
    >>> settings.clef_basics.clefs, settings.clef_basics.question_type = {"treble", "bass"}, "construction"
    >>> store().remove("clefBasics")
    """
    clefs = text_value(store(), key="clefBasics/clefs", default="")
    if clefs:
        settings.clef_basics.clefs = {
            c for c in clefs.split(",") if c in settings.CLEF_BASICS_CLEFS
        } or settings.clef_basics.clefs
    kind = text_value(store(), key="clefBasics/type", default="")
    if kind in settings.CLEF_QUESTION_TYPES:
        settings.clef_basics.question_type = kind


class ClefBasicsSettingsPanel(ExerciseSettingsPanel):
    """
    The settings of the clef basics exercise: a menu with two pages, Question Type and Clefs.

    Question Type chooses between Clef Construction (put a named clef on a blank staff) and Clef Identification (name the clef on
    a staff). Clefs lists the clefs in the same groups as the other exercises, with the French violin and subbass clefs, which
    only this exercise has, at the bottom. Edits are live: each changes the settings, saves them and emits `changed`.

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
    >>> panel = ClefBasicsSettingsPanel(settings.ClefBasicsSettings())
    >>> panel.stack.count()  # the menu and two pages
    3
    """

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
        >>> panel = ClefBasicsSettingsPanel(settings.ClefBasicsSettings(clefs={"subbass"}))
        >>> panel.boxes["subbass"].isChecked(), list(panel.boxes)[-2:]
        (True, ['french', 'subbass'])
        """
        super().__init__(parent)
        self.cfg = cfg
        self.stack = SlideStack()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        outer.addWidget(self.stack)
        menu = QWidget()
        mlay = QVBoxLayout(menu)
        mlay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        mlay.addWidget(QLabel("<h3>Settings</h3>"))
        self.type_row = _Row("Question Type")
        self.type_row.clicked.connect(lambda _=False: self._go(1))
        mlay.addWidget(self.type_row)
        self.clefs_row = _Row("Clefs")
        self.clef_pictures = ClefPictures()
        self.clefs_row.attach(self.clef_pictures)
        self.clefs_row.clicked.connect(lambda _=False: self._go(2))
        mlay.addWidget(self.clefs_row)
        mlay.addStretch()
        self.types: dict[str, QRadioButton] = {}
        type_body = QWidget()
        type_lay = QVBoxLayout(type_body)
        type_lay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        type_group = QButtonGroup(self)
        for key, label in settings.CLEF_QUESTION_TYPES.items():
            radio = QRadioButton(label)
            radio.setChecked(key == cfg.active_type())
            radio.toggled.connect(lambda on, chosen=key: self._type_chosen(chosen, on=on))
            type_group.addButton(radio)
            type_lay.addWidget(radio)
            self.types[key] = radio
        type_page = _subpage("Question Type", body=type_body, back=lambda: self._go(0))
        self.boxes, clefs_page = _clefs_page(
            settings.CLEF_BASICS_CLEFS,
            selected=cfg.clefs,
            edited=self._clefs_edited,
            back=lambda: self._go(0),
        )
        for page in (menu, type_page, clefs_page):
            self.stack.addWidget(page)
        self._refresh_summaries()

    def _go(self, index: int) -> None:
        """
        Slide to a page, refreshing the menu's summary when going back to it.

        Parameters
        ----------
        index : int
            0 for the menu, 1 for Question Type, 2 for Clefs.

        Examples
        --------
        >>> panel = ClefBasicsSettingsPanel(settings.ClefBasicsSettings())
        >>> panel._go(1)
        >>> panel.stack.sliding
        True
        """
        if self.stack.sliding or index == self.stack.currentIndex():
            return
        if index == 0:
            self._refresh_summaries()
        self.stack.slide_to(index)

    def _refresh_summaries(self) -> None:
        """
        Show the kind of question and the clefs that are asked for in the menu's rows.

        Examples
        --------
        >>> panel = ClefBasicsSettingsPanel(settings.ClefBasicsSettings(clefs={"alto"}))
        >>> panel.clef_pictures.clefs, panel.type_row.value.text()
        (['alto'], 'Construction')
        """
        self.clef_pictures.set_clefs(self.cfg.active_clefs())
        self.type_row.value.setText(settings.CLEF_QUESTION_TYPES[self.cfg.active_type()].removeprefix("Clef "))

    def _type_chosen(self, key: str, *, on: bool) -> None:
        """
        Take the kind of question chosen into the settings, save it and say so.

        Parameters
        ----------
        key : str
            A key of `CLEF_QUESTION_TYPES`.
        on : bool
            Whether its button was just switched on; the one switched off is ignored.

        Examples
        --------
        >>> cfg = settings.ClefBasicsSettings()
        >>> panel = ClefBasicsSettingsPanel(cfg)
        >>> panel.types["identification"].setChecked(True)
        >>> cfg.question_type, str(store().value("clefBasics/type"))
        ('identification', 'identification')
        >>> store().remove("clefBasics")
        """
        if not on:
            return
        self.cfg.question_type = key
        store().setValue("clefBasics/type", key)
        self.changed.emit()

    def _clefs_edited(self) -> None:
        """
        Take the checked clefs into the settings, save them and say so.

        The last checked clef cannot be unchecked.

        Examples
        --------
        >>> cfg = settings.ClefBasicsSettings()
        >>> panel = ClefBasicsSettingsPanel(cfg)
        >>> panel.boxes["french"].setChecked(True)
        >>> "french" in cfg.clefs, str(store().value("clefBasics/clefs"))
        (True, 'treble,bass,french')
        >>> store().remove("clefBasics")
        """
        self.cfg.clefs = {c for c, b in self.boxes.items() if b.isChecked()}
        _guard_last(list(self.boxes.values()))
        store().setValue("clefBasics/clefs", ",".join(self.cfg.active_clefs()))
        self.changed.emit()


def settings_inversion_names() -> tuple[str, ...]:
    """
    Return the inversions as they are written in the settings.

    Returns
    -------
    tuple of str
        'Root position', '1st inversion', '2nd inversion' and '3rd inversion'.

    Examples
    --------
    >>> settings_inversion_names()
    ('Root position', '1st inversion', '2nd inversion', '3rd inversion')
    """
    return tuple(n.capitalize() for n in INVERSION_NAMES)


def load_circle() -> None:
    """
    Load the saved circle of fifths settings into the shared settings object.

    Anything in the saved data that is not valid is ignored, and a list with nothing valid in it leaves the setting as it was. A
    saved color scheme that no longer exists (it was deleted, or comes from a newer Alto) leaves the default.

    Examples
    --------
    >>> store().setValue("circle/questions", "numeral,nonsense")
    >>> store().setValue("circle/scheme", "midnight")
    >>> load_circle()
    >>> settings.circle.questions, settings.circle.scheme
    ({'numeral'}, 'midnight')
    >>> settings.circle.questions = set(settings.CIRCLE_QUESTIONS)
    >>> settings.circle.scheme = DEFAULT_SCHEME
    >>> store().remove("circle")
    """
    saved_settings = store()
    questions = text_value(saved_settings, key="circle/questions", default="")
    if questions:
        settings.circle.questions = {
            q for q in questions.split(",") if q in settings.CIRCLE_QUESTIONS
        } or settings.circle.questions
    settings.circle.customs = load_customs(text_value(saved_settings, key="circle/customSchemes", default="[]"))
    wanted = text_value(saved_settings, key="circle/scheme", default=DEFAULT_SCHEME)
    if wanted == "colour-blind":  # Migrate the preset key saved by earlier versions.
        wanted = "color-blind"
    elif wanted == "chequer":
        wanted = "checker"
    known = set(PRESETS) | {record["id"] for record in settings.circle.customs}
    settings.circle.scheme = wanted if wanted in known else DEFAULT_SCHEME


def _scrolling(body: QWidget) -> QScrollArea:
    """
    Put a page's body in a scroll area, so a long page scrolls inside the pane and never makes the window taller.

    Parameters
    ----------
    body : QWidget
        What the page shows.

    Returns
    -------
    QScrollArea
        The scroll area that holds it, with no frame and no sideways scrolling.

    Examples
    --------
    >>> page = QWidget()
    >>> _scrolling(page).widget() is page
    True
    """
    scroll = QScrollArea()
    scroll.setWidget(body)
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setMinimumHeight(0)
    return scroll


def save_circle(cfg: settings.CircleSettings) -> None:
    """
    Save the circle of fifths settings.

    Parameters
    ----------
    cfg : CircleSettings
        The settings to save.

    Examples
    --------
    >>> save_circle(settings.CircleSettings(scheme="ink"))
    >>> store().value("circle/scheme")
    'ink'
    >>> store().remove("circle")
    """
    saved_settings = store()
    saved_settings.setValue("circle/questions", ",".join(cfg.active_questions()))
    saved_settings.setValue("circle/scheme", cfg.scheme)
    saved_settings.setValue("circle/customSchemes", dump_customs(cfg.customs))


class CircleSettingsPanel(ExerciseSettingsPanel):
    """
    The settings of the circle of fifths exercise: which kinds of question to ask, and the colors of the circle.

    The menu has two rows. Questions opens a page of switches. Colors opens a page of color schemes to choose from, with a
    button to make one of your own, which opens an editor. Edits are live: each changes the settings and saves them. A new kind
    of question emits `changed`, and a new color scheme emits `restyled`, which keeps the question.

    Attributes
    ----------
    cfg : CircleSettings
        The settings being edited.
    stack : SlideStack
        The menu and its pages: the menu, the questions, the color schemes and the editor of a scheme.
    questions_row : _Row
        The menu row for the questions.
    colors_row : _Row
        The menu row for the colors; its value is the name of the chosen scheme.
    questions : ChoiceChecklist
        The kinds of question: relative major, relative minor and Roman numerals.
    schemes : SchemePage
        The color schemes.
    editor : SchemeEditor
        The editor of a scheme of your own.

    Examples
    --------
    >>> panel = CircleSettingsPanel(settings.CircleSettings())
    >>> panel.questions_row.value.text(), panel.colors_row.value.text()
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
        >>> CircleSettingsPanel(settings.CircleSettings()).stack.count()  # the menu, the questions, the colors and the editor
        4
        """
        super().__init__(parent)
        self.cfg = cfg
        self.stack = SlideStack()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        outer.addWidget(self.stack)
        menu = QWidget()
        mlay = QVBoxLayout(menu)
        mlay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        mlay.addWidget(QLabel("<h3>Settings</h3>"))
        self.questions_row = _Row("Questions")
        self.questions_row.clicked.connect(lambda: self._go(1))
        mlay.addWidget(self.questions_row)
        self.colors_row = _Row("Colors")
        self.colors_row.clicked.connect(lambda: self._go(2))
        mlay.addWidget(self.colors_row)
        mlay.addStretch()
        self.questions = ChoiceChecklist([("", list(settings.CIRCLE_QUESTIONS.items()))], selected=cfg.questions)
        self.questions.changed.connect(self._questions_edited)
        note = QLabel(
            "Relative major: a minor key is shown, and you name its major. Relative minor: the other way around. Roman "
            "numerals: a key is shown with its six chords lit, and you give the numeral of one. One of the checked kinds is "
            "asked at random.",
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: gray;")
        body = QWidget()
        blay = QVBoxLayout(body)
        blay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
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
            _subpage("Questions", body=body, back=lambda: self._go(0)),
            _subpage("Colors", body=_scrolling(self.schemes), back=lambda: self._go(0), fill=True),
            _subpage("Your colors", body=_scrolling(self.editor), back=lambda: self._go(2), fill=True),
        )
        for page in pages:
            self.stack.addWidget(page)
        self.schemes.load(current=cfg.scheme, customs=cfg.customs)
        self._refresh_summaries()

    def _go(self, index: int) -> None:
        """
        Slide to a page, refreshing the menu's summaries when going back to it.

        Parameters
        ----------
        index : int
            0 for the menu, 1 for the questions, 2 for the color schemes and 3 for the editor of a scheme.

        Examples
        --------
        >>> panel = CircleSettingsPanel(settings.CircleSettings())
        >>> panel._go(1)
        >>> panel.stack.sliding
        True
        """
        if self.stack.sliding or index == self.stack.currentIndex():
            return
        if index == 0:
            self._refresh_summaries()
        self.stack.slide_to(index)

    def _refresh_summaries(self) -> None:
        """
        Update the menu's summaries: how many kinds of question are on, and the name of the color scheme.

        Examples
        --------
        >>> panel = CircleSettingsPanel(settings.CircleSettings(questions={"minor"}, scheme="midnight"))
        >>> panel._refresh_summaries()
        >>> panel.questions_row.value.text(), panel.colors_row.value.text()
        ('1 of 3', 'Midnight')
        """
        self.questions_row.value.setText(f"{len(self.cfg.active_questions())} of {len(settings.CIRCLE_QUESTIONS)}")
        self.colors_row.value.setText(self.cfg.active_scheme().name)

    def _questions_edited(self) -> None:
        """
        Take the checked kinds of question into the settings, save them and say so.

        Examples
        --------
        >>> cfg = settings.CircleSettings()
        >>> panel = CircleSettingsPanel(cfg)
        >>> panel.questions.boxes["numeral"].setChecked(False)
        >>> sorted(cfg.questions)
        ['major', 'minor']
        >>> store().remove("circle")
        """
        self.cfg.questions = self.questions.selected()
        save_circle(self.cfg)
        self.changed.emit()

    def _scheme_chosen(self, key: str) -> None:
        """
        Use a color scheme: take it into the settings, save it and say so.

        Parameters
        ----------
        key : str
            The key of the scheme that was clicked.

        Examples
        --------
        >>> cfg = settings.CircleSettings()
        >>> panel = CircleSettingsPanel(cfg)
        >>> panel._scheme_chosen("ember")
        >>> cfg.scheme, panel.schemes.thumbs["ember"].isChecked(), panel.colors_row.value.text()
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
        >>> panel = CircleSettingsPanel(settings.CircleSettings())
        >>> panel._new_scheme()
        >>> panel.editor.record()["id"], panel.editor.delete_button.isHidden()
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
        >>> mine = record_of("custom-1", name="Mine", mode="single", colors=["#2f6bd0"])
        >>> panel = CircleSettingsPanel(settings.CircleSettings(customs=[mine]))
        >>> panel._edit_scheme("custom-1")
        >>> panel.editor.name.text(), panel.editor.delete_button.isHidden()
        ('Mine', False)
        """
        for record in self.cfg.customs:
            if record["id"] == key:
                self.editor.load(record, taken=self.cfg.customs)
                self._go(3)
                return

    def _scheme_saved(self, record: CustomRecord) -> None:
        """
        Keep a scheme of your own, use it, save it and go back to the list.

        Parameters
        ----------
        record : CustomRecord
            The scheme from the editor: a new one is added, one that has the same key is replaced.

        Examples
        --------
        >>> cfg = settings.CircleSettings()
        >>> panel = CircleSettingsPanel(cfg)
        >>> panel._new_scheme()
        >>> panel._scheme_saved(panel.editor.record())
        >>> cfg.scheme, [r["name"] for r in cfg.customs], "custom-1" in panel.schemes.thumbs
        ('custom-1', ['My colors'], True)
        >>> store().remove("circle")
        """
        others = [existing for existing in self.cfg.customs if existing["id"] != record["id"]]
        self.cfg.customs = sorted([*others, record], key=lambda item: item["id"])
        self.cfg.scheme = record["id"]
        save_circle(self.cfg)
        self.schemes.load(current=record["id"], customs=self.cfg.customs)
        self._refresh_summaries()
        self.restyled.emit()
        self.stack.setCurrentIndex(3)
        self._go(2)

    def _scheme_deleted(self, key: str) -> None:
        """
        Delete a scheme of your own; if it was the one in use, go back to the default.

        Parameters
        ----------
        key : str
            Its key.

        Examples
        --------
        >>> from alto.circle_schemes import record_of
        >>> mine = record_of("custom-1", name="Mine", mode="single", colors=["#2f6bd0"])
        >>> cfg = settings.CircleSettings(customs=[mine], scheme="custom-1")
        >>> panel = CircleSettingsPanel(cfg)
        >>> panel._scheme_deleted("custom-1")
        >>> cfg.customs, cfg.scheme
        ([], 'cyan-indigo')
        >>> store().remove("circle")
        """
        self.cfg.customs = [record for record in self.cfg.customs if record["id"] != key]
        if self.cfg.scheme == key:
            self.cfg.scheme = DEFAULT_SCHEME
        save_circle(self.cfg)
        self.schemes.load(current=self.cfg.scheme, customs=self.cfg.customs)
        self._refresh_summaries()
        self.restyled.emit()
        self._go(2)


def settings_panel_for(exercise: Exercise) -> ExerciseSettingsPanel | None:
    """
    Return the settings panel for an exercise.

    Parameters
    ----------
    exercise : Exercise
        The exercise.

    Returns
    -------
    ExerciseSettingsPanel or None
        A panel with a `changed` signal, or None for an exercise with no settings.

    Examples
    --------
    >>> from alto.exercises.library import IntervalNames, NoteNames
    >>> type(settings_panel_for(NoteNames())).__name__
    'NoteNameSettingsPanel'
    >>> type(settings_panel_for(IntervalNames())).__name__
    'IntervalSettingsPanel'
    """
    if isinstance(exercise, NotationIdentification):
        return NotationSettingsPanel()
    if isinstance(exercise, NoteNames):
        return NoteNameSettingsPanel(settings.note_names)
    if isinstance(exercise, IntervalNames):
        return IntervalSettingsPanel(settings.intervals)
    if isinstance(exercise, KeyboardIntervals):
        return KeyboardIntervalSettingsPanel(settings.keyboard_intervals)
    if isinstance(exercise, KeyboardNotes):
        return KeyboardSettingsPanel(settings.keyboard)
    if isinstance(exercise, NoteConstruction):
        return NoteConstructionSettingsPanel(settings.construction)
    if isinstance(exercise, ArpeggioNames):
        return ArpeggioSettingsPanel(settings.arpeggio)
    if isinstance(exercise, KeySignatures):
        return KeySignatureSettingsPanel(settings.key_signatures)
    if isinstance(exercise, KeySignatureConstruction):
        return KeySignatureSettingsPanel(settings.key_construction, prefix="keyConstruction")
    if isinstance(exercise, ScaleIdentification):
        return KeySignatureSettingsPanel(settings.scale_identification, prefix="scaleIdentification")
    if isinstance(exercise, ScaleConstruction):
        return KeySignatureSettingsPanel(settings.scale_construction, prefix="scaleConstruction")
    if isinstance(exercise, ClefBasics):
        return ClefBasicsSettingsPanel(settings.clef_basics)
    if isinstance(exercise, CircleOfFifths):
        return CircleSettingsPanel(settings.circle)
    return None
