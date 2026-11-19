"""
Exercise framework. Register a ChoiceExercise for button answers or an Exercise for construction tasks.

An `Exercise` makes `Question` objects. The `Question` says what to show (a staff, a keyboard or only text), which
buttons to offer and which answer is right. The exercise screen and the scheduler work with those two classes only, so
a new exercise needs no new interface code.

Examples
--------
>>> question = Question("Name this note.", choices=["C", "D", "E"], answer="D")
>>> question.check("D"), question.check("E")
(True, False)
"""

from __future__ import annotations

import hashlib
import json
import random
from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Iterator
from dataclasses import (
    KW_ONLY,
    asdict,
    dataclass,
    field,
    is_dataclass,
    replace,
)
from functools import cache
from typing import Any

from alto.theory.pitch import Note


@dataclass
class Question:
    """
    One question, with what to show for it and which answer is right.

    Attributes
    ----------
    prompt : str
        The text shown above the question; may be empty.
    choices : list of str
        The answer buttons, in the order they should be offered. Keyword-only.
    answer : str
        The right answer, one of `choices` (or the note name for a "place this note" question). Keyword-only.
    staff : list of list of Note
        What to draw on the staff: each inner list is one chord or note. Keyword-only.
    clef : str, default "treble"
        The clef to draw on. Keyword-only.
    explanation : str, default ""
        Text shown after the answer to say why it is right. Keyword-only.
    key : int, default 0
        The key signature to draw: that many sharps if positive, flats if negative. Keyword-only.
    value : str, default "whole"
        The written duration for single notes and interval voices. Keyword-only.
    staff_signature : int or None
        Override the signature shown on the staff while retaining the key for scale degrees. Keyword-only.
    minor : bool, default False
        Use the signature's relative minor for scale degree naming. Keyword-only.
    grid : dict of str to tuple of (int, int) or None
        Where to put each answer button, as (row, column). Without it the choices form one row. Keyword-only.
    keyboard : Note or None
        A piano key to highlight, instead of drawing a staff. Keyword-only.
    keyboard_notes : list of Note
        Multiple piano keys to highlight together instead of drawing a staff. Keyword-only.
    key_staff : bool, default False
        Draw `key` as a small key-signature staff above the keyboard. Keyword-only.
    keyboard_range : tuple of (int, int) or None
        The keys (MIDI numbers, inclusive) the keyboard picture should show. Keyword-only.
    octaves : list of str or None
        When set, the answer is a choice button plus one of these second-row buttons. Keyword-only.
    second_label : str, default "Octave"
        What the second row of buttons is called. Keyword-only.
    joiner : str, default ""
        Put between the two parts to make the answer ("" for a note and its octave: C + 4 gives C4). Keyword-only.
    construct : Note or None
        The note to place on the staff: the answer is a position, not a button. Keyword-only.
    accidentals : bool, default False
        Show the sharp, natural and flat buttons for a construct question. Keyword-only.
    accept : tuple of str
        Other answers that count as right, such as the enharmonic name of a black key. Keyword-only.
    show_staff : bool, default False
        Draw the staff even with no notes on it, to show only its clef and key signature. Keyword-only.
    caption : str, default ""
        Text written on the staff itself, under the music, in place of the prompt above it. Keyword-only.
    build_key : bool, default False
        The learner builds the key signature `key` on a blank staff with the fork widget, instead of pressing a button.
        Keyword-only.
    place_signature : bool, default False
        Place each accidental of the named key on the staff. Keyword-only.
    starting_slots : list of int
        Zero-based positions of the accidentals already printed in an Order of Keys question.
    construct_scale : list of Note or None
        The notes of a scale to place on the staff one after another, left to right: the answer is the whole row.
        Keyword-only.
    construct_steps : list of str or None
        The steps between the notes of `construct_scale`, each "W" (whole) or "H" (half), to mark once the notes are placed;
        None if the steps are not asked. Keyword-only.
    notes_only : bool, default False
        Show note names without a scale degree context. Keyword-only.
    any_octave : bool, default False
        Accept a single constructed note with the right spelling in any octave. Keyword-only.
    exact_octave : bool, default False
        The scale has to be placed in the octave asked, not in any octave. Keyword-only.
    circle : int or None
        A question on the circle of fifths: the place asked about, clockwise from C at 0. Keyword-only.
    circle_kind : str, default ""
        What the circle asks: "major" (the relative major of a minor key), "minor" (the relative minor of a major key) or
        "numeral" (the Roman numeral of a chord of a key). Keyword-only.
    circle_ring : str, default "outer"
        Which ring the cell asked about is in: "outer" for the major keys or "inner" for the minor ones. Keyword-only.
    circle_key : int or None
        For a Roman numeral question, the place of the key whose chords they are. Keyword-only.
    required : tuple of str
        Answers that must all be given, one after another in any order, such as both names of a key with two: B and C♭.
        Empty for an ordinary question with one answer. Keyword-only.
    notation_target : tuple of (str, int) or None
        Notation part and zero-based note column or staff line to highlight. Keyword-only.
    notation_excerpt : str or None
        Versioned score containing the target. Its position is an index into the excerpt manifest. Keyword-only.
    place_clef : str, default ""
        The clef to put on a blank staff: the answer is a clef symbol (G, C or F) and a place on the staff, not a button.
        Empty for any other question. Keyword-only.

    Examples
    --------
    >>> q = Question("Which note is this?", choices=["C", "D", "E"], answer="D", staff=[[Note.parse("D4")]])
    >>> q.check("D")
    True
    >>> Question.from_dict(q.to_dict()) == q  # a question can be stored and asked again
    True
    """

    prompt: str
    _: KW_ONLY
    choices: list[str]
    answer: str
    # What to draw on the staff: each inner list is one simultaneous chord/note.
    staff: list[list[Note]] = field(default_factory=list)
    clef: str = "treble"
    explanation: str = ""
    key: int = 0  # key signature to draw: sharps (+) / flats (-)
    staff_signature: int | None = None
    minor: bool = False  # interpret the signature as a natural minor key for scale degrees
    value: str = "whole"  # written duration for single notes and interval voices
    # Optional button placement: choice -> (row, column). Without it the choices form one row.
    grid: dict[str, tuple[int, int]] | None = None
    keyboard: Note | None = None  # a piano key to highlight, instead of drawing a staff
    keyboard_notes: list[Note] = field(default_factory=list)
    key_staff: bool = False  # draw `key` as a small key-signature staff above the keyboard
    keyboard_range: tuple[int, int] | None = None  # the keys (MIDI, inclusive) the keyboard picture should show
    octaves: list[str] | None = None  # when set, the answer is a choice button plus one of these second-row buttons
    second_label: str = "Octave"  # what the second row of buttons is called
    joiner: str = ""  # put between the two parts to make the answer ("" for a note and its octave: C + 4 -> C4)
    construct: Note | None = None  # the note to place on the staff: the answer is a position, not a button
    accidentals: bool = False  # show the sharp / flat / natural buttons for a construct question
    accept: tuple[str, ...] = ()  # other answers that count as correct (e.g. the enharmonic name of a black key)
    show_staff: bool = False  # draw the staff even with no notes on it, to show only its clef and key signature
    caption: str = ""  # text written on the staff itself, under the music, in place of the prompt above it
    build_key: bool = False  # the learner builds the key signature `key` with the fork, on a staff that starts blank
    place_signature: bool = False
    starting_slots: list[int] = field(default_factory=list)
    construct_scale: list[Note] | None = None  # the notes of a scale to place on the staff, left to right
    construct_steps: list[str] | None = None  # the whole ("W") and half ("H") steps between them, if those are asked too
    notes_only: bool = False
    any_octave: bool = False
    exact_octave: bool = False  # the scale must be in the octave of `construct_scale`, not in any octave
    circle: int | None = None  # a question on the circle of fifths: the place asked about, clockwise from C at 0
    circle_kind: str = ""  # "major", "minor" or "numeral": what the circle asks
    circle_ring: str = "outer"  # the ring of the cell asked about: "outer" (majors) or "inner" (minors)
    circle_key: int | None = None  # for a numeral question, the place of the key whose chords they are
    required: tuple[str, ...] = ()  # answers that must all be given, in any order, such as both names of an enharmonic key
    place_clef: str = ""  # the clef to put on a blank staff, as a G, C or F symbol in the right place

    notation_target: tuple[str, int] | None = None
    notation_excerpt: str | None = None

    def check_placed(self, note: Note) -> bool:
        """
        Report whether a note placed on the staff is the one asked for.

        The spelling must match exactly. The octave must also match unless `any_octave` is set.

        Parameters
        ----------
        note : Note
            The note the learner placed.

        Returns
        -------
        bool
            True if it matches the requested note spelling and any required octave.

        Examples
        --------
        >>> q = Question("Place C4", choices=[], answer="C4", construct=Note.parse("C4"))
        >>> q.check_placed(Note.parse("C4"))
        True
        >>> q.check_placed(Note.parse("B#3"))  # sounds the same, but is spelled differently
        False
        """
        if self.any_octave and self.construct is not None:
            return note.name == self.construct.name
        return note == self.construct

    def check_scale(self, notes: list[Note]) -> bool:
        """
        Report whether the notes placed on the staff are the scale asked for.

        The spelling and the order of the notes must match, so a G♯ is not an A♭. Unless `exact_octave` is set the octave
        does not matter, as long as the whole scale is in the same one: the same scale an octave higher or lower is right,
        but a scale with one note in the wrong octave is not. With `exact_octave` the scale has to be in the octave asked.

        Parameters
        ----------
        notes : list of Note
            The notes the learner placed, left to right.

        Returns
        -------
        bool
            True if they are the notes of `construct_scale`, all moved by the same whole number of octaves (or, with
            `exact_octave`, not moved at all).

        Examples
        --------
        >>> asked = [Note.parse("C4"), Note.parse("D4")]
        >>> q = Question("Place C D.", choices=[], answer="C4 D4", construct_scale=asked)
        >>> q.check_scale([Note.parse("C4"), Note.parse("D4")])
        True
        >>> q.check_scale([Note.parse("C5"), Note.parse("D5")])  # the same scale, an octave higher
        True
        >>> q.check_scale([Note.parse("C4"), Note.parse("D5")])  # one note in another octave
        False
        >>> q.check_scale([Note.parse("C4"), Note.parse("D4"), Note.parse("E4")])
        False
        >>> exact = Question("Place C D.", choices=[], answer="C4 D4", construct_scale=asked, exact_octave=True)
        >>> exact.check_scale([Note.parse("C4"), Note.parse("D4")]), exact.check_scale([Note.parse("C5"), Note.parse("D5")])
        (True, False)
        """
        scale = self.construct_scale
        if scale is None or len(notes) != len(scale):
            return False
        if any(a.letter != b.letter or a.accidental != b.accidental for a, b in zip(notes, scale, strict=True)):
            return False
        shifts = {a.octave - b.octave for a, b in zip(notes, scale, strict=True)}
        return shifts == {0} if self.exact_octave else len(shifts) == 1

    def check_steps(self, steps: list[str]) -> bool:
        """
        Report whether the steps marked between the notes of a scale are the right ones.

        Parameters
        ----------
        steps : list of str
            The steps the learner marked, left to right, each "W" or "H".

        Returns
        -------
        bool
            True if the steps are not asked, or if they are those of `construct_steps`.

        Examples
        --------
        >>> q = Question("Mark the steps.", choices=[], answer="W H", construct_steps=["W", "H"])
        >>> q.check_steps(["W", "H"]), q.check_steps(["H", "W"]), q.check_steps(["W"])
        (True, False, False)
        >>> Question("No steps.", choices=[], answer="").check_steps([])
        True
        """
        return self.construct_steps is None or steps == self.construct_steps

    def check_built(self, count: int) -> bool:
        """
        Report whether a key signature built with the fork is the one asked for.

        Parameters
        ----------
        count : int
            The signature the learner built: that many sharps if positive, flats if negative.

        Returns
        -------
        bool
            True if it equals `key`.

        Examples
        --------
        >>> q = Question("Build D major.", choices=[], answer="2 sharps", key=2, show_staff=True, build_key=True)
        >>> q.check_built(2), q.check_built(-2)
        (True, False)
        """
        return count == self.key

    @property
    def places_sequence(self) -> bool:
        """
        Report whether the learner enters successive positions on the staff.

        Returns
        -------
        bool
            True for scales and handwritten key signatures.

        Examples
        --------
        >>> Question("D major", choices=[], answer="F♯5 C♯5", place_signature=True).places_sequence
        True
        """
        return self.construct_scale is not None or self.place_signature

    def check(self, choice: str) -> bool:
        """
        Report whether a chosen answer is right.

        Parameters
        ----------
        choice : str
            The text of the button that was pressed.

        Returns
        -------
        bool
            True if it is the answer or one of the other accepted answers.

        Examples
        --------
        >>> q = Question("", choices=["F♯", "G♭"], answer="F♯", accept=("G♭",))
        >>> q.check("F♯"), q.check("G♭"), q.check("A")
        (True, True, False)
        >>> both = Question("", choices=["B", "C♭", "D"], answer="B", required=("B", "C♭"))
        >>> both.check("B"), both.check("C♭"), both.check("D")  # each is right, but both are needed: see `complete`
        (True, True, False)
        """
        return choice == self.answer or choice in self.accept or choice in self.required

    def complete(self, given: set[str]) -> bool:
        """
        Report whether the answers given so far are all of those needed.

        Parameters
        ----------
        given : set of str
            The right answers given so far.

        Returns
        -------
        bool
            For an ordinary question, whether the answer has been given; for one with several `required`, whether all have.

        Examples
        --------
        >>> both = Question("", choices=["B", "C♭"], answer="B", required=("B", "C♭"))
        >>> both.complete({"B"}), both.complete({"C♭", "B"})
        (False, True)
        >>> Question("", choices=["C"], answer="C").complete({"C"})
        True
        """
        return set(self.required) <= given if self.required else any(self.check(g) for g in given)

    def item_key(self) -> str:
        """
        Return a stable identity for the question, so the same one can be recognized when it comes around again.

        It covers what is asked and where it is drawn, but not the note value or the order of the buttons.

        Returns
        -------
        str
            A 20-character hexadecimal string.

        Examples
        --------
        >>> a = Question("Name it.", choices=["C", "D"], answer="C")
        >>> b = Question("Name it.", choices=["D", "C"], answer="C")  # the same question, buttons in another order
        >>> a.item_key() == b.item_key()
        True
        >>> len(a.item_key())
        20
        """

        def spelled(n: Note | None) -> list[int] | None:
            """
            Describe a note in a form that can be written as JSON.

            Parameters
            ----------
            n : Note or None
                The note, or None for no note.

            Returns
            -------
            list of int or None
                `[octave, letter, accidental]`, or None if there was no note.

            Examples
            --------
            >>> on_keyboard = Question("Press it.", choices=["C"], answer="C", keyboard=Note.parse("C4"))
            >>> on_keyboard.item_key() == Question("Press it.", choices=["C"], answer="C").item_key()  # the key is part of it
            False
            """
            return None if n is None else [n.octave, n.letter, n.accidental]

        data: list[object] = [
            self.prompt,
            self.answer,
            self.clef,
            [[spelled(n) for n in col] for col in self.staff],
            self.key,
            spelled(self.keyboard),
            spelled(self.construct),
        ]
        if self.notation_target is not None:
            data.append(self.notation_target)
        if self.notation_excerpt is not None:
            data.append(self.notation_excerpt)
        if self.keyboard_notes:
            data.append([spelled(n) for n in self.keyboard_notes])
        if self.notes_only:
            data.append("notes only")
        if self.any_octave:
            data.append("any octave")
        if self.staff_signature is not None:
            data.append(["staff signature", self.staff_signature])
        if self.minor:
            data.append("minor")
        if self.starting_slots:
            data.append(["starting slots", self.starting_slots])
        return hashlib.sha1(json.dumps(data).encode()).hexdigest()[:20]

    def to_dict(self) -> dict:
        """
        Return the question as plain data, so it can be stored and asked again.

        Returns
        -------
        dict
            The fields of the question, with notes as dictionaries and tuples as lists.

        Examples
        --------
        >>> data = Question("Name it.", choices=["C"], answer="C", staff=[[Note.parse("C4")]]).to_dict()
        >>> data["answer"], data["staff"]
        ('C', [[{'octave': 4, 'letter': 0, 'accidental': 0}]])
        """
        d = asdict(self)
        d["grid"] = None if self.grid is None else {k: list(v) for k, v in self.grid.items()}
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Question:
        """
        Rebuild a question from the data that `to_dict` made.

        Parameters
        ----------
        d : dict
            The stored data. Questions saved by older versions, which may carry a `play` field, are accepted.

        Returns
        -------
        Question
            The question.

        Examples
        --------
        >>> q = Question("Name it.", choices=["C", "D"], answer="C", key=2, accept=("D",))
        >>> Question.from_dict(q.to_dict()) == q
        True
        """
        d = dict(d)
        if d.get("notation_target") is not None:
            d["notation_target"] = tuple(d["notation_target"])
        if d.pop("staff_key_hidden", False):
            d.setdefault("staff_signature", 0)
        d["staff"] = [[Note(**n) for n in col] for col in d.get("staff", [])]
        d["keyboard_notes"] = [Note(**n) for n in d.get("keyboard_notes", [])]
        d.pop("play", None)  # questions stored by an older version carried the notes of a scale to play
        d["keyboard"], d["construct"] = note_from(d.get("keyboard")), note_from(d.get("construct"))
        if d.get("construct_scale") is not None:
            d["construct_scale"] = [Note(**n) for n in d["construct_scale"]]
        if d.get("grid") is not None:
            d["grid"] = {k: tuple(v) for k, v in d["grid"].items()}
        if d.get("keyboard_range") is not None:
            d["keyboard_range"] = tuple(d["keyboard_range"])
        d["accept"] = tuple(d.get("accept", ()))
        d["required"] = tuple(d.get("required", ()))
        return cls(**d)


def note_from(v: dict | None) -> Note | None:
    """
    Rebuild a note from stored data.

    Parameters
    ----------
    v : dict or None
        A note as the dictionary `to_dict` stores, or None.

    Returns
    -------
    Note or None
        The note, or None if `v` was None.

    Examples
    --------
    >>> note_from({"octave": 4, "letter": 0, "accidental": 0})
    Note(octave=4, letter=0, accidental=0)
    >>> note_from(None) is None
    True
    """
    return None if v is None else Note(**v)


def signature(*parts: object) -> str:
    """
    Describe the exercise settings in force, so a stored question is only asked again under the settings it was made for.

    Parameters
    ----------
    *parts : object
        The settings to describe: dataclasses, dictionaries, lists, sets and plain values, nested as needed.

    Returns
    -------
    str
        A JSON string that is the same for equal settings, however their sets and dictionaries happen to be ordered.

    Examples
    --------
    >>> signature({"clefs": {"bass", "treble"}}, 3)
    '[{"clefs": ["bass", "treble"]}, 3]'
    >>> signature({"clefs": {"treble", "bass"}}, 3) == signature({"clefs": {"bass", "treble"}}, 3)
    True
    """

    def plain(o: Any) -> Any:  # noqa: ANN401  (settings are nested dicts, lists, sets and dataclasses of any content)
        """
        Turn settings into plain, ordered data that JSON can write.

        Parameters
        ----------
        o : Any
            A dataclass, dictionary, set, list, tuple or plain value.

        Returns
        -------
        Any
            Dataclasses become dictionaries, dictionary keys become strings, and sets become sorted lists.

        Examples
        --------
        >>> signature({3, 1, 2})  # a set is written as a sorted list
        '[[1, 2, 3]]'
        """
        if is_dataclass(o) and not isinstance(o, type):
            return plain(asdict(o))
        if isinstance(o, dict):
            return {str(k): plain(v) for k, v in o.items()}
        if isinstance(o, (set, frozenset)):
            return sorted(plain(x) for x in o)
        if isinstance(o, (list, tuple)):
            return [plain(x) for x in o]
        return o

    return json.dumps(plain(parts), sort_keys=True)


class Exercise(ABC):
    """
    What every exercise provides: its name, how it makes questions and how long a good answer takes.

    Attributes
    ----------
    name : str
        The title shown on the home screen and in the exercise list.
    category : str
        The heading it is listed under.
    description : str
        One line saying what the exercise is for.
    par_seconds : float, default 5.0
        How long a good first answer takes; much quicker earns credit and much slower counts against the question.
    has_sound : bool, default True
        False for an exercise that makes no sound at all, whatever the sound button says.

    Examples
    --------
    >>> class Demo(Exercise):
    ...     name = "Demo"
    ...     def generate(self, rng):
    ...         return Question("Pick A.", choices=["A", "B"], answer="A")
    >>> Demo().generate(random.Random(0)).answer
    'A'
    """

    name: str = ""
    category: str = ""
    description: str = ""
    par_seconds: float = 5.0  # how long a good first answer takes; much quicker earns credit, much slower counts against
    has_sound: bool = True  # False for an exercise that makes no sound at all, whatever the sound button says

    def settings_signature(self) -> str:
        """
        Return what identifies the settings that shape the questions.

        A stored question is only asked again while this is unchanged. Exercises with settings override it.

        Returns
        -------
        str
            An identifier; empty for an exercise with no settings.

        Examples
        --------
        >>> class Demo(Exercise):
        ...     def generate(self, rng):
        ...         return Question("?", choices=["A"], answer="A")
        >>> Demo().settings_signature()
        ''
        """
        return ""

    def card_groups(self) -> dict[str, str] | None:
        """
        Map playable examples to the skills that share a calendar review date.

        Returns
        -------
        dict of str to str or None
            Example item keys mapped to skill names, or None when every example has its own schedule.

        Examples
        --------
        >>> from alto.exercises.library import KeyboardNotes
        >>> KeyboardNotes().card_groups() is None
        True
        """
        return None

    def card_count(self) -> int | None:
        """
        Count distinct cards possible with the current settings when the exercise has an exact catalog.

        Returns
        -------
        int or None
            Catalog size, or None for an exercise that prepares a bounded daily sample.

        Examples
        --------
        >>> from alto.exercises.library import KeyboardNotes
        >>> KeyboardNotes().card_count() is None
        True
        """
        groups = self.card_groups()
        return len(set(groups.values())) if groups is not None else None

    def daily_candidates(self, rng: random.Random) -> Iterator[Question]:
        """
        Yield distinct questions until 100 consecutive draws find no new playable item.

        Parameters
        ----------
        rng : random.Random
            The generator for this day's sample.

        Yields
        ------
        Question
            A playable question. Finite exercises can override this to visit every eligible item.

        Examples
        --------
        >>> from alto.exercises.library import KeyboardNotes
        >>> isinstance(next(KeyboardNotes().daily_candidates(random.Random(1))), Question)
        True
        """
        seen: set[str] = set()
        misses = 0
        while misses < 100:
            question = self.generate(rng)
            key = question.item_key()
            if question.answer and key not in seen:
                seen.add(key)
                misses = 0
                yield question
            else:
                misses += 1

    def review_question(self, question: Question, *, same_settings: bool) -> Question | None:
        """
        Adapt a stored question for review under the active settings.

        Parameters
        ----------
        question : Question
            Previously introduced card.
        same_settings : bool
            Whether the saved presentation matches the active settings.

        Returns
        -------
        Question or None
            A playable question when the exercise recognizes this presentation.

        Examples
        --------
        >>> from alto.exercises.library import KeyboardNotes
        >>> ex = KeyboardNotes()
        >>> q = ex.generate(random.Random(1))
        >>> ex.review_question(q, same_settings=True) == q
        True
        """
        return self.refresh(question) if same_settings else None

    def refresh(self, question: Question) -> Question:
        """
        Bring a stored question up to date with how the exercise draws its questions now.

        A question that is asked again comes from the copy stored when it was first asked, which an older version may
        have drawn differently. The default leaves it as it is.

        Parameters
        ----------
        question : Question
            The question as it was stored.

        Returns
        -------
        Question
            The question as the exercise would draw it today.

        Examples
        --------
        >>> class Demo(Exercise):
        ...     def generate(self, rng):
        ...         return Question("?", choices=["A"], answer="A")
        >>> q = Question("?", choices=["A"], answer="A")
        >>> Demo().refresh(q) is q
        True
        """
        return question

    def instructions(self) -> str:
        """
        Return the help text shown from the exercise's help button.

        Exercises override it to describe themselves.

        Returns
        -------
        str
            Simple HTML; by default the one-line description.

        Examples
        --------
        >>> class Demo(Exercise):
        ...     description = "Spot the note."
        ...     def generate(self, rng):
        ...         return Question("?", choices=["A"], answer="A")
        >>> Demo().instructions()
        'Spot the note.'
        """
        return self.description

    @abstractmethod
    def generate(self, rng: random.Random) -> Question:
        """
        Make one new question.

        Parameters
        ----------
        rng : random.Random
            The random number generator to use, so tests can ask for a repeatable question.

        Returns
        -------
        Question
            The question.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> q = NoteNames().generate(random.Random(1))
        >>> q.answer in q.choices
        True
        """
        ...


@dataclass
class ButtonSettings:
    """
    An exercise’s choice of answer layout and maximum number of buttons per group.

    Examples
    --------
    >>> ButtonSettings().button_mode
    'all'
    """

    button_mode: str = "all"
    button_count: int = 6


class ChoiceExercise(Exercise):
    """
    A button-answer exercise with its own standard Buttons submenu.

    Supply the eligible choices in `make_question`. Set `default_limit` to start in Limited mode.

    Examples
    --------
    >>> from alto.exercises.library import ChordQualities
    >>> ChordQualities.button_settings().button_mode
    'limited'
    """

    default_limit: int | None = None

    @classmethod
    @cache
    def button_settings(cls) -> ButtonSettings:
        """
        Return the preferences shared by instances of this particular exercise.

        Returns
        -------
        ButtonSettings
            The exercise's answer layout.

        Examples
        --------
        >>> from alto.exercises.library import NoteNames
        >>> NoteNames.button_settings().button_mode
        'all'
        """
        return ButtonSettings("limited" if cls.default_limit else "all", cls.default_limit or 6)

    def settings_signature(self) -> str:
        """
        Include custom answer layouts when deciding which questions can be replayed.

        Returns
        -------
        str
            The original practice signature at the historical default, or a layout-specific signature.

        Examples
        --------
        >>> from alto.exercises.library import ChordQualities
        >>> ChordQualities().settings_signature()
        ''
        """
        original = self.practice_signature()
        cfg = self.button_settings()
        limit = cfg.button_count if cfg.button_mode == "limited" else None
        return original if limit == self.default_limit else signature(original, limit)

    def practice_signature(self) -> str:
        """
        Identify the exercise settings other than the answer layout.

        Returns
        -------
        str
            The signature for questions using the default layout.

        Examples
        --------
        >>> from alto.exercises.library import ChordQualities
        >>> ChordQualities().practice_signature()
        ''
        """
        return ""

    def generate(self, rng: random.Random) -> Question:
        """
        Generate the musical task and apply the selected button count.

        Parameters
        ----------
        rng : random.Random
            Source for the exercise and the distractor sample.

        Returns
        -------
        Question
            A question with its answer buttons ready for practice.

        Examples
        --------
        >>> from alto.exercises.library import ChordQualities
        >>> len(ChordQualities().generate(random.Random(0)).choices)
        5
        """
        return self.limit_buttons(self.make_question(rng), rng=rng)

    def limit_buttons(self, question: Question, *, rng: random.Random) -> Question:
        """
        Limit each answer group while keeping all the buttons needed to complete the question.

        Parameters
        ----------
        question : Question
            The task and its eligible answer choices.
        rng : random.Random
            Source for sampling distractors.

        Returns
        -------
        Question
            The question with its chosen layout.

        Examples
        --------
        A note and octave question keeps the correct name and octave in their respective groups.
        """
        cfg = self.button_settings()
        if cfg.button_mode == "all" or max(len(question.choices), len(question.octaves or ())) <= cfg.button_count:
            return question
        answers = {question.answer, *question.required, *question.accept}
        first, second = answers, set()
        if question.octaves:
            pairs = [(a, b) for a in question.choices for b in question.octaves if a + question.joiner + b in answers]
            first = {a for a, _ in pairs}
            second = {b for _, b in pairs}

        def sample(options: list[str], *, keep: set[str]) -> list[str]:
            """
            Fill the remaining slots with distinct distractors in their original display order.

            Parameters
            ----------
            options : list of str
                Eligible labels for this group.
            keep : set of str
                Correct labels in the group.

            Returns
            -------
            list of str
                Selected labels.

            Examples
            --------
            A relative-key question keeps both required enharmonic spellings.
            """
            if len(options) <= cfg.button_count:
                return options
            others = [label for label in options if label not in keep]
            keep = keep.intersection(options)
            keep.update(rng.sample(others, max(0, cfg.button_count - len(keep))))
            return [label for label in options if label in keep]

        choices = sample(question.choices, keep=first)
        octaves = sample(question.octaves, keep=second) if question.octaves else None
        return replace(question, choices=choices, octaves=octaves, grid=None if choices != question.choices else question.grid)

    @abstractmethod
    def make_question(self, rng: random.Random) -> Question:
        """
        Generate the task and eligible answer choices before the button limit is applied.

        Parameters
        ----------
        rng : random.Random
            The exercise's random source.

        Returns
        -------
        Question
            The musical task.

        Examples
        --------
        Note Identification supplies the note names appropriate to the active clef and key settings.
        """
        ...


REGISTRY: list[type[Exercise]] = []


def register(cls: type[Exercise]) -> type[Exercise]:
    """
    Add an exercise to `REGISTRY`, next to the others of its category.

    The categories come in the order they first appear, so the home screen and the exercise list can show each category
    once, with all its exercises under it. Used as a class decorator.

    Parameters
    ----------
    cls : type of Exercise
        The exercise class.

    Returns
    -------
    type of Exercise
        The same class, so the decorator can be applied to a class definition.

    Examples
    --------
    >>> @register
    ... class Demo(Exercise):
    ...     name = "Demo"
    ...     category = "A category no other exercise has"
    ...     def generate(self, rng):
    ...         return Question("?", choices=["A"], answer="A")
    >>> REGISTRY[-1] is Demo
    True
    >>> REGISTRY.remove(Demo)
    """
    last = max((i for i, other in enumerate(REGISTRY) if other.category == cls.category), default=None)
    if last is None:
        REGISTRY.append(cls)
    else:
        REGISTRY.insert(last + 1, cls)
    return cls


def pick_distractors(
    correct: str,
    *,
    pool: list[str],
    n: int,
    rng: random.Random,
) -> list[str]:
    """
    Choose wrong answers to offer alongside the right one, and shuffle them all.

    Parameters
    ----------
    correct : str
        The right answer. It is always in the result.
    pool : list of str
        Where the wrong answers come from; repeats and the right answer are ignored. Keyword-only.
    n : int
        How many wrong answers to include (fewer if the pool has fewer). Keyword-only.
    rng : random.Random
        The random number generator used to choose and shuffle. Keyword-only.

    Returns
    -------
    list of str
        The right answer and up to `n` others, in a random order.

    Examples
    --------
    >>> choices_ = pick_distractors("C", pool=["C", "D", "E", "F"], n=2, rng=random.Random(0))
    >>> len(choices_), "C" in choices_
    (3, True)
    """
    others = [p for p in dict.fromkeys(pool) if p != correct]
    rng.shuffle(others)
    choices = others[:n] + [correct]
    rng.shuffle(choices)
    return choices
