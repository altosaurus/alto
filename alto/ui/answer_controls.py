"""Choice buttons and placement actions in the exercise answer area."""

from __future__ import annotations

import re
from collections.abc import Callable

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QColor, QKeySequence
from PySide6.QtWidgets import (
    QAbstractButton,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from alto import settings as app_settings
from alto.exercises.base import ChoiceExercise, Exercise, Question
from alto.exercises.library import (
    BEAT_METERS,
    BeatIdentification,
    IntervalNames,
    KeyboardIntervals,
    NotationIdentification,
    RythmicEquations,
)
from alto.theory.note_naming import DEGREE_FUNCTIONS, FUNCTION_ALTERATIONS
from alto.theory.pitch import ACCIDENTAL_SYMBOLS, QUALITY_NAMES
from alto.ui import motion
from alto.ui.answer_bank import AnswerBank
from alto.ui.colors import (
    CORRECT_ANSWER_COLOR,
    blend,
)
from alto.ui.degree_text import DegreeButton
from alto.ui.meter_staff import MeterButton
from alto.ui.pictures import RHYTHM_SYMBOL_NAMES, ValuePictures
from alto.ui.placement_controls import PlacementControls
from alto.ui.zoom import px

NOTE_CHOICE = re.compile(
    r"^[A-G][♯♭]?m?$",
    # an answer that is a note or key name: C, F♯, B♭, or a minor key
    # such
    # as F♯m
)
DEGREE_CHOICE = re.compile(r"^([♯♭𝄪𝄫]?)([1-7])$")
INTERVAL_QUALITY_SYMBOLS = {
    name: symbol for symbol, name in QUALITY_NAMES.items()
}


def choice_keys(choices: list[str]) -> list[str]:
    """
    Choose a key for each answer button, so that every answer can be
    given from the keyboard.

    Nine answers or fewer take the digits 1 to 9. More than that, as on
    the piano keyboard, take the notes' own names: the
    letter for a natural, Shift and the letter for a sharp, Ctrl and the
    letter for a flat. A minor key, such as F♯m, is
    typed the same way as the major key of its name. Any other long list
    takes 1 to 9
    and then 0, and the rest can be reached with Tab. Scale-degree banks
    use the degree digit, with Shift for a sharp,
    Ctrl for a flat, and Alt added for double alterations.

    Parameters
    ----------
    choices : list of str
        The answers, in the order of their buttons.

    Returns
    -------
    list of str
        A key for each answer, such as "3" or "Shift+C"; "" for an
        answer that has none.

    Examples
    --------
    >>> choice_keys(
    ...     ["major", "minor", "diminished"]
    ... )
    ['1', '2', '3']
    >>> choice_keys(
    ...     list("CDEFGAB") + ["C♯", "B♭"] + ["F♯"]
    ... )
    ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'Shift+C', 'Ctrl+B', 'Shift+F']
    >>> choice_keys([str(n) for n in range(12)])[8:]
    ['9', '0', '', '']
    """
    if len(choices) <= 9:
        return [str(i + 1) for i in range(len(choices))]
    function_degrees = {
        name: str(index)
        for index, name in enumerate(DEGREE_FUNCTIONS, start=1)
    }
    degrees = []
    for choice in choices:
        plain = choice.replace("̂", "")
        sign = plain[0] if plain and plain[0] in "♯♭𝄪𝄫" else ""
        label = plain[len(sign) :]
        for alteration, prefix in FUNCTION_ALTERATIONS.items():
            if prefix and plain.startswith(prefix):
                sign, label = (
                    ACCIDENTAL_SYMBOLS[alteration],
                    plain[len(prefix) :],
                )
                break
        degrees.append(
            DEGREE_CHOICE.fullmatch(sign + function_degrees.get(label, label)),
        )
    if all(degrees):
        modifiers = {
            "": "",
            "♯": "Shift+",
            "♭": "Ctrl+",
            "𝄪": "Alt+Shift+",
            "𝄫": "Alt+Ctrl+",
        }
        return [
            modifiers[match[1]] + match[2]
            for match in degrees
            if match is not None
        ]
    if all(NOTE_CHOICE.match(c) for c in choices):
        keys = []
        for c in choices:
            sign = (
                c[1] if len(c) > 1 and c[1] in "♯♭" else ""
            )  # a trailing m only says that the key is minor
            keys.append(
                c[0]
                if not sign
                else f"{'Shift' if sign == '♯' else 'Ctrl'}+{c[0]}",
            )
        return keys
    return [*"123456789", "0", *[""] * (len(choices) - 10)]


def second_row_keys(
    first: list[str],
    *,
    labels: list[str],
) -> list[str]:
    """
    Choose a key for each button of the second row of a two-part answer,
    such as the octave or the inversion.

    They must not be keys that the first row has. When the first row
    uses the digits the second row takes the home row,
    A S D F and so on; when the first row uses letters (the notes'
    names) it takes the digits, and an octave that is a single
    digit takes that digit.

    Parameters
    ----------
    first : list of str
        The keys of the first row, as `choice_keys` chose them.
    labels : list of str
        The text of each button of the second row. Keyword-only.

    Returns
    -------
    list of str
        A key for each button; "" for one that has none.

    Examples
    --------
    >>> second_row_keys(
    ...     ["1", "2", "3"],
    ...     labels=[
    ...         "root position",
    ...         "1st inversion",
    ...     ],
    ... )
    ['A', 'S']
    >>> second_row_keys(
    ...     ["C", "Shift+C"], labels=["3", "4", "5"]
    ... )
    ['3', '4', '5']
    """
    if any(k.split("+")[-1].isalpha() for k in first):
        return [
            label if label in "123456789" and len(label) == 1 else ""
            for label in labels
        ]
    return [*"ASDFGHJKL"][: len(labels)] + [""] * max(0, len(labels) - 9)


def feedback_style(color: QColor) -> str:
    """
    Build the style sheet that colors an answer button for feedback.

    Parameters
    ----------
    color : QColor
        Background behind the button's white text.

    Returns
    -------
    str
        Style sheet for the button in its enabled and disabled states.

    Examples
    --------
    >>> sheet = feedback_style(QColor("#c62828"))
    >>> "background: #c62828" in sheet, "color: white" in sheet
    (True, True)
    """
    return (
        "QPushButton, QPushButton:disabled { background: "
        f"{color.name()}"
        "; color: white; }"
    )


class AnswerControls(QWidget):
    """
    Present answer choices or placement actions beneath the question.

    Attributes
    ----------
    placement : PlacementControls
        The action row for editing and submitting a construction.
    buttons : list of QPushButton
        Buttons for the first and optional second part, in choice order.
    choice_selected : Signal
        Emits the answer value for a one-part question.
    part_selected : Signal
        Emits the part and choice for a two-part question.

    Examples
    --------
    Note Identification can show letter names with a second row of
    octaves. Either row can be selected first.
    """

    choice_selected = Signal(str)
    part_selected = Signal(str, str)
    MAX_WIDTH = 760

    def __init__(self, exercise: Exercise) -> None:
        """
        Create the layouts shared by successive questions.

        Parameters
        ----------
        exercise : Exercise
            Determines the labels and layouts available for its choices.

        Examples
        --------
        Rhythm equations can show picture buttons for note values.
        """
        super().__init__()
        self.exercise = exercise
        self.buttons: list[QPushButton] = []
        self.setMaximumWidth(px(self.MAX_WIDTH))
        answer_layout = QVBoxLayout(self)
        answer_layout.setContentsMargins(0, 0, 0, 0)
        self.placement = PlacementControls()
        self.placement.hide()
        answer_layout.addWidget(self.placement)
        self.choice_area = QWidget()
        self.choice_box = QGridLayout(self.choice_area)
        self.choice_box.setContentsMargins(
            16,
            8,
            16,
            8,
        )
        self.choice_box.setSpacing(10)
        self.interval_answers = AnswerBank(
            show_all_rows=isinstance(exercise, RythmicEquations),
        )
        self.interval_answers.hide()
        self.quality_label = QLabel("Quality")
        answer_layout.addWidget(self.quality_label)
        answer_layout.addWidget(self.choice_area)
        answer_layout.addWidget(self.interval_answers)
        self.interval_label = QLabel("Interval")
        answer_layout.addWidget(self.interval_label)
        self.octave_row = QWidget()
        self.octave_box = QHBoxLayout(self.octave_row)
        self.octave_box.setContentsMargins(0, 4, 0, 0)
        answer_layout.addWidget(self.octave_row)

    def show_question(
        self,
        q: Question,
        *,
        named_meter: bool,
        locate_notation: bool,
    ) -> None:
        """
        Replace the answer choices, labels, and shortcuts.

        Parameters
        ----------
        q : Question
            Supplies the choices and optional second part.
        named_meter : bool
            Display meter names as text choices.
        locate_notation : bool
            Hide the choice grid while the learner answers on the staff.

        Examples
        --------
        A new question can switch from a single row to an answer bank.
        """
        for b in self.buttons:
            # Release the shortcut before deferred deletion.
            b.setShortcut(QKeySequence())
            b.hide()
            b.deleteLater()
        self.buttons.clear()
        for col in range(self.choice_box.columnCount()):
            self.choice_box.setColumnStretch(col, 0)
        interval_bank = (
            isinstance(self.exercise, KeyboardIntervals)
            and not q.octaves
            and (
                app_settings.keyboard_intervals.all_interval_buttons
                or len(q.choices) > 6
            )
        )
        if isinstance(self.exercise, IntervalNames):
            interval_bank = (
                app_settings.intervals.button_mode == "all"
                or len(q.choices) > 6
            )
        if isinstance(self.exercise, ChoiceExercise):
            interval_bank = len(q.choices) > 6 and (
                not q.grid or isinstance(self.exercise, NotationIdentification)
            )
            interval_bank = interval_bank or named_meter or q.identify_scale
            self.interval_answers.setAccessibleName("Answer choices")
        compact_intervals = isinstance(
            self.exercise,
            KeyboardIntervals,
        ) and bool(q.octaves)
        scale_buttons = bool(q.octaves) and q.second_label == "Mode"
        self.quality_label.setText("Tonic" if scale_buttons else "Quality")
        self.quality_label.setVisible(compact_intervals or scale_buttons)
        self.interval_label.setText(
            "Interval" if compact_intervals else q.second_label,
        )
        self.interval_label.setVisible(bool(q.octaves))
        self.choice_area.setVisible(
            bool(q.choices) and not interval_bank and not locate_notation,
        )
        self.interval_answers.setVisible(interval_bank and bool(q.choices))
        labels = (
            [choice.partition(" ")[0] for choice in q.choices]
            if q.identify_scale
            else q.choices
        )
        if (
            isinstance(self.exercise, RythmicEquations)
            and q.answer.isdecimal()
        ):
            keys = q.choices
        else:
            keys = choice_keys(labels)
        for i, c in enumerate(q.choices):
            b = self._choice_button(
                c,
                label=labels[i],
                named_meter=named_meter,
            )
            self._connect_choice(
                b,
                text=c,
                key=keys[i],
                part="name" if q.octaves else None,
            )
            row, col = q.grid[c] if q.grid else (0, i)
            if not interval_bank:
                self.choice_box.addWidget(b, row, col)
            self.buttons.append(b)
        bank_positions = (
            [q.grid[c] for c in q.choices]
            if interval_bank
            and isinstance(self.exercise, IntervalNames)
            and q.grid
            else None
        )
        self.interval_answers.set_buttons(
            list(self.buttons) if interval_bank else [],
            positions=bank_positions,
        )
        if not interval_bank:
            for col in {
                (q.grid[c][1] if q.grid else i)
                for i, c in enumerate(q.choices)
            }:
                self.choice_box.setColumnStretch(col, 1)  # equal-width columns
        self._show_second_row(q, keys=keys, scale_buttons=scale_buttons)

    def _connect_choice(
        self,
        button: QPushButton,
        *,
        text: str,
        key: str,
        part: str | None,
    ) -> None:
        """
        Bind a choice to its keyboard shortcut and selection signal.

        Parameters
        ----------
        button : QPushButton
            Button for this choice.
        text : str
            Answer text to emit when clicked.
        key : str
            Shortcut, or an empty string for a choice reached with Tab.
        part : str or None
            Part of a paired answer, or None for a complete answer.

        Examples
        --------
        Clicking octave 4 reports the octave part with value "4".
        """
        if key:
            motion.set_shortcut(button, key=key)
            button.setToolTip(f"Key {key}")
        if part is None:
            button.clicked.connect(
                lambda: self.choice_selected.emit(text),
            )
        else:
            button.setCheckable(True)
            button.clicked.connect(
                lambda: self.part_selected.emit(part, text),
            )

    def _choice_button(
        self,
        choice: str,
        *,
        label: str,
        named_meter: bool,
    ) -> QPushButton:
        """
        Render a primary choice with its notation and accessible name.

        Parameters
        ----------
        choice : str
            Choice as accepted by the question.
        label : str
            Visible label for the choice.
        named_meter : bool
            Use a text label for named meters.

        Returns
        -------
        QPushButton
            The choice button before it is assigned to a layout.

        Examples
        --------
        A numeric meter displays its numerator above its denominator.
        """
        if isinstance(self.exercise, BeatIdentification) and not named_meter:
            button = MeterButton(choice, meter=BEAT_METERS[choice])
            button.setMinimumHeight(px(50))
        else:
            button = DegreeButton(label)
            button.setMinimumHeight(px(40))
        if (
            isinstance(self.exercise, RythmicEquations)
            and choice in RHYTHM_SYMBOL_NAMES
        ):
            button.setAccessibleName(RHYTHM_SYMBOL_NAMES[choice])
            button.setText("")
            button.setIcon(ValuePictures.icon(choice))
            button.setIconSize(QSize(px(32), px(64)))
        if (
            isinstance(self.exercise, IntervalNames)
            and choice in INTERVAL_QUALITY_SYMBOLS
        ):
            button.setText(INTERVAL_QUALITY_SYMBOLS[choice])
            button.setAccessibleName(choice)
        for function in DEGREE_FUNCTIONS:
            if choice.endswith(function):
                prefix = choice[: -len(function)].rstrip()
                if prefix:
                    button.setText(f"{prefix}\n{function}")
                button.setMinimumHeight(px(56))
                button.setAccessibleName(choice)
                break
        return button

    def _show_second_row(
        self,
        q: Question,
        *,
        keys: list[str],
        scale_buttons: bool,
    ) -> None:
        """
        Build the second part of a question with its own shortcuts.

        Parameters
        ----------
        q : Question
            Supplies the second set of choices when present.
        keys : list of str
            Shortcuts already assigned to the first row.
        scale_buttons : bool
            Wrap the scale modes in a bank of buttons.

        Examples
        --------
        An octave row shares the available width between its buttons.
        """
        while self.octave_box.count():
            item = self.octave_box.takeAt(0)
            widget = item.widget() if item is not None else None
            if isinstance(widget, QAbstractButton):
                widget.setShortcut(QKeySequence())
            if widget is not None:
                widget.deleteLater()
        self.octave_row.setVisible(bool(q.octaves))
        if not q.octaves:
            return
        second_keys = second_row_keys(keys, labels=q.octaves)
        wrap_second = scale_buttons or (
            isinstance(self.exercise, KeyboardIntervals)
            and len(q.octaves) > 10
        )
        number_bank = AnswerBank() if wrap_second else None
        number_buttons = []
        for i, octave in enumerate(q.octaves):
            b = QPushButton(octave)
            b.setMinimumHeight(px(40))
            self._connect_choice(
                b,
                text=octave,
                key=second_keys[i],
                part="octave",
            )
            if number_bank is None:
                self.octave_box.addWidget(b, 1)
            else:
                number_buttons.append(b)
            self.buttons.append(b)
        if number_bank is not None:
            number_bank.setAccessibleName(
                "Mode buttons" if scale_buttons else "Interval number buttons",
            )
            number_bank.set_buttons(number_buttons)
            self.octave_box.addWidget(number_bank, 1)

    def buttons_for(
        self,
        q: Question,
        *,
        selected: tuple[str, ...],
    ) -> list[QPushButton]:
        """
        Find the buttons for the submitted parts of an answer.

        Parameters
        ----------
        q : Question
            Displayed question, with its choices in button order.
        selected : tuple of str
            Submitted choice, followed by the second part of a
            two-part answer.

        Returns
        -------
        list of QPushButton
            One button for each submitted part, or none when nothing
            was chosen.

        Examples
        --------
        A two-part answer finds one button in each row.
        """
        if not selected:
            return []
        first = self.buttons[q.choices.index(selected[0])]
        if q.octaves and len(selected) == 2:
            second = len(q.choices) + q.octaves.index(selected[1])
            return [
                first,
                self.buttons[second],
            ]
        return [first]

    def show_selection(self, q: Question, *, parts: dict[str, str]) -> None:
        """
        Check the chosen name and the chosen second part.

        Parameters
        ----------
        q : Question
            Displayed question, with its choices in button order.
        parts : dict[str, str]
            Chosen values keyed by answer part.

        Examples
        --------
        Choosing the octave first keeps it checked while the name is
        pending.
        """
        labels = [*q.choices, *(q.octaves or ())]
        for i, (button, label) in enumerate(
            zip(self.buttons, labels, strict=True),
        ):
            part = "name" if i < len(q.choices) else "octave"
            button.setChecked(parts.get(part) == label)

    def disable_choices(self) -> None:
        """
        Stop every answer button from accepting another choice.

        Examples
        --------
        A closed question keeps its buttons visible but unavailable.
        """
        for button in self.buttons:
            button.setEnabled(False)

    def clear_selection(self) -> None:
        """
        Uncheck the chosen buttons and remove their feedback color.

        Examples
        --------
        After an incorrect pair, both rows accept a new selection.
        """
        for button in self.buttons:
            if button.isChecked():
                button.setStyleSheet("")
                button.setChecked(False)

    @staticmethod
    def mark(button: QPushButton, *, color: str) -> None:
        """
        Color a button for feedback without a fade.

        Parameters
        ----------
        button : QPushButton
            Answer or placement button to color.
        color : str
            Final feedback color.

        Examples
        --------
        >>> choice = QPushButton("C")
        >>> AnswerControls.mark(choice, color="#c62828")
        >>> "#c62828" in choice.styleSheet()
        True
        """
        button.setStyleSheet(feedback_style(QColor(color)))

    @staticmethod
    def fade(
        button: QPushButton,
        *,
        target: str = CORRECT_ANSWER_COLOR,
    ) -> Callable[[float], None]:
        """
        Prepare a fade of a button from black to a feedback color.

        Parameters
        ----------
        button : QPushButton
            Answer or placement button to color.
        target : str
            Color at the end of the fade.

        Returns
        -------
        callable
            Colors the button for a fade position from 0 to 1.

        Examples
        --------
        >>> choice = QPushButton("C")
        >>> paint = AnswerControls.fade(choice, target="#c62828")
        >>> paint(1.0)
        >>> "#c62828" in choice.styleSheet()
        True
        """
        end, start = QColor(target), QColor("black")

        def step(t: float) -> None:
            """
            Color the button for one position of the fade.

            Parameters
            ----------
            t : float
                Fade position, from 0 at black to 1 at the target.

            Examples
            --------
            Halfway through, the button is half black and half the
            target color.
            """
            button.setStyleSheet(feedback_style(blend(start, b=end, t=t)))

        return step
