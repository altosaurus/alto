"""
The editor for a theme of the user's own: a name, and a color for every part of its light and dark versions.

Examples
--------
>>> editor = ThemeEditor()
>>> editor.load(None)
>>> editor.record()["name"]
'My theme'
"""

from __future__ import annotations

from PySide6.QtCore import (
    QEvent,
    QObject,
    Qt,
    Signal,
)
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from alto.ui.dropdown import FieldComboBox
from alto.ui.theme import (
    PART_NAMES,
    PARTS,
    CustomTheme,
    ThemeRecord,
    custom_theme,
    families,
    new_family_id,
    preview_colors,
)
from alto.ui.theme_cards import ThemeThumb
from alto.ui.zoom import css, px

QUIET = "color: gray; font-family: monospace; font-size: 9pt;"  # how the code beside a color looks
LIT = "color: palette(text); font-family: monospace; font-size: 9pt; font-weight: bold;"  # and while its color is pointed at
DEFAULT_NAME = "My theme"
START_FROM = "studio"  # the theme a new one starts as, until another is chosen


def theme_of(
    colors: dict[str, str],
    *,
    dark: bool,
) -> CustomTheme:
    """
    Make a theme from a set of colors, to draw a picture of it.

    Parameters
    ----------
    colors : dict of str to str
        A color for every part, as "#rrggbb".
    dark : bool
        True if it is the dark version. Keyword-only.

    Returns
    -------
    CustomTheme
        The theme, without a key or a name of its own.

    Examples
    --------
    >>> theme_of({part: "#102030" for part in PARTS}, dark=True).window
    '#102030'
    """
    return CustomTheme(
        key="",
        family="",
        label="",
        note="",
        dark=dark,
        window=colors["window"],
        panel=colors["panel"],
        ink=colors["ink"],
        muted=colors["muted"],
        line=colors["line"],
        accent=colors["accent"],
        track=colors["track"],
    )


class ThemeEditor(QWidget):
    """
    A form to make a theme, or change one: its name, and the colors of its light and dark versions.

    A small picture of each version follows the colors as they are chosen. Choosing a theme in the "Start from" list takes its
    colors at once.

    Attributes
    ----------
    name_edit : QLineEdit
        The theme's name.
    start_from : FieldComboBox
        The themes whose colors can be taken; choosing one takes them.
    colors : dict of str to dict of str to str
        The colors being made, by "light" or "dark", and then by part.
    buttons : dict of str to dict of str to QPushButton
        The button of each color, which opens the color picker, by version and part.
    pictures : dict of str to ThemeThumb
        The picture of each version.
    save_button : QPushButton
        Saves the theme.
    delete_button : QPushButton
        Deletes the theme; it is only there for a theme that has been saved.
    saved : Signal
        Emitted with the theme's key when it is saved.
    canceled : Signal
        Emitted when the editing is given up.
    deleted : Signal
        Emitted with the theme's key when it is deleted.

    Examples
    --------
    >>> ThemeEditor().save_button.text()
    'Save'
    """

    saved = Signal(str)
    canceled = Signal()
    deleted = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the form, ready to make a new theme.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns it.

        Examples
        --------
        >>> sorted(ThemeEditor().colors)
        ['dark', 'light']
        """
        super().__init__(parent)
        self._family = ""  # the key of the theme being changed; empty for a new one
        self.colors: dict[str, dict[str, str]] = {"light": {}, "dark": {}}
        self.buttons: dict[str, dict[str, QPushButton]] = {"light": {}, "dark": {}}
        self.pictures: dict[str, ThemeThumb] = {}
        self._values: dict[str, dict[str, QLabel]] = {"light": {}, "dark": {}}
        self._beside: dict[QObject, QLabel] = {}  # the code written beside each color button
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        # The heading and the buttons stay at the top, where they are always in view, and only the form below them scrolls.
        self.heading = QLabel()
        self.heading.setStyleSheet(css("font-weight: bold; font-size: 12pt;"))
        self.save_button = QPushButton("Save")
        self.save_button.setProperty("primary", True)  # filled with the accent color, in style.py
        self.save_button.setDefault(True)
        self.save_button.setToolTip("Keep this theme and use it")
        self.save_button.clicked.connect(lambda: self.saved.emit(self._family))
        cancel = QPushButton("Cancel")
        cancel.setToolTip("Give up the changes")
        cancel.clicked.connect(self.canceled)
        self.delete_button = QPushButton("Delete theme")
        self.delete_button.clicked.connect(lambda: self.deleted.emit(self._family))
        header = QHBoxLayout()
        header.addWidget(self.heading, 1)
        header.addWidget(self.delete_button)
        header.addWidget(cancel)
        header.addWidget(self.save_button)
        lay.addLayout(header)
        form = QWidget()
        body = QVBoxLayout(form)
        body.setContentsMargins(
            0,
            0,
            8,
            0,
        )
        top = QGridLayout()  # the labels are in a column of their own, so that the two fields start at the same place
        top.setHorizontalSpacing(10)
        top.addWidget(QLabel("Name"), 0, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setProperty("field", True)  # rounded, as the rest of the app is, in style.py
        self.name_edit.setMaxLength(40)
        self.name_edit.setAccessibleName("Theme name")
        self.name_edit.textChanged.connect(self._name_changed)
        top.addWidget(self.name_edit, 0, 1)
        top.addWidget(QLabel("Start from"), 1, 0)
        self.start_from = FieldComboBox()
        self.start_from.setProperty("field", True)
        self.start_from.setAccessibleName("Theme to take the colors of")
        self.start_from.activated.connect(lambda _index: self._copy_start())  # choosing one takes its colors at once
        top.addWidget(self.start_from, 1, 1)
        top.setColumnStretch(1, 1)
        body.addLayout(top)
        columns = QHBoxLayout()
        columns.setSpacing(24)
        for version, title in (("light", "Light version"), ("dark", "Dark version")):
            column = QVBoxLayout()
            column.addWidget(QLabel(f"<b>{title}</b>"))
            picture = ThemeThumb(version, colors={}, scale=1.0)
            picture.setEnabled(False)  # a picture of the colors as they are made, nothing to click
            self.pictures[version] = picture
            column.addWidget(picture)
            grid = QGridLayout()
            grid.setHorizontalSpacing(8)
            grid.setVerticalSpacing(3)
            for row, part in enumerate(PARTS):
                button = QPushButton()
                button.setFixedSize(px(56), px(26))
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                button.setToolTip(f"Click to change the color of the {PART_NAMES[part].lower()}")
                button.setAccessibleName(f"{title}, {PART_NAMES[part]}")
                button.clicked.connect(lambda _=False, v=version, p=part: self._choose(v, part=p))
                value = QLabel()
                value.setStyleSheet(QUIET)
                button.installEventFilter(self)  # the code beside a color lights up with it
                self._beside[button] = value
                grid.addWidget(QLabel(PART_NAMES[part]), row, 0)
                grid.addWidget(button, row, 1)
                grid.addWidget(value, row, 2)
                self.buttons[version][part] = button
                self._values[version][part] = value
            column.addLayout(grid)
            column.addStretch(1)
            columns.addLayout(column)
        columns.addStretch(1)
        body.addLayout(columns)
        body.addStretch(1)
        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(form)
        lay.addWidget(scroll, 1)
        self.load(None)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802, PLR0917 (a Qt override, with Qt's own name and arguments)
        """
        Light up the code written beside a color while the pointer is over the color.

        Parameters
        ----------
        watched : QObject
            The object the event is for.
        event : QEvent
            The event.

        Returns
        -------
        bool
            Always False: the color button still gets the event.

        Examples
        --------
        >>> editor = ThemeEditor()
        >>> button = editor.buttons["light"]["accent"]
        >>> _ = editor.eventFilter(button, QEvent(QEvent.Type.Enter))
        >>> "bold" in editor._values["light"]["accent"].styleSheet()
        True
        >>> _ = editor.eventFilter(button, QEvent(QEvent.Type.Leave))
        >>> "bold" in editor._values["light"]["accent"].styleSheet()
        False
        """
        label = self._beside.get(watched)
        if label is not None and event.type() in {QEvent.Type.Enter, QEvent.Type.Leave}:
            label.setStyleSheet(LIT if event.type() == QEvent.Type.Enter else QUIET)
        return False

    def load(self, record: ThemeRecord | None) -> None:
        """
        Fill the form from a theme that was saved, or for a new one that starts as Studio.

        Parameters
        ----------
        record : ThemeRecord or None
            The theme to change; None for a new theme.

        Examples
        --------
        >>> editor = ThemeEditor()
        >>> editor.load(None)
        >>> editor.delete_button.isHidden(), editor.name_edit.text()
        (True, 'My theme')
        """
        self.start_from.clear()
        self.start_from.addItem("Choose a theme to take its colors…", None)
        own = record["id"] if record is not None else ""
        for family, label, _note in families():
            if family != own and custom_theme(family) is not None and custom_theme(f"{family}_dark") is not None:
                self.start_from.addItem(label, family)
        if record is None:
            self.start_from.setCurrentIndex(max(self.start_from.findData(START_FROM), 0))
            self._family = new_family_id()
            self.heading.setText("New theme")
            self.name_edit.setText(DEFAULT_NAME)
            self._copy_start()
        else:
            self._family = record["id"]
            self.heading.setText("Change theme")
            self.name_edit.setText(record["name"])
            self.colors = {"light": dict(record["light"]), "dark": dict(record["dark"])}
            self._show_colors()
        self.delete_button.setVisible(record is not None)

    def record(self) -> ThemeRecord:
        """
        Give the theme as it is now in the form.

        Returns
        -------
        ThemeRecord
            The key, the name and the colors of both versions.

        Examples
        --------
        >>> editor = ThemeEditor()
        >>> editor.record()["light"]["window"] == editor.colors["light"]["window"]
        True
        """
        return ThemeRecord(
            id=self._family,
            name=self.name_edit.text().strip() or DEFAULT_NAME,
            light=dict(self.colors["light"]),
            dark=dict(self.colors["dark"]),
        )

    def _copy_start(self) -> None:
        """
        Take the colors of the theme chosen in "Start from", for both versions.

        The line that asks for a choice takes nothing.

        Examples
        --------
        >>> from alto.ui.theme import CUSTOM_THEMES
        >>> editor = ThemeEditor()
        >>> editor._copy_start()
        >>> editor.colors["light"]["window"] == CUSTOM_THEMES[0].window
        True
        """
        family = self.start_from.currentData()
        if family is None:  # the line that asks for a choice
            return
        for version, key in (("light", family), ("dark", f"{family}_dark")):
            theme = custom_theme(key)
            if theme is not None:
                self.colors[version] = {part: str(getattr(theme, part)) for part in PARTS}
        self._show_colors()

    def _choose(
        self,
        version: str,
        *,
        part: str,
    ) -> None:
        """
        Open the color picker for one color, and take what is chosen.

        Parameters
        ----------
        version : str
            "light" or "dark".
        part : str
            The part of the theme. Keyword-only.

        Examples
        --------
        >>> ThemeEditor()._choose  # doctest: +SKIP
        """
        chosen = QColorDialog.getColor(QColor(self.colors[version][part]), self, f"{PART_NAMES[part]}, {version} version")
        if chosen.isValid():
            self.colors[version][part] = chosen.name()
            self._show_colors()

    def _name_changed(self, text: str) -> None:
        """
        Allow saving only while the theme has a name.

        Parameters
        ----------
        text : str
            What the name now says.

        Examples
        --------
        >>> editor = ThemeEditor()
        >>> editor.name_edit.setText("  ")
        >>> editor.save_button.isEnabled()
        False
        """
        self.save_button.setEnabled(bool(text.strip()))

    def _show_colors(self) -> None:
        """
        Show the colors on their buttons, in words, and in the two pictures.

        Examples
        --------
        >>> editor = ThemeEditor()
        >>> editor._show_colors()
        >>> editor.pictures["light"].colors["window"] == editor.colors["light"]["window"]
        True
        """
        for version in ("light", "dark"):
            for part in PARTS:
                color = self.colors[version][part]
                ring = (
                    "#ffffff" if QColor(color).lightness() < 140 else "#1a1a1a"
                )  # a ring that shows on this color, whatever it is
                self.buttons[version][part].setStyleSheet(
                    css(
                        f"QPushButton {{ background: {color}; border: 1px solid gray; border-radius: 5px; }}"
                        f"QPushButton:hover {{ border: 3px solid {ring}; }}"  # shows that the color can be changed
                        f"QPushButton:pressed {{ border: 3px solid {ring}; padding-top: 1px; }}",
                    ),
                )
                self._values[version][part].setText(color)
            picture = self.pictures[version]
            picture.colors = preview_colors(theme_of(self.colors[version], dark=version == "dark"))
            picture.update()
