"""
The list on the left in lesson mode: the lessons, and the steps of the one that is open.

It is the lessons' counterpart of the exercise list, and looks the same.

Examples
--------
>>> nav = LessonNav()
>>> nav.show_lesson("circle-of-fifths")
>>> nav.count() > len(LESSONS)
True
"""

from __future__ import annotations

from PySide6.QtCore import (
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import (
    QFont,
    QPalette,
)
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QWidget,
)

from alto.lessons import LESSONS
from alto.ui import icons
from alto.ui.colors import blend
from alto.ui.home import EXERCISE_ICONS
from alto.ui.icons import svg_icon

LESSON_ROLE = Qt.ItemDataRole.UserRole  # holds the lesson's key on a lesson's row
STEP_ROLE = Qt.ItemDataRole.UserRole + 1  # holds the step's number on a step's row


def section_item(
    text: str,
    *,
    palette: QPalette,
) -> QListWidgetItem:
    """
    Make a section label for a list: small, grey capitals that cannot be selected.

    Parameters
    ----------
    text : str
        The heading, which is shown in capitals.
    palette : QPalette
        The palette to take the grey from. Keyword-only.

    Returns
    -------
    QListWidgetItem
        The row.

    Examples
    --------
    >>> section_item("Scales & Keys", palette=QPalette()).text()
    'SCALES & KEYS'
    """
    font = QFont()
    font.setPixelSize(10)
    font.setBold(True)
    font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.3)
    item = QListWidgetItem(text.upper())
    item.setFlags(Qt.ItemFlag.NoItemFlags)  # a section label: not selectable, no hover highlight
    item.setFont(font)
    item.setForeground(blend(palette.color(QPalette.ColorRole.Text), b=palette.color(QPalette.ColorRole.Window), t=0.5))
    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
    item.setSizeHint(QSize(0, 40))
    return item


class LessonNav(QListWidget):
    """
    A flat list of the lessons by category, with the steps of the open lesson listed under it.

    Attributes
    ----------
    lesson_chosen : Signal
        Emitted with a lesson's key when its row is clicked.
    step_chosen : Signal
        Emitted with a step's number, from 0, when its row is clicked.

    Examples
    --------
    >>> nav = LessonNav()
    >>> chosen = []
    >>> _ = nav.step_chosen.connect(chosen.append)
    >>> nav.show_lesson("circle-of-fifths")
    >>> nav.itemClicked.emit(nav.step_items[2])
    True
    >>> chosen
    [2]
    """

    lesson_chosen = Signal(str)
    step_chosen = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the list with no lesson open.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget that owns it.

        Examples
        --------
        >>> LessonNav().objectName()
        'nav'
        """
        super().__init__(parent)
        self.setObjectName("nav")  # styled in style.py, as the exercise list is
        self.setIconSize(QSize(20, 20))
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.setAccessibleName("Lessons")
        self.step_items: list[QListWidgetItem] = []
        self.itemClicked.connect(self._clicked)
        self.show_lesson(None)

    def show_lesson(self, key: str | None) -> None:
        """
        Fill the list, with the steps of one lesson under it.

        Parameters
        ----------
        key : str or None
            The key of the lesson that is open; None for none.

        Examples
        --------
        >>> nav = LessonNav()
        >>> nav.show_lesson("circle-of-fifths")
        >>> len(nav.step_items)
        8
        >>> nav.show_lesson(None)
        >>> nav.step_items
        []
        """
        self.clear()
        self.step_items = []
        ink = self.palette().color(QPalette.ColorRole.Text)
        seen: set[str] = set()
        for lesson in LESSONS:
            if lesson.category not in seen:
                seen.add(lesson.category)
                self.addItem(section_item(lesson.category, palette=self.palette()))
            row = QListWidgetItem(
                svg_icon(EXERCISE_ICONS.get(lesson.exercise, icons.EXERCISE_NOTE_NAMES), color=ink, size=20),
                lesson.title,
            )
            row.setData(LESSON_ROLE, lesson.key)
            row.setToolTip(lesson.summary)
            row.setSizeHint(QSize(0, 38))
            if lesson.key == key:
                font = row.font()
                font.setBold(True)
                row.setFont(font)
            self.addItem(row)
            if lesson.key == key:
                for number, step in enumerate(lesson.steps):
                    item = QListWidgetItem(f"      {number + 1}.  {step.title}")
                    item.setData(LESSON_ROLE, lesson.key)
                    item.setData(STEP_ROLE, number)
                    item.setSizeHint(QSize(0, 30))
                    self.addItem(item)
                    self.step_items.append(item)

    def select_step(self, number: int) -> None:
        """
        Highlight the step that is showing.

        Parameters
        ----------
        number : int
            The step, from 0.

        Examples
        --------
        >>> nav = LessonNav()
        >>> nav.show_lesson("circle-of-fifths")
        >>> nav.select_step(3)
        >>> nav.currentItem() is nav.step_items[3]
        True
        """
        if 0 <= number < len(self.step_items):
            self.setCurrentItem(self.step_items[number])

    def _clicked(self, item: QListWidgetItem) -> None:
        """
        Say which lesson or step was clicked.

        Parameters
        ----------
        item : QListWidgetItem
            The row.

        Examples
        --------
        >>> nav = LessonNav()
        >>> chosen = []
        >>> _ = nav.lesson_chosen.connect(chosen.append)
        >>> nav._clicked(nav.item(1))
        >>> chosen
        ['circle-of-fifths']
        """
        step = item.data(STEP_ROLE)
        if isinstance(step, int):
            self.step_chosen.emit(step)
            return
        key = item.data(LESSON_ROLE)
        if isinstance(key, str):
            self.lesson_chosen.emit(key)
