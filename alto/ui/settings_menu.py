"""
The building blocks of the settings panels that slide in beside an
exercise.

A panel is a menu of rows (Clefs, Range, Key signatures ...) that each
lead to a page, in a `SlideStack`. This module has the
rows, switches, checklists and editors those pages are made of, and the
panels' shared base classes: `ExerciseSettingsPanel`
(navigation and saving), `ClefsPanel` (a Clefs page) and
`StaffRangePanel` (a Range page per clef). The panels themselves are
in `alto.ui.settings_panel` and `alto.ui.pack_settings_panel`.

Examples
--------
>>> _key_label(2)
'D  ·  2♯'
>>> row = MenuRow("Clefs")
>>> row.title.text()
'<b>Clefs</b>'
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import (
    Callable,
    Iterable,
    Mapping,
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
    QPainter,
    QPaintEvent,
    QPalette,
    QPen,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QBoxLayout,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from alto import settings
from alto.exercises.base import ButtonSettings
from alto.learning.calendar import CALENDAR_SCHEDULERS
from alto.settings import (
    NOTE_VALUES,
    RANGE_LIMITS,
    diatonic_name,
)
from alto.theory.pitch import (
    MAJOR_KEYS,
    Note,
)
from alto.theory.scales import (
    format_key_signature,
    mode_tonic,
)
from alto.ui import (
    motion,
    zoom,
)
from alto.ui.colors import blend
from alto.ui.degree_text import DegreeCheckBox
from alto.ui.dropdown import FieldComboBox
from alto.ui.keyboard import KeyboardSpan
from alto.ui.pictures import (
    CLEF_NAMES,
    VALUE_NAMES,
    ClefPictures,
    KeySignaturePicture,
    RangePictures,
    ValuePictures,
    _Picture,
)
from alto.ui.practice_limits import DailyLimitsEditor
from alto.ui.staff import StaffWidget
from alto.ui.widgets import vertical_scroll_area
from alto.ui.zoom import (
    css,
    px,
)


def guard_last(
    boxes: Iterable[QAbstractButton],
    *,
    enabled: bool = True,
) -> None:
    """
    Disable the only checked box, so that at least one choice always
    stays selected.

    Parameters
    ----------
    boxes : iterable of QAbstractButton
        The checkboxes of one choice.
    enabled : bool, default True
        False disables them all (for when the whole choice is switched
        off). Keyword-only.

    Examples
    --------
    >>> first, second = QCheckBox(), QCheckBox()
    >>> first.setChecked(True)
    >>> guard_last([first, second])
    >>> first.isEnabled(), second.isEnabled()
    (False, True)
    >>> second.setChecked(True)
    >>> guard_last([first, second])
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
    return f"{MAJOR_KEYS[count]}  ·  " + (
        "none" if count == 0 else f"{abs(count)}{'♯' if count > 0 else '♭'}"
    )


def arrow_button(
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
    >>> button = arrow_button(
    ...     Qt.ArrowType.UpArrow,
    ...     tip="Raise the lowest note",
    ... )
    >>> button.toolTip(), button.autoRepeat()
    ('Raise the lowest note', True)
    """
    btn = QToolButton()
    btn.setArrowType(kind)
    btn.setProperty(
        "arrowButton",
        True,
    )  # styled with a visible border (see style.py)
    btn.setToolTip(tip)
    btn.setAccessibleName(tip)
    btn.setAutoRepeat(True)
    btn.setAutoRepeatDelay(350)
    btn.setAutoRepeatInterval(90)
    return btn


class RangeEditor(QWidget):
    """
    A staff showing the lowest and highest note asked for a clef.

    Arrows on the left move the lower bound, arrows on the right move
    the upper bound.

    Attributes
    ----------
    edited : Signal
        Emitted with the clef key, the lowest note and the highest note
        (as staff steps) after a change.
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
    >>> editor = RangeEditor(
    ...     "treble", low=28, high=34
    ... )
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
        limits: tuple[int, int] | None = None,
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
        limits : tuple of (int, int) or None, default None
            The furthest the bounds may go, as staff steps; None for the
            clef's usual limits. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns the editor. Keyword-only.

        Examples
        --------
        >>> RangeEditor(
        ...     "bass", low=14, high=28
        ... ).limits == settings.RANGE_LIMITS["bass"]
        True
        >>> RangeEditor(
        ...     "alto", low=21, high=30, limits=(21, 30)
        ... ).limits
        (21, 30)
        """
        super().__init__(parent)
        self.key, self.low, self.high = key, low, high
        self.limits = limits or RANGE_LIMITS[key]
        self.caption_text = QLabel()
        self.caption_text.setStyleSheet(css("font-size: 12pt;"))
        self.caption = (
            QWidget()
        )  # the clef as a picture, then the lowest and highest note
        caption_row = QHBoxLayout(self.caption)
        caption_row.setContentsMargins(0, 0, 0, 0)
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
        self.staff.setFixedWidth(px(168))
        self.low_up = arrow_button(
            Qt.ArrowType.UpArrow,
            tip="Raise the lowest note",
        )
        self.low_down = arrow_button(
            Qt.ArrowType.DownArrow,
            tip="Lower the lowest note",
        )
        self.high_up = arrow_button(
            Qt.ArrowType.UpArrow,
            tip="Raise the highest note",
        )
        self.high_down = arrow_button(
            Qt.ArrowType.DownArrow,
            tip="Lower the highest note",
        )
        self.low_up.clicked.connect(lambda: self._move(low=1))
        self.low_down.clicked.connect(lambda: self._move(low=-1))
        self.high_up.clicked.connect(lambda: self._move(high=1))
        self.high_down.clicked.connect(lambda: self._move(high=-1))

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        # keep the staff and its arrows together, centered in the pane
        row.addStretch()
        for column, buttons in (
            (0, (self.low_up, self.low_down)),
            (2, (self.high_up, self.high_down)),
        ):
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
        Move the bounds by steps, keeping the lower below the upper and
        both within the limits.

        Parameters
        ----------
        low : int, default 0
            How many staff steps to move the lower bound; positive is
            higher.
        high : int, default 0
            How many steps to move the upper bound. Keyword-only.

        Examples
        --------
        >>> editor = RangeEditor(
        ...     "treble", low=28, high=34
        ... )
        >>> got = []
        >>> _ = editor.edited.connect(
        ...     lambda key, lo, hi: got.append(
        ...         (key, lo, hi)
        ...     )
        ... )
        >>> editor._move(low=1)
        >>> got
        [('treble', 29, 34)]
        >>> editor._move(
        ...     low=100
        ... )  # the lower bound cannot pass the upper
        >>> editor.low
        34
        """
        self.low = min(
            max(self.low + low, self.limits[0]),
            self.high,
        )  # the lower bound can't pass the upper
        self.high = max(min(self.high + high, self.limits[1]), self.low)
        self._refresh()
        self.edited.emit(self.key, self.low, self.high)

    def _refresh(self) -> None:
        """
        Show the bounds on the staff and in the caption, and enable only
        the arrows that can still move.

        Examples
        --------
        >>> editor = RangeEditor(
        ...     "treble", low=22, high=30
        ... )  # 22 is the lowest the treble range goes
        >>> editor._refresh()
        >>> (
        ...     editor.low_down.isEnabled(),
        ...     editor.low_up.isEnabled(),
        ... )
        (False, True)
        """
        self.caption_text.setText(
            f"<b>{diatonic_name(self.low)} – {diatonic_name(self.high)}</b>",
        )
        self.staff.show_notes(
            [[Note.from_diatonic(self.low)], [Note.from_diatonic(self.high)]],
            clef=self.key,
        )
        self.low_up.setEnabled(self.low < self.high)
        self.low_down.setEnabled(self.low > self.limits[0])
        self.high_up.setEnabled(self.high < self.limits[1])
        self.high_down.setEnabled(self.high > self.low)


class KeyDiagram(QWidget):
    """
    A small fork showing which key signatures are selected.

    C major is on the left, then two rows of seven dots: 1 to 7 sharps
    on the top row and 1 to 7 flats on the bottom.
    Selected keys are filled, the rest are hollow.

    Attributes
    ----------
    DOT, PITCH, ROW_GAP, PAD : float
        The dot radius and the spacing, in pixels.
    keys : set of int
        The selected key signatures: sharps if positive, flats if
        negative.

    Examples
    --------
    >>> KeyDiagram({0, 2}).toolTip()
    'C, D'
    """

    DOT, PITCH, ROW_GAP, PAD = (
        4.4,
        12.6,
        13.0,
        1.5,
    )  # dot radius and spacing, in pixels

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
        zoomed = zoom.factor()  # the dots and their spacing follow the zoom
        self.DOT, self.PITCH, self.ROW_GAP, self.PAD = (
            value * zoomed
            for value in (
                type(self).DOT,
                type(self).PITCH,
                type(self).ROW_GAP,
                type(self).PAD,
            )
        )
        self.first_column = (
            self.PAD + 2 * self.DOT + px(7) + self.DOT
        )  # x of the 1-sharp / 1-flat dots
        self.setFixedSize(
            int(self.first_column + 6 * self.PITCH + self.DOT + self.PAD)
            + px(1),
            int(self.ROW_GAP + 2 * self.DOT + 2 * self.PAD) + px(3),
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
        )  # the row underneath is the click target
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
        Set the tooltip to the names of the selected keys, sharp keys
        first.

        Examples
        --------
        >>> diagram = KeyDiagram({3, 1})
        >>> diagram._update_tip()
        >>> diagram.toolTip()
        'G, A'
        """
        names = [
            MAJOR_KEYS[k]
            for k in sorted(self.keys, key=lambda k: (k < 0, abs(k)))
        ]
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
        base = pal.color(
            QPalette.ColorRole.Base,
        )  # the row is filled with the base color

        def shade(
            t: float,
        ) -> (
            QColor
        ):  # t of the way from the row's background to the text color
            """
            Return a color a fraction of the way from the row's
            background to the text color.

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

        filled, outline = (
            shade(0.85),
            shade(0.5),
        )  # both stand out from the background, in a light or a dark theme
        mid, top = self.height() / 2, self.height() / 2 - self.ROW_GAP / 2
        spots = [
            (0, self.PAD + self.DOT, mid),
        ]  # C major, between the two rows
        for n in range(1, 8):
            x = self.first_column + (n - 1) * self.PITCH
            spots += [(n, x, top), (-n, x, top + self.ROW_GAP)]
        for count, x, y in spots:
            selected = count in self.keys
            p.setPen(QPen(filled if selected else outline, 1.2))
            p.setBrush(filled if selected else base)
            p.drawEllipse(QPointF(x, y), self.DOT, self.DOT)


# room for a picture on its own line in a menu row (pane width less
# margins)
ROW_PICTURE_WIDTH = 238


def label_with_picture(
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
    >>> label_with_picture(
    ...     box,
    ...     picture=ClefPictures(["treble"]),
    ...     name="Treble",
    ... )
    >>> box.toolTip(), box.accessibleName()
    ('Treble', 'Treble')
    """
    picture.label_button(button)
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
    label_with_picture(
        button,
        picture=ClefPictures([clef], scale=scale),
        name=CLEF_NAMES[clef],
    )
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
    Lay the clef checkboxes out one under another, in three groups
    divided by a line.

    The groups are the grand staff; the treble, bass, alto and tenor
    clefs; and the soprano, mezzo-soprano and baritone
    clefs. A group none of the boxes belong to is left out. The list is
    indented under its heading.

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
    >>> boxes_ = {
    ...     clef: _clef_box(clef)
    ...     for clef in (
    ...         "treble",
    ...         "bass",
    ...         "soprano",
    ...     )
    ... }
    >>> widget_ = _clef_list(boxes_)
    >>> # noinspection PyUnresolvedReferences
    >>> # two boxes_, a dividing line, and one box
    >>> widget_.layout().count()
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
    groups = [
        [boxes[c] for c in group if c in boxes]
        for group in settings.CLEF_GROUPS
    ]
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


def clef_choice_page(
    choices: Iterable[str],
    *,
    selected: set[str],
    edited: Callable[[], object],
    back: Callable[[], object],
    title: str = "Clefs",
    hint: str = "One of the checked clefs is picked at random.",
) -> tuple[dict[str, QCheckBox], QWidget]:
    """
    Build the "Clefs" page that every exercise with a choice of clefs
    shares.

    Parameters
    ----------
    choices : iterable of str
        The clefs to offer, from `settings.RANGE_KEYS`; "grand" is left
        out of exercises that cannot use the grand staff.
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
        The page, with its title. The last checked clef cannot be
        unchecked.

    Examples
    --------
    >>> checked = []
    >>> boxes_, page_ = clef_choice_page(
    ...     ("treble", "bass"),
    ...     selected={"bass"},
    ...     edited=lambda: checked.append(1),
    ...     back=lambda: None,
    ... )
    >>> boxes_[
    ...     "bass"
    ... ].isEnabled()  # it is the only one checked, so it stays checked
    False
    >>> boxes_["treble"].setChecked(True)
    >>> (
    ...     sorted(
    ...         c
    ...         for c, ticked_box in boxes_.items()
    ...         if ticked_box.isChecked()
    ...     ),
    ...     checked,
    ... )
    (['bass', 'treble'], [1])
    """
    boxes = {c: _clef_box(c) for c in choices}
    body = QWidget()
    lay = QVBoxLayout(body)
    lay.setContentsMargins(0, 0, 0, 0)
    note = QLabel(hint)
    note.setWordWrap(True)
    note.setStyleSheet("color: gray;")
    lay.addWidget(note)
    for c, box in boxes.items():
        box.setChecked(c in selected)
    lay.addWidget(_clef_list(boxes))
    guard_last(
        list(boxes.values()),
    )  # the last checked clef can't be unchecked
    for box in boxes.values():
        box.toggled.connect(edited)
    return boxes, subpage(title, body=body, back=back)


def show_keys(
    row: MenuRow,
    *,
    diagram: KeyDiagram,
    enabled: bool,
    keys: set[int],
) -> None:
    """
    Show the selected keys as a diagram in a menu row, or "Off" when key
    signatures are switched off.

    Parameters
    ----------
    row : MenuRow
        The menu row.
    diagram : KeyDiagram
        The diagram to update. Keyword-only.
    enabled : bool
        Whether key signatures are on. Keyword-only.
    keys : set of int
        The selected key signatures. Keyword-only.

    Examples
    --------
    >>> row_, diagram_ = (
    ...     MenuRow("Key signatures"),
    ...     KeyDiagram(),
    ... )
    >>> show_keys(
    ...     row_,
    ...     diagram=diagram_,
    ...     enabled=False,
    ...     keys={0},
    ... )
    >>> row_.value.text(), diagram_.isHidden()
    ('Off', True)
    """
    diagram.set_keys(keys)
    diagram.setVisible(enabled)
    row.value.setText("" if enabled else "Off")


class _ValueLabel(QLabel):
    """
    The value shown on the right of a menu row, which a screen reader is
    also given as the row's description.

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


class MenuRow(QPushButton):
    """
    A menu row: title on the left, current value and a chevron on the
    right.

    A `tall` row puts a picture on a second line of its own, using the
    full width, for summaries that need room to be
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
    >>> row = MenuRow("Range", tall=True)
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
            Show a chevron on the right, to say it opens a page.
            Keyword-only.
        tall : bool, default False
            Give the row a second line for a picture. Keyword-only.

        Examples
        --------
        >>> MenuRow("Clefs").minimumHeight()
        48
        """
        super().__init__()
        self.tall = tall
        self._contents: QBoxLayout  # the layout inside the row
        self.title = QLabel(f"<b>{title}</b>")
        self.setAccessibleName(
            title,
            # the text is in labels on the button, which a screen reader
            # would not read as its name
        )
        self.value = _ValueLabel(self)
        self.value.setStyleSheet("color: gray;")
        self.value.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        )
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
        self.setMinimumHeight(px(48))
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

        Just after the value text, or (in a tall row) centered on its
        own line below.

        Parameters
        ----------
        widget : QWidget
            The widget, usually a small picture of the current choice.

        Examples
        --------
        >>> row = MenuRow("Clefs")
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
        >>> row = MenuRow("Range", tall=True)
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
        self.setFixedSize(px(self.W), px(self.H))
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
            0 for off up to 1 for on, with values between while it
            slides.

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

    def setChecked(
        self,
        on: bool,
    ) -> None:  # no animation when set programmatically
        """
        Turn the switch on or off without animating, as when a setting
        is loaded.

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
        off, on = (
            pal.color(QPalette.ColorRole.Mid),
            pal.color(QPalette.ColorRole.Highlight),
        )
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


class ToggleRow(MenuRow):
    """
    A menu row with a switch that changes a setting in place instead of
    opening a page.

    Attributes
    ----------
    switched : Signal
        Emitted with the new state when the row is clicked.
    switch : Switch
        The switch.

    Examples
    --------
    >>> row = ToggleRow("Accidentals")
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
        >>> ToggleRow("Accidentals").isOn()
        False
        """
        super().__init__(title, chevron=False)
        self.value.hide()
        self.switch = Switch()
        self.switch.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
        )  # the whole row is the click target
        self.switch.setFocusPolicy(
            Qt.FocusPolicy.NoFocus,
        )  # the row is what the keyboard reaches, not its picture of a switch
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
        >>> row = ToggleRow("Accidentals")
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
        >>> ToggleRow("Accidentals").isOn()
        False
        """
        return self.switch.isChecked()

    # noinspection PyPep8Naming
    def setOn(self, on: bool) -> None:
        """
        Set the switch without announcing it, as when a setting is
        loaded.

        Parameters
        ----------
        on : bool
            The new state.

        Examples
        --------
        >>> row = ToggleRow("Accidentals")
        >>> row.setOn(True)
        >>> row.isOn()
        True
        """
        self.switch.setChecked(on)


def subpage(
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
        Let the body take all the room (so a long page can scroll)
        instead of leaving space below it. Keyword-only.

    Returns
    -------
    QWidget
        The page.

    Examples
    --------
    >>> calls = []
    >>> page_ = subpage(
    ...     "Clefs",
    ...     body=QWidget(),
    ...     back=lambda: calls.append("back"),
    ... )
    >>> next(
    ...     b
    ...     for b in page_.findChildren(QToolButton)
    ...     if b.text() == "‹ Back"
    ... ).click()
    >>> calls
    ['back']
    """
    page = QWidget()
    lay = QVBoxLayout(page)
    lay.setContentsMargins(0, 0, 0, 0)
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
    A stacked widget whose pages slide in from the right (going deeper)
    or the left (going back).

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

        Going to a later page slides it in from the right and going back
        slides it in from the left. A request made during a
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
            Finish the slide: show the new page and put both pages back
            in place.

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
        motion.play(group)


class ExerciseSettingsPanel(QWidget):
    """
    What every exercise's settings pane has in common: it says when a
    setting has been edited.

    Attributes
    ----------
    changed : Signal
        Emitted after any setting is edited that changes what is asked,
        so the exercise asks a new question.
    restyled : Signal
        Emitted after a setting is edited that changes only how the
        exercise looks, so the question stays and the picture is
        drawn again.

    Examples
    --------
    >>> panel = ExerciseSettingsPanel()
    >>> got = []
    >>> _ = panel.changed.connect(
    ...     lambda: got.append(1)
    ... )
    >>> panel.changed.emit()
    True
    >>> got
    [1]
    """

    stack: SlideStack
    next_question_choices: QWidget
    next_question_row: MenuRow
    next_question_mode = "After Animation"
    choice_buttons_row: MenuRow | None = None
    changed = Signal()
    restyled = Signal()

    limits_row: MenuRow | None = None
    limits_editor: DailyLimitsEditor
    limits_page: int

    def _build_menu(self) -> tuple[QWidget, QVBoxLayout]:
        """
        Set up the sliding stack and create its Settings menu.

        Returns
        -------
        tuple of QWidget and QVBoxLayout
            The menu and the layout for its rows.

        Examples
        --------
        Each panel adds its own rows under the Settings heading.
        """
        self.stack = SlideStack()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.stack)
        menu = QWidget()
        layout = QVBoxLayout(menu)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel("<h3>Settings</h3>"))
        return menu, layout

    def refresh_limits(self, mode: str, *, self_grading: bool = False) -> None:
        """
        Update scheduling controls for the active scheduler and profile.

        Parameters
        ----------
        mode : str
            Selected question scheduler.
        self_grading : bool
            Disable Next Question when a passing grade advances the
            exercise.

        Examples
        --------
        Switching to ASRS hides the row and leaves its submenu.
        """
        self.next_question_row.setEnabled(not self_grading)
        self.next_question_choices.setEnabled(not self_grading)
        if self.limits_row is None:
            return
        enabled = mode in CALENDAR_SCHEDULERS
        self.limits_row.setVisible(enabled)
        if enabled:
            self.limits_editor.reload()
            editor = self.limits_editor
            new, reviews = (
                "∞" if box.isChecked() else field.value()
                for box, field in zip(
                    editor.unlimited,
                    editor.fields,
                    strict=True,
                )
            )
            self.limits_row.value.setText(f"{new} new · {reviews} reviews")
        elif self.stack.currentIndex() == self.limits_page:
            self.stack.setCurrentIndex(0)

    def _go(self, index: int) -> None:
        """
        Slide to a page, getting it ready first.

        A request made during a slide, or for the page already shown, is
        ignored.

        Parameters
        ----------
        index : int
            The page: 0 for the menu, the others in the order the pane
            added them.

        Examples
        --------
        >>> from alto.ui.settings_panel import (
        ...     ClefBasicsSettingsPanel,
        ... )
        >>> panel = ClefBasicsSettingsPanel(
        ...     settings.ClefBasicsSettings()
        ... )
        >>> panel._go(1)
        >>> panel.stack.sliding
        True
        """
        if self.stack.sliding or index == self.stack.currentIndex():
            return
        self._prepare(index)
        self.stack.slide_to(index)

    def _prepare(self, index: int) -> None:
        """
        Get a page ready to be shown: going back to the menu brings its
        summaries up to date.

        Panes with pages that need building when they open add to this.

        Parameters
        ----------
        index : int
            The page about to be shown.

        Examples
        --------
        >>> from alto.ui.settings_panel import (
        ...     ClefBasicsSettingsPanel,
        ... )
        >>> panel = ClefBasicsSettingsPanel(
        ...     settings.ClefBasicsSettings()
        ... )
        >>> panel.cfg.clefs = {"alto"}
        >>> panel._prepare(0)
        >>> panel.clef_pictures.clefs
        ['alto']
        """
        if index == 0:
            self._refresh_summaries()

    def _refresh_summaries(self) -> None:
        """
        Show the current settings in the menu's rows. Panes whose rows
        show nothing that can change leave this empty.

        Examples
        --------
        >>> ExerciseSettingsPanel()._refresh_summaries()
        """

    def _persist(self) -> None:
        """
        Save the settings this pane edits. Panes that save each setting
        as it is edited leave this empty.

        Examples
        --------
        >>> ExerciseSettingsPanel()._persist()
        """

    def _save_and_emit(self) -> None:
        """
        Save the settings and say they changed, so the exercise asks a
        new question.

        Examples
        --------
        >>> panel = ExerciseSettingsPanel()
        >>> got = []
        >>> _ = panel.changed.connect(
        ...     lambda: got.append(1)
        ... )
        >>> panel._save_and_emit()
        >>> got
        [1]
        """
        self._persist()
        self.changed.emit()


class KeyboardRangePanel(ExerciseSettingsPanel):
    """
    Settings for selecting a practice range on a keyboard.

    Examples
    --------
    Keyboard note identification allows the lowest and highest keys to
    coincide.
    """

    @abstractmethod
    def _step(self, which: str, *, delta: int) -> None:
        """
        Move an endpoint within the exercise's allowed range.

        Parameters
        ----------
        which : str
            Endpoint to move, low or high.
        delta : int
            Number of semitones to move.

        Examples
        --------
        Pressing the upper endpoint's left arrow lowers the highest key
        by a semitone.
        """

    def _range_body(
        self,
        span: KeyboardSpan,
        *,
        changed: Callable[[int, int], None],
        full: tuple[int, int] = settings.KEYBOARD_FULL,
        default: tuple[int, int] = settings.KEYBOARD_DEFAULT,
        single_note: bool = False,
    ) -> QWidget:
        """
        Build the range selector, endpoint arrows, and reset buttons.

        Parameters
        ----------
        span : KeyboardSpan
            Keyboard used for dragging and displaying the selected keys.
        changed : callable
            Receive the lowest and highest selected MIDI keys.
        full : tuple of int
            The instrument's full range.
        default : tuple of int
            The exercise's default range.
        single_note : bool
            Use the instructions and spacing for single-note
            identification.

        Returns
        -------
        QWidget
            The body of the Range page.

        Examples
        --------
        A plugin can display its instrument's own range while using the
        same endpoint buttons as a piano.
        """
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        if single_note:
            layout.setSpacing(10)
            hint = QLabel("Drag on the keyboard to choose the keys to ask.")
        else:
            hint = QLabel("Choose a range that fits both highlighted notes.")
            hint.setWordWrap(True)
        layout.addWidget(hint)
        span.full = full
        span.dragged.connect(changed)
        layout.addWidget(span)
        self.low_label, self.high_label = QLabel(), QLabel()
        self.arrows: dict[str, tuple[QToolButton, QToolButton]] = {}
        for title, label, which in (
            ("Lowest key", self.low_label, "low"),
            ("Highest key", self.high_label, "high"),
        ):
            row = QHBoxLayout()
            row.addWidget(QLabel(f"<b>{title}</b>"), 1)
            down = arrow_button(
                Qt.ArrowType.LeftArrow,
                tip=f"{title}: one key down",
            )
            up = arrow_button(
                Qt.ArrowType.RightArrow,
                tip=f"{title}: one key up",
            )
            down.clicked.connect(
                lambda _=False, w=which: self._step(w, delta=-1),
            )
            up.clicked.connect(lambda _=False, w=which: self._step(w, delta=1))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumWidth(px(48))
            row.addWidget(down)
            row.addWidget(label)
            row.addWidget(up)
            layout.addLayout(row)
            self.arrows[which] = (down, up)
        self.entire = QPushButton("Entire keyboard")
        self.entire.clicked.connect(lambda: changed(*full))
        self.default = QPushButton("Reset to default")
        self.default.clicked.connect(lambda: changed(*default))
        layout.addWidget(self.entire)
        layout.addWidget(self.default)
        return body


class ClefsPanel(ExerciseSettingsPanel):
    """
    A settings pane with a Clefs page, whose checkboxes choose the clefs
    that are asked about.

    Attributes
    ----------
    cfg : ClefChoice
        The settings being edited.
    boxes : dict of str to QCheckBox
        The checkbox of each clef.
    clef_pictures : ClefPictures
        The clefs shown in the menu's Clefs row.

    Examples
    --------
    >>> from alto.ui.settings_panel import (
    ...     ClefBasicsSettingsPanel,
    ... )
    >>> isinstance(
    ...     ClefBasicsSettingsPanel(
    ...         settings.ClefBasicsSettings()
    ...     ),
    ...     ClefsPanel,
    ... )
    True
    """

    cfg: settings.ClefChoice
    boxes: dict[str, QCheckBox]
    clef_pictures: ClefPictures

    def _clefs_edited(self) -> None:
        """
        Take the checked clefs into the settings, save them and say so.
        The last checked clef cannot be unchecked.

        Examples
        --------
        >>> from alto.ui.settings_panel import (
        ...     ClefBasicsSettingsPanel,
        ... )
        >>> from alto.ui.store import store
        >>> cfg = settings.ClefBasicsSettings()
        >>> panel = ClefBasicsSettingsPanel(cfg)
        >>> panel.boxes["french"].setChecked(True)
        >>> (
        ...     "french" in cfg.clefs,
        ...     str(store().value("clefBasics/clefs")),
        ... )
        (True, 'treble,bass,french')
        >>> panel.boxes["treble"].setChecked(False)
        >>> panel.boxes["bass"].setChecked(False)
        >>> (
        ...     panel.boxes["french"].isEnabled(),
        ...     cfg.active_clefs(),
        ... )
        (False, ['french'])
        >>> store().remove("clefBasics")
        """
        self.cfg.clefs = {c for c, b in self.boxes.items() if b.isChecked()}
        guard_last(list(self.boxes.values()))
        self._save_and_emit()


class StaffRangePanel(ClefsPanel):
    """
    Shared navigation and per-clef pitch range editors.

    Examples
    --------
    Note and interval identification both open Range on page two.
    """

    cfg: settings.StaffRangeSettings
    value_pictures: ValuePictures
    stack: SlideStack

    range_pictures: RangePictures
    range_row: MenuRow
    range_index = 2  # where the Range page sits in the stack

    def _limits(self, key: str) -> tuple[int, int] | None:
        """
        Say how far a clef's range may be moved.

        Parameters
        ----------
        key : str
            The clef.

        Returns
        -------
        tuple of (int, int) or None
            The lowest and highest staff step, or None for the clef's
            usual limits.

        Examples
        --------
        >>> from alto.settings import NoteNameSettings
        >>> from alto.ui.settings_panel import (
        ...     NoteNameSettingsPanel,
        ... )
        >>> NoteNameSettingsPanel(
        ...     NoteNameSettings()
        ... )._limits("treble") is None
        True
        """
        del key
        return None

    def _refresh_summaries(self) -> None:
        """
        Refresh the exercise-specific main menu previews.

        Examples
        --------
        Returning from Range refreshes its staff preview.
        """
        clefs = self.cfg.active_clefs()
        self.clef_pictures.set_clefs(clefs)
        self.range_pictures.set_items(
            [(c, *self.cfg.range_for(c)) for c in clefs],
        )
        self.range_row.fit()
        self.value_pictures.set_values(self.cfg.active_values())

    def _values_page(self, title: str) -> QWidget:
        """
        Build the shared note-value checklist with an engraved preview
        of each option.

        Parameters
        ----------
        title : str
            The settings row label.

        Returns
        -------
        QWidget
            The scrollable submenu.

        Examples
        --------
        >>> from alto.settings import NoteNameSettings
        >>> from alto.ui.settings_panel import (
        ...     NoteNameSettingsPanel,
        ... )
        >>> NoteNameSettingsPanel(
        ...     NoteNameSettings()
        ... ).value_boxes["whole"].isChecked()
        True
        """
        self.value_boxes = {v: QCheckBox(VALUE_NAMES[v]) for v in NOTE_VALUES}
        values_body = QWidget()
        vlay = QVBoxLayout(values_body)
        vlay.setContentsMargins(0, 0, 0, 0)
        vlay.setSpacing(2)
        values_hint = QLabel("One of the checked values is picked at random.")
        values_hint.setWordWrap(True)
        vlay.addWidget(values_hint)
        for v, box in self.value_boxes.items():
            picture = ValuePictures([v], scale=1.25, center_stemless=True)
            picture.label_button(box)
            box.setStyleSheet(css("QCheckBox { font-size: 11pt; }"))
            box.setChecked(v in self.cfg.note_values)
            box.toggled.connect(self._values_edited)
            vlay.addWidget(box)
        vlay.addStretch()
        guard_last(list(self.value_boxes.values()))
        return subpage(
            title,
            body=scrolling(values_body),
            back=lambda: self._go(0),
            fill=True,
        )

    def _values_edited(self) -> None:
        """
        Take the checked note values into the settings, save them and
        say so.

        Examples
        --------
        >>> from alto.settings import NoteNameSettings
        >>> from alto.ui.settings_panel import (
        ...     NoteNameSettingsPanel,
        ... )
        >>> panel = NoteNameSettingsPanel(
        ...     NoteNameSettings()
        ... )
        >>> panel.value_boxes["half"].setChecked(True)
        >>> "half" in panel.cfg.note_values
        True
        """
        self.cfg.note_values = {
            v for v, b in self.value_boxes.items() if b.isChecked()
        }
        guard_last(list(self.value_boxes.values()))
        self._save_and_emit()

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
        # Restoring a pane after a theme change selects its page
        # directly.
        self.stack.currentChanged.connect(
            lambda index: (
                self._build_range_rows()
                if index == self.range_index and not self.range_editors
                else None
            ),
        )
        scroll = QScrollArea()
        scroll.setWidget(self.range_body)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        )
        return subpage(
            "Range",
            body=scroll,
            back=lambda: self._go(0),
            fill=True,
        )

    def _prepare(self, index: int) -> None:
        """
        Get a page ready to be shown: the menu's summaries are brought
        up to date and the Range page's rows are built.

        Parameters
        ----------
        index : int
            The page about to be shown.

        Examples
        --------
        >>> from alto.settings import NoteNameSettings
        >>> from alto.ui.settings_panel import (
        ...     NoteNameSettingsPanel,
        ... )
        >>> panel = NoteNameSettingsPanel(
        ...     NoteNameSettings()
        ... )
        >>> panel._go(2)
        >>> (
        ...     sorted(panel.range_editors),
        ...     panel.stack.sliding,
        ... )
        (['bass', 'treble'], True)
        """
        super()._prepare(index)
        if index == self.range_index:
            self._build_range_rows()

    def _active_keys(self) -> list[str]:
        """
        Return the clefs in use.

        Returns
        -------
        list of str
            The chosen clefs, which the range editors and summaries are
            for.

        Examples
        --------
        >>> from alto.settings import NoteNameSettings
        >>> from alto.ui.settings_panel import (
        ...     NoteNameSettingsPanel,
        ... )
        >>> NoteNameSettingsPanel(
        ...     NoteNameSettings(clefs={"alto"})
        ... )._active_keys()
        ['alto']
        """
        return self.cfg.active_clefs()

    # range page
    def _build_range_rows(self) -> None:
        """
        Build a range editor for each clef in use, and a button to reset
        them to the defaults.

        Examples
        --------
        >>> from alto.settings import NoteNameSettings
        >>> from alto.ui.settings_panel import (
        ...     NoteNameSettingsPanel,
        ... )
        >>> panel = NoteNameSettingsPanel(
        ...     NoteNameSettings(clefs={"treble"})
        ... )
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
            editor = RangeEditor(
                key,
                low=low,
                high=high,
                limits=self._limits(key),
            )
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
        >>> from alto.settings import NoteNameSettings
        >>> from alto.ui.settings_panel import (
        ...     NoteNameSettingsPanel,
        ... )
        >>> panel = NoteNameSettingsPanel(
        ...     NoteNameSettings()
        ... )
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
        >>> from alto.settings import NoteNameSettings
        >>> from alto.ui.settings_panel import (
        ...     NoteNameSettingsPanel,
        ... )
        >>> panel = NoteNameSettingsPanel(
        ...     NoteNameSettings(
        ...         ranges={"treble": (30, 40)}
        ...     )
        ... )
        >>> panel._reset_ranges()
        >>> panel.cfg.ranges
        {}
        """
        self.cfg.ranges.clear()
        self._build_range_rows()
        self._save_and_emit()


class NoteAnswerSettingsPanel(StaffRangePanel):
    """
    Staff range settings for note names and optional octaves.

    Examples
    --------
    A plugin and the built-in note identification exercise can both
    require the octave in an answer.
    """

    cfg: settings.NoteNameSettings | settings.PackExerciseSettings

    def _accidentals_toggled(self, on: bool) -> None:
        """
        Save the Accidentals setting and emit the change.

        Parameters
        ----------
        on : bool
            Whether sharps, flats and naturals are asked.

        Examples
        --------
        >>> from alto.ui.settings_panel import (
        ...     NoteNameSettingsPanel,
        ... )
        >>> panel = NoteNameSettingsPanel(
        ...     settings.NoteNameSettings()
        ... )
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
        >>> from alto.ui.settings_panel import (
        ...     NoteNameSettingsPanel,
        ... )
        >>> panel = NoteNameSettingsPanel(
        ...     settings.NoteNameSettings()
        ... )
        >>> panel._octave_toggled(True)
        >>> panel.cfg.require_octave
        True
        """
        self.cfg.require_octave = on
        self._save_and_emit()


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
        >>> _LabeledKeyCheckBox().hitButton(
        ...     QPoint(-1, -1)
        ... )
        False
        """
        return self.rect().contains(pos)


class KeyChecklist(QWidget):
    """
    Checkboxes for the 15 major keys, flats on the left and sharps on
    the right.

    At least one stays checked. Each is labeled with a picture of its
    signature.

    Attributes
    ----------
    changed : Signal
        Emitted after a box is checked or unchecked.
    boxes : dict of int to QCheckBox
        The checkbox of each key signature, from -7 (seven flats) to 7
        (seven sharps).

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
        counts_only: bool = False,
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
        counts_only : bool, default False
            Label each box with its accidental count instead of drawing
            a signature. Keyword-only.
        key_names : dict of int to str or None, default None
            Key names to display beside the signature diagrams. With
            None, show only diagrams. Keyword-only.
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
                description = (
                    f"{name}, {signature}"
                    if count
                    else f"{name}, no sharps or flats"
                )
                box.setText(name)
                box.setToolTip(description)
                box.setAccessibleName(description)
                picture = KeySignaturePicture(count, scale=0.9)
                picture.setAttribute(
                    Qt.WidgetAttribute.WA_TransparentForMouseEvents,
                )
                label_width = box.sizeHint().width()
                contents = QHBoxLayout(box)
                contents.setContentsMargins(label_width + 4, 0, 0, 0)
                contents.addWidget(
                    picture,
                    alignment=Qt.AlignmentFlag.AlignLeft
                    | Qt.AlignmentFlag.AlignVCenter,
                )
                box.setMinimumWidth(label_width + 4 + picture.width())
                box.setMinimumHeight(picture.height())
                if count:
                    grid.addWidget(box, abs(count), int(count > 0))
                else:
                    grid.addWidget(box, 0, 0, 1, 2)
            for column in range(2):
                grid.setColumnStretch(column, 1)
        else:
            for (
                k,
                box,
                # each key is labeled with its signature, as written
                # after a
                # treble clef
            ) in self.boxes.items():
                if counts_only:
                    box.setText(
                        f"{abs(k)} {'♭' if k < 0 else '♯'}" if k else "0",
                    )
                    box.setAccessibleName(format_key_signature(k))
                else:
                    description = (
                        f"{MAJOR_KEYS[k]}"
                        " major, "
                        f"{_key_label(k).split('·')[1].strip()}"
                    )
                    label_with_picture(
                        box,
                        picture=KeySignaturePicture(k, scale=1.15),
                        name=description,
                    )
            # Two framed groups: C major on its own, and the keys with
            # sharps or flats (flats left, sharps right).
            outer = QVBoxLayout(self)
            outer.setContentsMargins(0, 0, 0, 0)
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
            guard_last(list(self.boxes.values()))

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
        >>> _ = checklist.changed.connect(
        ...     lambda: got.append(1)
        ... )
        >>> checklist.boxes[3].setChecked(True)
        >>> got
        [1]
        """
        if not self.allow_empty:
            guard_last(list(self.boxes.values()))
        self.changed.emit()


class KeySignaturePage(QWidget):
    """
    The key signature sub-page: a switch for using key signatures at
    all, and the keys to draw from.

    Attributes
    ----------
    changed : Signal
        Emitted after the switch or a key is changed.
    switch_row : ToggleRow
        The "Use key signatures" switch.
    checklist : KeyChecklist
        The keys; only enabled while the switch is on.

    Examples
    --------
    >>> page = KeySignaturePage(
    ...     True, selected={0, 1}
    ... )
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
            Key names to display beside the signature diagrams. With
            None, show only diagrams. Keyword-only.
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
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        self.switch_row = ToggleRow("Use key signatures")
        self.switch_row.setOn(enabled)
        self.switch_row.switched.connect(self._switched)
        self.checklist = KeyChecklist(
            selected,
            allow_empty=allow_empty,
            key_names=key_names,
        )
        self.checklist.changed.connect(self.changed)
        self.checklist.setEnabled(
            enabled,
        )  # the keys only matter while key signatures are on
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
        >>> KeySignaturePage(
        ...     True, selected={0}
        ... ).enabled()
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
        >>> KeySignaturePage(
        ...     True, selected={-2, 0}
        ... ).selected() == {-2, 0}
        True
        """
        return self.checklist.selected()

    def _switched(self, on: bool) -> None:
        """
        Enable the keys only while key signatures are on, and say that
        something changed.

        Parameters
        ----------
        on : bool
            The switch's new state.

        Examples
        --------
        >>> page = KeySignaturePage(True, selected={0})
        >>> got = []
        >>> _ = page.changed.connect(
        ...     lambda: got.append(1)
        ... )
        >>> page._switched(False)
        >>> page.checklist.isEnabled(), got
        (False, [1])
        """
        self.checklist.setEnabled(on)
        self.changed.emit()


class ScaleKeyPicker(QTabWidget):
    """
    Select major and minor keys independently.

    Examples
    --------
    >>> ScaleKeyPicker(
    ...     major_keys={0}, minor_keys={-2}
    ... ).count()
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
        >>> ScaleKeyPicker(
        ...     major_keys=set(), minor_keys={0}
        ... ).currentIndex()
        1
        """
        super().__init__()
        major_names = {count: f"{name}M" for count, name in MAJOR_KEYS.items()}
        self.major_keys = KeyChecklist(
            major_keys,
            allow_empty=True,
            key_names=major_names,
        )
        minor_names = {
            count: f"{mode_tonic(count, mode='Natural minor (Aeolian)').name}m"
            for count in range(-7, 8)
        }
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


class ChoiceChecklist(QWidget):
    """
    Checkboxes for a list of choices, optionally under headings and
    allowing an empty selection.

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
    >>> groups = [
    ...     (
    ...         "Triads",
    ...         [
    ...             ("major", "Major"),
    ...             ("minor", "Minor"),
    ...         ],
    ...     ),
    ...     ("", [("x", "Other")]),
    ... ]
    >>> checklist = ChoiceChecklist(
    ...     groups, selected={"major"}
    ... )
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
        positions: Mapping[object, tuple[int, int]] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the checklist.

        Parameters
        ----------
        groups : list of tuple of (str, list of tuple of (object, str))
            The headings and, under each, the choices as (key, label);
            an empty heading shows none.
        selected : set
            The keys to check initially. Keyword-only.
        allow_empty : bool, default False
            Allow all choices to be unchecked. Keyword-only.
        positions : mapping or None, default None
            Optional (row, column) for each key within its group.
            Keyword-only.
        parent : QWidget or None, default None
            The widget that owns it. Keyword-only.

        Examples
        --------
        >>> checklist = ChoiceChecklist(
        ...     [("", [(0, "Root"), (1, "1st")])],
        ...     selected={0},
        ... )
        >>> # noinspection PyTypeChecker
        >>> sorted(checklist.boxes)
        [0, 1]
        """
        super().__init__(parent)
        self.allow_empty = allow_empty
        self.boxes: dict[object, QCheckBox] = {}
        self.headings: dict[str, QLabel] = {}
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        for title, items in groups:
            if title:
                heading = QLabel(title)
                heading.setStyleSheet("color: gray;")
                self.headings[title] = heading
                lay.addWidget(heading)
            grid = None
            if positions is not None:
                grid = QGridLayout()
                grid.setSpacing(lay.spacing())
                lay.addLayout(grid)
                items = sorted(items, key=lambda item: positions[item[0]])
            for key, label in items:
                box = (
                    DegreeCheckBox(label) if "̂" in label else QCheckBox(label)
                )
                box.setChecked(key in selected)
                box.toggled.connect(self._toggled)
                self.boxes[key] = box
                if grid is not None and positions is not None:
                    row, column = positions[key]
                    grid.setColumnStretch(column, 1)
                    grid.addWidget(box, row, column)
                else:
                    lay.addWidget(box)
        if not self.allow_empty:
            guard_last(list(self.boxes.values()))

    def selected(self) -> set:
        """
        Return the checked choices.

        Returns
        -------
        set
            The keys of the checked boxes.

        Examples
        --------
        >>> ChoiceChecklist(
        ...     [("", [(0, "Root"), (1, "1st")])],
        ...     selected={0, 1},
        ... ).selected()
        {0, 1}
        """
        return {k for k, box in self.boxes.items() if box.isChecked()}

    def _toggled(self) -> None:
        """
        Keep one box checked, and say that something changed.

        Examples
        --------
        >>> checklist = ChoiceChecklist(
        ...     [("", [(0, "Root"), (1, "1st")])],
        ...     selected={0},
        ... )
        >>> got = []
        >>> _ = checklist.changed.connect(
        ...     lambda: got.append(1)
        ... )
        >>> checklist.boxes[1].setChecked(True)
        >>> got
        [1]
        """
        if not self.allow_empty:
            guard_last(list(self.boxes.values()))
        self.changed.emit()


def buttons_page(
    cfg: ButtonSettings
    | settings.IntervalSettings
    | settings.ScaleIdentificationSettings,
    *,
    changed: Callable[[], None],
    back: Callable[[], None],
) -> QWidget:
    """
    Build the shared Limited and All answer-button submenu.

    Parameters
    ----------
    cfg : ButtonSettings or IntervalSettings
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
    return subpage("Buttons", body=body, back=back)


def direction_choices(
    cfg: settings.ScaleIdentificationSettings
    | settings.ScaleConstructionSettings,
    *,
    edited: Callable[[], None],
) -> QWidget:
    """
    Choose the direction of a scale.

    Parameters
    ----------
    cfg : ScaleIdentificationSettings or ScaleConstructionSettings
        The exercise settings that store the selected motion.
    edited : callable
        Save the edit and refresh the exercise.

    Returns
    -------
    QWidget
        A pair of mutually exclusive Ascending and Descending radio
        buttons.

    Examples
    --------
    >>> cfg = settings.ScaleIdentificationSettings()
    >>> choices = direction_choices(
    ...     cfg, edited=lambda: None
    ... )
    >>> next(
    ...     b
    ...     for b in choices.findChildren(
    ...         QRadioButton
    ...     )
    ...     if b.text() == "Descending"
    ... ).click()
    >>> cfg.motion
    'descending'
    """

    def select(direction: str) -> None:
        """
        Save the direction when its radio button becomes checked.

        Parameters
        ----------
        direction : str
            The selected motion.

        Examples
        --------
        Selecting Descending saves the edit immediately.
        """
        cfg.motion = direction
        edited()

    body = QWidget()
    layout = QVBoxLayout(body)
    layout.setContentsMargins(0, 0, 0, 0)
    for direction in ("ascending", "descending"):
        radio = QRadioButton(direction.title())
        layout.addWidget(radio)
        radio.setChecked(cfg.motion == direction)
        radio.toggled.connect(
            lambda checked, value=direction: (
                select(value) if checked else None
            ),
        )

    return body


def scrolling(body: QWidget) -> QScrollArea:
    """
    Put a page's body in a scroll area, so a long page scrolls inside
    the pane and never makes the window taller.

    Parameters
    ----------
    body : QWidget
        What the page shows.

    Returns
    -------
    QScrollArea
        The scroll area that holds it, with no frame and no sideways
        scrolling.

    Examples
    --------
    >>> page = QWidget()
    >>> scrolling(page).widget() is page
    True
    """
    # Short option lists keep their natural height as the viewport
    # grows.
    policy = body.sizePolicy()
    policy.setVerticalPolicy(QSizePolicy.Policy.Maximum)
    body.setSizePolicy(policy)
    scroll = vertical_scroll_area(body)
    scroll.setMinimumHeight(0)
    return scroll
