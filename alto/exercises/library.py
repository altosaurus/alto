"""
The exercises: note names, intervals, key signatures, scales, chords,
arpeggios, keyboard keys and note construction.

Each class makes one kind of `Question` and registers itself with
`@register`, so importing this module is what adds
the exercises to the home screen.

Examples
--------
>>> from alto.exercises import REGISTRY
>>> [cls.name for cls in REGISTRY][:3]
['Note Identification', 'Keyboard Note Identification', 'Note
Construction']
"""

from __future__ import annotations

import random
from collections.abc import Iterator, Mapping
from copy import deepcopy
from dataclasses import asdict, replace
from functools import lru_cache
from itertools import accumulate
from types import MappingProxyType

from alto import settings
from alto.exercises.base import (
    ButtonSettings,
    ChoiceExercise,
    Exercise,
    Question,
    pick_distractors,
    register,
    signature,
)
from alto.exercises.rhythm_equations import (  # noqa: F401 (public rhythm helpers)
    counted_operands,
    equation_question,
    equation_tokens,
    number_question,
)
from alto.notation_excerpts import passages_by_term
from alto.notation_terms import CATALOG, MARKS, SIMILAR_MARKS
from alto.settings import spell
from alto.theory.fifths import (
    MAJORS,
    MINORS,
    NUMERALS,
    SIGNATURES,
    cells_of_key,
    display_major,
    display_minor,
    numeral_chords,
)
from alto.theory.key_signatures import written_signature
from alto.theory.pitch import (
    MAJOR_KEYS,
    NATURAL_LETTER_INDEX,
    NATURAL_SEMITONES,
    QUALITY_NAMES,
    Interval,
    Note,
    key_accidental,
)
from alto.theory.scales import (
    CHORDS,
    INVERSION_NAMES,
    MINOR_KEYS,
    MODE_WORDS,
    SCALES,
    arpeggio,
    build,
    format_key_signature,
    mode_tonic,
)

CLEF_RANGES = {  # inclusive diatonic range that sits comfortably on the staff
    "treble": (Note(3, letter=5), Note(5, letter=5)),  # A3..A5
    "bass": (Note(2, letter=0), Note(4, letter=0)),  # C2..C4
}


def _random_note(
    rng: random.Random,
    *,
    clef: str,
    accidentals: bool,
    span: tuple[int, int] | None = None,
) -> Note:
    """
    Return a random note, optionally with an accidental.

    Parameters
    ----------
    rng : random.Random
        The random number generator.
    clef : str
        "treble" or "bass", which decides the default range.
        Keyword-only.
    accidentals : bool
        Give the note a random sharp, flat or natural; otherwise it is
        natural. Keyword-only.
    span : tuple of (int, int) or None, default None
        An inclusive range of staff steps (`Note.diatonic`); the clef's
        comfortable range if None. Keyword-only.

    Returns
    -------
    Note
        The note.

    Examples
    --------
    >>> str(
    ...     _random_note(
    ...         random.Random(1),
    ...         clef="treble",
    ...         accidentals=False,
    ...         span=(28, 28),
    ...     )
    ... )
    'C4'
    """
    lo, hi = span or (
        CLEF_RANGES[clef][0].diatonic,
        CLEF_RANGES[clef][1].diatonic,
    )
    d = rng.randint(lo, hi)
    return Note.from_diatonic(
        d,
        accidental=rng.choice((-1, 0, 1)) if accidentals else 0,
    )


def _degree_choices(
    pool: set[tuple[int, int]],
    *,
    key: int,
    naming: str = "degrees",
    minor: bool = False,
) -> tuple[list[str], dict[str, tuple[int, int]]]:
    """
    Arrange scale-degree answers by degree, with raised degrees above
    lowered degrees.

    Parameters
    ----------
    pool : set of tuple of (int, int)
        Note spellings as letter index and accidental.
    key : int
        The major key signature. Keyword-only.
    naming : str, default "degrees"
        Caret notation ("degrees") or function names ("functions").
        Keyword-only.
    minor : bool, default False
        Count degrees from the relative natural minor tonic.
        Keyword-only.

    Returns
    -------
    tuple of (list of str, dict of str to tuple of (int, int))
        Answer labels and their grid positions: seven degree columns for
        carets, or four wider columns for function names.

    Examples
    --------
    >>> _degree_choices({(3, 1)}, key=1)
    (['7̂'], {'7̂': (0, 6)})
    """
    tonic_letter = (4 * key + (5 if minor else 0)) % 7
    ordered = sorted(
        pool,
        key=lambda item: ((item[0] - tonic_letter) % 7, item[1]),
    )
    alterations = [
        accidental - key_accidental(letter, count=key)
        for letter, accidental in ordered
    ]
    rows = {
        alteration: row
        for row, alteration in enumerate(
            sorted(set(alterations), reverse=True),
        )
    }
    choices, grid = [], {}
    for (letter, accidental), alteration in zip(
        ordered,
        alterations,
        strict=True,
    ):
        label = spell(
            Note(4, letter=letter, accidental=accidental),
            naming=naming,
            key=key,
            minor=minor,
        )
        choices.append(label)
        grid[label] = (
            divmod(len(choices) - 1, 4)
            if naming == "functions"
            else (rows[alteration], (letter - tonic_letter) % 7)
        )
    return choices, grid


def _note_card_prompt(q: Question, *, naming: str) -> str:
    """
    Say how to name a note on a flashcard in the chosen naming: letters,
    solfège or a scale degree, with the octave if it counts.

    Parameters
    ----------
    q : Question
        The question on the card.
    naming : str
        Naming system selected for this exercise.

    Returns
    -------
    str
        The instruction.

    Examples
    --------
    >>> _note_card_prompt(
    ...     Question(
    ...         "",
    ...         choices=[],
    ...         answer="C4",
    ...         octaves=["C4"],
    ...     ), naming="letters",
    ... )
    'Identify the note. Include the octave.'
    """
    prompt = "Identify the note."
    if naming == "solfege":
        prompt += " Use solfège."
    elif naming in settings.DEGREE_NAMINGS:
        term = (
            "scale degree" if naming == "degrees" else "scale-degree function"
        )
        tonic = (
            mode_tonic(q.key, mode="Natural minor (Aeolian)").name
            if q.minor
            else MAJOR_KEYS[q.key]
        )
        mode = "natural minor" if q.minor else "major"
        prompt += f" Give its {term} in {tonic} {mode}."
    if q.octaves:
        prompt += " Include the octave."
    return prompt


# Classical descending melodic minor uses the natural minor pitches.
_MINOR_SCALES = MappingProxyType(
    {
        "natural": "Natural minor (Aeolian)",
        "harmonic": "Harmonic minor",
        "melodic (asc.)": "Melodic minor",
        "melodic (desc.)": "Natural minor (Aeolian)",
    },
)
_MINOR_FORMS = tuple(_MINOR_SCALES)
_MELODIC_MOTION_DEGREES = (6, 7)


@lru_cache(maxsize=75)
def _degree_pitches(key: int, *, minor_form: str) -> tuple[Note, ...]:
    """
    Spell the seven degrees of a scale, in degree-number order.

    Parameters
    ----------
    key : int
        Number of sharps or flats in the key signature.
    minor_form : str
        Minor form from the clue, or an empty string for major.

    Returns
    -------
    tuple of Note
        One pitch spelling per degree, starting with the tonic.

    Examples
    --------
    >>> _degree_pitches(0, minor_form="harmonic")[6].name
    'G♯'
    """
    tonic = (MINOR_KEYS if minor_form else MAJOR_KEYS)[key]
    scale = _MINOR_SCALES.get(minor_form, "Major (Ionian)")
    return tuple(build(Note.parse(f"{tonic}4"), intervals=SCALES[scale]))


def _note_forms(
    letter: int,
    *,
    key: int,
    minor_scale: bool,
) -> tuple[str, ...]:
    """
    Return the forms that can ask about this written letter.

    Parameters
    ----------
    letter : int
        Written letter, from zero for C to six for B.
    key : int
        Reference key signature.
    minor_scale : bool
        Whether the question asks for a minor scale name.

    Returns
    -------
    tuple of str
        Available forms, with an empty string for ordinary note and
        major scale questions. Melodic directions are offered on the
        degrees where their pitches differ.

    Examples
    --------
    >>> _note_forms(0, key=0, minor_scale=True)  # C in A minor
    ('natural', 'harmonic')
    """
    if not minor_scale:
        return ("",)
    tonic = _degree_pitches(key, minor_form="natural")[0]
    degree = (letter - tonic.letter) % 7 + 1
    if degree in _MELODIC_MOTION_DEGREES:
        return _MINOR_FORMS
    return ("natural", "harmonic")


@register
class NoteNames(ChoiceExercise):
    """
    Name the note shown on a staff.

    Examples
    --------
    >>> q = NoteNames().generate(random.Random(1))
    >>> len(q.staff), q.answer in q.choices
    (1, True)
    """

    name = "Note Identification"
    category = "Notation"
    description = "Identify notes on the staff."
    par_seconds = 3.0

    def card_prompt(self, question: Question) -> str:
        """
        Say what to name on a flashcard, and in which form: letters,
        solfège or a scale degree, with the octave if it counts.

        Parameters
        ----------
        question : Question
            The question on the card.

        Returns
        -------
        str
            The instruction.

        Examples
        --------
        >>> NoteNames().card_prompt(
        ...     Question("", choices=[], answer="C")
        ... )
        'Identify the note.'
        """
        if question.identify_scale:
            return question.prompt
        return _note_card_prompt(question, naming=settings.note_names.naming)

    def practice_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The clefs, ranges, key signatures, note values and naming in
            force, and whether accidentals are asked.

        Examples
        --------
        >>> NoteNames().settings_signature() != NoteNames(
        ...     accidentals=True
        ... ).settings_signature()
        True
        """
        cfg = settings.note_names
        if cfg.scale_answer:
            scale_settings: list[object] = [
                "scale",
                cfg.clefs,
                cfg.ranges,
                sorted(cfg.scale_keys),
                cfg.note_values,
            ]
            if cfg.staff_keys != {0}:
                scale_settings.append(cfg.staff_keys)
            if cfg.scale_minor_keys:
                scale_settings.append(
                    (
                        "minor keys",
                        cfg.scale_minor_keys,
                        _MINOR_FORMS,
                        _MELODIC_MOTION_DEGREES,
                    ),
                )
            return signature(*scale_settings)
        parts = vars(cfg).copy()
        del (
            parts["scale_answer"],
            parts["scale_keys"],
            parts["scale_minor_keys"],
        )
        del parts["minor_keys"]
        if cfg.naming not in settings.DEGREE_NAMINGS:
            parts["key_signatures"] = set(cfg.active_keys())
        elif cfg.minor_keys:
            if cfg.key_signatures:
                parts["minor_keys"] = cfg.minor_keys
            else:
                # Retain the signature of an older minor-only deck.
                parts["key_signatures"] = cfg.minor_keys
                parts["minor_degrees"] = True
        if (
            len(cfg.staff_keys) == 1
            and cfg.staff_keys == parts["key_signatures"]
        ):
            # Preserve the signature of existing single-key decks.
            del parts["staff_keys"]
        return signature(parts, self.accidentals)

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML.

        Examples
        --------
        >>> (
        ...     "Press the button with its name"
        ...     in NoteNames().instructions()
        ... )
        True
        """
        if settings.note_names.scale_answer:
            return (
                "Read the note and the clue beneath it, then choose the "
                "tonic (the first note of the scale). M means major and m "
                "means minor. For F♯ with 3̂ M, choose D. Minor clues "
                "specify natural, harmonic, or melodic minor. Melodic "
                "minor questions ask about 6̂ and 7̂, the degrees that "
                "change between ascending and descending."
            )
        text = (
            "<b>Note Identification</b><br>A note is shown on the staff. "
            "Press the button with its name, or press the "
            "keys shown on it.<br><br>"
            "Use the sliders button to choose the clefs, the range of "
            "notes, the Staff Key drawn on the staff, and the Scale Key "
            "used in the question. Choose note values, letter, solfège or "
            "scale-degree names, or Scale to identify a key. "
            "Choose whether sharps, flats "
            "and naturals appear, and whether to ask for the octave too."
        )
        if settings.note_names.naming in settings.DEGREE_NAMINGS:
            text += (
                "<br><br>Degrees 1–7 start at the tonic of the major or "
                "natural minor key named in the question. "
                "A prefix such as ♭3 or ♯4 lowers or "
                "raises that degree. Type the degree digit; in a chromatic "
                "bank, add Shift for a sharp or Ctrl for a flat. "
                "Add Alt as well for a double alteration."
            )
        return text

    def __init__(self, accidentals: bool = False) -> None:
        """
        Create the exercise.

        Parameters
        ----------
        accidentals : bool, default False
            Ask notes with explicit sharps, flats and naturals, whatever
            the settings say.

        Examples
        --------
        >>> NoteNames(accidentals=True).accidentals
        True
        """
        self.accidentals = accidentals

    def make_question(self, rng: random.Random) -> Question:
        """
        Make a note to name, on one of the chosen clefs, in a chosen
        key.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            The note drawn on a staff, with one button for each name
            that could be the answer.

        Examples
        --------
        >>> q = NoteNames().generate(random.Random(2))
        >>> q.clef in (
        ...     "treble",
        ...     "bass",
        ...     "alto",
        ...     "tenor",
        ...     "soprano",
        ...     "mezzo",
        ...     "baritone",
        ...     "grand",
        ... )
        True
        """
        cfg = settings.note_names
        clef = rng.choice(cfg.active_clefs())
        key, minor = rng.choice(cfg.question_keys())
        value = rng.choice(cfg.active_values())
        with_accidentals = (
            self.accidentals or cfg.accidentals
        ) and not cfg.scale_answer

        letter_pos = rng.randint(*cfg.range_for(clef))
        in_key = key_accidental(letter_pos % 7, count=key)
        acc = in_key
        if (
            with_accidentals and rng.random() < 0.5
        ):  # an explicit sign that differs from the key signature
            acc = rng.choice([a for a in (-1, 0, 1) if a != in_key])
        note = Note.from_diatonic(diatonic=letter_pos, accidental=acc)
        forms = _note_forms(
            note.letter,
            key=key,
            minor_scale=cfg.scale_answer and minor,
        )

        return self._question_for(
            note=note,
            clef=clef,
            key=key,
            minor=minor,
            minor_form=rng.choice(forms) if cfg.scale_answer and minor else "",
            staff_key=rng.choice(sorted(cfg.staff_keys) or [0]),
            value=value,
            cfg=cfg,
        )

    def card_count(self) -> int:
        """
        Count written pitches across the selected ranges, clefs and
        signatures.

        Returns
        -------
        int
            Distinct cards across staff positions, spellings, staff keys
            and reference keys, including each requested scale form.

        Examples
        --------
        >>> NoteNames().card_count() > 0
        True
        """
        cfg = settings.note_names
        keys = cfg.question_keys()
        positions = 0
        for clef in cfg.active_clefs():
            low, high = cfg.range_for(clef)
            positions += sum(
                len(
                    _note_forms(
                        step % 7,
                        key=key,
                        minor_scale=cfg.scale_answer and minor,
                    ),
                )
                for key, minor in keys
                for step in range(low, high + 1)
            )
        return (
            positions
            * (len(cfg.staff_keys) or 1)
            * (
                3
                if (self.accidentals or cfg.accidentals)
                and not cfg.scale_answer
                else 1
            )
        )

    def daily_candidates(self, rng: random.Random) -> Iterator[Question]:
        """
        Visit each selectable written note once, in shuffled order.

        Parameters
        ----------
        rng : random.Random
            Source of the daily order and answer choices.

        Yields
        ------
        Question
            A distinct question within the selected clefs, ranges and
            keys.

        Examples
        --------
        >>> isinstance(
        ...     next(
        ...         NoteNames().daily_candidates(
        ...             random.Random(0)
        ...         )
        ...     ),
        ...     Question,
        ... )
        True
        """
        cfg = settings.note_names
        staff_keys = sorted(cfg.staff_keys) or [0]
        pitches = []
        for clef in cfg.active_clefs():
            low, high = cfg.range_for(clef)
            for key, minor in cfg.question_keys():
                for step in range(low, high + 1):
                    forms = _note_forms(
                        step % 7,
                        key=key,
                        minor_scale=cfg.scale_answer and minor,
                    )
                    signs = (
                        (-1, 0, 1)
                        if (self.accidentals or cfg.accidentals)
                        and not cfg.scale_answer
                        else (key_accidental(step % 7, count=key),)
                    )
                    pitches.extend(
                        (
                            clef,
                            key,
                            minor,
                            form,
                            staff_key,
                            Note.from_diatonic(step, accidental=sign),
                        )
                        for sign in signs
                        for form in forms
                        for staff_key in staff_keys
                    )
        rng.shuffle(pitches)
        for clef, key, minor, form, staff_key, note in pitches:
            yield self.limit_buttons(
                self._question_for(
                    note,
                    clef=clef,
                    key=key,
                    minor=minor,
                    minor_form=form,
                    staff_key=staff_key,
                    value=rng.choice(cfg.active_values()),
                    cfg=cfg,
                ),
                rng=rng,
            )

    def review_question(
        self,
        question: Question,
        *,
        same_settings: bool,
    ) -> Question | None:
        """
        Rebuild a previously seen note when its pitch and answer are
        eligible.

        Parameters
        ----------
        question : Question
            Saved note and answer.
        same_settings : bool
            Whether its original settings are active.

        Returns
        -------
        Question or None
            The note with the current answer bank, or None outside the
            selected material.

        Examples
        --------
        >>> ex = NoteNames()
        >>> q = ex.generate(random.Random(1))
        >>> ex.review_question(
        ...     q, same_settings=True
        ... ) == q
        True
        """
        if not question.staff or not question.staff[0]:
            return None
        note = question.staff[0][0]
        if question.minor_form not in _note_forms(
            note.letter,
            key=question.key,
            minor_scale=question.identify_scale and question.minor,
        ):
            return None
        if same_settings:
            return self.refresh(question)
        cfg = settings.note_names
        if (
            cfg.scale_answer != question.identify_scale
            or question.clef not in cfg.active_clefs()
            or (question.key, question.minor) not in cfg.question_keys()
            or question.written_key not in (cfg.staff_keys or {0})
        ):
            return None
        low, high = cfg.range_for(question.clef)
        if not low <= note.diatonic <= high:
            return None
        if not (
            cfg.scale_answer or self.accidentals or cfg.accidentals
        ) and note.accidental != key_accidental(
            note.letter,
            count=question.key,
        ):
            return None
        rng = random.Random(question.item_key())
        updated = self._question_for(
            note,
            clef=question.clef,
            key=question.key,
            minor=question.minor,
            minor_form=question.minor_form,
            staff_key=question.written_key,
            value=rng.choice(cfg.active_values()),
            cfg=cfg,
        )
        return (
            self.limit_buttons(updated, rng=rng)
            if updated.item_key() == question.item_key()
            else None
        )

    def _question_for(
        self,
        note: Note,
        *,
        clef: str,
        key: int,
        minor: bool,
        minor_form: str,
        staff_key: int,
        value: str,
        cfg: settings.NoteNameSettings,
    ) -> Question:
        """
        Build the prompt and answer bank for a written pitch.

        Parameters
        ----------
        note : Note
            Pitch on the staff.
        clef : str
            Written clef.
        key : int
            Reference key for the pitch and scale degree.
        minor : bool
            Count degrees from the natural minor tonic.
        minor_form : str
            Minor scale variant for Scale answers, empty otherwise.
        staff_key : int
            Signature drawn beside the clef.
        value : str
            Written duration.
        cfg : NoteNameSettings
            Enabled pitch names, octaves, and staff ranges.

        Returns
        -------
        Question
            The note and its full answer bank.

        Examples
        --------
        >>> NoteNames()._question_for(
        ...     Note.parse("C4"),
        ...     clef="treble",
        ...     key=0,
        ...     minor=False,
        ...     minor_form="",
        ...     staff_key=0,
        ...     value="whole",
        ...     cfg=settings.NoteNameSettings(),
        ... ).staff[0][0].name
        'C'
        """
        tonics = MINOR_KEYS if minor else MAJOR_KEYS
        tonic = tonics[key]
        mode = "natural minor" if minor else "major"
        if cfg.scale_answer:
            pitches = _degree_pitches(key, minor_form=minor_form)
            index = (note.letter - pitches[0].letter) % 7
            note = replace(note, accidental=pitches[index].accidental)
            degree = f"{index + 1}̂"
            mode = f"{minor_form.split()[0]} minor" if minor else "major"
            cue = f"m {minor_form}" if minor else "M"
            direction = minor_form.partition(" ")[2]
            scale_name = f"{tonic} {mode}"
            description = f"{scale_name} {direction}".rstrip()
            explanation = f"{note.name} is degree {degree} of {description}."
            keys = cfg.scale_minor_keys if minor else cfg.scale_keys
            choices = [
                f"{tonics[count]} {mode}" for count in sorted(keys) or [0]
            ]
            return Question(
                f"Which {mode} scale has this note at the given degree?",
                minor=minor,
                identify_scale=True,
                minor_form=minor_form,
                choices=choices,
                answer=scale_name,
                staff=[[note]],
                clef=clef,
                key=key,
                staff_signature=staff_key,
                value=value,
                caption=f"{degree} {cue}",
                explanation=explanation,
            )
        with_accidentals = self.accidentals or cfg.accidentals
        name = spell(note, naming=cfg.naming, key=key, minor=minor)
        octaves = None
        joiner = ""
        answer = name
        if cfg.require_octave:
            possible_octaves = set()
            for active_clef in cfg.active_clefs():
                low, high = cfg.range_for(active_clef)
                possible_octaves.update(
                    Note.from_diatonic(step).octave
                    for step in range(low, high + 1)
                )
            octaves = [str(octave) for octave in sorted(possible_octaves)]
            joiner = " / " if cfg.naming in settings.DEGREE_NAMINGS else ""
            answer += f"{joiner}{note.octave}"
        # One button for every name that can be the answer under the
        # current settings.
        if with_accidentals:
            pool = {(l, a) for l in range(7) for a in (-1, 0, 1)}
        elif cfg.naming in settings.DEGREE_NAMINGS:
            pool = {(l, key_accidental(l, count=key)) for l in range(7)}
        else:
            pool = {
                (l, key_accidental(l, count=k))
                for l in range(7)
                for k in cfg.active_keys()
            }
        if cfg.naming in settings.DEGREE_NAMINGS:
            choices, grid = _degree_choices(
                pool,
                key=key,
                naming=cfg.naming,
                minor=minor,
            )
        else:
            ordered = sorted(pool)
            choices = [
                spell(Note(4, letter=l, accidental=a), naming=cfg.naming)
                for l, a in ordered
            ]
            if (
                len(pool) == 7
            ):  # one name per letter: a single row, one column per letter
                grid = {c: (0, l) for c, (l, _) in zip(choices, ordered)}
            # columns are letters; sharps on the top row, then naturals,
            # then flats
            else:
                rows = {
                    a: r
                    for r, a in enumerate(
                        sorted({a for _, a in pool}, reverse=True),
                    )
                }
                grid = {c: (rows[a], l) for c, (l, a) in zip(choices, ordered)}

        expl = []
        if cfg.naming in settings.DEGREE_NAMINGS:
            expl.append(
                f"{note.name} is scale degree {name} in {tonic} {mode}.",
            )
        if key:
            expl.append(
                f"The reference signature has {format_key_signature(key)}.",
            )
        if note.accidental != key_accidental(note.letter, count=staff_key):
            expl.append(
                "The written accidental overrides the staff key signature.",
            )
        return Question(
            "",
            choices=choices,
            answer=answer,
            staff=[[note]],
            clef=clef,
            minor=minor,
            staff_signature=staff_key if staff_key != key else None,
            explanation=" ".join(expl),
            key=key,
            value=value,
            grid=grid,
            octaves=octaves,
            joiner=joiner,
        )


@lru_cache(maxsize=64)
def _interval_starts(
    intervals: tuple[Interval, ...],
    *,
    bounds: tuple[int, int],
    key: int,
    accidentals: frozenset[int],
) -> Mapping[Interval, tuple[Note, ...]]:
    """
    Find lower notes whose upper partners also fit the staff and
    accidental selection.

    Parameters
    ----------
    intervals : tuple of Interval
        The selected interval spellings.
    bounds : tuple of int
        Inclusive diatonic staff positions.
    key : int
        Signature drawn on the staff.
    accidentals : frozenset of int
        Allowed written signs. Zero allows a note with no sign beside
        it.

    Returns
    -------
    mapping of Interval to tuple of Note
        Possible starting notes for each playable interval.

    Examples
    --------
    >>> third = Interval.parse("M3")
    >>> _interval_starts(
    ...     (third,),
    ...     bounds=(28, 30),
    ...     key=0,
    ...     accidentals=frozenset({0}),
    ... )[third]
    (Note(octave=4, letter=0, accidental=0),)
    """
    allowed = []
    for letter in range(7):
        implied = key_accidental(letter, count=key)
        signs = accidentals - {0, implied}
        if 0 in accidentals:
            signs = signs | {implied}
        allowed.append(sorted(signs))

    bottom, top = bounds
    starts = {}
    for iv in intervals:
        notes = []
        for position in range(bottom, top - iv.number + 2):
            natural = Note.from_diatonic(position)
            upper = natural.transpose(iv)
            notes.extend(
                Note.from_diatonic(position, accidental=sign)
                for sign in allowed[natural.letter]
                if upper.accidental + sign in allowed[upper.letter]
            )
        if notes:
            starts[iv] = tuple(notes)
    return MappingProxyType(starts)


INTERVAL_CONSONANCE_PROMPT = "Is this interval consonant or dissonant?"
INTERVAL_INVERSION_PROMPTS = {
    "consonance": "Is the inverted interval consonant or dissonant?",
    "interval": "What is the number of the inverted interval?",
    "quality": "What is the quality of the inverted interval?",
    "combined": "What is the inversion of this interval?",
}


@register
class IntervalNames(Exercise):
    """
    Name the interval between two written notes.

    Examples
    --------
    >>> q = IntervalNames().generate(
    ...     random.Random(3)
    ... )
    >>> (
    ...     [len(chord) for chord in q.staff],
    ...     q.answer in q.choices,
    ... )
    ([2], True)
    """

    name = "Interval Identification"
    interval_voices = True
    category = "Intervals"
    description = "Name the interval between two notes."
    par_seconds = 6.0

    def card_prompt(self, question: Question) -> str:
        """
        Say whether to name the interval's number, its quality, both, or
        its inversion.

        Parameters
        ----------
        question : Question
            The question on the card.

        Returns
        -------
        str
            The instruction.

        Examples
        --------
        >>> IntervalNames().card_prompt(
        ...     Question("", choices=[], answer="3")
        ... )
        'Identify the numeric interval.'
        >>> IntervalNames().card_prompt(
        ...     Question("", choices=[], answer="M3")
        ... )
        'Identify the interval and quality.'
        """
        q = question
        if (
            q.prompt == INTERVAL_CONSONANCE_PROMPT
            or q.prompt in INTERVAL_INVERSION_PROMPTS.values()
        ):
            return q.prompt
        if q.answer.isdecimal():
            return "Identify the numeric interval."
        if q.answer in QUALITY_NAMES.values():
            return "Identify the quality."
        return "Identify the interval and quality."

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML.

        Examples
        --------
        >>> (
        ...     "quality followed by a number"
        ...     in IntervalNames().instructions()
        ... )
        True
        """
        return (
            "<b>Interval Identification</b><br>Name the interval between "
            "the two written notes."
            "<br><br>An interval has a quality followed by a number. The "
            "number counts the letter names it "
            "spans, including both notes. The quality is P (perfect), M "
            "(major), m (minor), A (augmented) or "
            "d (diminished). In Quality, choose whether to answer with the "
            "number, the full interval, or the quality alone. "
            "Turn on Consonance to classify the interval. In this exercise,"
            " perfect unisons, fourths, fifths and octaves, "
            "and major or minor thirds and sixths, are consonant, including"
            " their compound forms. "
            "Turn on Inversions to name the inverted interval. For example,"
            " C up to E is a major third. "
            "Move C up an octave. From E up to C, the interval is a minor "
            "sixth. Reduce compound intervals first. "
            "Use Display Mode to choose how the two notes appear. Under "
            "Melodic, check Ascending, Descending, or both. "
            "Note Value sets the written duration of both notes. You can "
            "click an answer or use the shortcut "
            "shown on its button."
        )

    def settings_signature(self) -> str:
        """
        Identify the settings used to generate and grade the interval.

        Returns
        -------
        str
            The stored-question review signature.

        Examples
        --------
        >>> "Harmonic" in IntervalNames().settings_signature()
        True
        """
        cfg = settings.intervals
        if cfg == settings.IntervalSettings(displays={"Melodic"}):
            # The original melodic questions were stored with an empty
            # signature.
            return ""
        parts = vars(cfg).copy()
        if not cfg.consonance:
            del parts["consonance"]
        if not cfg.inversions:
            del parts[
                "inversions"
            ]  # Keep earlier identification questions eligible for review.
        if cfg.quality_mode != "quality":
            # Keep reviews saved under the original on/off Quality
            # switch.
            del parts["quality_mode"]
            parts["quality"] = cfg.quality_mode == "combined"
        if (
            cfg.accidentals == settings.DEFAULT_INTERVAL_ACCIDENTALS
            and cfg.staff_keys == {0}
        ):
            del parts[
                "accidentals"
                # These are the same spellings that earlier blank-staff
                # questions allowed.
            ]
        del parts["directions"]
        if "Melodic" in cfg.displays and "descending" in cfg.directions:
            # Preserve the stored motion key and its single-direction
            # value for existing reviews.
            parts["motion"] = ",".join(sorted(cfg.directions))
        if cfg.note_values == {"whole"}:
            del parts[
                "note_values"
            ]  # Preserve review signatures for earlier whole-note questions.
        if cfg.button_mode == "limited" and cfg.button_count == 6:
            # Match questions saved before the Buttons setting existed.
            del parts["button_mode"], parts["button_count"]
        elif cfg.button_mode == "all":
            del parts["button_count"]
        return signature(parts)

    def refresh(self, question: Question) -> Question:
        """
        Arrange written interval answers by quality, with interval
        numbers in columns.

        Parameters
        ----------
        question : Question
            A new or saved interval question.

        Returns
        -------
        Question
            The same answer choices in reading order. Perfect and major
            share a row.

        Examples
        --------
        >>> q = Question(
        ...     "",
        ...     choices=["d3", "m3", "P4", "M3", "A3"],
        ...     answer="m3",
        ... )
        >>> IntervalNames().refresh(q).choices
        ['A3', 'M3', 'P4', 'm3', 'd3']
        """
        rows = settings.INTERVAL_QUALITY_ORDER
        if not question.choices or any(
            name[:1] not in rows or not name[1:].isdigit()
            for name in question.choices
        ):
            return question
        intervals = [Interval.parse(name) for name in question.choices]
        numbers = sorted({iv.number for iv in intervals})
        grid = {
            iv.short: (rows[iv.quality], numbers.index(iv.number))
            for iv in intervals
        }
        return replace(
            question,
            choices=sorted(question.choices, key=grid.__getitem__),
            grid=grid,
        )

    def generate(self, rng: random.Random) -> Question:
        """
        Make two notes whose interval is to be named.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            The lower and higher note on a staff, and the interval (such
            as 'M3' or 'P5') as the answer.

        Examples
        --------
        >>> q = IntervalNames().generate(
        ...     random.Random(4)
        ... )
        >>> q.answer[0] in "PMmAd" and q.answer[
        ...     1:
        ... ].isdigit()
        True
        """
        return self.refresh(
            _written_interval_question(
                settings.intervals,
                rng=rng,
                construction=False,
            ),
        )


def _written_interval_question(
    cfg: settings.IntervalSettings,
    *,
    rng: random.Random,
    construction: bool,
) -> Question:
    """
    Choose a playable written interval under the active clef, range, and
    spelling constraints.

    Parameters
    ----------
    cfg : IntervalSettings
        The settings belonging to this exercise.
    rng : random.Random
        Generator for the presentation and endpoints.
    construction : bool
        Ask for placement of the second note.

    Returns
    -------
    Question
        The playable interval or an instruction to change incompatible
        options.

    Examples
    --------
    An ascending melodic presentation starts on the lower endpoint.
    """
    selected = tuple(
        iv
        for name, iv in settings.WRITTEN_INTERVALS.items()
        if name in cfg.intervals
    )
    smallest = min((iv.number for iv in selected), default=2)
    clefs = [
        clef for clef in cfg.active_clefs() if cfg.staff_span(clef) >= smallest
    ]
    if not clefs:
        return Question(
            "Widen a clef’s Range or choose a smaller interval in Settings.",
            choices=[],
            answer="",
        )
    if not selected:
        return Question(
            "Select an interval in Settings to continue.",
            choices=[],
            answer="",
        )
    staves = [(clef, key) for clef in clefs for key in sorted(cfg.staff_keys)]
    rng.shuffle(staves)
    for clef, key in staves:
        starts = _interval_starts(
            selected,
            bounds=cfg.range_for(clef),
            key=key,
            accidentals=frozenset(cfg.accidentals),
        )
        if starts:
            break
    else:
        return Question(
            (
                "Change Accidentals, Intervals, Staff Key, or Range to fit"
                " an interval."
            ),
            choices=[],
            answer="",
        )
    available = list(starts)
    iv = rng.choice(available)
    low = rng.choice(starts[iv])
    high = low.transpose(iv)
    display = rng.choice(sorted(cfg.displays))
    descending = (
        display == "Melodic"
        and rng.choice(sorted(cfg.directions)) == "descending"
    )
    first, second = (high, low) if descending else (low, high)
    staff = [[first, second]] if display == "Harmonic" else [[first], [second]]
    if construction:
        return _interval_placement(
            cfg,
            rng=rng,
            clef=clef,
            key=key,
            interval=iv,
            staff=staff,
            starts=starts,
        )
    explanation = (
        f"{first}"
        " to "
        f"{second}"
        ": "
        f"{QUALITY_NAMES[iv.quality]}"
        " "
        f"{iv.number}"
        ", "
        f"{iv.semitones}"
        " semitones."
    )
    if cfg.inversions:
        inverted = iv.inversion
        explanation += f" The inversion of {iv.short} is {inverted.short}."
        iv = inverted
        available = sorted(
            dict.fromkeys(other.inversion for other in available),
            key=lambda other: other.number,
        )
    mode = "consonance" if cfg.consonance else cfg.quality_mode
    if mode == "consonance":
        prompt = INTERVAL_CONSONANCE_PROMPT
        consonant = ((iv.number - 1) % 7, iv.quality) in {
            (0, "P"),
            (3, "P"),
            (4, "P"),
            (2, "M"),
            (2, "m"),
            (5, "M"),
            (5, "m"),
        }
        answer = "Consonant" if consonant else "Dissonant"
        pool = ["Consonant", "Dissonant"]
        explanation += f" It is {answer.lower()}."
    elif mode == "interval":
        prompt, answer = "What is the interval number?", str(iv.number)
        pool = list(dict.fromkeys(str(other.number) for other in available))
    elif mode == "quality":
        prompt, answer = (
            "What is the interval quality?",
            QUALITY_NAMES[iv.quality],
        )
        qualities = {other.quality for other in available}
        pool = [
            QUALITY_NAMES[quality]
            for quality in settings.INTERVAL_QUALITY_ORDER
            if quality in qualities
        ]
    else:
        prompt, answer = "", iv.short
        pool = [other.short for other in available]
    return Question(
        INTERVAL_INVERSION_PROMPTS[mode] if cfg.inversions else prompt,
        choices=pool
        if mode == "consonance" or cfg.button_mode == "all"
        else pick_distractors(
            answer,
            pool=pool,
            n=cfg.button_count - 1,
            rng=rng,
        ),
        answer=answer,
        staff=staff,
        clef=clef,
        key=key,
        value=rng.choice(cfg.active_values()),
        explanation=explanation,
    )


def _interval_placement(
    cfg: settings.IntervalSettings,
    *,
    rng: random.Random,
    clef: str,
    key: int,
    interval: Interval,
    staff: list[list[Note]],
    starts: Mapping[Interval, tuple[Note, ...]],
) -> Question:
    """
    Build a placement prompt and all eligible spellings that satisfy it
    from the given note.

    Parameters
    ----------
    cfg : IntervalSettings
        Construction options.
    rng : random.Random
        Selects the written duration.
    clef : str
        Staff clef.
    key : int
        Drawn key signature.
    interval : Interval
        Selected spelling.
    staff : list of list of Note
        Endpoints in playback order.
    starts : mapping
        Playable lower notes for each interval on this staff.

    Returns
    -------
    Question
        A reproducible example solution and any other valid written
        endpoints.

    Examples
    --------
    A third above C can accept both E and E♭ when major and minor thirds
    are selected.
    """
    first, target = staff[0][0], staff[-1][-1]
    descending = first.diatonic > target.diatonic
    direction = "below" if descending else "above"
    sizes = (
        "second",
        "third",
        "fourth",
        "fifth",
        "sixth",
        "seventh",
        "octave",
        "ninth",
        "tenth",
        "eleventh",
        "twelfth",
        "thirteenth",
        "fourteenth",
        "fifteenth",
    )
    size = sizes[interval.number - 2]
    quality = QUALITY_NAMES[interval.quality]
    description = f"{quality} {size}"
    targets = [target]
    if cfg.quality_mode != "combined":
        by_number = cfg.quality_mode == "interval"
        description = size if by_number else f"{quality} interval"
        targets = []
        for other, lower_notes in starts.items():
            matches = (
                other.number == interval.number
                if by_number
                else other.quality == interval.quality
            )
            if matches:
                end = first.transpose(other, descending=descending)
                if (end if descending else first) in lower_notes:
                    targets.append(end)
    # A number or quality can have several solutions. Keep its card
    # identity independent of which one was drawn.
    target, *alternatives = targets
    solution = [[first, target]] if len(staff) == 1 else [[first], [target]]
    return Question(
        "Place "
        f"{('an' if description[0] in 'aeiou' else 'a')}"
        " "
        f"{description}"
        " "
        f"{direction}"
        " the given note.",
        choices=[],
        answer=str(target),
        accept=tuple(map(str, alternatives)),
        construct=target,
        staff=solution,
        clef=clef,
        key=key,
        notes_only=True,
        accidentals=True,
        value=rng.choice(cfg.active_values()),
        explanation=f"{target} is one valid placement."
        if alternatives
        else f"The second note is {target}.",
    )


@register
class IntervalConstruction(Exercise):
    """
    Place a second written note at the requested interval from a given
    note.

    Examples
    --------
    >>> q = IntervalConstruction().generate(
    ...     random.Random(2)
    ... )
    >>> q.construct is not None and q.check_placed(
    ...     q.construct
    ... )
    True
    """

    name = "Interval Construction"
    interval_voices = True
    category = "Intervals"
    description = (
        "Place a note above or below the given note to build an interval."
    )
    par_seconds = 8.0

    def instructions(self) -> str:
        """
        Explain staff placement and spelling for interval construction.

        Returns
        -------
        str
            Instructions for mouse and keyboard input.

        Examples
        --------
        The reference describes the difference between melodic and
        harmonic placement.
        """
        return (
            "<b>Interval Construction</b><br>Count lines and spaces from "
            "the given note in the requested direction. "
            "Choose an accidental if needed, then click to place the second"
            " note. You can also move with the arrow keys "
            "and press Enter. A harmonic interval stacks both notes. A "
            "melodic interval places them in sequence. "
            "For Interval Only or Quality Only, any selected interval that "
            "fits the prompt and settings counts."
        )

    def settings_signature(self) -> str:
        """
        Identify the construction settings used to generate a stored
        card.

        Returns
        -------
        str
            Stable signature of the exercise options.

        Examples
        --------
        A change in staff ranges changes which stored questions are
        eligible.
        """
        parts = vars(settings.interval_construction).copy()
        del parts["inversions"], parts["consonance"]
        return signature(parts)

    def generate(self, rng: random.Random) -> Question:
        """
        Generate a staff, an interval prompt, and its eligible
        placements.

        Parameters
        ----------
        rng : random.Random
            Generator for the presentation.

        Returns
        -------
        Question
            Written interval to construct.

        Examples
        --------
        A harmonic question asks for a note above its starting note.
        """
        return _written_interval_question(
            settings.interval_construction,
            rng=rng,
            construction=True,
        )


@register
class KeyboardIntervals(Exercise):
    """
    Identify the ascending interval between two highlighted piano keys.

    Attributes
    ----------
    INTERVALS : tuple of str
        Conventional names for every distance on the piano, including
        compound intervals and combined tritone answers.

    Examples
    --------
    >>> q = KeyboardIntervals().generate(
    ...     random.Random(5)
    ... )
    >>> (
    ...     len(q.keyboard_notes),
    ...     q.answer in q.choices,
    ...     q.staff,
    ... )
    (2, True, [])
    """

    name = "Keyboard Interval Identification"
    category = "Intervals"
    description = "Name the interval between two highlighted piano keys."
    par_seconds = 6.0
    INTERVALS = settings.KEYBOARD_INTERVAL_NAMES

    def card_prompt(self, question: Question) -> str:
        """
        Say what to name on a flashcard.

        Parameters
        ----------
        question : Question
            The question on the card.

        Returns
        -------
        str
            The instruction.

        Examples
        --------
        >>> KeyboardIntervals().card_prompt(
        ...     Question("", choices=[], answer="P5")
        ... )
        'Identify the interval.'
        """
        del question
        return "Identify the interval."

    def settings_signature(self) -> str:
        """
        Identify the keyboard range and selected intervals for
        stored-question reviews.

        Returns
        -------
        str
            The settings that determine which questions can be asked.

        Examples
        --------
        >>> bool(
        ...     KeyboardIntervals().settings_signature()
        ... )
        True
        """
        return signature(settings.keyboard_intervals)

    def instructions(self) -> str:
        """
        Explain how to identify an interval from two highlighted keys.

        Returns
        -------
        str
            HTML explaining interval names and enharmonic ambiguity on
            the keyboard.

        Examples
        --------
        >>> "A4 / d5" in KeyboardIntervals().instructions()
        True
        """
        return (
            "<b>Keyboard Interval Identification</b><br>Two piano keys are "
            "highlighted. Identify the interval from the "
            "lower key to the higher key. Intervals beyond an octave are "
            "included when they fit the selected range.<br><br>"
            "Count the half steps between "
            "the keys, including black keys: adjacent keys are one half "
            "step apart. P means perfect, M means major, "
            "and m means minor.<br><br>A keyboard shows pitches without "
            "their written spellings. Use the standard "
            "interval name for each distance. Six half steps form a "
            "tritone, labeled <b>A4 / d5</b> because an augmented "
            "fourth and a diminished fifth use the same keys.<br><br>Use "
            "Settings to choose the keyboard range and "
            "the intervals to practice. Only intervals that fit the "
            "selected range are available. Click an answer or "
            "press its number."
        )

    def generate(self, rng: random.Random) -> Question:
        """
        Highlight two distinct keys at a selected interval within the
        chosen range.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            Two highlighted keys and either a limited number of choices
            or a fixed bank for every selected interval.
            A prompt is returned if none are selected.

        Examples
        --------
        >>> q = KeyboardIntervals().generate(
        ...     random.Random(7)
        ... )
        >>> 1 <= q.keyboard_notes[
        ...     1
        ... ].midi - q.keyboard_notes[0].midi <= 12
        True
        """
        cfg = settings.keyboard_intervals
        lo, hi = cfg.bounds()
        intervals = cfg.active_intervals()
        if not intervals:
            return Question(
                "Select at least one interval in Settings to continue.",
                choices=[],
                answer="",
            )
        distance = rng.choice(intervals)
        lower = rng.randint(lo, hi - distance)
        notes = [
            _spelled(midi, letter=letter, accidental=accidental)
            for midi in (lower, lower + distance)
            for letter, accidental in _key_spellings(midi % 12, count=None)[:1]
        ]
        answer = self.INTERVALS[distance - 1]
        pool = [self.INTERVALS[value - 1] for value in intervals]
        choices = (
            pool
            if cfg.all_interval_buttons
            else pick_distractors(
                answer,
                pool=pool,
                n=cfg.answer_button_limit() - 1,
                rng=rng,
            )
        )
        numbers: list[str] | None = None
        accepted: tuple[str, ...] = ()
        if cfg.compact_buttons:
            spellings = [
                name for interval in pool for name in interval.split(" / ")
            ]
            choices = [
                quality
                for quality in ("P", "M", "m", "A", "d")
                if any(name.startswith(quality) for name in spellings)
            ]
            numbers = sorted(
                {name[1:] for name in spellings},
                key=lambda number: int(number),
            )
            accepted = tuple(answer.split(" / "))
        return Question(
            "",
            choices=choices,
            octaves=numbers,
            second_label="Number" if cfg.compact_buttons else "Octave",
            accept=accepted,
            answer=answer,
            keyboard_notes=notes,
            keyboard_range=(lo, hi),
            explanation=(
                "The highlighted keys are "
                f"{distance}"
                " half step"
                f"{('s' if distance != 1 else '')}"
                " apart: "
                f"{answer}"
                "."
            ),
        )


def _scale_name(mode: str) -> str:
    """
    Return the mode's name as it follows a tonic.

    Parameters
    ----------
    mode : str
        A key of `SCALES`.

    Returns
    -------
    str
        'major' or 'minor' for those two, otherwise the mode's own name
        such as 'Dorian'.

    Examples
    --------
    >>> _scale_name("Natural minor (Aeolian)")
    'minor'
    >>> _scale_name("Dorian")
    'Dorian'
    """
    return {"Major (Ionian)": "major", "Natural minor (Aeolian)": "minor"}.get(
        mode,
        mode,
    )


def _blank_scale(mode: str) -> str:
    """
    Return the caption that asks for a scale's tonic.

    Parameters
    ----------
    mode : str
        A key of `SCALES`.

    Returns
    -------
    str
        The scale's name after a blank: '_ Major', '_ minor', '_ Dorian'
        and so on.

    Examples
    --------
    >>> (
    ...     _blank_scale("Major (Ionian)"),
    ...     _blank_scale("Natural minor (Aeolian)"),
    ...     _blank_scale("Dorian"),
    ... )
    ('_ Major', '_ minor', '_ Dorian')
    """
    scale = _scale_name(mode)
    return f"_ {scale if scale == 'minor' else scale[0].upper() + scale[1:]}"


def _key_tonics(cfg: settings.KeySignatureSettings) -> list[str]:
    """
    Collect distinct tonic spellings in mode and signature order.

    Parameters
    ----------
    cfg : KeySignatureSettings
        Enabled modes and key signatures.

    Returns
    -------
    list of str
        Tonic names for the answer buttons.

    Examples
    --------
    >>> "C" in _key_tonics(settings.KeySignatureSettings())
    True
    """
    keys = cfg.active_keys()
    return list(
        dict.fromkeys(
            mode_tonic(key, mode=mode).name
            for mode in cfg.active_modes()
            for key in keys
        ),
    )


@register
class KeySignatures(ChoiceExercise):
    """
    Read a key signature drawn on a staff and name the key it belongs
    to.

    Examples
    --------
    >>> q = KeySignatures().generate(
    ...     random.Random(5)
    ... )
    >>> q.answer in q.choices
    True
    """

    name = "Key Signature Identification"
    category = "Scales & keys"
    description = "Name the key from its signature on a staff."
    par_seconds = 5.0
    has_sound = False

    def practice_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The kinds of question, clefs, scales and key signatures in
            force.

        Examples
        --------
        >>> KeySignatures().settings_signature().startswith(
        ...     "["
        ... )
        True
        """
        return signature(settings.key_signatures)

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML.

        Examples
        --------
        >>> (
        ...     "Key Signature Identification"
        ...     in KeySignatures().instructions()
        ... )
        True
        """
        return (
            "<b>Key Signature Identification</b><br>A key signature is "
            "drawn on a staff: press the tonic of the scale it "
            "belongs to (the caption under the staff says whether it is a "
            "major key, a minor key or a mode such as "
            "Dorian).<br><br>"
            "Sharp keys add sharps (G, D, A ...) and flat keys add flats "
            "(F, B♭, E♭ ...). A mode uses the signature of a "
            "major key, started from another degree: D Dorian has the "
            "signature of C major, started from its second note."
            "<br><br>You can press an answer's number instead of the "
            "button: 1 is the first.<br><br>"
            "Use the sliders button to choose the clefs, the scales and the"
            " key signatures."
        )

    def refresh(self, question: Question) -> Question:
        """
        Give a stored signature question the caption on its staff that
        older versions did not write.

        Parameters
        ----------
        question : Question
            The question as it was stored.

        Returns
        -------
        Question
            The same question, captioned '_ Major' (or '_ minor', '_
            Dorian' and so on) if it shows a staff and had no caption.

        Examples
        --------
        >>> old = Question(
        ...     "Which minor key has this key signature?",
        ...     choices=["C"],
        ...     answer="C",
        ...     key=-3,
        ...     show_staff=True,
        ... )
        >>> KeySignatures().refresh(old).caption
        '_ minor'
        """
        if not question.show_staff:
            return question
        for mode in SCALES:
            if question.prompt == (
                "Which "
                f"{MODE_WORDS.get(mode, f'{mode} scale')}"
                " has this key signature?"
            ):
                choices = _key_tonics(settings.key_signatures)
                updated = replace(
                    question,
                    caption=question.caption or _blank_scale(mode),
                    choices=choices,
                    grid={
                        choice: (
                            0 if "♯" in choice else 2 if "♭" in choice else 1,
                            "CDEFGAB".index(choice[0]),
                        )
                        for choice in choices
                    },
                )
                return self.limit_buttons(
                    updated,
                    rng=random.Random(question.item_key()),
                )
        return question

    def make_question(self, rng: random.Random) -> Question:
        """
        Make a key signature to read.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            A signature on a staff; the answer is the tonic of the scale
            that has it.

        Examples
        --------
        >>> q = KeySignatures().generate(
        ...     random.Random(6)
        ... )
        >>> q.show_staff and q.answer in q.choices
        True
        """
        cfg = settings.key_signatures
        mode = rng.choice(cfg.active_modes())
        count = rng.choice(cfg.active_keys())
        return self._read_question(
            mode_tonic(count, mode=mode),
            mode=mode,
            count=count,
            clef=rng.choice(cfg.active_clefs()),
            rng=rng,
            allowed=_key_tonics(cfg),
        )

    @staticmethod
    def _read_question(
        tonic: Note,
        *,
        mode: str,
        count: int,
        clef: str,
        rng: random.Random,
        allowed: list[str],
    ) -> Question:
        """
        Show a key signature on a staff and ask for the tonic of the
        scale that has it.

        Parameters
        ----------
        tonic : Note
            The tonic that is the right answer.
        mode : str
            A key of `SCALES`, such as "Major (Ionian)". Keyword-only.
        count : int
            The key signature to draw: positive for sharps, negative for
            flats. Keyword-only.
        clef : str
            The clef to draw it on. Keyword-only.
        rng : random.Random
            The random number generator, used to choose the wrong
            answers. Keyword-only.
        allowed : list of str
            Tonic names available for this question.

        Returns
        -------
        Question
            A staff with only a clef and the signature, captioned '_
            Major' (or '_ minor', '_ Dorian' and so on).

        Examples
        --------
        >>> # noinspection PyProtectedMember
        >>> q = KeySignatures._read_question(
        ...     Note.parse("G4"),
        ...     mode="Major (Ionian)",
        ...     count=1,
        ...     clef="treble",
        ...     rng=random.Random(0),
        ...     allowed=["C", "G"],
        ... )
        >>> q.answer, q.caption, q.show_staff
        ('G', '_ Major', True)
        """
        correct = tonic.name
        choices = pick_distractors(
            correct,
            pool=allowed,
            n=len(allowed) - 1,
            rng=rng,
        )
        word = MODE_WORDS.get(mode, f"{mode} scale")
        notes = [
            *build(tonic, intervals=SCALES[mode]),
            tonic.transpose(Interval(8, quality="P")),
        ]  # the scale, up to its octave
        return Question(
            f"Which {word} has this key signature?",
            choices=choices,
            grid={
                choice: (
                    0 if "♯" in choice else 2 if "♭" in choice else 1,
                    "CDEFGAB".index(choice[0]),
                )
                for choice in choices
            },
            answer=correct,
            clef=clef,
            key=count,
            show_staff=True,
            caption=_blank_scale(mode),
            explanation=(
                f"{format_key_signature(count)}"
                ": "
                f"{tonic.name}"
                " "
                f"{_scale_name(mode)}"
                ": "
            )
            + " ".join(n.name for n in notes),
        )


@register
class KeySignatureConstruction(Exercise):
    """
    Build the key signature of a named key on a blank staff, with the
    fork.

    Examples
    --------
    >>> q = KeySignatureConstruction().generate(
    ...     random.Random(5)
    ... )
    >>> q.build_key, q.staff, q.choices
    (True, [], [])
    """

    name = "Key Signature Construction"
    category = "Scales & keys"
    description = "Build the key signature of a named key."
    par_seconds = 6.0
    has_sound = False

    def settings_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The clefs, scales and key signatures in force.

        Examples
        --------
        >>> KeySignatureConstruction().settings_signature().startswith(
        ...     "["
        ... )
        True
        """
        return signature(settings.key_construction)

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML.

        Examples
        --------
        >>> (
        ...     "Key Signature Construction"
        ...     in KeySignatureConstruction().instructions()
        ... )
        True
        """
        return (
            "<b>Key Signature Construction</b><br>The key under the staff "
            "is the one to build. Pick how many sharps (top) "
            "or flats (bottom) it has on the fork under the staff, then "
            "press Answer (or Return). The staff shows what you "
            "have picked.<br><br>Click a number on the fork, or turn the "
            "mouse wheel to move the circle along it. The "
            "natural sign at the end of the stem is C major, with no sharps"
            " or flats.<br><br>"
            "Without the mouse: the Up or Right arrow adds a sharp, the "
            "Down or Left arrow adds a flat, and Home goes "
            "back to none. Then press Return to answer.<br><br>"
            "A mode uses the signature of a major key, started from another"
            " degree: D Dorian has the signature of C "
            "major.<br><br>Use the sliders button to choose the clefs, the "
            "scales and the key signatures."
        )

    def generate(self, rng: random.Random) -> Question:
        """
        Name a key whose signature is to be built.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            A blank staff captioned with the key, such as 'D Major'; the
            answer is its sharps or flats.

        Examples
        --------
        >>> q = KeySignatureConstruction().generate(
        ...     random.Random(1)
        ... )
        >>> q.caption.split()[0] in {
        ...     "C",
        ...     "D",
        ...     "E",
        ...     "F",
        ...     "G",
        ...     "A",
        ...     "B",
        ... } or "♯" in q.caption or "♭" in q.caption
        True
        >>> q.answer == format_key_signature(q.key)
        True
        """
        cfg = settings.key_construction
        mode = rng.choice(cfg.active_modes())
        count = rng.choice(cfg.active_keys())
        tonic = mode_tonic(count, mode=mode)
        # "D Major", "A♯ minor", "E Dorian"
        name = f"{tonic.name} {_blank_scale(mode)[2:]}"
        notes = [
            *build(tonic, intervals=SCALES[mode]),
            tonic.transpose(Interval(8, quality="P")),
        ]  # the scale, up to its octave
        return Question(
            f"Build the key signature of {name}.",
            choices=[],
            answer=format_key_signature(count),
            clef=rng.choice(cfg.active_clefs()),
            key=count,
            show_staff=True,
            caption=name,
            build_key=True,
            explanation=f"{name}: {format_key_signature(count)}: "
            + " ".join(n.name for n in notes),
        )


@register
class OrderOfKeys(Exercise):
    """
    Write the accidentals of a named key signature in order.

    Examples
    --------
    >>> OrderOfKeys().generate(
    ...     random.Random(1)
    ... ).place_signature
    True
    """

    name = "Order of Keys"
    category = "Scales & keys"
    description = "Place a key’s sharps or flats on the staff in order."
    par_seconds = 12.0
    has_sound = False

    def settings_signature(self) -> str:
        """
        Identify the selections used to generate a practice question.

        Returns
        -------
        str
            The original empty signature at the defaults, so earlier
            questions remain available for review.

        Examples
        --------
        >>> OrderOfKeys().settings_signature()
        ''
        """
        cfg = settings.order_of_keys
        base = settings.KeySignatureSettings(
            clefs=cfg.clefs,
            modes=cfg.modes,
            keys=cfg.keys,
        )
        if cfg.starting_accidentals == {0}:
            return (
                ""
                if base == settings.KeySignatureSettings()
                else signature(base)
            )
        return signature(base, cfg.starting_accidentals)

    def instructions(self) -> str:
        """
        Explain how to enter and submit a signature.

        Returns
        -------
        str
            The exercise help text.

        Examples
        --------
        >>> "Undo" in OrderOfKeys().instructions()
        True
        """
        return (
            "Read the key below the staff. Choose ♯ or ♭ and click the line"
            " or space for each sign, "
            "starting with the leftmost empty position. Leave any printed "
            "signs in place. "
            "You can also use ↑ and ↓ to choose a position and P to place "
            "the sign. "
            "Use Undo to take back the last sign. Press Answer or Return "
            "when the signature is complete. "
            "If the key has no sharps or flats, submit the empty staff."
        )

    def generate(self, rng: random.Random) -> Question:
        """
        Choose a key from the selected scales and signatures and spell
        it in a selected clef.

        Parameters
        ----------
        rng : random.Random
            Source for the key, mode, and clef.

        Returns
        -------
        Question
            The named key and the ordered signs with their exact staff
            octaves.

        Examples
        --------
        >>> q = OrderOfKeys().generate(random.Random(2))
        >>> q.show_staff and not q.choices
        True
        """
        cfg = settings.order_of_keys
        starts = sorted(
            cfg.starting_accidentals.intersection(cfg.available_starts()),
        ) or [0]
        start = starts[0] if len(starts) == 1 else rng.choice(starts)
        keys = [
            key
            for key in cfg.active_keys()
            if min(0, key) <= start <= max(0, key)
        ]
        count = rng.choice(keys)
        mode = rng.choice(cfg.active_modes())
        clef = rng.choice(cfg.active_clefs())
        name = f"{mode_tonic(count, mode=mode).name} {_scale_name(mode)}"
        signs = written_signature(clef, key=count)
        return Question(
            f"Write the key signature for {name}.",
            choices=[],
            answer=" ".join(map(str, signs)) or "No accidentals",
            caption=name,
            clef=clef,
            key=count,
            show_staff=True,
            place_signature=True,
            starting_slots=sorted(rng.sample(range(abs(count)), abs(start))),
            accidentals=True,
        )


def _scale_notes(
    rng: random.Random,
    *,
    clef: str,
    named: Note,
    mode: str,
    exact_octave: bool = False,
) -> list[Note]:
    """
    Place an ascending scale in a readable octave for its clef.

    Parameters
    ----------
    rng : random.Random
        The random number generator.
    clef : str
        The staff's clef. Keyword-only.
    named : Note
        The tonic spelling; its octave is replaced. Keyword-only.
    mode : str
        The scale type in `SCALES`. Keyword-only.
    exact_octave : bool, default False
        Allow any starting octave within the construction staff's input
        range. Keyword-only.

    Returns
    -------
    list of Note
        Eight notes, including the tonic an octave above the first note.

    Examples
    --------
    >>> notes = _scale_notes(
    ...     random.Random(1),
    ...     clef="bass",
    ...     named=Note.parse("D4"),
    ...     mode="Dorian",
    ... )
    >>> (
    ...     len(notes),
    ...     notes[0].name,
    ...     notes[-1].midi - notes[0].midi,
    ... )
    (8, 'D', 12)
    """
    bottom = settings.BOTTOM_LINES[clef].diatonic
    starts = [
        d for d in range(bottom - 3, bottom + 4) if d % 7 == named.letter
    ]
    if exact_octave:
        low, high = settings.RANGE_LIMITS[clef]
        starts = [
            d for d in range(low, high - 6) if d % 7 == named.letter
        ] or starts
    tonic = Note.from_diatonic(rng.choice(starts), accidental=named.accidental)
    return [
        *build(tonic, intervals=SCALES[mode]),
        tonic.transpose(Interval(8, quality="P")),
    ]


def _scale_material(
    rng: random.Random,
    *,
    cfg: settings.ScaleIdentificationSettings
    | settings.ScaleConstructionSettings,
) -> tuple[str, int, str, int, list[Note]]:
    """
    Sample the shared musical material for scale identification and
    construction.

    Parameters
    ----------
    rng : random.Random
        The random number generator.
    cfg : ScaleIdentificationSettings or ScaleConstructionSettings
        The independent clef, mode and key choices. Keyword-only.

    Returns
    -------
    tuple of (str, int, str, int, list of Note)
        Mode, scale signature, clef, staff signature and eight notes in
        the selected motion.

    Examples
    --------
    >>> material = _scale_material(
    ...     random.Random(1),
    ...     cfg=settings.ScaleIdentificationSettings(),
    ... )
    >>> len(material[-1])
    8
    """
    minor_mode = "Natural minor (Aeolian)"
    modes = cfg.active_modes()
    if cfg.minor_keys is None:
        mode = rng.choice(modes)
        count = rng.choice(cfg.active_keys())
    else:
        available = [
            mode
            for mode in modes
            if (cfg.minor_keys if mode == minor_mode else cfg.keys)
        ]
        mode = rng.choice(
            available or (["Major (Ionian)"] if cfg.keys else [minor_mode]),
        )
        count = rng.choice(
            sorted(cfg.minor_keys if mode == minor_mode else cfg.keys) or [0],
        )
    clef = rng.choice(cfg.active_clefs())
    staff_key = rng.choice(cfg.active_staff_keys())
    notes = _scale_notes(
        rng,
        clef=clef,
        named=mode_tonic(count, mode=mode),
        mode=mode,
        exact_octave=isinstance(cfg, settings.ScaleConstructionSettings)
        and cfg.octave,
    )
    if cfg.motion == "descending":
        notes.reverse()
    return mode, count, clef, staff_key, notes


@register
class ScaleIdentification(Exercise):
    """
    Identify the tonic and type of a scale drawn on a staff.

    Examples
    --------
    >>> q = ScaleIdentification().generate(
    ...     random.Random(7)
    ... )
    >>> len(q.staff), q.answer in q.choices
    (8, True)
    """

    name = "Scale Identification"
    category = "Scales & keys"
    description = "Identify a scale or mode written on the staff."
    par_seconds = 8.0

    def settings_signature(self) -> str:
        """
        Identify the clefs, scale types and staff and scale signatures
        in force.

        Returns
        -------
        str
            The serialized question settings.

        Examples
        --------
        >>> ScaleIdentification().settings_signature().startswith(
        ...     "["
        ... )
        True
        """
        cfg = settings.scale_identification
        # Keep existing ascending reviews under their original settings
        # signature.
        parts = vars(cfg).copy()
        if cfg.motion == "ascending":
            del parts["motion"]
        if cfg.button_mode == "limited":
            del parts["button_mode"]
        if cfg.button_mode == "all" or cfg.button_count == 6:
            del parts["button_count"]
        if cfg.question_type == "combined":
            del parts["question_type"]
        if cfg.minor_keys is None:
            del parts["minor_keys"]
        return signature(parts)

    def instructions(self) -> str:
        """
        Explain how to identify the scale, including a staff with a
        different signature.

        Returns
        -------
        str
            Simple HTML help text.

        Examples
        --------
        >>> (
        ...     "Scale Identification"
        ...     in ScaleIdentification().instructions()
        ... )
        True
        """
        return (
            "<b>Scale Identification</b><br>Read the scale on the staff and"
            " choose its tonic and scale type. "
            "The first and last notes are the tonic, one octave apart. Read"
            " the clef, key signature and each note's "
            "accidental, then use the whole and half steps to identify the "
            "scale or mode. "
            "The staff's key signature need not be the scale's own: written"
            " accidentals show where they differ. "
            "Use Settings to choose Clefs, Scales, Staff Key, Scale Key, "
            "Motion, Buttons, and Question Type. "
            "When asked for both with All buttons, choose the tonic and "
            "mode in either order. "
            "You can press an answer's number instead of clicking its "
            "button: 1 is the first."
        )

    def generate(self, rng: random.Random) -> Question:
        """
        Draw a one-octave scale and offer scale names without revealing
        the answer on the staff.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            Eight staff notes and a choice of tonic and scale type.

        Examples
        --------
        >>> q = ScaleIdentification().generate(
        ...     random.Random(8)
        ... )
        >>> q.staff[0][0].name == q.staff[-1][
        ...     0
        ... ].name and not q.caption
        True
        """
        cfg = settings.scale_identification
        mode, _, clef, staff_key, notes = _scale_material(rng, cfg=cfg)
        tonic = notes[0]
        kind = _blank_scale(mode)[2:]
        modes = [_blank_scale(m)[2:] for m in settings.KEY_MODES]
        tonics = [
            Note.from_diatonic(letter, accidental=sign).name
            for sign in (-1, 0, 1)
            for letter in range(7)
        ]
        all_buttons = cfg.button_mode == "all"
        combined = cfg.question_type == "combined"
        if cfg.question_type == "mode":
            prompt, answer, pool = (
                "Identify the mode on the staff.",
                kind,
                modes,
            )
        elif cfg.question_type == "key":
            prompt, answer, pool = (
                "Identify the tonic of the scale on the staff.",
                tonic.name,
                tonics,
            )
        else:
            prompt, answer = (
                "Identify the scale on the staff.",
                f"{tonic.name} {kind}",
            )
            pool = [
                f"{tonic.name} {_blank_scale(m)[2:]}"
                for m in cfg.active_modes()
            ]
            pool += [
                f"{mode_tonic(k, mode=mode).name} {kind}" for k in range(-7, 8)
            ]
        if all_buttons:
            choices = modes if cfg.question_type == "mode" else tonics
            grid = {choice: divmod(i, 7) for i, choice in enumerate(choices)}
        else:
            choices = pick_distractors(
                answer,
                pool=pool,
                n=cfg.button_count - 1,
                rng=rng,
            )
            grid = (
                {choice: divmod(i, 5) for i, choice in enumerate(choices)}
                if len(choices) > 6
                else None
            )
        split_buttons = all_buttons and combined
        return Question(
            prompt,
            choices=choices,
            answer=answer,
            grid=grid,
            octaves=modes if split_buttons else None,
            second_label="Mode" if split_buttons else "Octave",
            joiner=" " if split_buttons else "",
            staff=[[note] for note in notes],
            clef=clef,
            key=staff_key,
            explanation=f"{tonic.name} {kind}: "
            + " ".join(note.name for note in notes),
        )


@register
class ScaleConstruction(Exercise):
    """
    Place the notes of a named scale on a blank staff, one after
    another.

    Examples
    --------
    >>> q = ScaleConstruction().generate(
    ...     random.Random(5)
    ... )
    >>> (
    ...     len(q.construct_scale or []),
    ...     q.choices,
    ...     q.key,
    ... )
    (8, [], 0)
    """

    name = "Scale Construction"
    category = "Scales & keys"
    description = "Place the notes of a named scale on the staff."
    par_seconds = 25.0

    def settings_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The clefs, scales and key signatures in force.

        Examples
        --------
        >>> ScaleConstruction().settings_signature().startswith(
        ...     "["
        ... )
        True
        """
        cfg = settings.scale_construction
        # Keep existing ascending reviews under their original settings
        # signature.
        parts = vars(cfg).copy()
        if cfg.motion == "ascending":
            del parts["motion"]
        if cfg.minor_keys is None:
            del parts["minor_keys"]
        return signature(parts)

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML.

        Examples
        --------
        >>> "Scale Construction" in ScaleConstruction().instructions()
        True
        """
        text = [
            (
                "<b>Scale Construction</b><br>The name of a scale is under "
                "the blank staff. Click the staff to place its "
                "notes from left to right in the requested direction, "
                "ending an octave from the first note: eight notes in "
                "all. The note follows the pointer, and each click puts it "
                "in the next place. "
                + (
                    "The name says which octave the first note is in, such "
                    "as G2 Major: start on that note, G in octave 2 "
                    "(middle C is C4), and place the remaining notes in the"
                    " requested direction."
                    if settings.scale_construction.octave
                    else (
                        "Any octave will do for the first note. End one "
                        "octave away."
                    )
                )
            ),
            (
                "The staff has no key signature, so a note that needs a "
                "sharp or a flat needs its own sign. Right click "
                "the staff or turn the mouse wheel to step through no sign,"
                " ♯ and ♭ for the next note (or choose a sign "
                "with the buttons), then click. Only the exact spelling "
                "counts, so G♯ is not A♭."
            ),
        ]
        if any(settings.scale_construction.staff_keys):
            text.append(
                "The staff may have a key signature, and it need not be the"
                " scale's. A note you place with no sign takes "
                "the sign that the staff's signature gives its letter: with"
                " two flats, B and E are flat. So a scale with a "
                "different signature needs signs where it differs: a C "
                "major scale on that staff needs a natural (♮) on "
                "its B and E, and a note that the staff does not flatten "
                "but the scale does needs a flat.",
            )
        if settings.scale_construction.steps:
            text.append(
                "Once the eight notes are placed, mark the steps between "
                "them. Two lines rise from each pair of "
                "neighboring notes to a point above them, and the point "
                "takes W for a whole step or H for a half step. "
                "Turn the mouse wheel, right click, press the W and H "
                "buttons or keys, or use the arrow keys to choose, "
                "then click the staff (or press Return) to mark it and move"
                " on to the next pair.",
            )
        text.append(
            "You can do all of this without the mouse. The Up and Down "
            "arrows (or the Higher and Lower buttons) move the "
            "next note a line or space, Page Up and Page Down (or the "
            "Octave buttons) an octave, and typing a letter from A "
            "to G jumps to the nearest note with that name. The Left and "
            "Right arrows, or the keys + - and 0, choose its "
            "sign. Press Return (or Place note) to place it. The line under"
            " the staff says what comes next.",
        )
        text.append(
            "Undo (or Backspace) takes back the last thing you placed, the "
            "steps first. Press Answer (or Return) when "
            "everything is placed. A wrong scale is cleared so that you can"
            " try again. A right one is played, each note "
            "turning green as it sounds.",
        )
        text.append(
            "A mode uses the signature of a major key, started from another"
            " degree: D Dorian has the notes of C major, "
            "started from D. Use the sliders button to choose the clefs, "
            "the scales, the key signatures, Motion, and whether to "
            "mark the steps.",
        )
        return "<br><br>".join(text)

    def generate(self, rng: random.Random) -> Question:
        """
        Name a scale to be placed on the staff.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            A blank staff captioned with the scale, such as 'D Major'.
            The eight notes in the selected
            direction are stored in `construct_scale`.

        Examples
        --------
        >>> q = ScaleConstruction().generate(
        ...     random.Random(1)
        ... )
        >>> scale = q.construct_scale or []
        >>> scale[0].name == scale[
        ...     -1
        ... ].name and q.accidentals
        True
        >>> q.check_scale(scale)
        True
        """
        cfg = settings.scale_construction
        mode, count, clef, staff_key, notes = _scale_material(rng, cfg=cfg)
        tonic = notes[0]
        kind = _blank_scale(mode)[2:]  # "Major", "minor", "Dorian"
        name = (
            f"{tonic.name}{tonic.octave} {kind}"
            if cfg.octave
            else f"{tonic.name} {kind}"
        )  # "G2 Major", or "G Major"
        steps = (
            [
                "W" if abs(b.midi - a.midi) == 2 else "H"
                for a, b in zip(notes, notes[1:], strict=False)
            ]
            if cfg.steps
            else None
        )
        motion = (
            "descending" if notes[0].midi > notes[-1].midi else "ascending"
        )
        direction = f" {motion}" if cfg.motion != "ascending" else ""
        caption = f"{name} ({motion})" if direction else name
        explanation = f"{caption}: " + " ".join(n.name for n in notes)
        if steps:
            explanation += f" ({' '.join(steps)})"
        if (
            staff_key and staff_key != count
        ):  # a signature that is not the scale's own: say so
            explanation += (
                ". The staff has "
                f"{format_key_signature(staff_key)}"
                ", but the scale has "
                f"{format_key_signature(count)}"
            )
        return Question(
            f"Place the notes of the {name}{direction} scale on the staff"
            + (", then mark its whole and half steps." if steps else "."),
            choices=[],
            answer=" ".join(f"{n.name}{n.octave}" for n in notes),
            clef=clef,
            key=staff_key,
            construct_scale=notes,
            construct_steps=steps,
            exact_octave=cfg.octave,
            accidentals=True,
            caption=caption,
            explanation=explanation,
        )


MAJOR_CHOICES = (
    "C♯",
    "F♯",
    "C",
    "D",
    "E",
    "F",
    "G",
    "A",
    "B",
    "C♭",
    "D♭",
    "E♭",
    "G♭",
    "A♭",
    "B♭",
    # the major keys that can be named: the naturals, and the sharp and
    # flat
    # keys
)
MAJOR_GRID = {
    "C♯": (0, 0),
    "F♯": (0, 3),
    "C": (1, 0),
    "D": (1, 1),
    "E": (1, 2),
    "F": (1, 3),
    "G": (1, 4),
    "A": (1, 5),
    "B": (1, 6),
    "C♭": (2, 0),
    "D♭": (2, 1),
    "E♭": (2, 2),
    "G♭": (2, 4),
    "A♭": (2, 5),
    "B♭": (2, 6),
    # the letters in the middle row, the sharps above them and the flats
    # below, as on the piano keyboard exercise
}


MINOR_CHOICES = (
    "C♯m",
    "D♯m",
    "F♯m",
    "G♯m",
    "A♯m",
    "Cm",
    "Dm",
    "Em",
    "Fm",
    "Gm",
    "Am",
    "Bm",
    "E♭m",
    "A♭m",
    "B♭m",
    # the minor keys that can be named: the ones on the circle, with
    # their
    # other names
)
MINOR_GRID = {
    "C♯m": (0, 0),
    "D♯m": (0, 1),
    "F♯m": (0, 3),
    "G♯m": (0, 4),
    "A♯m": (0, 5),
    "Cm": (1, 0),
    "Dm": (1, 1),
    "Em": (1, 2),
    "Fm": (1, 3),
    "Gm": (1, 4),
    "Am": (1, 5),
    "Bm": (1, 6),
    "E♭m": (2, 2),
    "A♭m": (2, 5),
    "B♭m": (2, 6),
    # laid out like the major keys: the letters in the middle row, the
    # sharps above and the flats below
}
NUMERAL_CHOICES: list[str] = list(
    NUMERALS,
    # the six chords of a key that are on the circle: capitals are
    # major,
    # small letters minor
)


@register
class CircleOfFifths(ChoiceExercise):
    """
    Questions on the circle of fifths: a relative major, a relative
    minor, or the Roman numeral of a chord.

    Examples
    --------
    >>> q = CircleOfFifths().generate(
    ...     random.Random(3)
    ... )
    >>> q.circle is not None and q.answer in q.choices
    True
    """

    name = "Circle of Fifths"
    category = "Scales & keys"
    description = (
        "Find relative keys and the chords of a key on the circle of fifths."
    )
    par_seconds = 7.0
    has_sound = False

    def practice_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The kinds of question in force.

        Examples
        --------
        >>> CircleOfFifths().settings_signature().startswith(
        ...     "["
        ... )
        True
        """
        return signature(settings.circle)

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML, with a paragraph for each kind of question that
            is switched on.

        Examples
        --------
        >>> "circle of fifths" in CircleOfFifths().instructions()
        True
        """
        kinds = settings.circle.active_questions()
        text = [
            (
                "<b>Circle of Fifths</b><br>This is the circle of fifths. "
                "The outer ring has the major keys, with C at the "
                "top and a fifth higher at each step clockwise. The inner "
                "ring has their relative minors, which have the "
                "same key signature: A minor sits under C major. Each "
                "question lights one cell and leaves its answer blank. "
                "A right answer lights the cell, writes its name and shows "
                "the key signature on the staff in the middle. A "
                "wrong one flashes the cell red, striped, so you can try "
                "again."
            ),
        ]
        if "major" in kinds:
            text.append(
                (
                    "<b>Relative major.</b> A minor key is shown. Press "
                    "the name of its relative major."
                ),
            )
        if "minor" in kinds:
            text.append(
                (
                    "<b>Relative minor.</b> A major key is shown. Press "
                    "the name of its relative minor."
                ),
            )
        if "numeral" in kinds:
            text.append(
                "<b>Roman numerals.</b> A key is in the middle, with its "
                "staff, and its six chords that are on the circle "
                "are lit: the major chords I, IV and V on the outer ring, "
                "and the minor chords ii, iii and vi on the inner "
                "ring. (There is a seventh chord, vii°, which is "
                "diminished, and has no place on the circle.) Press the "
                "numeral of the chord asked about. Capitals are major "
                "chords and small letters are minor ones. A right "
                "answer shows the numerals of all six chords.",
            )
        text.append(
            "Some keys have two names, such as B and C♭ or G♯m and A♭m. For"
            " those you press both names, in either order. "
            "Press the letter of a key, Shift and the letter for a sharp, "
            "or Ctrl and the letter for a flat. A numeral is "
            "on the number keys.",
        )
        return "<br><br>".join(text)

    def make_question(self, rng: random.Random) -> Question:
        """
        Pick a kind of question that is switched on, and ask it.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            A question on the circle: `circle_kind` says which kind.

        Examples
        --------
        >>> settings.circle.questions = {"minor"}
        >>> q = CircleOfFifths().generate(
        ...     random.Random(5)
        ... )
        >>> q.circle_kind, q.prompt
        ('minor', 'Which minor key is the relative minor of F major?')
        >>> settings.circle.questions = set(
        ...     settings.CIRCLE_QUESTIONS
        ... )
        """
        kind = rng.choice(settings.circle.active_questions())
        if kind == "numeral":
            return self._numeral_question(rng)
        place = rng.randrange(len(MAJORS))
        return (
            self._minor_question(place)
            if kind == "minor"
            else self._major_question(place)
        )

    @staticmethod
    def _major_question(place: int) -> Question:
        """
        Ask for the relative major of a minor key.

        Parameters
        ----------
        place : int
            The place on the circle of the pair.

        Returns
        -------
        Question
            The minor key is shown; the answer is its major. A key with
            two names needs both.

        Examples
        --------
        >>> # noinspection PyProtectedMember
        >>> q = CircleOfFifths._major_question(5)
        >>> q.answer, q.required, q.circle_ring
        ('B', ('B', 'C♭'), 'outer')
        >>> # noinspection PyProtectedMember
        >>> CircleOfFifths._major_question(
        ...     3
        ... ).required  # one name: nothing more to press
        ()
        """
        names = MAJORS[place]
        main, double = names[0], len(names) > 1
        both = " Press both of its names." if double else ""
        return Question(
            "Which major key is the relative major of "
            f"{display_minor(place)}"
            "?"
            f"{both}",
            choices=list(MAJOR_CHOICES),
            answer=main,
            required=names if double else (),
            grid=dict(MAJOR_GRID),
            circle=place,
            circle_kind="major",
            circle_ring="outer",
            caption=f"{MINORS[place][0][:-1]} minor",
            explanation=(
                f"{display_major(place)}"
                " and "
                f"{display_minor(place)}"
                " have the same key signature: "
                f"{format_key_signature(SIGNATURES[place])}"
                ". A relative minor starts on the sixth note of the "
                "major."
            ),
        )

    @staticmethod
    def _minor_question(place: int) -> Question:
        """
        Ask for the relative minor of a major key.

        Parameters
        ----------
        place : int
            The place on the circle of the pair.

        Returns
        -------
        Question
            The major key is shown; the answer is its minor. A key with
            two names needs both.

        Examples
        --------
        >>> # noinspection PyProtectedMember
        >>> q = CircleOfFifths._minor_question(7)
        >>> q.answer, q.required, q.circle_ring
        ('B♭m', ('B♭m', 'A♯m'), 'inner')
        """
        names = MINORS[place]
        main, double = names[0], len(names) > 1
        both = " Press both of its names." if double else ""
        return Question(
            "Which minor key is the relative minor of "
            f"{display_major(place)}"
            "?"
            f"{both}",
            choices=list(MINOR_CHOICES),
            answer=main,
            required=names if double else (),
            grid=dict(MINOR_GRID),
            circle=place,
            circle_kind="minor",
            circle_ring="inner",
            caption=f"{MAJORS[place][0]} major",
            explanation=(
                f"{display_major(place)}"
                " and "
                f"{display_minor(place)}"
                " have the same key signature: "
                f"{format_key_signature(SIGNATURES[place])}"
                ". A relative minor starts on the sixth note of the "
                "major."
            ),
        )

    @staticmethod
    def _numeral_question(rng: random.Random) -> Question:
        """
        Ask for the Roman numeral of one of the six chords of a key that
        are on the circle.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            A key is shown, with its six chords lit; the answer is the
            numeral of one of them.

        Examples
        --------
        >>> # noinspection PyProtectedMember
        >>> q = CircleOfFifths._numeral_question(
        ...     random.Random(2)
        ... )
        >>> (
        ...     q.circle_kind,
        ...     q.circle_key is not None,
        ...     q.answer in NUMERAL_CHOICES,
        ... )
        ('numeral', True, True)
        """
        key = rng.randrange(len(MAJORS))
        (ring, place), numeral = rng.choice(list(cells_of_key(key).items()))
        chords = numeral_chords(key)
        tonic = MAJORS[key][0]
        return Question(
            "In "
            f"{tonic}"
            " major, which Roman numeral is the chord "
            f"{chords[numeral]}"
            "?",
            choices=list(NUMERAL_CHOICES),
            answer=numeral,
            circle=place,
            circle_kind="numeral",
            circle_ring=ring,
            circle_key=key,
            caption=f"{tonic} major",
            explanation=f"In {tonic} major: "
            + ", ".join(f"{n} {chords[n]}" for n in NUMERALS)
            + ".",
        )


@register
class ChordQualities(ChoiceExercise):
    """
    Identify the quality of a triad or seventh chord in root position.

    Examples
    --------
    >>> q = ChordQualities().generate(
    ...     random.Random(9)
    ... )
    >>> len(q.staff[0]) in (
    ...     3,
    ...     4,
    ... ) and q.answer in q.choices
    True
    """

    name = "Chord Quality"
    category = "Chords"
    description = "Identify triads and seventh chords in root position."
    default_limit = 5
    par_seconds = 6.0

    def card_prompt(self, question: Question) -> str:
        """
        Say what to name on a flashcard.

        Parameters
        ----------
        question : Question
            The question on the card.

        Returns
        -------
        str
            The instruction.

        Examples
        --------
        >>> ChordQualities().card_prompt(
        ...     Question("", choices=[], answer="Major")
        ... )
        'Identify the Chord Quality.'
        """
        del question
        return "Identify the Chord Quality."

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML.

        Examples
        --------
        >>> "root position" in ChordQualities().instructions()
        True
        """
        return (
            "<b>Chord Quality</b><br>A chord is shown in root position. "
            "Press its type. Check the size of the "
            "intervals stacked above the lowest note to tell the types "
            "apart. You can press an answer's number instead "
            "of the button: 1 is the first."
        )

    def make_question(self, rng: random.Random) -> Question:
        """
        Make a chord in root position whose quality is to be named.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            The chord drawn as one stack of notes, with its type (such
            as 'minor 7th') as the answer.

        Examples
        --------
        >>> q = ChordQualities().generate(
        ...     random.Random(10)
        ... )
        >>> q.answer in CHORDS
        True
        """
        while True:
            clef = rng.choice(("treble", "bass"))
            quality = rng.choice(list(CHORDS))
            root = _random_note(rng, clef=clef, accidentals=True)
            chord = build(root, intervals=CHORDS[quality])
            if (
                all(abs(note.accidental) <= 1 for note in chord)
                and chord[-1].diatonic <= CLEF_RANGES[clef][1].diatonic + 3
            ):
                break
        choices = list(CHORDS)
        if self.button_settings().button_mode == "limited":
            rng.shuffle(choices)
        expl = f"{root.name} {quality}: " + " ".join(n.name for n in chord)
        return Question(
            "",
            choices=choices,
            answer=quality,
            staff=[chord],
            clef=clef,
            explanation=expl,
        )


# Where the lowest and highest note of an arpeggio may sit on each clef
# (up to two ledger lines either side of the staff).
ARPEGGIO_WINDOWS = {
    "treble": (Note(3, letter=6), Note(6, letter=0)),  # B3..C6
    "bass": (Note(2, letter=0), Note(4, letter=2)),  # C2..E4
    "alto": (Note(2, letter=6), Note(5, letter=1)),  # B2..D5
    "tenor": (Note(2, letter=4), Note(4, letter=6)),  # G2..B4
    "soprano": (Note(3, letter=3), Note(5, letter=5)),  # F3..A5
    "mezzo": (Note(3, letter=1), Note(5, letter=3)),  # D3..F5
    "baritone": (Note(2, letter=2), Note(4, letter=4)),  # E2..G4
}


@register
class ArpeggioNames(ChoiceExercise):
    """
    Name the type and the inversion of a broken chord.

    Examples
    --------
    >>> q = ArpeggioNames().generate(
    ...     random.Random(11)
    ... )
    >>> q.octaves is not None and len(q.staff) >= 4
    True
    """

    name = "Arpeggio Identification"
    category = "Chords"
    description = "Name the type and the inversion of a broken chord."
    par_seconds = 9.0

    def practice_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The clefs, chord types, inversions and key signatures in
            force.

        Examples
        --------
        >>> ArpeggioNames().settings_signature().startswith(
        ...     "["
        ... )
        True
        """
        return signature(settings.arpeggio)

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML.

        Examples
        --------
        >>> "inversion" in ArpeggioNames().instructions()
        True
        """
        return (
            "<b>Arpeggio Identification</b><br>A chord is played one note "
            "at a time, rising from its lowest note to "
            "the same note an octave higher. Press its type, then its "
            "inversion. The type is on the number keys, 1 for the "
            "first, and the inversion is on the home row: A for the first, "
            "S for the second and so on.<br><br>"
            "Find the chord's root by looking for the notes a third apart. "
            "The inversion is which chord tone is "
            "lowest: the root (root position), the third (1st inversion), "
            "the fifth (2nd inversion) or the seventh "
            "(3rd inversion, seventh chords only).<br><br>"
            "Use the sliders button to choose the clefs, the types of "
            "arpeggio, the inversions and key signatures."
        )

    def make_question(self, rng: random.Random) -> Question:
        """
        Make an arpeggio on one of the chosen clefs, in a chosen
        position.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            The arpeggio's notes one after another on a staff; the
            answer is the chord type and inversion, such as
            'major · 1st inversion'.

        Raises
        ------
        RuntimeError
            If no arpeggio fits the chosen clefs, chord types and
            inversions.

        Examples
        --------
        >>> q = ArpeggioNames().generate(
        ...     random.Random(12)
        ... )
        >>> " · " in q.answer
        True
        """
        cfg = settings.arpeggio
        for _ in range(500):
            chord_type = rng.choice(cfg.active_types())
            inversion = rng.choice(cfg.inversions_for(chord_type))
            clef = rng.choice(cfg.active_clefs())
            key = rng.choice(cfg.active_keys()) if cfg.key_signature else 0
            root = Note(
                4,
                letter=rng.randrange(7),
                accidental=rng.choice((-1, 0, 1)),
            )
            if (root.letter, root.accidental) in (
                (2, 1),
                (6, 1),
                (0, -1),
                (3, -1),
            ):  # E♯ B♯ C♭ F♭ are not worth asking
                continue
            notes = arpeggio(
                root,
                intervals=CHORDS[chord_type],
                inversion=inversion,
            )
            if any(
                abs(n.accidental) > 1 for n in notes
            ):  # no double sharps or flats
                continue
            low, high = (n.diatonic for n in ARPEGGIO_WINDOWS[clef])
            fits = [
                s
                for s in range(-28, 29, 7)
                if notes[0].diatonic + s >= low
                and notes[-1].diatonic + s <= high
            ]
            if not fits:
                continue
            shift = rng.choice(fits) // 7
            notes = [
                Note(
                    n.octave + shift,
                    letter=n.letter,
                    accidental=n.accidental,
                )
                for n in notes
            ]
            return self._question(
                chord_type,
                inversion=inversion,
                root=root,
                notes=notes,
                clef=clef,
                key=key,
                cfg=cfg,
            )
        raise RuntimeError("no arpeggio fits the chosen settings")

    @staticmethod
    def _question(
        chord_type: str,
        *,
        inversion: int,
        root: Note,
        notes: list[Note],
        clef: str,
        key: int,
        cfg: settings.ArpeggioSettings,
    ) -> Question:
        """
        Build the question for an arpeggio that has been chosen.

        Parameters
        ----------
        chord_type : str
            A key of `CHORDS`, such as "major".
        inversion : int
            0 for root position, 1 for the first inversion and so on.
            Keyword-only.
        root : Note
            The root of the chord. Keyword-only.
        notes : list of Note
            The arpeggio's notes, already moved to the right octave.
            Keyword-only.
        clef : str
            The clef to draw on. Keyword-only.
        key : int
            The key signature to draw. Keyword-only.
        cfg : ArpeggioSettings
            The settings, which decide which types and inversions have
            buttons. Keyword-only.

        Returns
        -------
        Question
            The notes drawn one after another, with a row of type
            buttons and a row of inversion buttons.

        Examples
        --------
        >>> cfg_ = settings.ArpeggioSettings()
        >>> notes_ = arpeggio(
        ...     Note.parse("C4"),
        ...     intervals=CHORDS["major"],
        ... )
        >>> # noinspection PyProtectedMember
        >>> q = ArpeggioNames._question(
        ...     "major",
        ...     inversion=0,
        ...     root=Note.parse("C4"),
        ...     notes=notes_,
        ...     clef="treble",
        ...     key=0,
        ...     cfg=cfg_,
        ... )
        >>> q.answer
        'major · root position'
        """
        joiner = " \u00b7 "
        types = cfg.active_types()
        inversions = sorted({i for t in types for i in cfg.inversions_for(t)})
        answer = f"{chord_type}{joiner}{INVERSION_NAMES[inversion]}"
        grid = (
            {t: divmod(i, 5) for i, t in enumerate(types)}
            if len(types) > 5
            else None
        )  # two rows once there are many
        expl = (
            f"{root.name} {chord_type}, {INVERSION_NAMES[inversion]}: "
            + " ".join(n.name for n in notes)
        )
        return Question(
            "What type of arpeggio is this, and which inversion?",
            choices=types,
            answer=answer,
            staff=[[n] for n in notes],
            clef=clef,
            explanation=expl,
            key=key,
            value="quarter",
            grid=grid,
            octaves=[INVERSION_NAMES[i] for i in inversions],
            second_label="Inversion",
            joiner=joiner,
        )


# Black keys: pitch class -> (letter, accidental) for the sharp name and
# for the flat name.
_BLACK_KEY_NAMES = {
    1: ((0, 1), (1, -1)),
    3: ((1, 1), (2, -1)),
    6: ((3, 1), (4, -1)),
    8: ((4, 1), (5, -1)),
    10: ((5, 1), (6, -1)),
}


def _key_tonic(count: int) -> Note:
    """
    Return the tonic of a major key.

    Parameters
    ----------
    count : int
        Sharps (positive) or flats (negative) in the key signature, from
        -7 to 7.

    Returns
    -------
    Note
        The tonic, in octave 4.

    Examples
    --------
    >>> str(_key_tonic(2)), str(_key_tonic(-3))
    ('D4', 'E♭4')
    """
    name = MAJOR_KEYS[count]
    return Note(
        4,
        letter="CDEFGAB".index(name[0]),
        accidental=1 if "♯" in name else -1 if "♭" in name else 0,
    )


def _key_spellings(
    pc: int,
    *,
    count: int | None,
) -> list[tuple[int, int]]:
    """
    Return the names that are correct for a piano key in a key
    signature.

    Notes of the key keep the spelling the key gives them (the F key is
    E♯ in C♯ major). Other white keys use their natural
    name. Other black keys are spelled with sharps in a sharp key and
    flats in a flat key; with no signature (or none given)
    either name is right.

    Parameters
    ----------
    pc : int
        The key's pitch class, 0 for C up to 11 for B.
    count : int or None
        The key signature: sharps if positive, flats if negative, 0 for
        none, or None for no key signature shown. Keyword-only.

    Returns
    -------
    list of tuple of (int, int)
        The correct (letter, accidental) pairs, most preferred first.

    Examples
    --------
    >>> _key_spellings(
    ...     6, count=None
    ... )  # a black key with no signature: F♯ or G♭
    [(3, 1), (4, -1)]
    >>> _key_spellings(
    ...     6, count=-2
    ... # in B♭ major it is not in the key, so a flat key spells it with
    ... # a flat
    ... )
    [(4, -1)]
    >>> _key_spellings(0, count=None)
    [(0, 0)]
    """
    diatonic = {}
    if count is not None:
        diatonic = {
            n.pitch_class: (n.letter, n.accidental)
            for n in build(
                _key_tonic(count),
                intervals=SCALES["Major (Ionian)"],
            )
        }
    if pc in diatonic:
        return [diatonic[pc]]
    if pc in NATURAL_LETTER_INDEX:
        return [(NATURAL_LETTER_INDEX[pc], 0)]
    sharp, flat = _BLACK_KEY_NAMES[pc]
    if count and count > 0:
        return [sharp]
    if count and count < 0:
        return [flat]
    return [sharp, flat]


def _spelled(
    midi: int,
    *,
    letter: int,
    accidental: int,
) -> Note:
    """
    Return the note that sounds as a MIDI number when written with a
    given letter name.

    Parameters
    ----------
    midi : int
        The MIDI note number.
    letter : int
        An index into `LETTERS`. Keyword-only.
    accidental : int
        The accidental it is written with. Keyword-only.

    Returns
    -------
    Note
        The note; B3 written as C♭ is C♭4.

    Examples
    --------
    >>> str(
    ...     _spelled(61, letter=1, accidental=-1)
    ... )  # MIDI 61 written as D♭
    'D♭4'
    >>> str(
    ...     _spelled(59, letter=0, accidental=-1)
    ... )  # MIDI 59 written as C♭
    'C♭4'
    """
    return Note(
        (midi - accidental - NATURAL_SEMITONES[letter]) // 12 - 1,
        letter=letter,
        accidental=accidental,
    )


@register
class KeyboardNotes(ChoiceExercise):
    """
    Name the highlighted key on a piano keyboard.

    Examples
    --------
    >>> q = KeyboardNotes().generate(
    ...     random.Random(13)
    ... )
    >>> q.keyboard is not None and q.answer in q.choices
    True
    """

    name = "Keyboard Note Identification"
    category = "Notation"
    description = "Name the highlighted key on a piano keyboard."
    par_seconds = 3.0

    def card_prompt(self, question: Question) -> str:
        """
        Say what to name on a flashcard. Letter names give the octave if
        it counts, and follow the key signature if one is shown.

        Parameters
        ----------
        question : Question
            The question on the card.

        Returns
        -------
        str
            The instruction.

        Examples
        --------
        >>> KeyboardNotes().card_prompt(
        ...     Question(
        ...         "",
        ...         choices=[],
        ...         answer="C4",
        ...         octaves=["C4"],
        ...     )
        ... )
        'Identify the note by letter and octave.'
        """
        q = question
        if settings.keyboard.naming != "letters":
            return _note_card_prompt(q, naming=settings.keyboard.naming)
        prompt = (
            "Identify the note by letter and octave."
            if q.octaves
            else "Identify the note by letter."
        )
        if q.key_staff:
            prompt += " Use the spelling for the displayed key signature."
        return prompt

    def practice_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The keyboard range, black keys, octave and key signature
            settings, and the naming in force.

        Examples
        --------
        >>> KeyboardNotes().settings_signature().startswith(
        ...     "["
        ... )
        True
        """
        # Preserve the signature format of saved review questions.
        parts = asdict(settings.keyboard)
        naming = parts.pop("naming")
        return signature(parts, naming)

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML, with paragraphs added for the octave and key
            signature settings that are on.

        Examples
        --------
        >>> "highlighted" in KeyboardNotes().instructions()
        True
        """
        cfg = settings.keyboard
        text = [
            (
                "<b>Keyboard Note Identification</b><br>One key on the "
                "keyboard is highlighted. Press the button with its name, "
                "or type its name on the keyboard: the letter for a "
                "natural, Shift and the letter for a sharp, Ctrl and "
                "the letter for a flat."
            ),
        ]
        if cfg.naming in settings.DEGREE_NAMINGS:
            text = [
                (
                    "<b>Keyboard Note Identification</b><br>Name the "
                    "highlighted key by its scale degree, 1–7, in the major"
                    " key "
                    "of the signature. Without a key signature, use C "
                    "major. Altered degrees have a prefix, such "
                    "as ♭3 or ♯4. Type the degree digit; add Shift for a "
                    "sharp or Ctrl for a flat, "
                    "and Alt for a double alteration."
                ),
            ]
        if cfg.require_octave:
            text.append(
                "Choose its octave too, from the row below, using the "
                "shortcuts shown on the buttons. "
                "Octaves count up from C, so middle C is the C in octave 4.",
            )
        if cfg.key_signature:
            text.append(
                "A key signature is shown above the keyboard. Name the key "
                "the way that signature spells it. Only "
                "that spelling counts, so F♯ and G♭ are not "
                "interchangeable. A black key that is not in the key "
                "is spelled with sharps in a sharp key and with flats in a "
                "flat key.",
            )
        else:
            text.append(
                (
                    "Black keys have two names, such as C♯ and D♭. Either "
                    "one is accepted."
                ),
            )
        return "<br><br>".join(text)

    def make_question(self, rng: random.Random) -> Question:
        """
        Make a keyboard with one key highlighted.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            The keyboard, a grid of name buttons (and a row of octave
            buttons if octaves are asked), and the key's name as
            the answer, with the other spelling of a black key accepted.

        Examples
        --------
        >>> q = KeyboardNotes().generate(
        ...     random.Random(14)
        ... )
        >>> # noinspection PyUnresolvedReferences
        >>> q.keyboard_range[
        ...     0
        ... ] <= q.keyboard.midi <= q.keyboard_range[1]
        True
        """
        cfg = settings.keyboard
        lo, hi = sorted((cfg.low, cfg.high))
        span = range(lo, hi + 1)
        naturals = [midi for midi in span if midi % 12 in NATURAL_LETTER_INDEX]
        candidates = list(span) if cfg.black_keys else naturals
        candidates = candidates or [lo]
        count = rng.choice(cfg.active_keys()) if cfg.key_signature else None
        midi = rng.choice(candidates)

        return self._question_for(
            midi,
            count=count,
            candidates=candidates,
            keyboard_range=(lo, hi),
            cfg=cfg,
        )

    @staticmethod
    def _question_for(
        midi: int,
        *,
        count: int | None,
        candidates: list[int],
        keyboard_range: tuple[int, int],
        cfg: settings.KeyboardSettings,
    ) -> Question:
        """
        Spell a selected piano key and build its accepted answers.

        Parameters
        ----------
        midi : int
            The selected key.
        count : int or None
            Written key signature, or None for enharmonic answers.
        candidates : list of int
            Playable keys used to determine the available octaves.
        keyboard_range : tuple of int
            Inclusive bounds of the displayed keyboard.
        cfg : KeyboardSettings
            Naming, accidental, and octave preferences.

        Returns
        -------
        Question
            The highlighted key and its answer buttons.

        Examples
        --------
        >>> q = KeyboardNotes._question_for(
        ...     60, count=None, candidates=[60],
        ...     keyboard_range=(60, 60),
        ...     cfg=settings.KeyboardSettings(),
        ... )
        >>> q.answer
        'C'
        """
        naming = cfg.naming
        spelled = [
            _spelled(midi, letter=letter, accidental=acc)
            for letter, acc in _key_spellings(midi % 12, count=count)
        ]
        key = spelled[0]  # Use the signature’s spelling for playback.
        names = [spell(n, naming=naming, key=count or 0) for n in spelled]
        answer, accept = names[0], tuple(names[1:])
        octaves = None
        if cfg.require_octave:
            octaves = [
                str(o)
                for o in sorted(
                    {
                        _spelled(
                            m,
                            letter=letter,
                            accidental=accidental,
                        ).octave
                        for m in candidates
                        for letter, accidental in _key_spellings(
                            m % 12,
                            count=count,
                        )[:1]  # the first spelling of each
                    },
                )
            ]
            names_with_octaves = [
                spell(
                    n,
                    naming=naming,
                    key=count or 0,
                    octave=True,
                )
                for n in spelled
            ]
            answer, accept = (
                names_with_octaves[0],
                tuple(names_with_octaves[1:]),
            )

        if len(spelled) > 1:
            explanation = f"{names[0]} and {names[1]} are the same black key."
        elif count is not None:
            # noinspection PyTypeChecker
            in_key = midi % 12 in {
                n.pitch_class
                for n in build(
                    _key_tonic(count),
                    intervals=SCALES["Major (Ionian)"],
                )
            }
            # noinspection PyTypeChecker
            explanation = (
                "In "
                f"{MAJOR_KEYS[count]}"
                " major ("
                f"{format_key_signature(count)}"
                ") this key is called "
                f"{names[0]}"
                "."
            )
            if not in_key and midi % 12 not in NATURAL_LETTER_INDEX:
                # noinspection PyTypeChecker
                explanation += (
                    " It is not in the key, so it is spelled with "
                    f"{('sharps' if count > 0 else 'flats')}"
                    "."
                )
        else:
            explanation = ""

        # One button per name: sharps on the top row, naturals in the
        # middle, flats below, a column per letter.
        # A key signature can need any spelling (E♯, C♭ ...), so it gets
        # the full set.
        if cfg.key_signature:
            extra = [
                (letter, acc, 0 if acc > 0 else 2)
                for letter in range(7)
                for acc in (1, -1)
            ]
        elif cfg.black_keys:
            extra = [
                (letter, acc, row)
                for (sharp, flat) in _BLACK_KEY_NAMES.values()
                for (letter, acc), row in ((sharp, 0), (flat, 2))
            ]
        else:
            extra = []
        if naming in settings.DEGREE_NAMINGS:
            pool = {(letter, 0) for letter in range(7)} | {
                (letter, acc) for letter, acc, _row in extra
            }
            choices, grid = _degree_choices(
                pool,
                key=count or 0,
                naming=naming,
            )
        else:
            grid, choices = {}, []
            for letter in range(7):
                n = spell(Note(4, letter=letter), naming=naming)
                choices.append(n)
                grid[n] = (1, letter)
            for letter, acc, row in extra:
                n = spell(
                    Note(4, letter=letter, accidental=acc),
                    naming=naming,
                )
                choices.append(n)
                grid[n] = (row, letter)

        return Question(
            "",
            choices=choices,
            answer=answer,
            keyboard=key,
            accept=accept,
            explanation=explanation,
            grid=grid,
            keyboard_range=keyboard_range,
            octaves=octaves,
            key=count or 0,
            key_staff=cfg.key_signature,
            joiner=" / " if naming in settings.DEGREE_NAMINGS else "",
        )


@register
class NoteConstruction(Exercise):
    """
    Place a named note on the staff.

    Examples
    --------
    >>> q = NoteConstruction().generate(
    ...     random.Random(15)
    ... )
    >>> q.construct is not None and q.prompt.startswith(
    ...     "Place "
    ... )
    True
    """

    name = "Note Construction"
    category = "Notation"
    description = "Place the named note on the staff."
    par_seconds = 6.0

    def card_prompt(self, question: Question) -> str:
        """
        Say which note to place, whichever way the on-screen prompt
        words it.

        Parameters
        ----------
        question : Question
            The question on the card.

        Returns
        -------
        str
            The instruction.

        Examples
        --------
        >>> NoteConstruction().card_prompt(
        ...     Question(
        ...         "Place F♯4 on the staff.",
        ...         choices=[],
        ...         answer="F♯4",
        ...     )
        ... )
        'Place F♯4 on the staff.'
        >>> NoteConstruction().card_prompt(
        ...     Question("", choices=[], answer="B♭3")
        ... )
        'Place B♭3 on the staff.'
        """
        q = question
        target = (
            (q.prompt or q.answer)
            .removeprefix("Place ")
            .removesuffix(".")
            .removesuffix(" on the staff")
        )
        return f"Place {target} on the staff."

    def settings_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The clefs, accidentals and key signature settings, and the
            naming in force.

        Examples
        --------
        >>> NoteConstruction().settings_signature().startswith(
        ...     "["
        ... )
        True
        """
        cfg = settings.construction
        parts = vars(cfg).copy()
        if cfg.question_type == "notes" or cfg.degrees == set(range(1, 8)):
            del parts["degrees"]
        if cfg.octave:
            del parts["octave"]
        if cfg.staff_keys is None:
            del parts["staff_keys"]
        if cfg.question_type == "notes":
            for field in (
                "keys",
                "minor_keys",
                "major",
                "minor",
                "key_signature",
            ):
                del parts[field]
        else:
            del parts["question_type"]
            if not cfg.minor:
                del parts["minor"]
            if not cfg.minor or not cfg.major:
                del parts["major"]
            if (
                not cfg.minor
                or not cfg.key_signature
                or cfg.minor_keys is None
                or cfg.minor_keys == cfg.keys
            ):
                del parts["minor_keys"]
        return signature(parts, settings.note_names.naming)

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML, with paragraphs added for the key signature and
            accidental settings that are on.

        Examples
        --------
        >>> "Click the staff" in NoteConstruction().instructions()
        True
        """
        cfg = settings.construction
        text = [
            (
                "<b>Note Construction</b><br>A note name is shown. Click "
                "the staff where that note belongs. The octave "
                "counts when shown: the number says which C-to-B you mean, "
                "and middle C is C4. Otherwise, any octave works. "
                "On a grand staff, click the upper"
                "staff for notes from middle C up and the lower staff for "
                "the notes below it."
            ),
        ]
        if (
            cfg.question_type == "scale"
            and settings.note_names.naming in settings.DEGREE_NAMINGS
        ):
            text.append(
                "The question gives a scale degree in the named key. Degree"
                " 1 is the tonic; "
                "a prefix such as ♭3 or ♯4 lowers or raises the degree. "
                "The octave is the written note's C-to-B octave, not a "
                "count from the tonic.",
            )
        if cfg.key_signature:
            text.append(
                "A key signature is drawn at the start of the staff "
                "according to Staff Key. It applies to every note of that "
                "letter, so in G major you place F♯ on the F line with no "
                "sign. A note that the key does not "
                "give you needs its own sign. The staff signature may "
                "differ from the key named in the prompt.",
            )
        text.append(
            "Choose ♯, ♮ or ♭ before placing a note, or right-click the "
            "staff to cycle through the signs. "
            "♮ cancels a sharp or flat from the key signature. Only the "
            "exact spelling counts.",
        )
        text.append(
            "You can do all of this without the mouse. The Up and Down "
            "arrows (or the Higher and Lower buttons) move the "
            "note a line or space, and Page Up and Page Down (or the Octave"
            " buttons) an octave. Typing a letter from A to G "
            "jumps to the nearest note with that name. Press Return (or "
            "Place note) to place it. "
            "The Left and Right arrows, or the keys + - and 0, choose a sign.",
        )
        text.append(
            (
                "A wrong click shows the note you placed so you can adjust"
                " and try again."
            ),
        )
        return "<br><br>".join(text)

    def generate(self, rng: random.Random) -> Question:
        """
        Make a note name to be placed on the staff.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            A prompt such as 'Place F♯4 on the staff.'; the answer is
            the note's name, and `construct` is the note to place.

        Examples
        --------
        >>> q = NoteConstruction().generate(
        ...     random.Random(16)
        ... )
        >>> q.answer in q.prompt
        True
        """
        cfg = settings.construction
        naming = settings.note_names.naming
        clef = rng.choice(cfg.active_clefs())
        notes_only = cfg.question_type == "notes"
        minor = (
            not notes_only
            and cfg.minor
            and (not cfg.major or rng.choice((False, True)))
        )
        count = (
            rng.choice(self._scale_keys(minor, cfg=cfg))
            if cfg.key_signature and not notes_only
            else 0
        )
        diatonic = rng.choice(
            self._positions(clef, count=count, minor=minor, cfg=cfg),
        )
        staff_keys = self._staff_keys(count, keys=cfg.staff_keys)
        staff_signature = (
            rng.choice(staff_keys) if len(staff_keys) > 1 else staff_keys[0]
        )
        implied = key_accidental(
            diatonic % 7,
            count=staff_signature if notes_only else count,
        )
        accidental = implied
        if cfg.accidentals and rng.random() < (
            0.4 if cfg.key_signature else 0.5
        ):
            accidental = rng.choice(
                [a for a in (-1, 0, 1) if a != implied],
            )  # a sign that differs from the key
        note = Note.from_diatonic(diatonic, accidental=accidental)
        return self._placement(
            note,
            clef=clef,
            count=count,
            minor=minor,
            staff_signature=staff_signature,
            cfg=cfg,
            naming=naming,
        )

    @staticmethod
    def _scale_keys(
        minor: bool,
        *,
        cfg: settings.ConstructionSettings,
    ) -> list[int]:
        """
        Return selectable scale signatures for one mode.

        Parameters
        ----------
        minor : bool
            Whether to use the minor key selection.
        cfg : ConstructionSettings
            Options for the construction exercise.

        Returns
        -------
        list of int
            The signature counts used by the question generator.

        Examples
        --------
        >>> cfg = settings.ConstructionSettings()
        >>> bool(NoteConstruction()._scale_keys(False, cfg=cfg))
        True
        """
        if not cfg.key_signature or cfg.question_type == "notes":
            return [0]
        return (
            sorted(cfg.minor_keys)
            if minor and cfg.minor_keys
            else cfg.active_keys()
        )

    @staticmethod
    def _staff_keys(count: int, *, keys: set[int] | None) -> list[int]:
        """
        Return staff signatures allowed for a scale key.

        Parameters
        ----------
        count : int
            Scale signature.
        keys : set of int or None
            Enabled staff signatures, or None to follow the scale.

        Returns
        -------
        list of int
            Selected staff signatures, or the scale signature when the
            staff follows the key.

        Examples
        --------
        >>> bool(NoteConstruction()._staff_keys(0, keys=None))
        True
        """
        return [count] if keys is None else sorted(keys) or [0]

    @staticmethod
    def _positions(
        clef: str,
        *,
        count: int,
        minor: bool,
        cfg: settings.ConstructionSettings,
    ) -> range | list[int]:
        """
        Return staff positions that meet the degree selection.

        Parameters
        ----------
        clef : str
            Selected clef.
        count : int
            Scale signature.
        minor : bool
            Whether degrees are relative to the minor tonic.
        cfg : ConstructionSettings
            Options for the construction exercise.

        Returns
        -------
        range or list of int
            Absolute diatonic positions.

        Examples
        --------
        >>> bool(
        ...     NoteConstruction()._positions(
        ...         "treble", count=0, minor=False,
        ...         cfg=settings.ConstructionSettings(),
        ...     )
        ... )
        True
        """
        low, high = settings.DEFAULT_RANGES[clef]
        positions = range(low, high + 1)
        if (
            cfg.question_type == "notes"
            or not cfg.degrees
            or cfg.degrees == set(range(1, 8))
        ):
            return positions
        tonic = 4 * count + (5 if minor else 0)
        return [d for d in positions if (d - tonic) % 7 + 1 in cfg.degrees]

    def _groups(
        self,
        cfg: settings.ConstructionSettings,
    ) -> Iterator[tuple[str, bool, int, int, range | list[int]]]:
        """
        Group construction cards by clef, mode, scale key and staff
        signature.

        Parameters
        ----------
        cfg : ConstructionSettings
            Enabled clefs, modes, degrees, and signatures.

        Yields
        ------
        tuple
            A combination of settings and its eligible diatonic
            positions.

        Examples
        --------
        >>> cfg = settings.ConstructionSettings()
        >>> next(NoteConstruction()._groups(cfg))[
        ...     0
        ... ] in settings.RANGE_KEYS
        True
        """
        modes = [False]
        if cfg.minor and cfg.question_type != "notes":
            modes = [False, True] if cfg.major else [True]
        for clef in cfg.active_clefs():
            for minor in modes:
                for count in self._scale_keys(minor, cfg=cfg):
                    positions = self._positions(
                        clef,
                        count=count,
                        minor=minor,
                        cfg=cfg,
                    )
                    for staff_key in self._staff_keys(
                        count,
                        keys=cfg.staff_keys,
                    ):
                        yield clef, minor, count, staff_key, positions

    def card_count(self) -> int:
        """
        Count distinct construction cards without rendering them.

        Returns
        -------
        int
            Number of eligible written placements under the current
            settings.

        Examples
        --------
        >>> NoteConstruction().card_count() > 0
        True
        """
        cfg = settings.construction
        return sum(len(positions) for *_, positions in self._groups(cfg)) * (
            3 if cfg.accidentals else 1
        )

    def daily_candidates(self, rng: random.Random) -> Iterator[Question]:
        """
        Visit all eligible placements in a randomized order.

        Parameters
        ----------
        rng : random.Random
            Source for the order of the signatures and placements.

        Yields
        ------
        Question
            One playable placement for each combination.

        Examples
        --------
        >>> next(
        ...     NoteConstruction().daily_candidates(
        ...         random.Random(5)
        ...     )
        ... ).construct is not None
        True
        """
        cfg = settings.construction
        naming = settings.note_names.naming
        spellings = 3 if cfg.accidentals else 1
        groups = []
        for clef, minor, count, staff_key, positions in self._groups(cfg):
            size = len(positions) * spellings
            if size:
                groups.append(
                    (
                        clef,
                        minor,
                        count,
                        staff_key,
                        positions,
                        rng.sample(range(size), size),
                    ),
                )
        while groups:
            index = rng.randrange(len(groups))
            clef, minor, count, staff_key, positions, remaining = groups[index]
            pitch, sign = divmod(remaining.pop(), spellings)
            step = positions[pitch]
            accidental = (
                sign - 1
                if cfg.accidentals
                else key_accidental(
                    step % 7,
                    count=staff_key if cfg.question_type == "notes" else count,
                )
            )
            if not remaining:
                groups[index] = groups[-1]
                groups.pop()
            yield self._placement(
                Note.from_diatonic(step, accidental=accidental),
                clef=clef,
                count=count,
                minor=minor,
                staff_signature=staff_key,
                cfg=cfg,
                naming=naming,
            )

    def review_question(
        self,
        question: Question,
        *,
        same_settings: bool,
    ) -> Question | None:
        """
        Determine whether an introduced placement belongs to the current
        construction catalog.

        Parameters
        ----------
        question : Question
            Stored construction card.
        same_settings : bool
            Whether its original settings are still active.

        Returns
        -------
        Question or None
            The playable card if its placement and prompt remain
            eligible.

        Examples
        --------
        >>> ex = NoteConstruction()
        >>> q = ex.generate(random.Random(3))
        >>> ex.review_question(
        ...     q, same_settings=True
        ... ) == q
        True
        """
        if same_settings:
            return question
        cfg = settings.construction
        naming = settings.note_names.naming
        note = question.construct
        minor = question.minor
        notes_only = cfg.question_type == "notes"
        if (
            note is None
            or question.notes_only != notes_only
            or question.clef not in cfg.active_clefs()
        ):
            return None
        if (
            minor
            and (notes_only or not cfg.minor)
            or (not minor and not notes_only and cfg.minor and not cfg.major)
        ):
            return None
        count = question.key
        staff = (
            count
            if question.staff_signature is None
            else question.staff_signature
        )
        if count not in self._scale_keys(
            minor,
            cfg=cfg,
        ) or staff not in self._staff_keys(count, keys=cfg.staff_keys):
            return None
        if note.diatonic not in self._positions(
            question.clef,
            cfg=cfg,
            count=count,
            minor=minor,
        ):
            return None
        if not cfg.accidentals and note.accidental != key_accidental(
            note.letter,
            count=staff if notes_only else count,
        ):
            return None
        rebuilt = self._placement(
            note,
            clef=question.clef,
            count=count,
            minor=minor,
            staff_signature=staff,
            cfg=cfg,
            naming=naming,
        )
        return rebuilt if rebuilt.item_key() == question.item_key() else None

    @staticmethod
    def _placement(
        note: Note,
        *,
        clef: str,
        count: int,
        minor: bool,
        staff_signature: int,
        cfg: settings.ConstructionSettings,
        naming: str,
    ) -> Question:
        """
        Build the question for a selected placement.

        Parameters
        ----------
        note : Note
            Required written pitch.
        clef : str
            Staff clef.
        count : int
            Scale signature.
        minor : bool
            Whether the scale is minor.
        staff_signature : int
            Signature printed on the staff.
        cfg : ConstructionSettings
            Options for the construction exercise.
        naming : str
            Selected pitch naming system.

        Returns
        -------
        Question
            The playable construction card.

        Examples
        --------
        >>> NoteConstruction()._placement(
        ...     Note.parse("C4"),
        ...     clef="treble",
        ...     count=0,
        ...     minor=False,
        ...     staff_signature=0,
        ...     cfg=settings.ConstructionSettings(),
        ...     naming="letters",
        ... ).construct.name
        'C'
        """
        notes_only = cfg.question_type == "notes"
        tonic = (
            mode_tonic(count, mode="Natural minor (Aeolian)").name
            if minor
            else MAJOR_KEYS[count]
        )
        key_name = f"{tonic} {'minor' if minor else 'major'}"
        accidental = note.accidental
        if notes_only and naming in settings.DEGREE_NAMINGS:
            naming = "letters"
        name = spell(
            note,
            naming=naming,
            key=count,
            octave=cfg.octave,
            minor=minor,
        )
        prompt = name if notes_only else f"Place {name} on the staff."
        if naming in settings.DEGREE_NAMINGS:
            degree = spell(note, naming=naming, key=count, minor=minor)
            if naming == "degrees":
                octave = (
                    str(note.octave).translate(
                        str.maketrans("0123456789-", "₀₁₂₃₄₅₆₇₈₉₋"),
                    )
                    if cfg.octave
                    else ""
                )
                prompt = f"{tonic}{'m' if minor else 'M'} {degree}{octave}"
            else:
                target = (
                    f"the {degree}"
                    if naming == "functions"
                    else f"degree {degree}"
                )
                register = f", octave {note.octave}," if cfg.octave else ""
                prompt = f"Place {target}{register} in {key_name}."
        staff_accidental = key_accidental(note.letter, count=staff_signature)
        explanation = ""
        word = {1: "sharp", -1: "flat", 0: "natural"}
        if accidental != staff_accidental:
            explanation = (
                f"{note.name} needs a {word[accidental]} on this staff."
            )
        elif staff_accidental:
            explanation = (
                "The staff signature already makes this note "
                f"{word[staff_accidental]}"
                ", so it needs no sign."
            )
        return Question(
            prompt,
            choices=[],
            answer=name,
            clef=clef,
            construct=note,
            any_octave=not cfg.octave,
            notes_only=notes_only,
            accidentals=True,
            key=count,
            minor=minor,
            staff_signature=staff_signature
            if staff_signature != count
            else None,
            explanation=explanation,
            caption=prompt
            if notes_only or naming in settings.DEGREE_NAMINGS
            else "",
        )


# What to say about where each clef goes, for the explanation after a
# question about it.
CLEF_FACTS = {
    "treble": (
        "The treble clef is the G clef on the second line: its curl "
        "circles the G above middle C."
    ),
    "bass": (
        "The bass clef is the F clef on the fourth line: its two dots are "
        "either side of the F below middle C."
    ),
    "alto": (
        "The alto clef is the C clef on the middle line: its middle is on "
        "middle C."
    ),
    "tenor": (
        "The tenor clef is the C clef on the fourth line: its middle is on"
        " middle C."
    ),
    "soprano": (
        "The soprano clef is the C clef on the bottom line: its middle is "
        "on middle C."
    ),
    "mezzo": (
        "The mezzo-soprano clef is the C clef on the second line: its "
        "middle is on middle C."
    ),
    "baritone": (
        "The baritone clef is the F clef on the middle line, or the C clef"
        " on the top line: both are used."
    ),
    "french": (
        "The French violin clef is the G clef on the bottom line, a step "
        "lower than the treble clef."
    ),
    "subbass": (
        "The subbass clef is the F clef on the top line, a step higher "
        "than the bass clef."
    ),
}


@register
class ClefBasics(ChoiceExercise):
    """
    Put a named clef on a blank staff: choose the G, C or F symbol and
    put it on the line that makes the clef asked for.

    Examples
    --------
    >>> q = ClefBasics().generate(random.Random(1))
    >>> (
    ...     q.answer == q.place_clef
    ...     and q.place_clef in settings.CLEF_BASICS_CLEFS
    ... )
    True
    """

    name = "Clef Basics"
    category = "Notation"
    description = "Identify clef symbols and place them on the staff."
    par_seconds = 5.0
    has_sound = False

    def settings_signature(self) -> str:
        """
        Use button preferences for reviews only when the learner answers
        with buttons.

        Returns
        -------
        str
            The signature for the active question type.

        Examples
        --------
        Changing Button count leaves staff-placement reviews available.
        """
        return (
            self.practice_signature()
            if settings.clef_basics.active_type() == "construction"
            else super().settings_signature()
        )

    def practice_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The clefs asked for.

        Examples
        --------
        >>> ClefBasics().settings_signature().startswith(
        ...     "["
        ... )
        True
        """
        return signature(settings.clef_basics)

    def instructions(self) -> str:
        """
        Return the help text for the exercise, for the kind of question
        that is being asked.

        Returns
        -------
        str
            Simple HTML.

        Examples
        --------
        >>> "Clef Basics" in ClefBasics().instructions()
        True
        """
        if settings.clef_basics.active_type() == "identification":
            return (
                "<b>Clef Basics: Clef Identification</b><br>A clef is drawn"
                " on a staff. Press the button with its name. The "
                "C clef is the alto, tenor, mezzo-soprano or soprano clef, "
                "by the line it is centered on (the line of middle C); "
                "the G clef is the treble clef, or the French violin clef "
                "on the bottom line; the F clef is the bass clef, "
                "the baritone clef on the middle line, or the subbass clef "
                "on the top line. The baritone clef can also be "
                "written as a C clef on the top line.<br><br>Use the "
                "sliders button to choose which clefs are asked for, and "
                "to ask you to put a named clef on a blank staff instead."
            )
        return (
            "<b>Clef Basics: Clef Construction</b><br>The staff is blank "
            "and the name of a clef is shown. Every clef is one of "
            "three symbols, the G clef, the C clef or the F clef, put on a "
            "line: the G clef circles the G line, the F clef has "
            "its dots around the F line, and a C clef is centered on middle"
            " C. So the mezzo-soprano clef is the C clef on the "
            "second line.<br><br>Choose the symbol with the buttons under "
            "the staff, the mouse wheel or a right click, then "
            "click where it goes. The clef can be tried on the lines, the "
            "spaces and the ledger lines above and below the "
            "staff, but only one place is right, except for the baritone "
            "clef, which is the F clef on the middle line or the "
            "C clef on the top line.<br><br>Without the mouse: the Left and"
            " Right arrows choose the symbol, the Up and Down "
            "arrows move it up or down a line or space, and Answer (or "
            "Return) places it.<br><br>Use the sliders button to "
            "choose which clefs are asked for, and to ask you to name a "
            "clef on a staff instead."
        )

    def make_question(self, rng: random.Random) -> Question:
        """
        Name a clef to place, or draw a clef to name.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            For construction, a blank staff and the name of the clef,
            which is the question written under the staff. For
            identification, a staff with the clef drawn on it, and a
            button for each clef that can be asked for.

        Examples
        --------
        >>> q = ClefBasics().generate(random.Random(3))
        >>> q.prompt.startswith(
        ...     "Place the "
        ... ) and q.caption == q.prompt
        True
        >>> settings.clef_basics.question_type = (
        ...     "identification"
        ... )
        >>> q = ClefBasics().generate(random.Random(3))
        >>> (
        ...     q.answer in q.choices,
        ...     q.place_clef,
        ...     q.caption,
        ... )
        (True, '', 'Which clef is this?')
        >>> settings.clef_basics.question_type = (
        ...     "construction"
        ... )
        """
        cfg = settings.clef_basics
        clef = rng.choice(cfg.active_clefs())
        name = settings.CLEF_NAMES[clef]
        if cfg.active_type() == "identification":
            names = [settings.CLEF_NAMES[c] for c in cfg.answer_clefs()]
            return Question(
                "Which clef is this?",
                choices=names,
                answer=name,
                grid={
                    choice: divmod(i, 5) for i, choice in enumerate(names)
                },  # rows of five, not one long row
                clef=clef,
                show_staff=True,
                # the question goes under the staff, in the white area
                caption="Which clef is this?",
                explanation=CLEF_FACTS[clef],
            )
        words = (
            name if name.startswith("French") else name.lower()
        )  # "mezzo-soprano", but "French violin"
        return Question(
            f"Place the {words} clef.",
            choices=[],
            answer=clef,
            show_staff=True,
            # the question goes under the staff, in the white area
            caption=f"Place the {words} clef.",
            place_clef=clef,
            explanation=CLEF_FACTS[clef],
        )


@register
class NotationIdentification(ChoiceExercise):
    """
    Identify the highlighted part of a written phrase.

    Examples
    --------
    >>> q = NotationIdentification().generate(
    ...     random.Random(2)
    ... )
    >>> bool(
    ...     q.staff or q.notation_excerpt
    ... ) and q.answer in q.choices
    True
    """

    name = "Notation Identification"
    category = "Notation"
    description = (
        "Name a highlighted marking or find a named component on the staff."
    )
    has_sound = False

    default_limit = 4
    _phrases = ("E4 G4 A4 G4", "B4 A4 G4 E4", "G4 B4 D5 C5", "D5 C5 A4 B4")

    def settings_signature(self) -> str:
        """
        Use button preferences for reviews only when the learner answers
        with buttons.

        Returns
        -------
        str
            The signature for the active question type.

        Examples
        --------
        Changing Button count leaves staff-placement reviews available.
        """
        return (
            self.practice_signature()
            if settings.notation.question_type == "staff"
            else super().settings_signature()
        )

    def practice_signature(self) -> str:
        """
        Identify the terms eligible for review.

        Returns
        -------
        str
            The selected terms, or the original empty signature when all
            terms are enabled.

        Examples
        --------
        >>> NotationIdentification().settings_signature()
        ''
        """
        if settings.notation.question_type == "staff":
            return signature("staff", settings.notation.terms)
        return (
            ""
            if settings.notation.terms == set(settings.NOTATION_TERMS)
            else signature(settings.notation.terms)
        )

    def instructions(self) -> str:
        """
        Explain how to answer the notation question.

        Returns
        -------
        str
            Help for mouse and keyboard users.

        Examples
        --------
        >>> "number" in NotationIdentification().instructions()
        True
        """
        if settings.notation.question_type == "staff":
            return (
                "Read the prompt, then click the named component in the music."
            )
        return (
            "Look for the blue part of the music. Click its name or press "
            "the number shown on the matching button."
        )

    @staticmethod
    def _choices(
        part: str,
        *,
        group: str,
        terms: set[str],
        buttons: ButtonSettings,
        rng: random.Random,
    ) -> list[str]:
        """
        Pick checked terms, favoring the target's category and close
        visual matches.

        Parameters
        ----------
        part : str
            The highlighted term.
        group : str
            Category containing the target. Keyword-only.
        rng : random.Random
            Source for sampling and ordering the buttons. Keyword-only.
        terms : set of str
            Enabled notation terms.
        buttons : ButtonSettings
            Answer layout and maximum button count.

        Returns
        -------
        list of str
            Distinct enabled answers, including the target.

        Examples
        --------
        >>> "Turn" in NotationIdentification._choices(
        ...     "Turn",
        ...     group="Ornaments",
        ...     terms={"Turn", "Trill"},
        ...     buttons=ButtonSettings(),
        ...     rng=random.Random(0),
        ... )
        True
        """
        if buttons.button_mode == "all":
            return [term for term in settings.NOTATION_TERMS if term in terms]
        needed = buttons.button_count - 1
        alternatives = [
            term for term in CATALOG[group] if term != part and term in terms
        ]
        rng.shuffle(alternatives)
        if rng.random() < 0.8:
            similar = next(
                (family for family in SIMILAR_MARKS if part in family),
                (),
            )
            alternatives.sort(key=lambda term: term not in similar)
        if len(alternatives) < needed:
            others = [
                term
                for term in settings.NOTATION_TERMS
                if term in terms and term not in CATALOG[group]
            ]
            alternatives.extend(
                rng.sample(
                    others,
                    min(len(others), needed - len(alternatives)),
                ),
            )
        choices = [part, *alternatives[:needed]]
        rng.shuffle(choices)
        return choices

    def refresh(self, question: Question) -> Question:
        """
        Replace unchecked distractors in older practice questions before
        replay.

        Parameters
        ----------
        question : Question
            Stored question matching the current settings signature.

        Returns
        -------
        Question
            The original notation with eligible answer buttons.

        Examples
        --------
        >>> ex = NotationIdentification()
        >>> q = ex.generate(random.Random(1))
        >>> ex.refresh(q) == q
        True
        """
        cfg = settings.notation
        if all(term in cfg.terms for term in question.choices):
            return question
        return self._with_buttons(
            question,
            rng=random.Random(question.item_key()),
            cfg=cfg,
            buttons=self.button_settings(),
        )

    def make_question(self, rng: random.Random) -> Question:
        """
        Choose a phrase and a single visible feature to highlight.

        Parameters
        ----------
        rng : random.Random
            Source for the phrase, feature, and its position.

        Returns
        -------
        Question
            A short phrase with the selected marking and checked answer
            choices.

        Examples
        --------
        >>> q = NotationIdentification().generate(
        ...     random.Random(0)
        ... )
        >>> q.notation_target[0] == q.answer
        True
        """
        cfg = settings.notation
        if not cfg.terms:
            return Question(
                "Select a notation term in Settings to continue.",
                choices=[],
                answer="",
            )
        phrase = rng.choice(self._phrases)
        selected = [
            term for term in settings.NOTATION_TERMS if term in cfg.terms
        ]
        repertoire = passages_by_term()
        represented = [term for term in selected if term in repertoire]
        part = rng.choice(
            represented if represented and rng.random() < 0.5 else selected,
        )
        group = next(name for name, terms in CATALOG.items() if part in terms)
        locate = cfg.question_type == "staff"
        choices = (
            []
            if locate
            else self._choices(
                part,
                group=group,
                rng=rng,
                terms=cfg.terms,
                buttons=self.button_settings(),
            )
        )
        if part in repertoire:
            passage = rng.choice(list(repertoire[part]))
            locations = repertoire[part][passage]
            index = locations[0] if locate else rng.choice(locations)
            return self._example(
                part,
                group=group,
                locate=locate,
                choices=choices,
                source=passage,
                position=index,
                excerpt=True,
            )
        position = rng.randrange(5 if part == "Staff line" else 4)
        return self._example(
            part,
            group=group,
            locate=locate,
            choices=choices,
            source=phrase,
            position=position,
            excerpt=False,
        )

    @staticmethod
    def _example(
        part: str,
        *,
        group: str,
        locate: bool,
        choices: list[str],
        source: str,
        position: int,
        excerpt: bool,
    ) -> Question:
        """
        Build one playable question from an excerpt marker or a
        generated staff position.

        Parameters
        ----------
        part : str
            The target term.
        group : str
            Its notation category.
        locate : bool
            Whether the learner clicks on the staff.
        choices : list of str
            Enabled answer buttons.
        source : str
            Excerpt ID or space-separated pitches.
        position : int
            Marker index, note column, or staff line.
        excerpt : bool
            Whether the source names a bundled score.

        Returns
        -------
        Question
            The music, prompt, and target for the chosen presentation.

        Examples
        --------
        >>> ex = NotationIdentification()
        >>> ex._example(
        ...     "Slur",
        ...     group="Staff and rhythm",
        ...     locate=True,
        ...     choices=[],
        ...     source="E4 G4 A4 G4",
        ...     position=0,
        ...     excerpt=False,
        ... ).prompt
        'Click the slur.'
        """
        if excerpt:
            prompt = "Which part of the music is highlighted?"
            if locate:
                if group == "Accidentals":
                    prompt = f"Click a {part.lower()} beside a note."
                elif part == "Barline":
                    prompt = "Click a single barline."
                else:
                    prompt = f"Click an example of {part.lower()}."
            return Question(
                prompt,
                show_staff=True,
                notation_excerpt=source,
                notation_target=(part, position),
                choices=choices,
                grid={
                    choice: divmod(i, 2) for i, choice in enumerate(choices)
                },
                answer=part,
            )
        placement, symbol = MARKS[part]
        phrase = source
        clef = "treble"
        if placement == "clef":
            clef = str(symbol)
            phrase = {
                "bass": "G2 B2 C3 D3",
                "tenor": "D3 F3 A3 G3",
                "baritone": "B2 D3 F3 G3",
            }.get(clef, "C4 D4 E4 D4")
        notes = phrase.split()
        if part in ("Tie", "Slur", "Beam", "Triplet", "Glissando"):
            position = 0
            notes = ["E4", "E4" if part == "Tie" else "G4", "A4", "G4"]
        if part == "Ledger line":
            notes[position] = "C4"
        key = 2 if part == "Key signature" else 0
        if key:
            notes = ["D4", "F#4", "A4", "D5"]
        staff = [[Note.parse(name)] for name in notes]
        if placement == "rest":
            staff[position] = []
        elif placement == "arpeggio":
            staff[position] = [Note.parse(name) for name in ("E4", "G4", "B4")]
        context = {
            "Brass": "brass part",
            "Woodwinds": "woodwind part",
            "Strings and plucked instruments": "string part",
            "Keyboard and organ": "keyboard part",
        }.get(group)
        prompt = (
            f"Which marking in this {context} is highlighted?"
            if context
            else "Which part of the music is highlighted?"
        )
        if locate:
            ordinal = ("first", "second", "third", "fourth", "fifth")[position]
            if part == "Staff line":
                prompt = f"Click the {ordinal} staff line from the bottom."
            elif part in ("Notehead", "Stem"):
                prompt = f"Click the {part.lower()} of the {ordinal} note."
            else:
                prompt = f"Click the {part.lower()}."
        return Question(
            prompt,
            staff=staff,
            clef=clef,
            key=key,
            grid={choice: divmod(i, 2) for i, choice in enumerate(choices)},
            value="half" if locate and part == "Quarter note" else "quarter",
            choices=choices,
            answer=part,
            notation_target=(part, position),
        )

    @classmethod
    def _examples(
        cls,
        part: str,
        *,
        locate: bool,
        repertoire: dict[str, dict[str, list[int]]],
    ) -> dict[str, Question]:
        """
        Index the current score examples for a term by their persistent
        card identities.

        Parameters
        ----------
        part : str
            Enabled notation term.
        locate : bool
            Whether the learner marks a location on the staff.
        repertoire : dict
            Excerpt locations indexed by term and passage.

        Returns
        -------
        dict of str to Question
            Templates for the active question type, without distractors.

        Examples
        --------
        >>> len(
        ...     NotationIdentification._examples(
        ...         "Koron", locate=False, repertoire={},
        ...     )
        ... ) > 0
        True
        """
        passages = repertoire.get(part, {})
        return cls._catalog(
            part,
            locate=locate,
            passages=tuple(
                (name, tuple(indices)) for name, indices in passages.items()
            ),
        )

    @classmethod
    @lru_cache(maxsize=512)
    def _catalog(
        cls,
        part: str,
        *,
        locate: bool,
        passages: tuple[tuple[str, tuple[int, ...]], ...],
    ) -> dict[str, Question]:
        """
        Enumerate distinct targets using the same engraving and prompts
        as ordinary practice.

        Parameters
        ----------
        part : str
            Target symbol.
        locate : bool
            Whether any matching excerpt marker can be clicked.
        passages : tuple
            Available excerpt IDs and matching marker indices.

        Returns
        -------
        dict of str to Question
            One template for each distinct question.

        Examples
        --------
        >>> len(
        ...     NotationIdentification._catalog(
        ...         "Slur", locate=True, passages=()
        ...     )
        ... )
        1
        """
        group = next(name for name, terms in CATALOG.items() if part in terms)
        positions = tuple(range(5 if part == "Staff line" else 4))
        sources = passages or tuple(
            (phrase, positions) for phrase in cls._phrases
        )
        examples = {}
        for source, indices in sources:
            for index in indices[:1] if passages and locate else indices:
                q = cls._example(
                    part,
                    group=group,
                    locate=locate,
                    choices=[],
                    source=source,
                    position=index,
                    excerpt=bool(passages),
                )
                examples[q.item_key()] = q
        return examples

    def card_groups(self) -> dict[str, str]:
        """
        Group the active question type’s playable examples by the symbol
        being practiced.

        Returns
        -------
        dict of str to str
            Map from each eligible example’s item key to its selected
            term.

        Examples
        --------
        >>> bool(NotationIdentification().card_groups())
        True
        """
        cfg = settings.notation
        repertoire = passages_by_term()
        return {
            key: term
            for term in cfg.terms
            for key in self._examples(
                term,
                locate=cfg.question_type == "staff",
                repertoire=repertoire,
            )
        }

    def daily_candidates(self, rng: random.Random) -> Iterator[Question]:
        """
        Choose one example for each selected notation term.

        Parameters
        ----------
        rng : random.Random
            Randomizes term order, examples and distractors.

        Yields
        ------
        Question
            A distinct playable card with the current answer controls.

        Examples
        --------
        >>> next(
        ...     NotationIdentification().daily_candidates(
        ...         random.Random(4)
        ...     )
        ... ).answer in settings.notation.terms
        True
        """
        cfg = settings.notation
        repertoire = passages_by_term()
        buttons = self.button_settings()
        terms = sorted(cfg.terms)
        rng.shuffle(terms)
        for term in terms:
            examples = self._examples(
                term,
                locate=cfg.question_type == "staff",
                repertoire=repertoire,
            )
            example = rng.choice(list(examples.values()))
            yield self._with_buttons(
                deepcopy(example),
                rng=rng,
                cfg=cfg,
                buttons=buttons,
            )

    def _with_buttons(
        self,
        question: Question,
        *,
        rng: random.Random,
        cfg: settings.NotationSettings,
        buttons: ButtonSettings,
    ) -> Question:
        """
        Apply the current answer controls to a notation card.

        Parameters
        ----------
        question : Question
            Playable score and target.
        rng : random.Random
            Source for the distractor selection.
        cfg : NotationSettings
            Enabled terms and answer method.
        buttons : ButtonSettings
            Answer layout and maximum button count.

        Returns
        -------
        Question
            The same target with the current answer layout.

        Examples
        --------
        >>> ex = NotationIdentification()
        >>> q = ex.generate(random.Random(4))
        >>> ex._with_buttons(
        ...     q, rng=random.Random(1),
        ...     cfg=settings.NotationSettings(),
        ...     buttons=ButtonSettings(),
        ... ).item_key() == q.item_key()
        True
        """
        if cfg.question_type == "staff":
            return question
        group = next(
            name for name, terms in CATALOG.items() if question.answer in terms
        )
        choices = self._choices(
            question.answer,
            group=group,
            rng=rng,
            terms=cfg.terms,
            buttons=buttons,
        )
        return replace(
            question,
            choices=choices,
            grid={choice: divmod(i, 2) for i, choice in enumerate(choices)},
        )

    def review_question(
        self,
        question: Question,
        *,
        same_settings: bool,
    ) -> Question | None:
        """
        Recover an eligible saved example under the current term and
        button selections.

        Parameters
        ----------
        question : Question
            Saved question.
        same_settings : bool
            Whether the presentation settings still match.

        Returns
        -------
        Question or None
            The current presentation of the card, or None if its term or
            example is outside the catalog.

        Examples
        --------
        >>> ex = NotationIdentification()
        >>> q = ex.generate(random.Random(4))
        >>> ex.review_question(
        ...     q, same_settings=True
        ... ) == q
        True
        """
        cfg = settings.notation
        if question.answer not in cfg.terms:
            return None
        examples = self._examples(
            question.answer,
            locate=cfg.question_type == "staff",
            repertoire=passages_by_term(),
        )
        if question.item_key() not in examples:
            return None
        return (
            self.refresh(question)
            if same_settings
            else self._with_buttons(
                question,
                rng=random.Random(question.item_key()),
                cfg=cfg,
                buttons=self.button_settings(),
            )
        )


_BEAT_CLASSIFICATIONS = {
    "Simple duple": (2, 4),
    "Simple triple": (3, 4),
    "Simple quadruple": (4, 4),
    "Compound duple": (6, 8),
    "Compound triple": (9, 8),
    "Compound quadruple": (12, 8),
}
_TUPLET_HINT = (
    "A bracket marked 3 fits three notes into the time of two. "
    "A bracket marked 2 fits two notes into the time of three."
)
# RISM first openings, 1700–1899 (studies/time-signatures/tuplets.csv
# and tuplet-prevalence.csv). One group is a single generator choice.
_IDENTIFICATION_TUPLETS = {
    "triplet": 611,
    "quadruplet": 2,
    "quintuplet": 11,
    "sextuplet": 40,
    "septuplet": 5,
    "nonuplet": 2,
}
_TUPLET_GROUPS = sum(_IDENTIFICATION_TUPLETS.values())
_TUPLET_CHANCE = _TUPLET_GROUPS / (99_078 + _TUPLET_GROUPS)
BEAT_METERS = {
    f"{top}/{bottom}": (top, bottom)
    for top, bottom in _BEAT_CLASSIFICATIONS.values()
}


def beat_meter(answer: str) -> tuple[int, int]:
    """
    Look up the written time signature for either kind of answer.

    Parameters
    ----------
    answer : str
        A time signature or meter classification from the exercise.

    Returns
    -------
    tuple of int
        Numerator and denominator for engraving the rhythm.

    Examples
    --------
    >>> beat_meter("Compound duple")
    (6, 8)
    """
    if answer in BEAT_METERS:
        return BEAT_METERS[answer]
    return _BEAT_CLASSIFICATIONS[answer]


@register
class BeatIdentification(ChoiceExercise):
    """
    Identify the time signature or classify the meter of a rhythm.

    Examples
    --------
    >>> q = BeatIdentification().generate(random.Random(2))
    >>> q.answer in q.choices and bool(q.rhythm)
    True
    """

    name = "Beat Identification"
    category = "Rhythm"
    description = "Read two measures and identify the time signature or meter."
    has_sound = False

    def practice_signature(self) -> str:
        """
        Keep separate review settings for the two rhythm components.

        Returns
        -------
        str
            The original empty signature for time signature practice,
            or the selected component for classification practice.

        Examples
        --------
        >>> BeatIdentification().practice_signature()
        ''
        """
        component = settings.beat_rhythm_component
        original = "" if component == "Time signature" else component
        values = settings.beat_note_types["beatIdentification"]
        if settings.beat_tuplets["beatIdentification"]:
            return signature(original, values, "tuplets")
        if values == settings.DEFAULT_BEAT_NOTE_TYPES["beatIdentification"]:
            return original
        return signature(original, values)

    def instructions(self) -> str:
        """
        Explain how to answer from the two written measures.

        Returns
        -------
        str
            The task and its keyboard shortcut directions.

        Examples
        --------
        >>> "keys" in BeatIdentification().instructions()
        True
        """
        if settings.beat_rhythm_component == "Beat and meter":
            task = (
                "Read the time signature. A simple beat divides into two "
                "equal parts, and a compound beat divides into three. "
                "Count the main beats in "
                "one measure. Two beats are duple, three are triple, and "
                "four are quadruple."
            )
        else:
            task = (
                "Choose the time signature that fits both measures. Count the "
                "note and rest lengths and look at which notes share a beam."
            )
        if settings.beat_tuplets["beatIdentification"]:
            task += (
                " A numbered bracket groups notes into a tuplet. For "
                "example, three triplet eighths last one quarter beat."
            )
        return f"{task} Click an answer or use the keys shown when you hover."

    def make_question(self, rng: random.Random) -> Question:
        """
        Generate two complete measures in a randomly chosen meter.

        Parameters
        ----------
        rng : random.Random
            Chooses the time signature and how each beat is written.

        Returns
        -------
        Question
            The rhythm and the answers for the selected component.

        Examples
        --------
        >>> q = BeatIdentification().make_question(random.Random(0))
        >>> q.prompt
        'What is the time signature?'
        """
        classify = settings.beat_rhythm_component == "Beat and meter"
        meters = _BEAT_CLASSIFICATIONS if classify else BEAT_METERS
        values = frozenset(settings.beat_note_types["beatIdentification"])
        answer, rhythm = _beat_example(
            rng,
            prefix="beatIdentification",
            values=values,
            classify=classify,
        )
        if settings.beat_tuplets["beatIdentification"]:
            rhythm = _identification_tuplets(
                rng,
                answer=answer,
                rhythm=rhythm,
                values=values,
            )
        return Question(
            "What are the beat and meter?"
            if classify
            else "What is the time signature?",
            choices=list(meters),
            answer=answer,
            rhythm=rhythm,
        )


def _identification_tuplets(
    rng: random.Random,
    *,
    answer: str,
    rhythm: tuple[str, ...],
    values: frozenset[str],
) -> tuple[str, ...]:
    """
    Substitute complete tuplet groups at the study's event frequency.

    Parameters
    ----------
    rng : random.Random
        Draws group opportunities, types, and placements.
    answer : str
        The meter or classification, with a visible cue for hidden
        signatures of equal length.
    rhythm : tuple of str
        Two measures of ordinary notes and rests in this meter.
    values : frozenset of str
        Enabled note types for the tuplet groups.

    Returns
    -------
    tuple of str
        Two measures with the original durations and opening meter cue.

    Examples
    --------
    >>> rhythm = ("whole", "whole")
    >>> _identification_tuplets(
    ...     random.Random(1),
    ...     answer="4/4",
    ...     rhythm=rhythm,
    ...     values=frozenset({"quarter"}),
    ... )
    ('whole', 'whole')
    """
    remaining = len(rhythm)
    replacements: dict[int, tuple[int, tuple[str, ...]]] = {}
    top, bottom = beat_meter(answer)
    bar = top * settings.RHYTHM_DURATIONS["whole"] / bottom
    beat = 4 if bottom == 4 else 6
    # Keep the opening beam that distinguishes the two hidden meters.
    cue = beat if answer in ("3/4", "6/8") else 0
    durations = (settings.RHYTHM_DURATIONS[value] for value in rhythm)
    offsets = list(accumulate(durations, initial=0.0))
    indices = {offset: i for i, offset in enumerate(offsets)}
    while remaining > 0:
        remaining -= 1
        if rng.random() >= _TUPLET_CHANCE:
            continue
        # Draw the kind before considering placements. Having more
        # ways to write a particular tuplet should not favor its type.
        kind = rng.choices(
            list(_IDENTIFICATION_TUPLETS),
            weights=list(_IDENTIFICATION_TUPLETS.values()),
        )[0]
        count, ordinary = settings.BEAT_TUPLET_RATIOS[kind]
        placements = []
        for value in settings.BEAT_NOTE_TYPES:
            if value.startswith("dotted-") or value not in values:
                continue
            span = ordinary * settings.RHYTHM_DURATIONS[value]
            for start, offset in enumerate(offsets[:-1]):
                end = indices.get(offset + span)
                in_bar = offset % bar
                if (
                    end is None
                    or offset < cue
                    or in_bar + span > bar
                    or in_bar % min(beat, span) != 0
                ):
                    continue
                if all(
                    end <= left or start >= right
                    for left, (right, _) in replacements.items()
                ):
                    placements.append((start, end, value))
        if placements:
            start, end, value = rng.choice(placements)
            replacements[start] = (end, (f"{kind}-{value}",) * count)
            # This group took the place of multiple ordinary decisions.
            remaining -= end - start - 1
    if not replacements:
        return rhythm
    result = list(rhythm)
    for start in sorted(replacements, reverse=True):
        end, group = replacements[start]
        result[start:end] = group
    return tuple(result)


def _beat_rhythm(
    rng: random.Random,
    *,
    meter: tuple[int, int],
    sustained: bool = False,
) -> tuple[str, ...]:
    """
    Compose two measures with a full beam group in the opening beat.

    Parameters
    ----------
    rng : random.Random
        Chooses how to write the remaining beats.
    meter : tuple of int
        One of the supported time signatures.
    sustained : bool
        Start measure two with a note that spans two beats.

    Returns
    -------
    tuple of str
        Written rhythms from the start of the first measure to the end
        of the second.

    Examples
    --------
    >>> _beat_rhythm(random.Random(1), meter=(2, 4), sustained=True)[-1]
    'half'
    """
    numerator, denominator = meter
    if denominator == 4:
        group = ("eighth", "eighth")
        patterns = (group, ("quarter",), ("eighth-rest", "eighth"))
        beats = numerator
        long_note = "half"
    else:
        group = ("eighth", "eighth", "eighth")
        patterns = (group, ("dotted-quarter",), ("quarter", "eighth"))
        beats = numerator // 3
        long_note = "dotted-half"
    if not sustained:
        return group + tuple(
            value
            for _ in range(2 * beats - 1)
            for value in rng.choice(patterns)
        )
    first = tuple(
        value for _ in range(beats - 1) for value in rng.choice(patterns)
    )
    second = tuple(
        value for _ in range(beats - 2) for value in rng.choice(patterns)
    )
    return group + first + (long_note,) + second


_BeatPattern = tuple[int, tuple[str, ...]]


@lru_cache(maxsize=512)
def _beat_fills(
    meter: tuple[int, int],
    *,
    values: frozenset[str],
    tuplets: bool = False,
) -> tuple[tuple[_BeatPattern, ...], ...]:
    """
    Find patterns that leave the rest of a measure fillable.

    Parameters
    ----------
    meter : tuple of int
        Time signature for the measure.
    values : frozenset of str
        Permitted written note values.
    tuplets : bool
        Include triplets in simple meter and duplets in compound meter.

    Returns
    -------
    tuple of tuple of beat patterns
        For each number of beats remaining, the playable patterns
        and their lengths in beats.

    Examples
    --------
    >>> _beat_fills((4, 4), values=frozenset({"whole"}))[-1]
    ((4, ('whole',)),)
    """
    top, bottom = meter
    beats, unit = (top, 4) if bottom == 4 else (top // 3, 6)
    patterns = []
    for value in settings.BEAT_NOTE_TYPES:
        if value not in values:
            continue
        duration = settings.RHYTHM_DURATIONS[value]
        if duration % unit == 0:
            patterns.append((int(duration / unit), (value,)))
        elif unit % duration == 0:
            patterns.append((1, (value,) * int(unit / duration)))
        if tuplets and not value.startswith("dotted-"):
            kind = "triplet" if bottom == 4 else "duplet"
            count, ordinary = settings.BEAT_TUPLET_RATIOS[kind]
            group = (f"{kind}-{value}",) * count
            span = ordinary * duration
            if span % unit == 0:
                patterns.append((int(span / unit), group))
            elif unit % span == 0:
                patterns.append((1, group * int(unit / span)))
    if "eighth" in values:
        if bottom == 4:
            patterns.append((1, ("eighth-rest", "eighth")))
        elif "quarter" in values:
            patterns.append((1, ("quarter", "eighth")))
    fills: list[tuple[_BeatPattern, ...]] = [()]
    for remaining in range(1, beats + 1):
        fills.append(
            tuple(
                (length, pattern)
                for length, pattern in patterns
                if length == remaining
                or (length < remaining and fills[remaining - length])
            ),
        )
    return tuple(fills)


def _beat_example(
    rng: random.Random,
    *,
    prefix: str,
    values: frozenset[str],
    tuplets: bool = False,
    classify: bool = False,
) -> tuple[str, tuple[str, ...]]:
    """
    Choose a compatible meter and fill two measures with enabled values.

    Parameters
    ----------
    rng : random.Random
        Source of meter and note choices.
    prefix : str
        Exercise whose default patterns apply.
    values : frozenset of str
        Enabled written note types.
    tuplets : bool
        Include construction tuplets when filling measures.
    classify : bool
        Use the meter classification as the answer.

    Returns
    -------
    tuple of str and tuple of str
        Answer and written rhythm.

    Examples
    --------
    >>> key = "beatConstruction"
    >>> values = frozenset(settings.DEFAULT_BEAT_NOTE_TYPES[key])
    >>> _beat_example(
    ...     random.Random(1), prefix=key, values=values
    ... )[0]
    '3/4'
    """
    meters = _BEAT_CLASSIFICATIONS if classify else BEAT_METERS
    construction = prefix == "beatConstruction"
    if not tuplets and values == settings.DEFAULT_BEAT_NOTE_TYPES[prefix]:
        answer = rng.choice(list(meters))
        return answer, _beat_rhythm(
            rng,
            meter=meters[answer],
            sustained=construction,
        )

    short_notes = values.intersection(settings.RHYTHM_BEAM_COUNTS)
    eligible = []
    for answer, meter in meters.items():
        # 3/4 and 6/8 have the same bar length. A hidden signature needs
        # a visible beat group to distinguish them.
        if answer in ("3/4", "6/8") and not construction and not short_notes:
            continue
        if _beat_fills(meter, values=values, tuplets=tuplets)[-1]:
            eligible.append(answer)
    answer = rng.choice(eligible)
    fills = _beat_fills(meters[answer], values=values, tuplets=tuplets)
    rhythm = []
    needs_tuplet = tuplets
    for bar in range(2):
        remaining = len(fills) - 1
        while remaining:
            options = fills[remaining]
            if remaining == len(fills) - 1:
                if bar == 0 and not construction and answer in ("3/4", "6/8"):
                    options = [
                        pair for pair in options if pair[1][0] in short_notes
                    ]
                elif bar == 1 and construction:
                    holds = [
                        pair
                        for pair in options
                        if pair[0] > 1 and len(pair[1]) == 1
                    ]
                    options = holds or options
            if needs_tuplet:
                groups = [
                    pair
                    for pair in options
                    if settings.beat_note(pair[1][0])[1]
                ]
                if groups:
                    options = groups
                    needs_tuplet = False
            length, pattern = rng.choice(options)
            rhythm.extend(pattern)
            remaining -= length
    return answer, tuple(rhythm)


def beat_positions(meter: tuple[int, int]) -> frozenset[int]:
    """
    Get the main beat starts in two measures, measured in eighth notes.

    Parameters
    ----------
    meter : tuple of int
        One of the supported time signatures.

    Returns
    -------
    frozenset of int
        Zero-based positions from the start of the first measure.

    Examples
    --------
    >>> sorted(beat_positions((6, 8)))
    [0, 3, 6, 9]
    """
    numerator, denominator = meter
    span = numerator * (8 // denominator)
    return frozenset(range(0, 2 * span, 2 if denominator == 4 else 3))


@register
class BeatConstruction(Exercise):
    """
    Mark where the main beats begin in two written measures.

    Examples
    --------
    >>> q = BeatConstruction().generate(random.Random(2))
    >>> q.answer in BEAT_METERS and not q.choices
    True
    """

    name = "Beat Construction"
    category = "Rhythm"
    description = "Place the beats in two measures of written rhythm."
    has_sound = True

    def settings_signature(self) -> str:
        """
        Identify the note types used in a saved construction question.

        Returns
        -------
        str
            Empty for the original selection, otherwise its signature.

        Examples
        --------
        >>> BeatConstruction().settings_signature()
        ''
        """
        values = settings.beat_note_types["beatConstruction"]
        if settings.beat_tuplets["beatConstruction"]:
            return signature(values, "tuplets")
        if values == settings.DEFAULT_BEAT_NOTE_TYPES["beatConstruction"]:
            return ""
        return signature(values)

    def instructions(self) -> str:
        """
        Explain how to place and submit the beats.

        Returns
        -------
        str
            Counting guidance and keyboard controls.

        Examples
        --------
        >>> "arrow keys" in BeatConstruction().instructions()
        True
        """
        task = (
            "Mark where each main beat starts, even if a note is still "
            "sounding or there is a rest. In meters like 3/4, each beat "
            "lasts a quarter note. In 6/8, 9/8, and 12/8, each beat lasts "
            "a dotted quarter, or three ordinary eighth notes."
        )
        if settings.beat_tuplets["beatConstruction"]:
            task = f"{task} {_TUPLET_HINT}"
        return (
            f"{task} Click a blank to fill or "
            "clear it, or use the arrow keys and Space. Press Return to check."
        )

    def generate(self, rng: random.Random) -> Question:
        """
        Choose a time signature and write two measures to mark.

        Parameters
        ----------
        rng : random.Random
            Chooses the meter and the written rhythm.

        Returns
        -------
        Question
            The rhythm and its time signature, without answer choices.

        Examples
        --------
        >>> BeatConstruction().generate(random.Random(1)).prompt
        'Place the beats in both measures.'
        """
        answer, rhythm = _beat_example(
            rng,
            prefix="beatConstruction",
            values=frozenset(settings.beat_note_types["beatConstruction"]),
            tuplets=settings.beat_tuplets["beatConstruction"],
        )
        if not any(value.endswith("-rest") for value in rhythm):
            index = rng.randrange(len(rhythm))
            values = list(rhythm)
            values[index] += "-rest"
            rhythm = tuple(values)
        return Question(
            "Place the beats in both measures.",
            choices=[],
            answer=answer,
            rhythm=rhythm,
        )


@register
class RythmicEquations(ChoiceExercise):
    """
    Complete arithmetic equations with written note values.

    Examples
    --------
    >>> q = RythmicEquations().generate(
    ...     random.Random(2)
    ... )
    >>> "_" in q.prompt and q.answer in q.choices
    True
    """

    name = "Rythmic Equations"
    category = "Rhythm"
    description = (
        "Fill in the missing symbol or number to balance the equation."
    )
    has_sound = False

    durations = settings.RHYTHM_DURATIONS

    def instructions(self) -> str:
        """
        Explain how to complete the equation with a button or its
        shortcut.

        Returns
        -------
        str
            Instructions for the exercise.

        Examples
        --------
        >>> "keys" in RythmicEquations().instructions()
        True
        """
        return (
            "Choose the symbol or number that balances the equation. "
            "If you see parentheses, work inside them first. "
            "Click its button or use the keys shown when you hover."
        )

    def card_prompt(self, question: Question) -> str:
        """
        Ask for the missing symbol or number on an exported card.

        Parameters
        ----------
        question : Question
            The equation on the card.

        Returns
        -------
        str
            The instruction shown above the equation.

        Examples
        --------
        >>> RythmicEquations().card_prompt(
        ...     Question("", choices=[], answer="")
        ... )
        'Which note or rest balances the equation?'
        """
        if question.answer.isdecimal():
            return (
                question.caption + " Which number balances the equation?"
            ).strip()
        return "Which note or rest balances the equation?"

    def practice_signature(self) -> str:
        """
        Keep review questions tied to the options that generated them.

        Returns
        -------
        str
            The selected operators and symbols, or an empty string for
            the original defaults.

        Examples
        --------
        >>> RythmicEquations().practice_signature()
        ''
        """
        left = settings.rhythm_left_signs
        right = settings.rhythm_right_signs
        counts = (
            settings.rhythm_left_operators,
            settings.rhythm_right_operators,
        )
        # Keep the shared selection's historical signature whenever one
        # set of signs describes every active side.
        if left == right or not counts[1]:
            operators = left
        elif not counts[0]:
            operators = right
        else:
            operators = {"left": left, "right": right}
        groups = {
            name: True
            for name, enabled in (
                ("ties", settings.rhythm_ties),
                ("beams", settings.rhythm_beams),
            )
            if enabled
        }
        # Older mixed-operation questions could group sums before
        # multiplication or division.
        if max(counts) >= 2:
            previously_grouped = any(
                count >= 2 and signs & {"+", "−"} and signs & {"×", "÷"}
                for count, signs in zip(counts, (left, right), strict=True)
            )
            if settings.rhythm_parentheses != previously_grouped:
                groups["parentheses"] = settings.rhythm_parentheses
        if settings.rhythm_answer_types != {"symbol"}:
            return signature(
                operators,
                settings.rhythm_symbols,
                groups,
                counts,
                settings.rhythm_answer_types,
            )
        if counts != (1, 0):
            return signature(
                operators,
                settings.rhythm_symbols,
                groups,
                counts,
            )
        if groups:
            return signature(
                operators,
                settings.rhythm_symbols,
                groups,
            )
        if (
            operators == settings.DEFAULT_RHYTHM_OPERATORS
            and settings.rhythm_symbols == settings.DEFAULT_RHYTHM_SYMBOLS
        ):
            return ""
        return signature(operators, settings.rhythm_symbols)

    def make_question(self, rng: random.Random) -> Question:
        """
        Write a rhythm equation and hide a symbol or number.

        Parameters
        ----------
        rng : random.Random
            Chooses the note value, operation, and blank position.

        Returns
        -------
        Question
            The equation and the note values available as answers.

        Examples
        --------
        >>> RythmicEquations().make_question(
        ...     random.Random(0)
        ... ).prompt.count("_")
        1
        """
        symbols = {
            name: duration
            for name, duration in self.durations.items()
            if name in settings.rhythm_symbols
        }
        return equation_question(
            rng,
            symbols=symbols,
            ties=settings.rhythm_ties,
            beams=settings.rhythm_beams,
            left=settings.rhythm_left_operators,
            right=settings.rhythm_right_operators,
            operators=tuple(sorted(settings.rhythm_left_signs)),
            right_operators=tuple(sorted(settings.rhythm_right_signs)),
            parentheses=settings.rhythm_parentheses,
            answer_types=settings.rhythm_answer_types,
        )
