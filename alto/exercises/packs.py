"""Load third-party instrument packs from ZIP archives and authoring folders."""

from __future__ import annotations

import hashlib
import random
import shutil
from collections.abc import Iterator
from contextlib import nullcontext
from copy import deepcopy
from dataclasses import dataclass, replace
from os import stat_result
from os.path import samestat
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile
from zlib import error as ZlibError

from PySide6.QtCore import QFile, QLockFile

from alto import settings
from alto.audio import INSTRUMENT_BY_KEY, Instrument, sounds
from alto.exercises.base import REGISTRY, ChoiceExercise, FingerboardPosition, PicturePosition, Question, register, signature
from alto.instrument_packs import (
    INSTALLED,
    PackFiles,
    PackInstrument,
    identifier,
    image_point,
    pitch,
    plain_text,
    read_focus,
    read_icon,
    read_instrument,
    read_marker_size,
)
from alto.lessons import register_lesson
from alto.lessons.base import Lesson
from alto.lessons.packs import read_lessons
from alto.terms import (
    PLUGIN_TERMS,
    PluginTerm,
    read_terms,
    register_term,
)
from alto.theory.pitch import LETTERS, NATURAL_SEMITONES, Note


class PackExercise(ChoiceExercise):
    """
    A finite set of illustrated multiple-choice cards declared by an instrument pack.

    Examples
    --------
    The viola pack contributes one practice card for every eligible string and pitch.
    """

    category = "Instruments"
    pack_id: str
    pack_name: str
    instruments: dict[str, PackInstrument]
    cards: tuple[Question, ...]
    catalog_signature: str
    lessons: tuple[Lesson, ...] = ()
    terms: tuple[PluginTerm, ...] = ()
    controls: dict[str, str | bool] = {}  # the settings the pack declared for this exercise, by kind
    spec: dict = {}  # the exercise's manifest entry, kept to build cards for the learner's settings
    pack_instrument: PackInstrument
    span: tuple[int, int] = (0, 0)  # lowest and highest staff step among the listed notes
    range_clef: str = ""  # the clef the range is drawn on, when the pack offers a range
    key_span: tuple[int, int] = (0, 0)  # a keyboard exercise: the lowest and highest key it has cards for, as MIDI numbers
    key_default: tuple[int, int] = (0, 0)  # a keyboard exercise: the keys it asks until the learner chooses another range
    interval_names: tuple[str, ...] = ()  # a keyboard exercise: every interval it can ask
    manual_names: tuple[str, ...] = ()  # a keyboard exercise: the keyboards its keys can sit on, in the manifest's order
    _subset_cache: dict = {}  # a keyboard exercise: the cards of each range and set of intervals already chosen

    @classmethod
    def options(cls) -> settings.PackExerciseSettings:
        """
        Return the learner's options for this exercise, creating the defaults the first time.

        Returns
        -------
        PackExerciseSettings
            The shared, editable options, kept under the exercise's class name.

        Examples
        --------
        >>> class Demo(PackExercise):
        ...     span = (21, 30)
        ...     range_clef = "alto"
        >>> Demo.options().range_for("alto"), Demo.options().sound
        ((21, 30), None)
        >>> _ = settings.pack_exercises.pop("Demo")
        """
        found = settings.pack_exercises.get(cls.__name__)
        if found is None:
            clef = cls.range_clef or "alto"
            found = settings.pack_exercises[cls.__name__] = settings.PackExerciseSettings(
                clefs={clef},
                ranges={clef: cls.span} if cls.range_clef else {},
            )
        return found

    @property
    def is_keyboard(self) -> bool:
        """
        Report whether this is a keyboard interval exercise.

        Returns
        -------
        bool
            True when the pack declared the exercise with type ``keyboard-intervals``.

        Examples
        --------
        >>> class Demo(PackExercise):
        ...     spec = {"type": "keyboard-intervals"}
        >>> Demo().is_keyboard
        True
        """
        return self.spec.get("type") == "keyboard-intervals"

    @classmethod
    def chosen_keys(cls) -> tuple[int, int]:
        """
        Find the lowest and highest key a keyboard exercise asks.

        Returns
        -------
        tuple of int
            The learner's range if the plugin offers one and it fits the exercise, otherwise the plugin's default range.

        Examples
        --------
        >>> class Demo(PackExercise):
        ...     key_span, key_default = (28, 89), (48, 72)
        >>> Demo.chosen_keys()
        (48, 72)
        """
        keys = cls.options().keys if cls.controls.get("range") else None
        low, high = keys or cls.key_default
        return (low, high) if cls.key_span[0] <= low < high <= cls.key_span[1] else cls.key_default

    @classmethod
    def chosen_span(cls) -> tuple[str, str]:
        """
        Name the lowest and highest key a keyboard exercise asks, for drawing the keyboards over that range.

        Returns
        -------
        tuple of str
            The two keys, such as ``("C3", "C5")``.

        Examples
        --------
        >>> class Demo(PackExercise):
        ...     key_span, key_default = (28, 89), (48, 72)
        >>> Demo.chosen_span()
        ('C3', 'C5')
        """
        low, high = cls.chosen_keys()
        return _key_name(low), _key_name(high)

    @classmethod
    def chosen_intervals(cls) -> tuple[str, ...]:
        """
        Find the intervals a keyboard exercise asks.

        Returns
        -------
        tuple of str
            The learner's choice among the intervals the plugin lists, or all of them if the plugin offers no choice or
            the choice leaves none.

        Examples
        --------
        >>> class Demo(PackExercise):
        ...     interval_names = ("m2", "M2", "m3")
        >>> Demo.chosen_intervals()
        ('m2', 'M2', 'm3')
        """
        picked = cls.options().intervals if cls.controls.get("intervals") else None
        names = tuple(name for name in cls.interval_names if picked is None or name in picked)
        return names or cls.interval_names

    @classmethod
    def chosen_manuals(cls) -> tuple[str, ...]:
        """
        Find the keyboards a keyboard exercise puts its highlighted keys on.

        Returns
        -------
        tuple of str
            The learner's choice among the keyboards the exercise uses, or all of them if the plugin offers no choice or
            the choice leaves none.

        Examples
        --------
        >>> class Demo(PackExercise):
        ...     manual_names = ("Upper manual", "Lower manual")
        >>> Demo.chosen_manuals()
        ('Upper manual', 'Lower manual')
        """
        picked = cls.options().manuals if cls.controls.get("manuals") else None
        names = tuple(name for name in cls.manual_names if picked is None or name in picked)
        return names or cls.manual_names

    def _keyboard_active(self) -> tuple[Question, ...]:
        """
        Pick the keyboard cards inside the chosen range and intervals, drawn over that range.

        Returns
        -------
        tuple of Question
            The cards whose two keys both lie in the range and whose interval was chosen, with the chosen intervals as
            answer buttons. If none fit, the cards of the default range and every interval.

        Examples
        --------
        A learner who narrows the range to one octave is asked only the intervals that fit within it.
        """
        cls = type(self)
        cache = cls.__dict__.get("_subset_cache")
        if cache is None:
            cache = {}
            cls._subset_cache = cache
        picked = _keyboard_subset(
            self.cards,
            keys=self.chosen_keys(),
            names=self.chosen_intervals(),
            manuals=self.chosen_manuals(),
            cache=cache,
        )
        return picked or _keyboard_subset(
            self.cards,
            keys=self.key_default,
            names=self.interval_names,
            manuals=self.manual_names,
            cache=cache,
        )

    def active_cards(self) -> tuple[Question, ...]:
        """
        Build the cards for the learner's settings: the sharps and flats, the octave, and the range they chose.

        Returns
        -------
        tuple of Question
            The cards, or all of the pack's cards for an exercise with no settings, or when the range leaves none.

        Examples
        --------
        An exercise whose pack declares no settings always asks every card.
        """
        if self.is_keyboard:
            return self._keyboard_active()
        if not self.controls:
            return self.cards
        chosen = self.options()
        cards = _fingerboard_cards(
            self.spec,
            model=self.pack_instrument,
            key=type(self).__name__,
            accidentals=bool(self.controls.get("accidentals")) and chosen.accidentals,
            octave=bool(self.controls.get("octave")) and chosen.require_octave,
        )
        if self.range_clef:
            low, high = chosen.range_for(self.range_clef)
            cards = [c for c in cards if c.fingerboard and low <= Note.parse(c.fingerboard.note).diatonic <= high]
        return tuple(cards) or self.cards

    def sound_instrument(self, key: str | None) -> str | None:
        """
        Play the pack's own sound unless the pack offers the choice and the learner chose another instrument.

        Parameters
        ----------
        key : str or None
            The key of the pack's instrument.

        Returns
        -------
        str or None
            The learner's chosen instrument if there is one and it is installed, otherwise the pack's own.

        Examples
        --------
        An exercise with no sound setting always plays the pack's instrument.
        """
        if "sound" not in self.controls:
            return key
        chosen = self.options().sound
        return chosen if chosen in INSTRUMENT_BY_KEY else key

    @classmethod
    def sound_options(cls) -> list[tuple[str, list[tuple[str, str]]]]:
        """
        List the instruments a learner can choose to sound in this exercise, in the order they are offered.

        The instruments that came with the plugin come first, then other instruments of the same kind (other harpsichords
        for a harpsichord), then every other installed instrument, whatever its kind. An instrument with no recordings on
        disk is left out.

        Returns
        -------
        list of tuple of str and list of tuple of str and str
            Each group's heading and its instruments as (key, label), with empty groups left out.

        Examples
        --------
        >>> from alto.audio import INSTRUMENTS
        >>> class Demo(PackExercise):
        ...     pack_name = "Demo pack"
        ...     instruments = {}
        >>> [heading for heading, _ in Demo.sound_options()]
        ['Other instruments']
        """
        own = [model.sound for model in getattr(cls, "instruments", {}).values() if model.sound is not None]
        taken = {inst.key for inst in own}
        main = getattr(getattr(cls, "pack_instrument", None), "sound", None)
        kind = main.kind_name if main is not None and main.kind else ""
        others = [inst for inst in INSTRUMENT_BY_KEY.values() if inst.key not in taken and sounds.recordings(inst)]
        same = [inst for inst in others if kind and inst.kind_name == kind]
        rest = [inst for inst in others if inst not in same]

        def named(inst: Instrument, *, own: bool = False) -> tuple[str, str]:
            """
            Pair an instrument's key with the name shown for it, adding its plugin when it has one.

            Parameters
            ----------
            inst : Instrument
                The instrument.
            own : bool, default False
                The instrument came with this plugin, so its plugin's name is left out. Keyword-only.

            Returns
            -------
            tuple of str
                The key and the label.

            Examples
            --------
            A plugin's sound is shown as its name followed by the plugin's name in brackets.
            """
            return inst.key, f"{inst.label} ({inst.pack_name})" if inst.pack_name and not own else inst.label

        groups = [
            (f"From {getattr(cls, 'pack_name', 'the plugin')}", [named(inst, own=True) for inst in own]),
            (f"Other {kind}s" if kind else "", [named(inst) for inst in same]),
            ("Other instruments", [named(inst) for inst in rest]),
        ]
        return [(heading, items) for heading, items in groups if items]

    def practice_signature(self) -> str:
        """
        Identify the pack settings used to generate this catalog.

        Returns
        -------
        str
            Signature shared by cards from this exercise revision.

        Examples
        --------
        Adding an eligible pitch changes the signature, and so does asking sharps and flats or the octave.
        """
        if self.is_keyboard:
            keys, names, manuals = self.chosen_keys(), self.chosen_intervals(), self.chosen_manuals()
            if keys == self.key_default and names == self.interval_names and manuals == self.manual_names:
                return self.catalog_signature  # the settings every learner starts with keep their history
            if manuals == self.manual_names:
                return signature(self.catalog_signature, keys, names)  # unchanged by the manuals setting, so keeps history
            return signature(self.catalog_signature, keys, names, manuals)
        if not self.controls:
            return self.catalog_signature
        chosen = self.options()
        low_high = chosen.range_for(self.range_clef) if self.range_clef else self.span
        if not (chosen.accidentals or chosen.require_octave) and low_high == self.span:
            return self.catalog_signature  # the settings every learner starts with keep their history
        return signature(self.catalog_signature, chosen.accidentals, chosen.require_octave, low_high)

    def refresh(self, question: Question) -> Question:
        """
        Restore the instrument reference on cards saved by the single-instrument prototype.

        Parameters
        ----------
        question : Question
            Saved question.

        Returns
        -------
        Question
            Card with its pack-qualified instrument reference.

        Examples
        --------
        An existing D-string card keeps its original position when a pack is upgraded.
        """
        position = question.fingerboard
        current = self.cards[0].fingerboard
        if position and current and not position.instrument and position.strings == current.strings:
            return replace(question, fingerboard=replace(position, instrument=current.instrument))
        return question

    def make_question(self, rng: random.Random) -> Question:
        """
        Pick one of the illustrated questions in the pack.

        Parameters
        ----------
        rng : random.Random
            Source of the question choice.

        Returns
        -------
        Question
            The marked position, prompt, and answer choices.

        Examples
        --------
        An open D4 on a viola asks for D.
        """
        return deepcopy(rng.choice(self.active_cards()))

    def daily_candidates(self, rng: random.Random) -> Iterator[Question]:
        """
        Visit each question in the pack once in shuffled order.

        Parameters
        ----------
        rng : random.Random
            Source of the order and button selection.

        Yields
        ------
        Question
            Each distinct marked position.

        Examples
        --------
        Open G and G on the C string yield separate cards.
        """
        cards = self.active_cards()
        for card in rng.sample(cards, len(cards)):
            yield self.limit_buttons(deepcopy(card), rng=rng)

    def card_count(self) -> int:
        """
        Count the distinct questions in the exercise.

        Returns
        -------
        int
            Number of cards in this exercise.

        Examples
        --------
        The viola example offers twenty positions.
        """
        return len(self.active_cards())


CONTROL_KINDS = ("sound", "range", "accidentals", "octave")  # the settings a note exercise can offer
KEYBOARD_CONTROL_KINDS = ("sound", "range", "intervals", "manuals")  # the settings a keyboard interval exercise can offer


def read_controls(value: object, *, key: str, kinds: tuple[str, ...] = CONTROL_KINDS) -> dict[str, str | bool]:
    """
    Validate the settings a pack offers for one of its exercises.

    Parameters
    ----------
    value : object
        The exercise's ``settings`` entry: an object that may hold ``sound`` (the label of a switch that plays the pack's own
        sound), ``range`` (a clef to draw a range selector on, or true for the keys of a keyboard exercise),
        ``accidentals`` and ``octave`` (true for a switch), ``intervals`` (true for a choice of intervals),
        ``manuals`` (true for a choice of keyboards), or None.
    key : str
        The exercise id, for diagnostics. Keyword-only.
    kinds : tuple of str, default CONTROL_KINDS
        The settings this kind of exercise can have. Keyword-only.

    Returns
    -------
    dict of str to str or bool
        The declared settings by kind; empty when the pack declares none.

    Raises
    ------
    ValueError
        If the entry has an unknown kind or a value of the wrong type.

    Examples
    --------
    >>> read_controls({"range": "alto", "octave": True}, key="pack.v.notes")
    {'range': 'alto', 'octave': True}
    >>> read_controls({"range": True, "intervals": True}, key="pack.v.keys", kinds=KEYBOARD_CONTROL_KINDS)
    {'range': True, 'intervals': True}
    >>> read_controls(None, key="pack.v.notes")
    {}
    """
    if value is None:
        return {}
    if not isinstance(value, dict) or not value or set(value) - set(kinds):
        raise ValueError(f"Give the settings of {key} as an object with any of: {', '.join(kinds)}.")
    keyboard = kinds == KEYBOARD_CONTROL_KINDS
    for kind, setting in value.items():
        if kind == "sound" and not plain_text(setting, limit=30):
            raise ValueError(f"Give the sound setting of {key} a plain-text label of at most 30 characters.")
        if kind == "range" and keyboard and setting is not True:
            raise ValueError(f"Set range in the settings of {key} to true, or leave it out.")
        if kind == "range" and not keyboard and setting not in settings.CLEFS:
            raise ValueError(f"Set the range of {key} to one clef: {', '.join(settings.CLEFS)}.")
        if kind in ("accidentals", "octave", "intervals", "manuals") and setting is not True:
            raise ValueError(f"Set {kind} in the settings of {key} to true, or leave it out.")
    return dict(value)


def _sharp(midi: int) -> Note:
    """
    Write a black key as the note a semitone below it, raised by a sharp.

    Parameters
    ----------
    midi : int
        MIDI number of a black key.

    Returns
    -------
    Note
        The sharp spelling.

    Examples
    --------
    >>> str(_sharp(61))
    'C♯4'
    """
    below = midi - 1
    letter = next(index for index, semitones in enumerate(NATURAL_SEMITONES) if semitones == below % 12)
    return Note(below // 12 - 1, letter=letter, accidental=1)


def _fingerboard_cards(
    exercise: dict,
    *,
    model: PackInstrument,
    key: str,
    accidentals: bool = False,
    octave: bool = False,
) -> list[Question]:
    """
    Build a finite card for each requested string and pitch.

    Parameters
    ----------
    exercise : dict
        Exercise manifest entry.
    model : PackInstrument
        Calibrated strings and image.
    key : str
        Exercise id for diagnostics.
    accidentals : bool, default False
        Also ask each note between the listed ones on a string, written as a sharp and accepted as its flat. Keyword-only.
    octave : bool, default False
        Make the answer include the written octave. Keyword-only.

    Returns
    -------
    list of Question
        Distinct playable positions.

    Raises
    ------
    ValueError
        If the tuning or notes cannot produce a playable card.

    Examples
    --------
    An open G3 and a G3 on the C string yield separate questions.
    """
    if not model.strings:
        raise ValueError(f"Declare strings on {model.key} for a fingerboard-notes exercise.")
    tuning = tuple(string.pitch for string in model.strings)
    midis = [pitch(s).midi for s in tuning]
    rows = exercise.get("notes")
    if not isinstance(rows, dict) or not rows:
        raise ValueError(f'List the notes to practice under "notes" for {key}.')
    positions = []
    names = {letter: Note(4, letter=index) for index, letter in enumerate(LETTERS)}  # each answer button, and the note it means
    for string, pitches in rows.items():
        if string not in tuning or not isinstance(pitches, list) or not pitches:
            raise ValueError(f"Give a list of notes for an open string from the tuning. Check {string!r}.")
        index = tuning.index(string)
        seen = set()
        spellings = []
        for spelling in pitches:
            note = pitch(spelling)
            if not 0 <= note.midi - midis[index] <= 12:
                raise ValueError(f"{spelling} must be within one octave above the open {string} string, including both ends.")
            if note.midi in seen:
                raise ValueError(f"The same position appears twice on {string}. Check {spelling}.")
            seen.add(note.midi)
            spellings.append(spelling)
            names[note.name] = Note(4, letter=note.letter, accidental=note.accidental)
        if accidentals:
            for midi in range(min(seen), max(seen) + 1):
                if midi not in seen:
                    black = _sharp(midi)
                    spellings.append(f"{LETTERS[black.letter]}#{black.octave}")
            spellings.sort(key=lambda spelled: pitch(spelled).midi)
        positions.extend(FingerboardPosition(tuning, index, spelling, model.key) for spelling in spellings)
    grid = None
    if accidentals:
        names = {
            Note(4, letter=letter, accidental=accidental).name: Note(4, letter=letter, accidental=accidental)
            for letter in range(7)
            for accidental in (-1, 0, 1)
        }
        ordered = sorted(names.values(), key=lambda ref: (ref.letter, ref.accidental))
        row_of = {1: 0, 0: 1, -1: 2}  # sharps on the top row, then naturals, then flats
        grid = {note.name: (row_of[note.accidental], note.letter) for note in ordered}
        names = {note.name: note for note in ordered}
    prompt = exercise.get("prompt", "Name the note at the dot.")
    if not plain_text(prompt, limit=120):
        raise ValueError(f"Give {key} a plain-text prompt of at most 120 characters.")
    cards = []
    for position in positions:
        note = Note.parse(position.note)
        if octave:
            alternatives = tuple(
                f"{name}{(note.midi - NATURAL_SEMITONES[ref.letter] - ref.accidental) // 12 - 1}"
                for name, ref in names.items()
                if ref.pitch_class == note.pitch_class and name != note.name
            )
        else:
            alternatives = tuple(name for name, ref in names.items() if ref.pitch_class == note.pitch_class and name != note.name)
        cards.append(
            Question(
                prompt,
                choices=list(names),
                answer=f"{note.name}{note.octave}" if octave else note.name,
                accept=alternatives,
                fingerboard=position,
                explanation=f"{position.note} on the {tuning[position.string]} string.",
                grid=grid,
                octaves=sorted({str(Note.parse(p.note).octave) for p in positions}, key=int) if octave else None,
            ),
        )
    return cards


def _keyboard_limits(exercise: dict, *, key: str) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    Read the range of keys a keyboard exercise has cards for, and the part of it asked until the learner chooses another.

    Parameters
    ----------
    exercise : dict
        Exercise manifest entry, with ``lowest`` and ``highest`` and optionally ``default_range``.
    key : str
        Exercise id for diagnostics. Keyword-only.

    Returns
    -------
    tuple of tuple of int
        The lowest and highest key available, then the lowest and highest key of the default range, as MIDI numbers.

    Raises
    ------
    ValueError
        If a key is not a note, the range is empty, or the default range does not lie within it.

    Examples
    --------
    >>> _keyboard_limits({"lowest": "E1", "highest": "F6", "default_range": ["C3", "C5"]}, key="pack.v.keys")
    ((28, 89), (48, 72))
    >>> _keyboard_limits({"lowest": "C3", "highest": "C5"}, key="pack.v.keys")
    ((48, 72), (48, 72))
    """
    low, high = pitch(exercise.get("lowest")).midi, pitch(exercise.get("highest")).midi
    if not 1 <= high - low:
        raise ValueError(f"Put the lowest key of {key} below its highest key.")
    chosen = exercise.get("default_range")
    if chosen is None:
        return (low, high), (low, high)
    if not isinstance(chosen, list) or len(chosen) != 2:
        raise ValueError(f"Give the default_range of {key} as the lowest and the highest key to ask at first.")
    start, end = pitch(chosen[0]).midi, pitch(chosen[1]).midi
    if not low <= start < end <= high:
        raise ValueError(
            f"Keep the default_range of {key} inside its lowest and highest keys, with the lowest below the highest.",
        )
    return (low, high), (start, end)


def _keyboard_cards(exercise: dict, *, model: PackInstrument, key: str) -> list[Question]:
    """
    Build a card for each interval, each lowest key, and each placement of the two keys on the instrument's keyboards.

    Parameters
    ----------
    exercise : dict
        Exercise manifest entry. It names the ``keyboards`` to use, the ``lowest`` and ``highest`` key of the range, the
        ``intervals`` to ask, and whether the keys sit on the ``same`` keyboard or ``across`` two.
    model : PackInstrument
        The instrument whose keyboards Alto draws.
    key : str
        Exercise id for diagnostics. Keyword-only.

    Returns
    -------
    list of Question
        One question for each distinct pair of highlighted keys.

    Raises
    ------
    ValueError
        If a keyboard, interval, range or placement is missing or invalid.

    Examples
    --------
    A two-manual harpsichord asks a minor third on its lower manual, on its upper manual, or from one manual to the other.
    """
    if not model.keyboards:
        raise ValueError(f"Declare keyboards on {model.key} for a keyboard-intervals exercise.")
    names = exercise.get("keyboards", [board.name for board in model.keyboards])
    if not isinstance(names, list) or not names or len(set(names)) != len(names):
        raise ValueError(f"List each keyboard of {key} once.")
    boards = []
    for name in names:
        board = model.keyboard(name) if isinstance(name, str) else None
        if board is None:
            raise ValueError(f"{key} names a keyboard {name!r} that {model.key} does not have.")
        boards.append(board)
    (low, high), _ = _keyboard_limits(exercise, key=key)
    table = settings.KEYBOARD_INTERVAL_NAMES[:12]
    wanted = exercise.get("intervals", list(table))
    if not isinstance(wanted, list) or not wanted or len(set(wanted)) != len(wanted) or any(name not in table for name in wanted):
        raise ValueError(f"List distinct intervals for {key}, from {', '.join(table)}.")
    placements = exercise.get("placements", ["same", "across"])
    if not isinstance(placements, list) or not placements or not set(placements) <= {"same", "across"}:
        raise ValueError(f'Set placements for {key} to "same", "across" or both.')
    if "across" in placements and len(boards) < 2:
        raise ValueError(f'Use "across" in {key} only with two or more keyboards.')
    pairs = []
    if "same" in placements:
        pairs.extend((board, board) for board in boards)
    if "across" in placements:
        pairs.extend((first, second) for first in boards for second in boards if first is not second)
    prompt = exercise.get("prompt", "Name the interval from the lower key to the higher key.")
    if not plain_text(prompt, limit=120):
        raise ValueError(f"Give {key} a plain-text prompt of at most 120 characters.")
    cards = []
    for name in wanted:
        distance = table.index(name) + 1
        for lower in range(low, high - distance + 1):
            for first, second in pairs:
                a, b = _key_name(lower), _key_name(lower + distance)
                if not (first.has(a) and second.has(b)):
                    continue
                cards.append(
                    Question(
                        prompt,
                        choices=list(wanted),
                        answer=name,
                        picture=PicturePosition(
                            model.key,
                            (0.0, 0.0),
                            "",
                            0.0,
                            (),
                            False,
                            "",
                            ((first.name, a), (second.name, b)),
                            (a, b),
                            (_key_name(low), _key_name(high)),
                        ),
                        explanation=f"{a} to {b} is {distance} half step{'s' if distance != 1 else ''}: {name}.",
                    ),
                )
    if not cards:
        raise ValueError(f"{key} has no pair of keys to ask. Check its range, intervals and keyboards.")
    return cards


def _keyboard_subset(
    cards: tuple[Question, ...],
    *,
    keys: tuple[int, int],
    names: tuple[str, ...],
    manuals: tuple[str, ...] | None = None,
    cache: dict | None = None,
) -> tuple[Question, ...]:
    """
    Pick the keyboard cards that lie within a range of keys and ask one of some intervals.

    Parameters
    ----------
    cards : tuple of Question
        Every card of a keyboard interval exercise.
    keys : tuple of int
        The lowest and highest key allowed, as MIDI numbers. Keyword-only.
    names : tuple of str
        The intervals to ask. They become the answer buttons. Keyword-only.
    manuals : tuple of str or None, default None
        The keyboards both highlighted keys must sit on, or None for any. Keyword-only.
    cache : dict or None, default None
        Where to remember each card's two keys and each choice already made, so dragging a range selector does not
        search thousands of cards again. Keyword-only.

    Returns
    -------
    tuple of Question
        The matching cards, each drawn over the chosen range of keys.

    Examples
    --------
    >>> card = Question("?", choices=["M3"], answer="M3", picture=PicturePosition("a", (0, 0), notes=("C4", "E4")))
    >>> [q.picture.span for q in _keyboard_subset((card,), keys=(48, 72), names=("M3",))]
    [('C3', 'C5')]
    >>> _keyboard_subset((card,), keys=(48, 62), names=("M3",))
    ()
    >>> placed = PicturePosition("a", (0, 0), keys=(("Upper", "C4"), ("Lower", "E4")), notes=("C4", "E4"))
    >>> card = Question("?", choices=["M3"], answer="M3", picture=placed)
    >>> len(_keyboard_subset((card,), keys=(48, 72), names=("M3",), manuals=("Upper",)))
    0
    """
    store = {} if cache is None else cache
    pick = (keys, names, manuals)
    if pick in store:
        return store[pick]
    if "midis" not in store:
        store["midis"] = [
            tuple(Note.parse(name).midi for name in card.picture.notes) if card.picture else (0, 0) for card in cards
        ]
    low, high = keys
    span = (_key_name(low), _key_name(high))
    chosen = []
    for card, (first, second) in zip(cards, store["midis"], strict=True):
        picture = card.picture
        if picture is None or card.answer not in names or not (low <= first and second <= high):
            continue
        if manuals is None or all(board in manuals for board, _ in picture.keys):
            chosen.append(replace(card, choices=list(names), picture=replace(picture, span=span)))
    if len(store) > 24:
        store.clear()
    store[pick] = tuple(chosen)
    return store[pick]


def _key_name(midi: int) -> str:
    """
    Write a key's pitch with a sharp for each black key.

    Parameters
    ----------
    midi : int
        MIDI number of a key.

    Returns
    -------
    str
        The pitch, such as ``C4`` or ``F#3``.

    Examples
    --------
    >>> _key_name(60), _key_name(66)
    ('C4', 'F#4')
    """
    if midi % 12 in NATURAL_SEMITONES:
        letter = NATURAL_SEMITONES.index(midi % 12)
        return f"{LETTERS[letter]}{midi // 12 - 1}"
    black = _sharp(midi)
    return f"{LETTERS[black.letter]}#{black.octave}"


def _image_cards(exercise: dict, *, model: PackInstrument) -> list[Question]:
    """
    Build author-written questions marked directly on an instrument image.

    Parameters
    ----------
    exercise : dict
        Exercise manifest entry.
    model : PackInstrument
        Instrument that supplies the picture and optional sound.

    Returns
    -------
    list of Question
        Illustrated multiple-choice cards.

    Raises
    ------
    ValueError
        If a question has an incomplete or repeated answer, marker, or prompt.

    Examples
    --------
    A question can mark the bell on a trumpet and offer names of instrument parts.
    """
    rows = exercise.get("questions")
    if not isinstance(rows, list) or not rows:
        raise ValueError("An image-choice exercise needs a nonempty questions list.")
    cards = []
    keys = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each question must be an object.")
        prompt, choices, answer = row.get("prompt"), row.get("choices"), row.get("answer")
        if not isinstance(choices, list) or len(choices) < 2:
            raise ValueError("Give each question at least two answer choices.")
        if not isinstance(prompt, str) or any(
            not isinstance(text, str) or not text.strip() or "<" in text or ">" in text for text in (prompt, *choices)
        ):
            raise ValueError("Use plain text for each prompt and choice.")
        if not isinstance(answer, str) or len(set(choices)) != len(choices) or answer not in choices:
            raise ValueError("Use distinct choices and an answer that exactly matches one of them.")
        view = row.get("view", "")
        found = model.picture(view) if isinstance(view, str) else None
        if found is None:
            raise ValueError(f"Set view to the name of one of this instrument's views, or leave it out: {view!r}.")
        width, height = found[1]
        point = image_point(row.get("point"), width=width, height=height)
        note = row.get("note", "")
        if "note" in row:
            pitch(note)
        size = read_marker_size(row.get("marker_size", 0))
        focus = row.get("focus", [])
        if focus:
            left, top, span_x, span_y = read_focus(focus, width=width, height=height)
            if not (left <= point[0] <= left + span_x and top <= point[1] <= top + span_y):
                raise ValueError("Keep the marked point inside its focus region.")
            focus = [left, top, span_x, span_y]
        card = Question(
            prompt,
            choices=choices,
            answer=answer,
            picture=PicturePosition(model.key, point, note, float(size), tuple(float(v) for v in focus), True, view),
        )
        if card.item_key() in keys:
            raise ValueError("Duplicate image-choice question.")
        keys.add(card.item_key())
        cards.append(card)
    return cards


def read_pack(path: Path) -> list[type[PackExercise]]:
    """
    Read and validate every exercise before making any of them available.

    Parameters
    ----------
    path : Path
        A pack.json file or a ZIP containing it at the root.

    Returns
    -------
    list of type
        Exercise classes with stable identifiers.

    Raises
    ------
    ValueError
        If the file or one of its exercises has an invalid format.

    Examples
    --------
    The viola example contributes note identification and instrument anatomy exercises.
    """
    archive = ZipFile(path) if path.suffix.lower() == ".zip" else nullcontext(None)
    with archive as opened:
        files = PackFiles(path, archive=opened)
        data = files.manifest()
        pack_id = identifier(data.get("id"))
        rows = data.get("instruments")
        if not isinstance(rows, list) or not rows:
            raise ValueError("Include at least one instrument with its artwork.")
        instruments = {}
        for row in rows:
            model = read_instrument(row, pack=pack_id, pack_name=data["name"], files=files)
            if model.key in instruments:
                raise ValueError(f"Duplicate instrument id {model.key}.")
            instruments[model.key] = model
        icons = {}
        for name in _icon_names(data):
            icons[name] = read_icon(files, name=name)
    exercises = data.get("exercises")
    if not isinstance(exercises, list) or not exercises:
        raise ValueError('Include at least one entry under "exercises".')
    classes: dict[str, type[PackExercise]] = {}
    exercise_keys: dict[str, str] = {}
    for exercise in exercises:
        if not isinstance(exercise, dict) or exercise.get("type") not in (
            "fingerboard-notes",
            "image-choice",
            "keyboard-intervals",
        ):
            raise ValueError('Set the exercise type to "fingerboard-notes", "image-choice" or "keyboard-intervals".')
        key = f"pack.{pack_id}.{identifier(exercise.get('id'))}"
        exercise_keys[identifier(exercise.get("id"))] = key
        if key in classes:
            raise ValueError(f"Duplicate exercise id {key}.")
        title = exercise.get("title")
        if not isinstance(title, str) or not title.strip() or "<" in title or ">" in title:
            raise ValueError(f"Give {key} a plain-text title.")
        description = exercise.get("description")
        if description is not None and not plain_text(description, limit=400):
            raise ValueError(f"Give {key} a plain-text description of at most 400 characters.")
        instrument_id = f"pack.{pack_id}.{identifier(exercise.get('instrument'))}"
        if instrument_id not in instruments:
            raise ValueError(f"Unknown instrument {instrument_id} in {key}.")
        model = instruments[instrument_id]
        keyboard = exercise["type"] == "keyboard-intervals"
        controls = read_controls(exercise.get("settings"), key=key, kinds=KEYBOARD_CONTROL_KINDS if keyboard else CONTROL_KINDS)
        span = (0, 0)
        key_span = key_default = (0, 0)
        interval_names: tuple[str, ...] = ()
        manual_names: tuple[str, ...] = ()
        if exercise["type"] == "fingerboard-notes":
            cards = _fingerboard_cards(exercise, model=model, key=key)
            heights = [Note.parse(spot.note).diatonic for card in cards if (spot := card.fingerboard)]
            span = (min(heights), max(heights))
            tuning = ", ".join(string.pitch for string in model.strings)
            help_text = f"Name the note marked on the fingerboard. The open strings from lowest to highest are {tuning}."
        elif exercise["type"] == "keyboard-intervals":
            cards = _keyboard_cards(exercise, model=model, key=key)
            key_span, key_default = _keyboard_limits(exercise, key=key)
            interval_names = tuple(exercise.get("intervals", settings.KEYBOARD_INTERVAL_NAMES[:12]))
            manual_names = tuple(exercise.get("keyboards", [board.name for board in model.keyboards]))
            help_text = "Name the interval between the two highlighted keys."
        else:
            cards = _image_cards(exercise, model=model)
            if controls:
                raise ValueError(f"Only a fingerboard-notes exercise can have settings. Check {key}.")
            help_text = "Look at the marked location on the instrument and choose the answer to the question."
        # Alto uses the class name as the exercise key in settings, practice history and exports.
        classes[key] = type(
            key,
            (PackExercise,),
            {
                "pack_id": pack_id,
                "pack_name": data["name"],
                "name": title.strip(),
                "cards": tuple(cards),
                "description": description.strip() if isinstance(description, str) else help_text,
                "catalog_signature": hashlib.sha256(
                    signature({k: v for k, v in exercise.items() if k != "settings"}, model.strings).encode(),
                ).hexdigest(),
                "icon": icons[exercise["icon"]] if "icon" in exercise else "",
                "controls": controls,
                "spec": deepcopy(exercise),
                "pack_instrument": model,
                "span": span,
                "range_clef": "" if keyboard else str(controls.get("range", "")),
                "key_span": key_span,
                "key_default": key_default,
                "interval_names": interval_names,
                "manual_names": manual_names,
                "has_sound": any(c.fingerboard or (c.picture and (c.picture.note or c.picture.notes)) for c in cards),
                "instruments": instruments,
                "_asset_cache": files.cache,
            },
        )
    lessons = read_lessons(
        data.get("lessons"),
        pack_id=pack_id,
        pack_name=data["name"],
        instruments=instruments,
        exercises=exercise_keys,
        icons=icons,
    )
    lessons = _link_exercises_to_lessons(exercises, lessons=lessons, pack_id=pack_id, exercise_keys=exercise_keys)
    terms = read_terms(
        data.get("glossary"),
        pack_id=pack_id,
        pack_name=data["name"],
        instruments=instruments,
        exercises=exercise_keys,
        lessons={lesson.key.removeprefix(f"pack.{pack_id}."): lesson.key for lesson in lessons},
    )
    for cls in classes.values():
        cls.lessons = lessons
        cls.terms = terms
    return list(classes.values())


def _icon_names(data: dict) -> list[str]:
    """
    List the icon files that a manifest's exercises and lessons name, each once.

    Parameters
    ----------
    data : dict
        The parsed manifest.

    Returns
    -------
    list of str
        The file names, in the order they appear.

    Raises
    ------
    ValueError
        If an icon is not a file name.

    Examples
    --------
    >>> _icon_names({"exercises": [{"icon": "a.svg"}], "lessons": [{"icon": "a.svg"}, {"icon": "b.svg"}]})
    ['a.svg', 'b.svg']
    """
    names: list[str] = []
    for field in ("exercises", "lessons"):
        rows = data.get(field)
        for row in rows if isinstance(rows, list) else ():
            if isinstance(row, dict) and "icon" in row:
                if not isinstance(row["icon"], str):
                    raise ValueError("Set each icon to the path of an SVG file in the plugin.")
                if row["icon"] not in names:
                    names.append(row["icon"])
    return names


def _link_exercises_to_lessons(
    rows: list,
    *,
    lessons: tuple[Lesson, ...],
    pack_id: str,
    exercise_keys: dict[str, str],
) -> tuple[Lesson, ...]:
    """
    Let an exercise name its lessons, so each lesson also offers that exercise on its last page.

    A lesson already names its exercises. An exercise's ``lessons`` list is the same link written from the other end, and Alto
    shows both: the lesson's practice buttons, and the lesson buttons in the exercise's reference pane.

    Parameters
    ----------
    rows : list
        The manifest's exercises.
    lessons : tuple of Lesson
        The plugin's lessons.
    pack_id : str
        The plugin's id. Keyword-only.
    exercise_keys : dict of str to str
        The plugin's exercises, from manifest id to registered key. Keyword-only.

    Returns
    -------
    tuple of Lesson
        The lessons with the exercises that named them added to their related exercises.

    Raises
    ------
    ValueError
        If an exercise lists a lesson the plugin does not have.

    Examples
    --------
    >>> _link_exercises_to_lessons([], lessons=(), pack_id="demo", exercise_keys={})
    ()
    """
    by_key = {lesson.key: lesson for lesson in lessons}
    for row in rows:
        named = row.get("lessons", [])
        if not isinstance(named, list) or len(named) > 5 or len(set(map(str, named))) != len(named):
            raise ValueError("List up to five distinct lessons for each exercise.")
        key = exercise_keys[row["id"]]
        for item in named:
            lesson_key = f"pack.{pack_id}.{item}" if isinstance(item, str) else ""
            lesson = by_key.get(lesson_key)
            if lesson is None:
                raise ValueError(f"The exercise {key} lists a lesson this plugin does not have: {item!r}.")
            if key != lesson.exercise and key not in lesson.related_exercises:
                by_key[lesson_key] = replace(lesson, related_exercises=(*lesson.related_exercises, key))
    return tuple(by_key[lesson.key] for lesson in lessons)


def pack_manifests(folder: Path) -> tuple[list[Path], list[str]]:
    """
    Find each installed ZIP or folder manifest, including packs that failed validation.

    Parameters
    ----------
    folder : Path
        The plugins directory.

    Returns
    -------
    tuple of list of Path and list of str
        ZIP files and pack.json files in discovery order, and any discovery errors.

    Examples
    --------
    An author can install either viola.zip or viola/pack.json.
    """
    try:
        entries = sorted(folder.iterdir())
    except FileNotFoundError:
        return [], []
    except OSError as error:
        return [], [str(error)]
    manifests = []
    problems = []
    for entry in entries:
        try:
            path = entry if entry.is_file() and entry.suffix.lower() == ".zip" else entry / "pack.json"
            if path.is_file():
                manifests.append(path)
        except OSError as error:
            problems.append(f"{entry.name} — {error}")
    return manifests, problems


def installed_pack_info(path: Path) -> dict:
    """
    Read a pack's manifest for display or duplicate detection without loading its media.

    Parameters
    ----------
    path : Path
        An installed ZIP or an editable pack.json.

    Returns
    -------
    dict
        The manifest, or an empty dictionary for an invalid manifest or archive.

    Examples
    --------
    A damaged pack can still be listed for removal by filename.
    """
    try:
        with ZipFile(path) if path.suffix.lower() == ".zip" else nullcontext(None) as archive:
            return PackFiles(path, archive=archive).manifest()
    except (ValueError, BadZipFile, RuntimeError, OverflowError, ZlibError, EOFError):
        return {}


@dataclass(frozen=True, kw_only=True)
class InstalledPlugin:
    """
    One pack in the plugins folder, as listed for removal.

    Attributes
    ----------
    title : str
        The pack's name, or its file name without the .zip extension when the manifest cannot be read.
    path : Path
        The ZIP file or editable pack folder that removal moves to the trash.
    manifest : Path
        The ZIP or the folder's pack.json.
    snapshot : stat_result
        The state of ``path`` when it was listed, used to notice a change before removal.

    Examples
    --------
    >>> from pathlib import Path
    >>> import os
    >>> plugin = InstalledPlugin(title="Viola", path=Path("viola.zip"), manifest=Path("viola.zip"), snapshot=os.stat("."))
    >>> plugin.title
    'Viola'
    """

    title: str
    path: Path
    manifest: Path
    snapshot: stat_result


def installed_plugins(folder: Path) -> tuple[list[InstalledPlugin], list[str]]:
    """
    List the packs in the plugins folder, including damaged ones, so each can be removed.

    Parameters
    ----------
    folder : Path
        The plugins directory.

    Returns
    -------
    tuple of list of InstalledPlugin and list of str
        The packs in discovery order, and any discovery errors.

    Examples
    --------
    >>> from pathlib import Path
    >>> installed_plugins(Path("no-such-plugins-folder"))
    ([], [])
    """
    manifests, problems = pack_manifests(folder)
    plugins = []
    for manifest in manifests:
        path = manifest if manifest.parent == folder else manifest.parent
        try:
            name = installed_pack_info(manifest).get("name")
        except OSError:
            name = None  # Allow removal even if the manifest cannot be opened.
        try:
            snapshot = path.lstat()
        except OSError as error:
            problems.append(f"{path.name} — {error}")
            continue
        plugins.append(
            InstalledPlugin(
                title=str(name) if name else path.stem if path.suffix.lower() == ".zip" else path.name,
                path=path,
                manifest=manifest,
                snapshot=snapshot,
            ),
        )
    return plugins, problems


def install_pack(
    source: Path,
    *,
    folder: Path,
    expected_id: str | None = None,
    replacing: InstalledPlugin | None = None,
) -> str:
    """
    Validate a copy of the selected ZIP and install it for the next startup.

    Parameters
    ----------
    source : Path
        The downloaded instrument pack ZIP.
    folder : Path
        The plugins directory used at startup.
    expected_id : str or None
        The manifest ID assigned to a registered download.
    replacing : InstalledPlugin or None
        The previously selected ZIP to replace after validation.

    Returns
    -------
    str
        The installed pack's display name.

    Raises
    ------
    ValueError
        If the ZIP is invalid or conflicts with an existing installation.
    OSError
        If the installation cannot be read or written.

    Examples
    --------
    Installing a downloaded viola.zip adds both of its exercises on the next launch.
    """
    if source.suffix.lower() != ".zip":
        raise ValueError("Choose an Alto instrument pack ZIP file.")
    folder.mkdir(parents=True, exist_ok=True)
    destination = replacing.path if replacing else folder / source.name
    with TemporaryDirectory(dir=folder) as staging:
        staged = Path(staging) / "pack.zip"
        shutil.copyfile(source, staged)
        try:
            pack = read_pack(staged)[0]
        except (BadZipFile, RuntimeError, OverflowError, ZlibError, EOFError) as error:
            raise ValueError(f"Could not read the pack ZIP: {error}") from error
        if expected_id is not None and pack.pack_id != expected_id:
            raise ValueError(f"The downloaded pack ID {pack.pack_id!r} does not match the registered ID {expected_id!r}.")
        lock = QLockFile(str(folder / ".install.lock"))
        if not lock.tryLock(0):
            raise OSError("Could not lock the plugins folder for installation. Try again.")
        try:
            manifests, problems = pack_manifests(folder)
            if problems:
                raise OSError("\n".join(problems))
            if replacing is not None:
                if destination.parent != folder or destination != replacing.manifest or destination.is_symlink():
                    raise ValueError("Only an installed plugin ZIP can be updated.")
                current = destination.lstat()
                if (
                    not samestat(current, replacing.snapshot)
                    or current.st_mtime_ns != replacing.snapshot.st_mtime_ns
                    or current.st_size != replacing.snapshot.st_size
                    or installed_pack_info(destination).get("id") != pack.pack_id
                ):
                    raise ValueError("The installed plugin changed. Select it again to update.")
            for path in manifests:
                if replacing is not None and path == destination:
                    continue
                if installed_pack_info(path).get("id") == pack.pack_id:
                    raise ValueError(f'The pack "{pack.pack_id}" is already installed as {path.relative_to(folder)}.')
            if replacing is not None:
                staged.replace(destination)
                return pack.pack_name
            if destination.exists() or destination.is_symlink():
                raise ValueError(f"{source.name} is already in the plugins folder. Choose a different ZIP filename.")
            archive_file = QFile(str(staged))
            if not archive_file.rename(str(destination)):
                raise OSError(archive_file.errorString())
        finally:
            lock.unlock()
    return pack.pack_name


def load_packs(folder: Path) -> list[str]:
    """
    Register valid packs and return readable errors for any packs that were skipped.

    Parameters
    ----------
    folder : Path
        The plugins folder containing pack ZIPs or editable pack folders.

    Returns
    -------
    list of str
        File names and reasons for packs that could not be loaded.

    Examples
    --------
    A missing plugins folder yields an empty list.
    """
    manifests, problems = pack_manifests(folder)
    known = {cls.pack_id for cls in REGISTRY if issubclass(cls, PackExercise)}
    for path in manifests:
        label = path.relative_to(folder).as_posix()
        try:
            classes = read_pack(path)
            pack_id = classes[0].pack_id
            if pack_id in known:
                problems.append(f'{label} — Another pack already uses the id "{pack_id}".')
                continue
            taken = next((term.name for term in classes[0].terms if term.name in PLUGIN_TERMS), None)
            if taken is not None:
                problems.append(f"{label} — The glossary term {taken!r} is already supplied by {PLUGIN_TERMS[taken].pack}.")
                continue
        except (ValueError, OSError, BadZipFile, RuntimeError, OverflowError, ZlibError) as error:
            problems.append(f"{label} — {error}")
            continue
        known.add(pack_id)
        for model in classes[0].instruments.values():
            INSTALLED[model.key] = model
            if model.sound is not None:
                INSTRUMENT_BY_KEY[model.key] = model.sound
        for cls in classes:
            register(cls)
        for lesson in classes[0].lessons:
            register_lesson(lesson)
        for term in classes[0].terms:
            register_term(term)
    return problems
