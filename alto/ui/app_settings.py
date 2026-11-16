"""
The application-wide settings dialog.

It holds the colour theme, the notation font, the keyboard style, the transitions, the instrument and what updates follow.

Changes apply as soon as they are made. Each style is a card that previews it.

Examples
--------
>>> dialog = AppSettingsDialog()
>>> dialog.windowTitle()
'Settings'
>>> dialog.pages.count()  # Appearance, Sound and Updates
3
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import (
    QEvent,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QPalette,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from alto import updates
from alto.theory.pitch import Note
from alto.ui import (
    keyboard_styles,
    notation,
)
from alto.ui.colors import blend
from alto.ui.instrument_picker import InstrumentPicker
from alto.ui.keyboard import KeyboardWidget
from alto.ui.lesson_nav import section_item
from alto.ui.pictures import ClefPictures
from alto.ui.staff import StaffWidget
from alto.ui.theme import (
    FAMILIES,
    USER_PREFIX,
    apply_theme,
    delete_user_theme,
    families,
    family_of,
    save_theme,
    saved_theme,
    upsert_user_theme,
    user_records,
    variant_key,
)
from alto.ui.theme_cards import (
    ThemeCard,
    ThemeThumb,
)
from alto.ui.theme_editor import ThemeEditor
from alto.ui.transition_preview import TransitionPreview
from alto.ui.transitions import (
    TRANSITIONS,
    save_transition,
    saved_transition,
    transition_named,
)
from alto.ui.update_flow import (
    save_channel,
    saved_channel,
)

NEW_THEME = "__new__"  # what the row that makes a new theme holds in place of a theme's key


class _LazyPages(QStackedWidget):
    """
    A settings stack that builds each page once, when it is first selected.

    Examples
    --------
    >>> pages = _LazyPages()
    >>> pages.add_page(lambda: QLabel("First"))
    0
    >>> pages.add_page(lambda: QLabel("Second"))
    1
    >>> pages.setCurrentIndex(1)
    >>> isinstance(pages.currentWidget(), QLabel)
    True
    """

    def __init__(self) -> None:
        """
        Create an empty stack.

        Examples
        --------
        >>> _LazyPages().count()
        0
        """
        super().__init__()
        self._factories: dict[int, Callable[[], QWidget]] = {}
        self.currentChanged.connect(self._ensure_page)

    def add_page(self, factory: Callable[[], QWidget]) -> int:
        """
        Reserve a page, building it immediately only if it becomes the selected page.

        Parameters
        ----------
        factory : callable
            Builds the page when it is first selected.

        Returns
        -------
        int
            The page's index.

        Examples
        --------
        >>> _LazyPages().add_page(QWidget)
        0
        """
        index = self.count()
        self._factories[index] = factory
        return self.addWidget(QWidget())

    def _ensure_page(self, index: int) -> None:
        """
        Replace a selected placeholder with its page, keeping every page index unchanged.

        Parameters
        ----------
        index : int
            The page that was selected.

        Examples
        --------
        >>> pages = _LazyPages()
        >>> pages.add_page(QWidget)
        0
        >>> pages._ensure_page(0)
        >>> pages.count()
        1
        """
        factory = self._factories.pop(index, None)
        if factory is None:
            return
        page = factory()
        placeholder = self.widget(index)
        assert placeholder is not None
        selected = self.currentIndex()
        blocked = self.blockSignals(True)
        try:
            self.removeWidget(placeholder)
            self.insertWidget(index, page)
            self.setCurrentIndex(selected)
        finally:
            self.blockSignals(blocked)
        placeholder.deleteLater()


class StyleCard(QPushButton):
    """
    A selectable tile that previews a notation style: a short phrase on a staff, drawn in that style.

    Attributes
    ----------
    style_key : str
        The key of the style the card stands for.
    staff : StaffWidget
        The preview.

    Examples
    --------
    >>> card = StyleCard(notation.BY_KEY["leland"])
    >>> card.style_key, card.isCheckable()
    ('leland', True)
    """

    def __init__(
        self,
        style: notation.NotationStyle,
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the card for a notation style.

        Parameters
        ----------
        style : NotationStyle
            The style to preview; its label and a few words about it are shown under the staff.
        parent : QWidget or None, default None
            The widget that owns the card. Keyword-only.

        Examples
        --------
        >>> StyleCard(notation.BY_KEY["bravura"]).width()
        232
        """
        super().__init__(parent)
        self.style_key = style.key
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(232, 150)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            8,
            8,
            8,
            6,
        )
        lay.setSpacing(4)
        self.staff = StaffWidget(
            gap=6.5,
            side=8.0,
            note_offset=44.0,
            margin=3.2,
            compact=True,
        )
        self.staff.notation_style = style
        self.staff.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.staff.setFixedWidth(214)
        self.staff.show_notes(
            [
                [Note(5, letter=1)],
                [Note(5, letter=2, accidental=-1)],
                [Note(5, letter=0)],
                [Note(4, letter=6)],
            ],
            clef="treble",
            key=0,
            value="quarter",
        )
        name = QLabel(f"<b>{style.label}</b>")
        name.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        blurb = QLabel(style.note)
        blurb.setStyleSheet("color: gray; font-size: 9pt;")
        blurb.setWordWrap(True)
        blurb.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lay.addWidget(self.staff)
        lay.addWidget(name)
        lay.addWidget(blurb)


RIM = "rgba(136, 136, 136, 0.5)"  # the faint outline of the builder's swatches and chips


class KeyboardCard(QPushButton):
    """
    A selectable tile that previews a keyboard style: a short stretch of keys drawn in that style.

    Attributes
    ----------
    style_key : str
        The key of the style the card stands for.
    keys : KeyboardWidget
        The preview.

    Examples
    --------
    >>> card = KeyboardCard(keyboard_styles.BY_KEY["modern"])
    >>> card.style_key
    'modern'
    """

    def __init__(
        self,
        style: keyboard_styles.KeyboardStyle,
        *,
        parent: QWidget | None = None,
    ) -> None:
        """
        Build the card for a keyboard style.

        Parameters
        ----------
        style : KeyboardStyle
            The style to preview; its label and a few words about it are shown under the keys.
        parent : QWidget or None, default None
            The widget that owns the card. Keyword-only.

        Examples
        --------
        >>> # noinspection PyUnresolvedReferences
        >>> KeyboardCard(keyboard_styles.BY_KEY["classic"]).keys.style_override.key
        'classic'
        """
        super().__init__(parent)
        self.style_key = style.key
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(232, 222)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            8,
            8,
            8,
            6,
        )
        lay.setSpacing(4)
        self.keys = KeyboardWidget()
        self.keys.style_override = style
        self.keys.pad = 6.0
        self.keys.max_key_width = 16.0
        self.keys.setFixedWidth(2 * 6 + 10 * 16)  # ten white keys, C4 to E5
        self.keys.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.keys.show_key(None, span=(60, 76))
        holder = QWidget()
        holder.setFixedHeight(int(2 * 6 + 30 + 16 * 6.2))  # room for the tallest strip above the keys
        holder.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        holder_lay = QVBoxLayout(holder)
        holder_lay.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        holder_lay.addWidget(self.keys, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        name = QLabel(f"<b>{style.label}</b>")
        name.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        blurb = QLabel(style.note)
        blurb.setStyleSheet("color: gray; font-size: 9pt;")
        blurb.setWordWrap(True)
        blurb.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lay.addWidget(holder)
        lay.addWidget(name)
        lay.addWidget(blurb)
        lay.addStretch(1)

    def show_style(self, style: keyboard_styles.KeyboardStyle) -> None:
        """
        Redraw the preview in a style.

        The custom card follows the colours being edited.

        Parameters
        ----------
        style : KeyboardStyle
            The style to preview.

        Examples
        --------
        >>> card = KeyboardCard(keyboard_styles.BY_KEY["classic"])
        >>> card.show_style(keyboard_styles.BY_KEY["modern"])
        >>> # noinspection PyUnresolvedReferences
        >>> card.keys.style_override.key
        'modern'
        """
        self.keys.style_override = style
        self.keys.refit()


class KeyboardBuilder(QFrame):
    """
    Rows for colouring each part of a keyboard.

    Each has a swatch that opens the colour picker, and chips for colours named after materials. Changing anything selects
    the Custom style.

    Attributes
    ----------
    changed : Signal
        Emitted after a part is recoloured.
    swatches : dict of str to QPushButton
        The swatch of each part ("naturals", "sharps", "case", "felt" and "caps").

    Examples
    --------
    >>> builder = KeyboardBuilder()
    >>> sorted(builder.swatches)
    ['caps', 'case', 'felt', 'naturals', 'sharps']
    """

    changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the rows and show each part's current colour.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns the builder.

        Examples
        --------
        >>> KeyboardBuilder().swatches["naturals"].width()
        46
        """
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(
            0,
            8,
            0,
            0,
        )
        lay.setSpacing(6)
        lay.addWidget(QLabel("<b>Build your own</b>"))
        about = QLabel(
            "Choose a colour for each part, from a material or with the colour picker. "
            "Changing any part switches to the Custom style.",
        )
        about.setWordWrap(True)
        about.setStyleSheet("color: gray;")
        lay.addWidget(about)
        self.swatches: dict[str, QPushButton] = {}
        for part, label, optional in keyboard_styles.COMPONENTS:
            row = QHBoxLayout()
            row.setSpacing(4)
            name = QLabel(label)
            name.setFixedWidth(84)
            row.addWidget(name)
            swatch = QPushButton()
            swatch.setFixedSize(46, 24)
            swatch.setCursor(Qt.CursorShape.PointingHandCursor)
            swatch.setToolTip(f"Pick a colour for the {label.lower()}")
            swatch.clicked.connect(lambda _=False, p=part, t=label: self._pick(p, title=t))
            row.addWidget(swatch)
            row.addSpacing(6)
            self.swatches[part] = swatch
            if optional:
                none = self._chip("None", colour=None)
                none.setText("✕")
                none.clicked.connect(lambda _=False, p=part: self._set(p, colour=None))
                row.addWidget(none)
            else:
                row.addSpacing(24)  # line the chips up with the rows that have a None chip
            for material, colour in keyboard_styles.MATERIALS:
                chip = self._chip(f"{material}  {colour}", colour=colour)
                chip.clicked.connect(lambda _=False, p=part, c=colour: self._set(p, colour=c))
                row.addWidget(chip)
            row.addStretch(1)
            lay.addLayout(row)
        self.refresh()

    @staticmethod
    def _chip(
        tip: str,
        *,
        colour: str | None,
    ) -> QToolButton:
        """
        Make a small round colour chip.

        Parameters
        ----------
        tip : str
            The tooltip, such as the material's name and colour.
        colour : str or None
            The chip's colour, or None for the "leave this part out" chip.

        Returns
        -------
        QToolButton
            The chip.

        Examples
        --------
        >>> chip_ = KeyboardBuilder._chip("Ivory  #f1e5c6", colour="#f1e5c6")
        >>> chip_.toolTip()
        'Ivory  #f1e5c6'
        """
        chip = QToolButton()
        chip.setFixedSize(20, 20)
        chip.setToolTip(tip)
        chip.setCursor(Qt.CursorShape.PointingHandCursor)
        if colour:
            chip.setStyleSheet(f"QToolButton {{ background: {colour}; border: 1px solid {RIM}; border-radius: 10px; }}")
        else:
            chip.setStyleSheet(f"QToolButton {{ border: 1px solid {RIM}; border-radius: 10px; color: gray; }}")
        return chip

    def refresh(self) -> None:
        """
        Show each part's current colour on its swatch.

        Examples
        --------
        >>> builder = KeyboardBuilder()
        >>> builder.refresh()
        >>> builder.swatches["naturals"].text()  # a colour is set, so the swatch shows it, not "none"
        ''
        """
        for part, colour in keyboard_styles.custom_colours().items():
            swatch = self.swatches[part]
            swatch.setText("" if colour else "none")
            swatch.setStyleSheet(
                f"QPushButton {{ background: {colour}; border: 1px solid {RIM}; border-radius: 6px; }}"
                if colour
                else f"QPushButton {{ border: 1px dashed {RIM}; border-radius: 6px; color: gray; }}",
            )

    def _set(
        self,
        part: str,
        *,
        colour: str | None,
    ) -> None:
        """
        Recolour a part (or leave it out) and switch to the custom style.

        Parameters
        ----------
        part : str
            "naturals", "sharps", "case", "felt" or "caps".
        colour : str or None
            The new colour, or None to leave an optional part out. Keyword-only.

        Examples
        --------
        >>> builder = KeyboardBuilder()
        >>> changes = []
        >>> _ = builder.changed.connect(lambda: changes.append(1))
        >>> builder._set("naturals", colour="#ffffff")
        >>> keyboard_styles.custom_colours()["naturals"], changes
        ('#ffffff', [1])
        >>> builder._set("naturals", colour=keyboard_styles.DEFAULT_CUSTOM["naturals"])
        >>> keyboard_styles.set_style(keyboard_styles.DEFAULT)
        """
        keyboard_styles.set_custom_colour(part, colour=colour)
        self.refresh()
        self.changed.emit()

    def _pick(
        self,
        part: str,
        *,
        title: str,
    ) -> None:
        """
        Open the colour picker for a part and apply the colour chosen.

        Parameters
        ----------
        part : str
            "naturals", "sharps", "case", "felt" or "caps".
        title : str
            The part's label, used in the picker's title. Keyword-only.

        Examples
        --------
        >>> KeyboardBuilder()._pick("case", title="Case")  # doctest: +SKIP
        """
        current = keyboard_styles.custom_colours()[part] or "#ffffff"
        colour = QColorDialog.getColor(QColor(current), self, f"Colour for the {title.lower()}")
        if colour.isValid():
            self._set(part, colour=colour.name())


class AppSettingsDialog(QDialog):
    """
    Application-wide settings. Changes apply immediately, and the main window can be used while the dialog is open.

    Pages are built when first selected, so hidden previews do not slow down opening Settings or changing themes.

    Attributes
    ----------
    theme_changed : bool
        True once the theme has been changed, so the window can be rebuilt in it.
    categories : QListWidget
        The list of pages on the left: Appearance, Sound and Updates.
    pages : QStackedWidget
        The page for the chosen category.
    instruments : InstrumentPicker
        The instrument chooser, available after the Sound page is first selected.
    theme_list : QListWidget
        The themes, on the Theme section, with the one in use in bold.
    theme_items : dict of str to QListWidgetItem
        The rows of that list, by the key of the theme's family.
    theme_pages : QStackedWidget
        The card of the theme chosen in the list, or the editor.
    theme_editor : ThemeEditor
        The form that makes a theme of the user's own, or changes one.
    new_theme_item : QListWidgetItem
        The row of the list that makes a new theme.
    theme_cards : dict of str to ThemeCard
        The cards built so far, by the key of the theme's family. A card is built when its row is first chosen, because every
        widget makes a change of theme slower; use `card` to get one.
    theme_scrolls : dict of str to QScrollArea
        The scroll area each built card is in, which is what the stack shows; use `scroll` to get one.
    theme_thumbs : dict of str to ThemeThumb
        The clickable pictures of every built card, by the key of the theme each chooses; use `thumb` to get one.
    transition_list : QListWidget
        The choice of transition, available after the Transitions section is first selected.
    transition_items : dict of str to QListWidgetItem
        The rows of that list, by the transition's key.
    transition_preview : TransitionPreview
        Plays the transition that is chosen, beside the choices.

    Examples
    --------
    >>> dialog = AppSettingsDialog()
    >>> dialog.theme_changed
    False
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the dialog with the Appearance page showing.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns the dialog.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.categories.currentRow()
        0
        """
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(False)  # the window stays usable while the settings are open
        self.resize(1000, 640)
        self.theme_changed = False
        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        # The categories sit in a list on the left; choosing one shows its settings on the right.
        self.categories = QListWidget()
        self.categories.setObjectName("categories")  # styled in style.py
        self.categories.setFixedWidth(170)
        self.pages = _LazyPages()
        for name, factory in (
            ("Appearance", self._appearance_page),
            ("Sound", self._sound_page),
            ("Updates", self._updates_page),
        ):
            item = QListWidgetItem(name)
            item.setSizeHint(QSize(0, 36))
            self.categories.addItem(item)
            self.pages.add_page(factory)
        self.categories.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.categories.setCurrentRow(0)
        body = QHBoxLayout()
        body.setSpacing(14)
        body.addWidget(self.categories)
        body.addWidget(self.pages, 1)
        lay.addLayout(body, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        lay.addWidget(buttons)

    @staticmethod
    def _page() -> tuple[QWidget, QVBoxLayout]:
        """
        Make an empty page with a vertical layout.

        Returns
        -------
        tuple of (QWidget, QVBoxLayout)
            The page and its layout.

        Examples
        --------
        >>> page_, layout = AppSettingsDialog._page()
        >>> layout.count()
        0
        """
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(
            4,
            4,
            4,
            4,
        )
        lay.setSpacing(10)
        return page, lay

    @staticmethod
    def _heading(
        lay: QVBoxLayout,
        *,
        title: str,
        about: str,
    ) -> None:
        """
        Add a heading and a line of grey explanation to a layout.

        Parameters
        ----------
        lay : QVBoxLayout
            The layout to add to.
        title : str
            The heading. Keyword-only.
        about : str
            The explanation under it. Keyword-only.

        Examples
        --------
        >>> layout = QVBoxLayout()
        >>> AppSettingsDialog._heading(layout, title="Instrument", about="The sound used for notes.")
        >>> layout.count()
        2
        """
        lay.addWidget(QLabel(f"<h3>{title}</h3>"))
        text = QLabel(about)
        text.setStyleSheet("color: gray;")
        text.setWordWrap(True)
        lay.addWidget(text)

    @staticmethod
    def _about(text: str) -> QLabel:
        """
        Make a line of grey explanatory text.

        Parameters
        ----------
        text : str
            What to say.

        Returns
        -------
        QLabel
            The label, which wraps to fit.

        Examples
        --------
        >>> AppSettingsDialog._about("The music font.").text()
        'The music font.'
        """
        label = QLabel(text)
        label.setStyleSheet("color: gray;")
        label.setWordWrap(True)
        return label

    @staticmethod
    def _scrolling(page: QWidget) -> QScrollArea:
        """
        Wrap a page so that it scrolls when it is taller than the dialog.

        Parameters
        ----------
        page : QWidget
            The page.

        Returns
        -------
        QScrollArea
            A scroll area holding the page, with no horizontal scroll bar.

        Examples
        --------
        >>> page_ = QWidget()
        >>> AppSettingsDialog._scrolling(page_).widget() is page_
        True
        """
        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setFrameShape(QScrollArea.Shape.NoFrame)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        area.setWidget(page)
        return area

    def _appearance_page(self) -> QWidget:
        """
        Build the Appearance page.

        It has four sections, switched with a segmented control: the colour theme, the notation style, the keyboard style and the
        transitions.

        Returns
        -------
        QWidget
            The page.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.appearance_pages.count()
        4
        """
        page, lay = self._page()
        self.appearance_pages = _LazyPages()
        self.appearance_pages.add_page(self._theme_tab)  # its cards and its editor scroll by themselves, not the page
        self.appearance_pages.add_page(lambda: self._scrolling(self._notation_tab()))
        self.appearance_pages.add_page(lambda: self._scrolling(self._keyboard_tab()))
        self.appearance_pages.add_page(lambda: self._scrolling(self._transitions_tab()))
        self.segments = QFrame()
        self.segments.setObjectName("segments")
        row = QHBoxLayout(self.segments)
        row.setContentsMargins(
            3,
            3,
            3,
            3,
        )
        row.setSpacing(2)
        group = QButtonGroup(self)
        group.setExclusive(True)
        self.segment_buttons = []
        for i, label in enumerate(("Theme", "Notation style", "Keyboard style", "Transitions")):
            b = QPushButton(label)
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setChecked(i == 0)
            group.addButton(b, i)
            b.clicked.connect(lambda _=False, k=i: self.appearance_pages.setCurrentIndex(k))
            row.addWidget(b)
            self.segment_buttons.append(b)
        self._style_segments()
        top = QHBoxLayout()
        top.addWidget(self.segments)
        top.addStretch(1)
        lay.addLayout(top)
        lay.addWidget(self.appearance_pages, 1)
        return page

    def _style_segments(self) -> None:
        """
        Style the segmented control: a rounded track with the chosen segment raised and tinted, from the current palette.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog._style_segments()
        >>> "segments" in dialog.segments.styleSheet()
        True
        """
        pal = self.palette()
        roles = (
            QPalette.ColorRole.Window,
            QPalette.ColorRole.Text,
            QPalette.ColorRole.Base,
            QPalette.ColorRole.Highlight,
        )
        window, text, base, accent = (pal.color(r) for r in roles)
        track = blend(window, b=text, t=0.07)
        self.segments.setStyleSheet(
            f"QFrame#segments {{ background: {track.name()}; border-radius: 12px; }}"
            "QFrame#segments QPushButton { border: 0; border-radius: 9px; padding: 6px 18px; background: transparent; }"
            f"QFrame#segments QPushButton:checked {{ background: {base.name()}; color: {accent.name()}; "
            f"border: 1px solid {pal.color(QPalette.ColorRole.Mid).name()}; }}",
        )

    def changeEvent(self, event: QEvent) -> None:
        """
        Restyle the segmented control when the palette changes, so it follows the theme.

        Parameters
        ----------
        event : QEvent
            The change.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.changeEvent(QEvent(QEvent.Type.PaletteChange))
        """
        if event.type() == QEvent.Type.PaletteChange and hasattr(self, "segments"):
            self._style_segments()
        super().changeEvent(event)

    def _theme_tab(self) -> QWidget:
        """
        Build the theme section: the themes in a list on the left, and the one chosen in the list on the right.

        The right side is the theme's card, with three pictures one above another to click: the theme light, dark, and System,
        which is light or dark as the desktop is and is cut through on a slant to show it. Choosing a row uses that theme, in
        whichever of light, dark and System was chosen last. The themes the user made are at the top of the list, with a row that
        makes a new one; the editor for them is on the right.

        Returns
        -------
        QWidget
            The page.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> len(dialog.theme_items) == len(families()), len(dialog.theme_cards)  # only the card in view is built
        (True, 1)
        """
        page, lay = self._page()
        body = QHBoxLayout()
        body.setSpacing(18)
        self.theme_list = QListWidget()
        self.theme_list.setObjectName("categories")  # styled as the list of settings pages is
        self.theme_list.setFixedWidth(220)
        self.theme_list.setAccessibleName("Themes")
        self.theme_pages = QStackedWidget()
        self.theme_editor = ThemeEditor()
        self.theme_editor.saved.connect(self._save_theme)
        self.theme_editor.cancelled.connect(self._fill_themes)
        self.theme_editor.deleted.connect(self._delete_theme)
        self.theme_pages.addWidget(self.theme_editor)
        self.theme_cards = {}
        self.theme_thumbs = {}
        self.theme_items = {}
        self.theme_scrolls = {}
        self._version = family_of(saved_theme())[1]  # the version last chosen, which stays as the list is moved
        self.theme_list.currentItemChanged.connect(lambda now, _before: self._choose_family(now))
        self._fill_themes()
        body.addWidget(self.theme_list)
        side = QVBoxLayout()
        side.addWidget(self.theme_pages)
        side.addStretch(1)
        body.addLayout(side, 1)
        lay.addLayout(body, 1)
        return page

    def _fill_themes(self, select: str | None = None) -> None:
        """
        Fill the list and the cards: the themes the user made and a row to make one, then the built-in themes.

        Parameters
        ----------
        select : str or None, default None
            The key of the theme whose row to choose; None for the theme in use.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog._fill_themes()
        >>> dialog.theme_list.item(0).text()
        'MY THEMES'
        """
        self.theme_list.blockSignals(True)
        self.theme_list.clear()
        for scroll in self.theme_scrolls.values():
            self.theme_pages.removeWidget(scroll)
            scroll.deleteLater()
        self.theme_cards, self.theme_thumbs, self.theme_items, self.theme_scrolls = {}, {}, {}, {}
        own = [(key, label) for key, label, _note in families() if key.startswith(USER_PREFIX)]
        sections = (("My themes", own, True), ("Themes", [(key, label) for key, label, _note in FAMILIES], False))
        for title, rows, mine in sections:
            self.theme_list.addItem(section_item(title, palette=self.palette()))
            for family, label in rows:
                row = QListWidgetItem(label)
                row.setData(Qt.ItemDataRole.UserRole, family)
                row.setSizeHint(QSize(0, 34))
                self.theme_list.addItem(row)
                self.theme_items[family] = row
            if mine:
                self.new_theme_item = QListWidgetItem("＋  New theme…")
                self.new_theme_item.setData(Qt.ItemDataRole.UserRole, NEW_THEME)
                self.new_theme_item.setSizeHint(QSize(0, 34))
                self.theme_list.addItem(self.new_theme_item)
        self.theme_list.blockSignals(False)
        in_use = saved_theme()
        self._show_theme(in_use)
        family = select if select is not None and select in self.theme_items else family_of(in_use)[0]
        self.theme_list.setCurrentItem(self.theme_items[family])
        self.theme_pages.setCurrentWidget(self.card_page(family))

    def card(self, family: str) -> ThemeCard:
        """
        Give the card of a theme, building it the first time it is asked for.

        Every card is a few dozen widgets, and Qt styles every widget again when the theme changes, so only the cards that have
        been looked at exist.

        Parameters
        ----------
        family : str
            The key of the theme's family.

        Returns
        -------
        ThemeCard
            Its card.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> "sage" in dialog.theme_cards
        False
        >>> dialog.card("sage") is dialog.card("sage"), "sage" in dialog.theme_cards
        (True, True)
        """
        card = self.theme_cards.get(family)
        if card is None:
            card = ThemeCard(family, scale=1.45)
            card.chosen.connect(self._pick_theme)
            card.edit_requested.connect(self._edit_theme)
            scroll = self._scrolling(card)  # a card that does not fit the dialog scrolls, and the list does not
            self.theme_pages.addWidget(scroll)
            self.theme_scrolls[family] = scroll
            self.theme_cards[family] = card
            self.theme_thumbs.update(card.thumbs)
            card.show_current(saved_theme())
        return card

    def card_page(self, family: str) -> QScrollArea:
        """
        Give the scroll area that holds a theme's card, which is the page the stack shows for it.

        Parameters
        ----------
        family : str
            The key of the theme's family.

        Returns
        -------
        QScrollArea
            The area, with the card built if it was not yet.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.card_page("sage").widget() is dialog.card("sage")
        True
        """
        self.card(family)
        return self.theme_scrolls[family]

    def thumb(self, key: str) -> ThemeThumb:
        """
        Give the clickable picture that chooses a theme, with the card it is on built if it was not yet.

        Parameters
        ----------
        key : str
            The key of the theme, such as "light" or "sage_dark".

        Returns
        -------
        ThemeThumb
            Its picture.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.thumb("sage_dark").isChecked()
        False
        """
        return self.card(family_of(key)[0]).thumbs[key]

    def _choose_family(self, row: QListWidgetItem | None) -> None:
        """
        Show the card of the theme whose row was chosen in the list, and use the theme, in the version that was last chosen.

        The row that makes a new theme opens the editor instead, and uses nothing.

        Parameters
        ----------
        row : QListWidgetItem or None
            The row that is now chosen.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.thumb("dark").click()
        >>> dialog.theme_list.setCurrentItem(dialog.theme_items["sage"])
        >>> dialog.theme_pages.currentWidget() is dialog.card_page("sage"), saved_theme()
        (True, 'sage_dark')
        >>> dialog._pick_theme("system")
        """
        if row is None:
            return
        family = str(row.data(Qt.ItemDataRole.UserRole))
        if family == NEW_THEME:
            self.theme_editor.load(None)
            self.theme_pages.setCurrentWidget(self.theme_editor)
            return
        self.theme_pages.setCurrentWidget(self.card_page(family))
        key = variant_key(family, version=self._version)
        if key != saved_theme():
            self.choose_theme(key)
        self._show_theme(key)

    def _edit_theme(self, family: str) -> None:
        """
        Open the editor on a theme the user made.

        Parameters
        ----------
        family : str
            The theme's key.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog._edit_theme("my_nothing")  # no such theme: nothing opens
        >>> dialog.theme_pages.currentWidget() is dialog.theme_editor
        False
        """
        record = next((made for made in user_records() if made["id"] == family), None)
        if record is not None:
            self.theme_editor.load(record)
            self.theme_pages.setCurrentWidget(self.theme_editor)

    def _save_theme(self, family: str) -> None:
        """
        Save the theme in the editor, and use it, in the version that was last chosen.

        Parameters
        ----------
        family : str
            The theme's key.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog._save_theme  # doctest: +SKIP
        """
        upsert_user_theme(self.theme_editor.record())
        key = variant_key(family, version=self._version)
        self.choose_theme(key)
        self._fill_themes(select=family)

    def _delete_theme(self, family: str) -> None:
        """
        Delete a theme the user made, after asking. If it was in use, the desktop's own colours are used instead.

        Parameters
        ----------
        family : str
            The theme's key.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog._delete_theme("my_nothing")  # no such theme: nothing to ask
        """
        record = next((made for made in user_records() if made["id"] == family), None)
        if record is None:
            return
        asked = QMessageBox.question(
            self,
            "Delete theme",
            f"Delete the theme \u201c{record['name']}\u201d? This cannot be undone.",
        )
        if asked != QMessageBox.StandardButton.Yes:
            return
        if (
            family_of(saved_theme())[0] == family
        ):  # in use: the desktop's own colours first, while the theme can still be let go of
            self._version = "system"
            self.choose_theme("system")
        delete_user_theme(family)
        self._fill_themes()

    def _show_theme(self, key: str) -> None:
        """
        Mark the theme that is in use in the gallery.

        Parameters
        ----------
        key : str
            The key of the theme in use.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> sage = dialog.card("sage")
        >>> dialog._show_theme("sage_auto")
        >>> dialog.thumb("sage_auto").isChecked(), dialog.thumb("sage").isChecked()
        (True, False)
        """
        for card in self.theme_cards.values():
            card.show_current(key)
        for family, row in self.theme_items.items():
            font = row.font()
            font.setBold(family == family_of(key)[0])  # the row of the theme in use is bold
            row.setFont(font)

    def _pick_theme(self, key: str) -> None:
        """
        Choose the theme whose picture was clicked, and mark it in the gallery.

        Parameters
        ----------
        key : str
            The key of the theme.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog._pick_theme("light")
        >>> saved_theme(), dialog.thumb("light").isChecked()
        ('light', True)
        >>> dialog._pick_theme("system")
        """
        self._version = family_of(key)[1]  # moving to another theme keeps to this version
        if key != saved_theme():
            self.choose_theme(key)
        self._show_theme(key)

    def _notation_tab(self) -> QWidget:
        """
        Build the notation section: a card for each music font, and the choice of how the baritone clef is written.

        Returns
        -------
        QWidget
            The page.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.segment_buttons[1].click()
        >>> sorted(dialog.baritone_buttons)
        ['c', 'f']
        """
        page, lay = self._page()
        lay.addWidget(self._about("The music font used to draw clefs, notes and accidentals."))
        grid = QGridLayout()
        grid.setSpacing(10)
        group = QButtonGroup(self)
        group.setExclusive(True)
        for i, st in enumerate(notation.STYLES):
            card = StyleCard(st)
            card.setChecked(st.key == notation.current().key)
            group.addButton(card)
            card.clicked.connect(lambda _=False, k=st.key: self._choose_notation(k))
            grid.addWidget(card, i // 3, i % 3)
        grid.setColumnStretch(3, 1)  # keep the cards at the left edge
        lay.addLayout(grid)

        lay.addSpacing(8)
        lay.addWidget(QLabel("<h3>Baritone clef</h3>"))
        lay.addWidget(self._about("The baritone clef can be written two ways. The staff and the notes on it are the same."))
        self.baritone_buttons = {}
        baritone_group = QButtonGroup(self)
        for kind, label in notation.BARITONE_CLEFS.items():
            radio = QRadioButton(label)
            radio.setChecked(kind == notation.baritone_clef())
            baritone_group.addButton(radio)
            radio.clicked.connect(lambda _=False, k=kind: notation.set_baritone_clef(k))
            self.baritone_buttons[kind] = radio
            lay.addWidget(radio)
        self._draw_baritone_icons()
        lay.addStretch(1)
        return page

    def _transitions_tab(self) -> QWidget:
        """
        Build the transitions section: the choices in a list on the left, and a preview of the one chosen on the right.

        The transitions are how the home page changes between the exercises and the lessons. The preview plays the one chosen
        once, and a Replay button plays it again.

        Returns
        -------
        QWidget
            The page.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.segment_buttons[3].click()
        >>> dialog.transition_list.count() == len(TRANSITIONS)
        True
        >>> dialog.transition_preview.transition.key == saved_transition()
        True
        """
        page, lay = self._page()
        lay.addWidget(self._about("How the cards change when you switch between the exercises and the lessons on the home page."))
        body = QHBoxLayout()
        body.setSpacing(18)
        self.transition_preview = TransitionPreview()
        name = QLabel()
        name.setStyleSheet("font-weight: bold; font-size: 12pt;")
        about = self._about("")
        self.transition_list = QListWidget()
        self.transition_list.setObjectName("categories")  # styled as the list of settings pages is
        self.transition_list.setFixedWidth(220)
        self.transition_list.setAccessibleName("Transitions")
        self.transition_items = {}
        for transition in TRANSITIONS:
            row = QListWidgetItem(transition.label)
            row.setData(Qt.ItemDataRole.UserRole, transition.key)
            row.setSizeHint(QSize(0, 34))
            self.transition_list.addItem(row)
            self.transition_items[transition.key] = row
        chosen = saved_transition()
        self.transition_list.setCurrentItem(self.transition_items[chosen])

        def choose(picked_row: QListWidgetItem | None) -> None:
            """
            Remember the transition whose row is chosen, play it in the preview and say what it does.

            Parameters
            ----------
            picked_row : QListWidgetItem or None
                The row that is now chosen.

            Examples
            --------
            >>> choose  # doctest: +SKIP
            """
            if picked_row is None:
                return
            picked = transition_named(str(picked_row.data(Qt.ItemDataRole.UserRole)))
            save_transition(picked.key)
            self.transition_preview.show_transition(picked.key)
            name.setText(picked.label)
            about.setText(picked.about)

        self.transition_list.currentItemChanged.connect(lambda now, _previous: choose(now))
        replay = QPushButton("Replay")
        replay.setToolTip("Play the transition again")
        replay.clicked.connect(self.transition_preview.replay)
        right = QVBoxLayout()
        right.addWidget(self.transition_preview, 1)
        row = QHBoxLayout()
        row.addWidget(name, 1)
        row.addWidget(replay)
        right.addLayout(row)
        right.addWidget(about)
        body.addWidget(self.transition_list)
        body.addLayout(right, 1)
        lay.addLayout(body, 1)
        current = transition_named(chosen)
        self.transition_preview.show_transition(current.key)
        name.setText(current.label)
        about.setText(current.about)
        return page

    def _choose_notation(self, key: str) -> None:
        """
        Choose a notation font and redraw the baritone pictures in it.

        Parameters
        ----------
        key : str
            A key of `notation.BY_KEY`.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.segment_buttons[1].click()
        >>> dialog._choose_notation("leland")
        >>> notation.current().key
        'leland'
        >>> dialog._choose_notation(notation.DEFAULT)
        """
        notation.set_style(key)
        self._draw_baritone_icons()  # the two baritone clefs are pictured in the font just chosen

    def _draw_baritone_icons(self) -> None:
        """
        Draw the two ways of writing the baritone clef on their buttons, in the notation font in use.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.segment_buttons[1].click()
        >>> dialog._draw_baritone_icons()
        >>> dialog.baritone_buttons["f"].icon().isNull()
        False
        """
        for kind, radio in self.baritone_buttons.items():
            picture = ClefPictures([f"baritone_{kind}"], scale=1.4)
            radio.setIcon(picture.to_icon())
            radio.setIconSize(picture.size())

    def _keyboard_tab(self) -> QWidget:
        """
        Build the keyboard section: a card for each style, and the builder for your own.

        Returns
        -------
        QWidget
            The page.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.segment_buttons[2].click()
        >>> keyboard_styles.CUSTOM in dialog.keyboard_cards
        True
        """
        page, lay = self._page()
        lay.addWidget(self._about("How the piano keyboard looks: the colours and materials of its keys."))
        grid = QGridLayout()
        grid.setSpacing(10)
        group = QButtonGroup(self)
        group.setExclusive(True)
        self.keyboard_cards = {}
        styles = (*keyboard_styles.STYLES, keyboard_styles.custom_style())
        for i, st in enumerate(styles):
            card = KeyboardCard(st)
            card.setChecked(st.key == keyboard_styles.current().key)
            group.addButton(card)
            card.clicked.connect(lambda _=False, k=st.key: keyboard_styles.set_style(k))
            grid.addWidget(card, i // 3, i % 3)
            self.keyboard_cards[st.key] = card
        grid.setColumnStretch(3, 1)  # keep the cards at the left edge
        lay.addLayout(grid)
        self.builder = KeyboardBuilder()
        self.builder.changed.connect(self._custom_edited)
        lay.addWidget(self.builder)
        lay.addStretch(1)
        return page

    def _custom_edited(self) -> None:
        """
        Show the result of recolouring a part on the Custom card and make it the chosen one.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.segment_buttons[2].click()
        >>> dialog._custom_edited()
        >>> dialog.keyboard_cards[keyboard_styles.CUSTOM].isChecked()
        True
        """
        card = self.keyboard_cards[keyboard_styles.CUSTOM]
        card.show_style(keyboard_styles.custom_style())
        card.setChecked(True)

    def _sound_page(self) -> QWidget:
        """
        Build the Sound page: the instrument chooser.

        Returns
        -------
        QWidget
            The page.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.categories.setCurrentRow(1)
        >>> dialog.instruments.list.count() > 0
        True
        """
        page, lay = self._page()
        self._heading(
            lay,
            title="Instrument",
            about="The sound used for notes and for the correct-answer chime. Choose an instrument to see what it is "
            "made from, and press Hear it to listen.",
        )
        self.instruments = InstrumentPicker()
        lay.addWidget(self.instruments, 1)
        return page

    def _updates_page(self) -> QWidget:
        """
        Build the Updates page: the version that is running, and whether updates follow the main branch.

        Returns
        -------
        QWidget
            The page.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.categories.setCurrentRow(2)
        >>> dialog.main_channel.isChecked()
        False
        """
        page, lay = self._page()
        self._heading(
            lay,
            title="Updates",
            about="Check for updates… in the menu looks for a newer Alto.",
        )
        lay.addWidget(QLabel(f"You have Alto {updates.installed_version()}."))
        self.main_channel = QCheckBox("Follow the main branch (the latest changes, which may be unstable)")
        self.main_channel.setChecked(saved_channel() == updates.MAIN)
        self.main_channel.toggled.connect(self._choose_channel)
        lay.addWidget(self.main_channel)
        lay.addWidget(
            self._about(
                "By default, updates follow releases: a version is offered once it has been published. With this on, updates "
                "follow the main branch instead, so you get each change as soon as it is merged, before it has been released. "
                "This works for a copy installed with the install script; a packaged copy always follows releases.",
            ),
        )
        lay.addStretch(1)
        return page

    @staticmethod
    def _choose_channel(on: bool) -> None:
        """
        Remember whether updates follow the main branch.

        Parameters
        ----------
        on : bool
            True to follow the main branch, False to follow releases.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.categories.setCurrentRow(2)
        >>> dialog.main_channel.setChecked(True)
        >>> saved_channel()
        'main'
        >>> dialog.main_channel.setChecked(False)
        >>> saved_channel()
        'releases'
        """
        save_channel(updates.MAIN if on else updates.RELEASES)

    def choose_theme(self, key: str) -> None:
        """
        Switch the colour theme, remember it, and note that the window should be rebuilt in it.

        Parameters
        ----------
        key : str
            "system", "light" or "dark", or the key of a theme with colours of its own.

        Examples
        --------
        >>> dialog = AppSettingsDialog()
        >>> dialog.choose_theme("light")
        >>> dialog.theme_changed, saved_theme()
        (True, 'light')
        >>> dialog.choose_theme("system")
        """
        save_theme(key)
        apply_theme(key)
        self.theme_changed = True
