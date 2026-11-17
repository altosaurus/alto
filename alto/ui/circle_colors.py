"""
The pages of the circle of fifths settings that choose its colors: a grid of schemes to pick from, and an editor to make one.

Examples
--------
>>> from alto.circle_schemes import preset
>>> SchemeThumb(preset("midnight")).scheme.name
'Midnight'
"""

from __future__ import annotations

from PySide6.QtCore import (
    QPointF,
    QRectF,
    QSize,
    Qt,
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
    QColorDialog,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from alto.circle_schemes import (
    CUSTOM_LIMIT,
    MODES,
    PRESETS,
    CustomRecord,
    Scheme,
    custom_scheme,
    hsl_of,
    next_custom_key,
)
from alto.ui.circle import (
    DISC,
    OUTER_FROM,
    wedge_color,
    wedge_path,
)

START_COLORS = ["#1fa7c9", "#2f6bd0", "#6a4fe0"]  # what a new scheme starts with: the idea of "Cyan to indigo"
THUMB = 112  # the size of a scheme's picture, in pixels


def blank(key: str) -> CustomRecord:
    """
    Make the scheme a new one starts as: colors by key signature, from cyan through blue to indigo, on dark wedges.

    Parameters
    ----------
    key : str
        The key the new scheme gets.

    Returns
    -------
    CustomRecord
        The scheme.

    Examples
    --------
    >>> blank("custom-3")["id"], blank("custom-3")["mode"]
    ('custom-3', 'signature')
    """
    return {"id": key, "name": "My colors", "mode": "signature", "colors": list(START_COLORS), "light": False}


class SchemeThumb(QPushButton):
    """
    A small picture of the circle in a color scheme, to click to choose the scheme.

    Attributes
    ----------
    scheme : Scheme
        The scheme it shows and chooses.

    Examples
    --------
    >>> from alto.circle_schemes import preset
    >>> thumb = SchemeThumb(preset("paper"))
    >>> thumb.isCheckable(), thumb.toolTip()
    (True, 'Pastel wedges of every hue with dark names, which deepen when lit.')
    """

    def __init__(
        self,
        scheme: Scheme,
        *,
        size: int = THUMB,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the picture.

        Parameters
        ----------
        scheme : Scheme
            The color scheme to draw.
        size : int, default 112
            Its width and height in pixels. Keyword-only.
        parent : QWidget or None, default None
            The widget that owns it. Keyword-only.

        Examples
        --------
        >>> from alto.circle_schemes import preset
        >>> SchemeThumb(preset("paper"), size=80).width()
        80
        """
        super().__init__(parent)
        self.scheme = scheme
        self.setCheckable(True)
        self.setFixedSize(size, size)
        self.setToolTip(scheme.description)
        self.setAccessibleName(scheme.name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)

    def sizeHint(self) -> QSize:
        """
        Return the size it asks for.

        Returns
        -------
        QSize
            The size it was built with.

        Examples
        --------
        >>> from alto.circle_schemes import preset
        >>> SchemeThumb(preset("paper"), size=90).sizeHint().width()
        90
        """
        return self.size()

    def paintEvent(self, _: QPaintEvent) -> None:
        """
        Draw the circle, with one cell asked and its relative lit, and a ring around it when it is the chosen scheme.

        Parameters
        ----------
        _ : QPaintEvent
            The paint request.

        Examples
        --------
        >>> from alto.circle_schemes import preset
        >>> SchemeThumb(preset("midnight")).grab().isNull()
        False
        """
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        box = QRectF(self.rect()).adjusted(3, 3, -3, -3)
        radius = min(box.width(), box.height()) / 2
        center = QPointF(box.center())
        scheme = self.scheme
        window = self.palette().color(QPalette.ColorRole.Window)
        p.setPen(QPen(window, max(radius / 60, 0.8)))
        for index in range(12):
            for ring, (inner, outer) in {"outer": (OUTER_FROM, 1.0), "inner": (DISC, OUTER_FROM)}.items():
                lift = (0.6 if ring == "outer" else 0.4) if index == 0 else 0.0
                p.setBrush(wedge_color(index, inner=ring == "inner", lift=lift, scheme=scheme))
                p.drawPath(wedge_path(center=center, inner=inner * radius, outer=outer * radius, index=index))
        p.setBrush(window)
        p.drawEllipse(center, DISC * radius, DISC * radius)
        if self.isChecked():
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(self.palette().highlight().color(), 2.5))
            p.drawEllipse(center, radius + 1, radius + 1)


class SchemePage(QWidget):
    """
    The page that lists the color schemes: the presets, the user's own, and a button to make another.

    Attributes
    ----------
    chosen : Signal
        Emitted with the key of the scheme that was clicked.
    new : Signal
        Emitted when "Create your own" is clicked.
    edit_asked : Signal
        Emitted with the key of one of the user's schemes when its Edit button is clicked.
    thumbs : dict of str to SchemeThumb
        The picture of each scheme, by its key.

    Examples
    --------
    >>> page = SchemePage()
    >>> page.load(current="midnight", customs=[])
    >>> page.thumbs["midnight"].isChecked(), len(page.thumbs)
    (True, 14)
    """

    chosen = Signal(str)
    new = Signal()
    edit_asked = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the page, empty until `load` is called.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns it.

        Examples
        --------
        >>> SchemePage().thumbs
        {}
        """
        super().__init__(parent)
        self.thumbs: dict[str, SchemeThumb] = {}
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

    def load(
        self,
        *,
        current: str,
        customs: list[CustomRecord],
    ) -> None:
        """
        Fill the page: a picture and a name for each scheme, with the current one marked.

        Parameters
        ----------
        current : str
            The key of the chosen scheme. Keyword-only.
        customs : list of CustomRecord
            The user's own schemes. Keyword-only.

        Examples
        --------
        >>> page = SchemePage()
        >>> from alto.circle_schemes import record_of
        >>> mine = record_of("custom-1", name="Mine", mode="single", colors=["#2f6bd0"])
        >>> page.load(current="custom-1", customs=[mine])
        >>> page.thumbs["custom-1"].isChecked(), page.thumbs["midnight"].isChecked()
        (True, False)
        """
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        self.thumbs = {}
        self._section("Presets", schemes=list(PRESETS.values()), current=current, editable=False)
        if customs:
            self._section("Your own", schemes=[custom_scheme(record) for record in customs], current=current, editable=True)
        make = QPushButton("Create your own…")
        make.setEnabled(len(customs) < CUSTOM_LIMIT)
        make.clicked.connect(self.new.emit)
        self._layout.addWidget(make)
        self._layout.addStretch()

    def _section(
        self,
        title: str,
        *,
        schemes: list[Scheme],
        current: str,
        editable: bool,
    ) -> None:
        """
        Add a heading and a grid of schemes.

        Parameters
        ----------
        title : str
            The heading.
        schemes : list of Scheme
            The schemes to show. Keyword-only.
        current : str
            The key of the chosen scheme. Keyword-only.
        editable : bool
            Whether each gets an Edit button. Keyword-only.

        Examples
        --------
        >>> from alto.circle_schemes import preset
        >>> page = SchemePage()
        >>> page._section("Some", schemes=[preset("ink")], current="ink", editable=False)
        >>> page.thumbs["ink"].isChecked()
        True
        """
        heading = QLabel(f"<b>{title}</b>")
        self._layout.addWidget(heading)
        holder = QWidget()
        grid = QGridLayout(holder)
        grid.setContentsMargins(0, 0, 0, 0)
        for number, scheme in enumerate(schemes):
            cell = QVBoxLayout()
            thumb = SchemeThumb(scheme)
            thumb.setChecked(scheme.key == current)
            thumb.clicked.connect(lambda _=False, key=scheme.key: self.chosen.emit(key))
            self.thumbs[scheme.key] = thumb
            cell.addWidget(thumb, alignment=Qt.AlignmentFlag.AlignHCenter)
            name = QLabel(scheme.name)
            name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            name.setWordWrap(True)
            cell.addWidget(name)
            if editable:
                edit = QPushButton("Edit")
                edit.clicked.connect(lambda _=False, key=scheme.key: self.edit_asked.emit(key))
                cell.addWidget(edit)
            cell.addStretch()
            grid.addLayout(cell, number // 2, number % 2)
        self._layout.addWidget(holder)


class SchemeEditor(QWidget):
    """
    The editor for a color scheme of the user's own: a name, how its colors are made, and the colors.

    The colors are what a cell looks like when lit; the quiet cells are made from them. A picture shows the result as it is
    edited.

    Attributes
    ----------
    saved : Signal
        Emitted with the record when Save is clicked.
    deleted : Signal
        Emitted with the scheme's key when Delete is clicked (only an existing scheme can be deleted).
    canceled : Signal
        Emitted when Cancel is clicked.
    name : QLineEdit
        The name.
    mode : QComboBox
        How the colors are made: a key of `MODES` is each item's data.
    wedges : QComboBox
        Whether the wedges are dark, with light names, or light, with dark names.
    swatches : list of QPushButton
        One button for each color the mode takes; the others are hidden.
    preview : SchemeThumb
        The picture of the scheme as it is.

    Examples
    --------
    >>> editor = SchemeEditor()
    >>> editor.load(None, taken=[])
    >>> editor.record()["mode"], editor.record()["id"]
    ('signature', 'custom-1')
    """

    saved = Signal(object)
    deleted = Signal(str)
    canceled = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the editor.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns it.

        Examples
        --------
        >>> len(SchemeEditor().swatches)
        3
        """
        super().__init__(parent)
        self._key = ""
        self._colors = list(START_COLORS)
        self.name = QLineEdit()
        self.name.setMaxLength(40)
        self.mode = QComboBox()
        for key, (label, _) in MODES.items():
            self.mode.addItem(label, key)
        self.mode.setCurrentIndex(self.mode.findData("signature"))
        self.wedges = QComboBox()
        self.wedges.addItem("Dark wedges, light names", False)
        self.wedges.addItem("Light wedges, dark names", True)
        self.swatches = [QPushButton() for _ in range(3)]
        self._labels = [QLabel() for _ in range(3)]
        self.preview = SchemeThumb(custom_scheme(blank("")), size=150)
        self.preview.setEnabled(False)
        self.delete_button = QPushButton("Delete")
        form = QGridLayout()
        form.addWidget(QLabel("Name"), 0, 0)
        form.addWidget(self.name, 0, 1)
        form.addWidget(QLabel("Colors made"), 1, 0)
        form.addWidget(self.mode, 1, 1)
        form.addWidget(QLabel("Wedges"), 2, 0)
        form.addWidget(self.wedges, 2, 1)
        for number, (label, button) in enumerate(zip(self._labels, self.swatches, strict=True)):
            form.addWidget(label, 3 + number, 0)
            form.addWidget(button, 3 + number, 1)
            button.clicked.connect(lambda _=False, at=number: self._pick(at))
        buttons = QHBoxLayout()
        save, cancel = QPushButton("Save"), QPushButton("Cancel")
        save.clicked.connect(lambda: self.saved.emit(self.record()))
        cancel.clicked.connect(self.canceled.emit)
        self.delete_button.clicked.connect(lambda: self.deleted.emit(self._key))
        for button in (save, cancel, self.delete_button):
            buttons.addWidget(button)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.preview, alignment=Qt.AlignmentFlag.AlignHCenter)
        outer.addLayout(form)
        outer.addWidget(QLabel("A color is what a cell looks like when it is lit."))
        outer.addLayout(buttons)
        outer.addStretch()
        self.mode.currentIndexChanged.connect(self._refresh)
        self.wedges.currentIndexChanged.connect(self._refresh)
        self.name.textChanged.connect(self._refresh)

    def load(
        self,
        record: CustomRecord | None,
        *,
        taken: list[CustomRecord],
    ) -> None:
        """
        Start editing a scheme, or a new one.

        Parameters
        ----------
        record : CustomRecord or None
            The scheme to edit, or None to start a new one.
        taken : list of CustomRecord
            The user's schemes, so that a new one gets a key none of them has. Keyword-only.

        Examples
        --------
        >>> editor = SchemeEditor()
        >>> editor.load(None, taken=[])
        >>> editor.name.text(), editor.delete_button.isHidden()
        ('My colors', True)
        """
        draft = record or blank(next_custom_key(taken))
        self._key = draft["id"]
        self.name.setText(draft["name"])
        self.mode.setCurrentIndex(max(self.mode.findData(draft["mode"]), 0))
        self.wedges.setCurrentIndex(1 if draft["light"] else 0)
        self._colors = [*draft["colors"], *START_COLORS][:3]
        self.delete_button.setHidden(record is None)
        self._refresh()

    def record(self) -> CustomRecord:
        """
        Return the scheme as it is being edited.

        Returns
        -------
        CustomRecord
            Its key, name, mode, colors and whether its wedges are light.

        Examples
        --------
        >>> editor = SchemeEditor()
        >>> editor.load(None, taken=[])
        >>> editor.record()["colors"]
        ['#1fa7c9', '#2f6bd0', '#6a4fe0']
        """
        return self._draft()

    def set_color(
        self,
        index: int,
        *,
        color: str,
    ) -> None:
        """
        Set one of the colors.

        Parameters
        ----------
        index : int
            Which color of the mode: 0, 1 or 2.
        color : str
            The color, "#rrggbb". Keyword-only.

        Examples
        --------
        >>> editor = SchemeEditor()
        >>> editor.load(None, taken=[])
        >>> editor.set_color(0, color="#ff0000")
        >>> editor.record()["colors"][0]
        '#ff0000'
        """
        self._colors[index] = color
        self._refresh()

    def _draft(self) -> CustomRecord:
        """
        Gather the fields into a record, with only the colors the chosen mode takes.

        Returns
        -------
        CustomRecord
            The scheme.

        Examples
        --------
        >>> SchemeEditor()._draft()["mode"]
        'signature'
        """
        mode = str(self.mode.currentData())
        return {
            "id": self._key,
            "name": self.name.text().strip() or "My colors",
            "mode": mode,
            "colors": self._colors[: len(MODES[mode][1])],
            "light": bool(self.wedges.currentData()),
        }

    def _pick(self, index: int) -> None:
        """
        Ask for one of the colors in a color dialog.

        Parameters
        ----------
        index : int
            Which color of the mode.

        Examples
        --------
        >>> SchemeEditor()._pick.__name__
        '_pick'
        """
        chosen = QColorDialog.getColor(QColor(self._colors[index]), self, "Choose a color")
        if chosen.isValid():
            self.set_color(index, color=chosen.name())

    def _refresh(self) -> None:
        """
        Show only the colors the mode takes, label and tint them, and redraw the picture.

        Examples
        --------
        >>> editor = SchemeEditor()
        >>> editor.load(None, taken=[])
        >>> editor.mode.setCurrentIndex(editor.mode.findData("single"))
        >>> [swatch.isHidden() for swatch in editor.swatches]
        [False, True, True]
        """
        record = self._draft()
        labels = MODES[record["mode"]][1]
        for number, (label, button) in enumerate(zip(self._labels, self.swatches, strict=True)):
            visible = number < len(labels)
            label.setVisible(visible)
            button.setVisible(visible)
            if visible:
                label.setText(labels[number])
                shown = self._colors[number]
                ink = "#000000" if hsl_of(shown)[2] > 0.55 else "#ffffff"
                button.setText(shown)
                button.setStyleSheet(f"background: {shown}; color: {ink};")
        self.preview.scheme = custom_scheme(record)
        self.preview.update()
