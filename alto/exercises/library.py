"""
The exercises: note names, intervals, key signatures, scales, chords, arpeggios, keyboard keys and note construction.

Each class makes one kind of `Question` and registers itself with `@register`, so importing this module is what adds
the exercises to the home screen.

Examples
--------
>>> from alto.exercises import REGISTRY
>>> [cls.name for cls in REGISTRY][:3]
['Note Identification', 'Keyboard Identification', 'Note Construction']
"""

from __future__ import annotations

import random
from dataclasses import replace

from alto import settings
from alto.exercises.base import (
    Exercise,
    Question,
    pick_distractors,
    register,
    signature,
)
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
from alto.theory.pitch import (
    MAJOR_KEYS,
    NATURAL_SEMITONES,
    QUALITY_NAMES,
    Interval,
    Note,
    key_accidental,
)
from alto.theory.scales import (
    CHORDS,
    INVERSION_NAMES,
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
        "treble" or "bass", which decides the default range. Keyword-only.
    accidentals : bool
        Give the note a random sharp, flat or natural; otherwise it is natural. Keyword-only.
    span : tuple of (int, int) or None, default None
        An inclusive range of staff steps (`Note.diatonic`); the clef's comfortable range if None. Keyword-only.

    Returns
    -------
    Note
        The note.

    Examples
    --------
    >>> str(_random_note(random.Random(1), clef="treble", accidentals=False, span=(28, 28)))
    'C4'
    """
    lo, hi = span or (CLEF_RANGES[clef][0].diatonic, CLEF_RANGES[clef][1].diatonic)
    d = rng.randint(lo, hi)
    return Note.from_diatonic(d, accidental=rng.choice((-1, 0, 1)) if accidentals else 0)


@register
class NoteNames(Exercise):
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
    description = "Identify notes on the grand staff or on any of seven clefs, from treble to baritone."
    par_seconds = 3.0

    def settings_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The clefs, ranges, key signatures, note values and naming in force, and whether accidentals are asked.

        Examples
        --------
        >>> NoteNames().settings_signature() != NoteNames(accidentals=True).settings_signature()
        True
        """
        return signature(settings.note_names, self.accidentals)

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML.

        Examples
        --------
        >>> "Press the button with its name" in NoteNames().instructions()
        True
        """
        return (
            "<b>Note Identification</b><br>A note is shown on the staff. Press the button with its name, or press its number "
            "(1 is the first button).<br><br>"
            "Use the sliders button to choose the clefs, the range of notes, key signatures (the name then has to "
            "match the signature), note values, letter or solfège names, and whether sharps, flats and naturals appear."
        )

    def __init__(self, accidentals: bool = False) -> None:
        """
        Create the exercise.

        Parameters
        ----------
        accidentals : bool, default False
            Ask notes with explicit sharps, flats and naturals, whatever the settings say.

        Examples
        --------
        >>> NoteNames(accidentals=True).accidentals
        True
        """
        self.accidentals = accidentals

    def generate(self, rng: random.Random) -> Question:
        """
        Make a note to name, on one of the chosen clefs, in a chosen key.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            The note drawn on a staff, with one button for each name that could be the answer.

        Examples
        --------
        >>> q = NoteNames().generate(random.Random(2))
        >>> q.clef in ("treble", "bass", "alto", "tenor", "soprano", "mezzo", "baritone", "grand")
        True
        """
        cfg = settings.note_names
        clef = rng.choice(cfg.active_clefs())
        key = rng.choice(cfg.active_keys())
        value = rng.choice(cfg.active_values())
        with_accidentals = self.accidentals or cfg.accidentals

        letter_pos = rng.randint(*cfg.range_for(clef))
        in_key = key_accidental(letter_pos % 7, count=key)
        acc = in_key
        if with_accidentals and rng.random() < 0.5:  # an explicit sign that differs from the key signature
            acc = rng.choice([a for a in (-1, 0, 1) if a != in_key])
        note = Note.from_diatonic(letter_pos, accidental=acc)

        name = spell(note, naming=cfg.naming)
        # One button for every name that can be the answer under the current settings.
        if with_accidentals:
            pool = {(l, a) for l in range(7) for a in (-1, 0, 1)}
        else:
            pool = {(l, key_accidental(l, count=k)) for l in range(7) for k in cfg.active_keys()}
        ordered = sorted(pool)
        choices = [spell(Note(4, letter=l, accidental=a), naming=cfg.naming) for l, a in ordered]
        if len(pool) == 7:  # one name per letter: a single row, one column per letter
            grid = {c: (0, l) for c, (l, _) in zip(choices, ordered)}
        else:  # columns are letters; sharps on the top row, then naturals, then flats
            rows = {a: r for r, a in enumerate(sorted({a for _, a in pool}, reverse=True))}
            grid = {c: (rows[a], l) for c, (l, a) in zip(choices, ordered)}

        expl = []
        if key:
            expl.append(f"{MAJOR_KEYS[key]} major has {format_key_signature(key)}.")
        if acc != in_key:
            expl.append("The accidental on the note overrides the key signature.")
        return Question(
            "",
            choices=choices,
            answer=name,
            staff=[[note]],
            clef=clef,
            explanation=" ".join(expl),
            key=key,
            value=value,
            grid=grid,
        )


@register
class IntervalNames(Exercise):
    """
    Name the interval between two notes, up to an octave.

    Attributes
    ----------
    QUALITIES : dict of int to str
        For each interval number, the qualities that can occur, separated by spaces.

    Examples
    --------
    >>> q = IntervalNames().generate(random.Random(3))
    >>> len(q.staff), q.answer in q.choices
    (2, True)
    """

    name = "Interval Identification"
    category = "Intervals"
    description = "Name the interval between two notes (up to an octave)."
    par_seconds = 6.0

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML.

        Examples
        --------
        >>> "quality followed by a number" in IntervalNames().instructions()
        True
        """
        return (
            "<b>Interval Identification</b><br>Two notes are shown. Name the interval from the lower note to the "
            "higher one.<br><br>An interval has a quality followed by a number. The number counts the letter names it "
            "spans, including both notes. The quality is P (perfect), M (major), m (minor), A (augmented) or "
            "d (diminished).<br><br>You can press an answer's number instead of the button: 1 is the first."
        )

    QUALITIES = {
        1: "P A d",
        2: "M m A d",
        3: "M m A d",
        4: "P A d",
        5: "P A d",
        6: "M m A d",
        7: "M m A d",
        8: "P",
    }

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
            The lower and higher note on a staff, and the interval (such as 'M3' or 'P5') as the answer.

        Examples
        --------
        >>> q = IntervalNames().generate(random.Random(4))
        >>> q.answer[0] in "PMmAd" and q.answer[1:].isdigit()
        True
        """
        clef = rng.choice(("treble", "bass"))
        low = _random_note(rng, clef=clef, accidentals=True)
        number = rng.randint(2, 8)
        quality = rng.choice(self.QUALITIES[number].split())
        iv = Interval(number, quality=quality)
        high = low.transpose(iv)
        if abs(high.accidental) > 1 or abs(low.accidental) > 1:
            return self.generate(rng)
        pool = [f"{q}{n}" for n, qs in self.QUALITIES.items() if n > 1 for q in qs.split()]
        near = [f"{q}{number}" for q in self.QUALITIES[number].split()]
        choices = pick_distractors(
            iv.short,
            pool=near + pool,
            n=5,
            rng=rng,
        )
        expl = f"{low} to {high}: {QUALITY_NAMES[quality]} {number}, {iv.semitones} semitones."
        return Question(
            "",
            choices=choices,
            answer=iv.short,
            staff=[[low], [high]],
            clef=clef,
            explanation=expl,
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
        'major' or 'minor' for those two, otherwise the mode's own name such as 'Dorian'.

    Examples
    --------
    >>> _scale_name("Natural minor (Aeolian)")
    'minor'
    >>> _scale_name("Dorian")
    'Dorian'
    """
    return {"Major (Ionian)": "major", "Natural minor (Aeolian)": "minor"}.get(mode, mode)


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
        The scale's name after a blank: '_ Major', '_ minor', '_ Dorian' and so on.

    Examples
    --------
    >>> _blank_scale("Major (Ionian)"), _blank_scale("Natural minor (Aeolian)"), _blank_scale("Dorian")
    ('_ Major', '_ minor', '_ Dorian')
    """
    scale = _scale_name(mode)
    return f"_ {scale if scale == 'minor' else scale[0].upper() + scale[1:]}"


@register
class KeySignatures(Exercise):
    """
    Read a key signature drawn on a staff and name the key it belongs to.

    Examples
    --------
    >>> q = KeySignatures().generate(random.Random(5))
    >>> q.answer in q.choices
    True
    """

    name = "Key Signature Identification"
    category = "Scales & keys"
    description = "Name the key from its signature on a staff."
    par_seconds = 5.0
    has_sound = False

    def settings_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The kinds of question, clefs, scales and key signatures in force.

        Examples
        --------
        >>> KeySignatures().settings_signature().startswith("[")
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
        >>> "Key Signature Identification" in KeySignatures().instructions()
        True
        """
        return (
            "<b>Key Signature Identification</b><br>A key signature is drawn on a staff: press the tonic of the scale it "
            "belongs to (the caption under the staff says whether it is a major key, a minor key or a mode such as "
            "Dorian).<br><br>"
            "Sharp keys add sharps (G, D, A ...) and flat keys add flats (F, B♭, E♭ ...). A mode uses the signature of a "
            "major key, started from another degree: D Dorian has the signature of C major, started from its second note."
            "<br><br>You can press an answer's number instead of the button: 1 is the first.<br><br>"
            "Use the sliders button to choose the clefs, the scales and the key signatures."
        )

    def refresh(self, question: Question) -> Question:
        """
        Give a stored signature question the caption on its staff that older versions did not write.

        Parameters
        ----------
        question : Question
            The question as it was stored.

        Returns
        -------
        Question
            The same question, captioned '_ Major' (or '_ minor', '_ Dorian' and so on) if it shows a staff and had no caption.

        Examples
        --------
        >>> old = Question("Which minor key has this key signature?", choices=["C"], answer="C", key=-3, show_staff=True)
        >>> KeySignatures().refresh(old).caption
        '_ minor'
        """
        if question.caption or not question.show_staff:
            return question
        for mode in SCALES:
            if question.prompt == f"Which {MODE_WORDS.get(mode, f'{mode} scale')} has this key signature?":
                return replace(question, caption=_blank_scale(mode))
        return question

    def generate(self, rng: random.Random) -> Question:
        """
        Make a key signature to read.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            A signature on a staff; the answer is the tonic of the scale that has it.

        Examples
        --------
        >>> q = KeySignatures().generate(random.Random(6))
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
        )

    @staticmethod
    def _read_question(
        tonic: Note,
        *,
        mode: str,
        count: int,
        clef: str,
        rng: random.Random,
    ) -> Question:
        """
        Show a key signature on a staff and ask for the tonic of the scale that has it.

        Parameters
        ----------
        tonic : Note
            The tonic that is the right answer.
        mode : str
            A key of `SCALES`, such as "Major (Ionian)". Keyword-only.
        count : int
            The key signature to draw: positive for sharps, negative for flats. Keyword-only.
        clef : str
            The clef to draw it on. Keyword-only.
        rng : random.Random
            The random number generator, used to choose the wrong answers. Keyword-only.

        Returns
        -------
        Question
            A staff with only a clef and the signature, captioned '_ Major' (or '_ minor', '_ Dorian' and so on).

        Examples
        --------
        >>> # noinspection PyProtectedMember
        >>> q = KeySignatures._read_question(Note.parse("G4"), mode="Major (Ionian)", count=1, clef="treble",
        ...                                  rng=random.Random(0))
        >>> q.answer, q.caption, q.show_staff
        ('G', '_ Major', True)
        """
        correct = tonic.name
        near = [mode_tonic(c, mode=mode).name for c in range(count - 2, count + 3) if abs(c) <= 7]
        everyone = [mode_tonic(c, mode=mode).name for c in range(-7, 8)]
        choices = pick_distractors(
            correct,
            pool=near + everyone,
            n=5,
            rng=rng,
        )
        word = MODE_WORDS.get(mode, f"{mode} scale")
        notes = [*build(tonic, intervals=SCALES[mode]), tonic.transpose(Interval(8, quality="P"))]  # the scale, up to its octave
        return Question(
            f"Which {word} has this key signature?",
            choices=choices,
            answer=correct,
            clef=clef,
            key=count,
            show_staff=True,
            caption=_blank_scale(mode),
            explanation=f"{format_key_signature(count)}: {tonic.name} {_scale_name(mode)}: " + " ".join(n.name for n in notes),
        )


@register
class KeySignatureConstruction(Exercise):
    """
    Build the key signature of a named key on a blank staff, with the fork.

    Examples
    --------
    >>> q = KeySignatureConstruction().generate(random.Random(5))
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
        >>> KeySignatureConstruction().settings_signature().startswith("[")
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
        >>> "Key Signature Construction" in KeySignatureConstruction().instructions()
        True
        """
        return (
            "<b>Key Signature Construction</b><br>The key under the staff is the one to build. Pick how many sharps (top) "
            "or flats (bottom) it has on the fork under the staff, then press Answer (or Return). The staff shows what you "
            "have picked.<br><br>Click a number on the fork, or turn the mouse wheel to move the circle along it. The "
            "natural sign at the end of the stem is C major, with no sharps or flats.<br><br>"
            "Without the mouse: the Up or Right arrow adds a sharp, the Down or Left arrow adds a flat, and Home goes "
            "back to none. Then press Return to answer.<br><br>"
            "A mode uses the signature of a major key, started from another degree: D Dorian has the signature of C "
            "major.<br><br>Use the sliders button to choose the clefs, the scales and the key signatures."
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
            A blank staff captioned with the key, such as 'D Major'; the answer is its sharps or flats.

        Examples
        --------
        >>> q = KeySignatureConstruction().generate(random.Random(1))
        >>> q.caption.split()[0] in {"C", "D", "E", "F", "G", "A", "B"} or "♯" in q.caption or "♭" in q.caption
        True
        >>> q.answer == format_key_signature(q.key)
        True
        """
        cfg = settings.key_construction
        mode = rng.choice(cfg.active_modes())
        count = rng.choice(cfg.active_keys())
        tonic = mode_tonic(count, mode=mode)
        name = f"{tonic.name} {_blank_scale(mode)[2:]}"  # "D Major", "A♯ minor", "E Dorian"
        notes = [*build(tonic, intervals=SCALES[mode]), tonic.transpose(Interval(8, quality="P"))]  # the scale, up to its octave
        return Question(
            f"Build the key signature of {name}.",
            choices=[],
            answer=format_key_signature(count),
            clef=rng.choice(cfg.active_clefs()),
            key=count,
            show_staff=True,
            caption=name,
            build_key=True,
            explanation=f"{name}: {format_key_signature(count)}: " + " ".join(n.name for n in notes),
        )


@register
class ScaleDegrees(Exercise):
    """
    Spell a note of a scale or mode from its tonic.

    Examples
    --------
    >>> q = ScaleDegrees().generate(random.Random(7))
    >>> q.prompt.startswith("In ") and q.answer in q.choices
    True
    """

    name = "Scale Spelling"
    category = "Scales & keys"
    description = "Spell a note of a scale or mode from its tonic."
    par_seconds = 8.0

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML.

        Examples
        --------
        >>> "degree" in ScaleDegrees().instructions()
        True
        """
        return (
            "<b>Scale Spelling</b><br>Work out the note at the given degree of the scale or mode and press its name. "
            "Each scale uses every letter name once, so use a sharp or flat where the pattern needs one. You can press an "
            "answer's number instead of the button: 1 is the first."
        )

    def generate(self, rng: random.Random) -> Question:
        """
        Make a question asking for one degree of a scale.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            For example 'In E♭ Dorian, what is scale degree 6?', answered 'C'.

        Examples
        --------
        >>> q = ScaleDegrees().generate(random.Random(8))
        >>> "scale degree" in q.prompt
        True
        """
        scale = rng.choice(list(SCALES))
        tonic = rng.choice([Note(4, letter=l, accidental=a) for l in range(7) for a in (-1, 0, 1)])
        degree = rng.randint(2, 7)
        notes = build(tonic, intervals=SCALES[scale])
        if any(abs(n.accidental) > 1 for n in notes):
            return self.generate(rng)
        target = notes[degree - 1]
        pool = [Note(4, letter=l, accidental=a).name for l in range(7) for a in (-1, 0, 1)]
        near = [Note.from_diatonic(target.diatonic, accidental=a).name for a in (-1, 0, 1)]
        choices = pick_distractors(
            target.name,
            pool=near + pool,
            n=5,
            rng=rng,
        )
        spelled = " ".join(n.name for n in notes)
        return Question(
            f"In {tonic.name} {scale}, what is scale degree {degree}?",
            choices=choices,
            answer=target.name,
            explanation=f"{tonic.name} {scale}: {spelled}",
        )


@register
class ScaleConstruction(Exercise):
    """
    Place the notes of a named scale on a blank staff, one after another.

    Examples
    --------
    >>> q = ScaleConstruction().generate(random.Random(5))
    >>> len(q.construct_scale or []), q.choices, q.key
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
        >>> ScaleConstruction().settings_signature().startswith("[")
        True
        """
        return signature(settings.scale_construction)

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
                "<b>Scale Construction</b><br>The name of a scale is under the blank staff. Click the staff to place its "
                "notes from left to right, going up from the first note to the same note an octave higher: eight notes in "
                "all. The note follows the pointer, and each click puts it in the next place. "
                + (
                    "The name says which octave the first note is in, such as G2 Major: start on that note, G in octave 2 "
                    "(middle C is C4), and place the whole scale above it."
                    if settings.scale_construction.octave
                    else "Any octave will do, as long as all eight notes are in the same one."
                )
            ),
            (
                "The staff has no key signature, so a note that needs a sharp or a flat needs its own sign. Right click "
                "the staff or turn the mouse wheel to step through no sign, ♯ and ♭ for the next note (or choose a sign "
                "with the buttons), then click. Only the exact spelling counts, so G♯ is not A♭."
            ),
        ]
        if any(settings.scale_construction.staff_keys):
            text.append(
                "The staff may have a key signature, and it need not be the scale's. A note you place with no sign takes "
                "the sign that the staff's signature gives its letter: with two flats, B and E are flat. So a scale with a "
                "different signature needs signs where it differs: a C major scale on that staff needs a natural (♮) on "
                "its B and E, and a note that the staff does not flatten but the scale does needs a flat.",
            )
        if settings.scale_construction.steps:
            text.append(
                "Once the eight notes are placed, mark the steps between them. Two lines rise from each pair of "
                "neighbouring notes to a point above them, and the point takes W for a whole step or H for a half step. "
                "Turn the mouse wheel, right click, press the W and H buttons or keys, or use the arrow keys to choose, "
                "then click the staff (or press Return) to mark it and move on to the next pair.",
            )
        text.append(
            "You can do all of this without the mouse. The Up and Down arrows (or the Higher and Lower buttons) move the "
            "next note a line or space, Page Up and Page Down (or the Octave buttons) an octave, and typing a letter from A "
            "to G jumps to the nearest note with that name. The Left and Right arrows, or the keys + - and 0, choose its "
            "sign. Press Return (or Place note) to place it. The line under the staff says what comes next.",
        )
        text.append(
            "Undo (or Backspace) takes back the last thing you placed, the steps first. Press Answer (or Return) when "
            "everything is placed. A wrong scale is cleared so that you can try again. A right one is played, each note "
            "turning green as it sounds.",
        )
        text.append(
            "A mode uses the signature of a major key, started from another degree: D Dorian has the notes of C major, "
            "started from D. Use the sliders button to choose the clefs, the scales, the key signatures and whether to "
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
            A blank staff captioned with the scale, such as 'D Major'; `construct_scale` is its eight notes, going up an octave.

        Examples
        --------
        >>> q = ScaleConstruction().generate(random.Random(1))
        >>> scale = q.construct_scale or []
        >>> scale[0].name == scale[-1].name and q.accidentals
        True
        >>> q.check_scale(scale)
        True
        """
        cfg = settings.scale_construction
        mode = rng.choice(cfg.active_modes())
        count = rng.choice(cfg.active_keys())
        clef = rng.choice(cfg.active_clefs())
        staff_key = rng.choice(cfg.active_staff_keys())  # the signature on the staff, whatever the scale's own is
        named = mode_tonic(count, mode=mode)
        bottom = settings.BOTTOM_LINES[clef].diatonic
        starts = [d for d in range(bottom - 3, bottom + 4) if d % 7 == named.letter]  # the scale sits on the staff
        if cfg.octave:  # the octave is part of the question, so any octave where the whole scale can be placed will do
            low, high = settings.RANGE_LIMITS[clef]  # the furthest the staff can be clicked, ledger lines and all
            starts = [d for d in range(low, high - 6) if d % 7 == named.letter] or starts  # the top note is 7 steps up
        tonic = Note.from_diatonic(rng.choice(starts), accidental=named.accidental)
        notes = [*build(tonic, intervals=SCALES[mode]), tonic.transpose(Interval(8, quality="P"))]
        kind = _blank_scale(mode)[2:]  # "Major", "minor", "Dorian"
        name = f"{tonic.name}{tonic.octave} {kind}" if cfg.octave else f"{tonic.name} {kind}"  # "G2 Major", or "G Major"
        steps = ["W" if b.midi - a.midi == 2 else "H" for a, b in zip(notes, notes[1:], strict=False)] if cfg.steps else None
        explanation = f"{name}: " + " ".join(n.name for n in notes)
        if steps:
            explanation += f" ({' '.join(steps)})"
        if staff_key and staff_key != count:  # a signature that is not the scale's own: say so
            explanation += f". The staff has {format_key_signature(staff_key)}, but the scale has {format_key_signature(count)}"
        return Question(
            f"Place the notes of the {name} scale on the staff" + (", then mark its whole and half steps." if steps else "."),
            choices=[],
            answer=" ".join(f"{n.name}{n.octave}" for n in notes),
            clef=clef,
            key=staff_key,
            construct_scale=notes,
            construct_steps=steps,
            exact_octave=cfg.octave,
            accidentals=True,
            caption=name,
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
)  # the major keys that can be named: the naturals, and the sharp and flat keys
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
}  # the letters in the middle row, the sharps above them and the flats below, as on the piano keyboard exercise


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
)  # the minor keys that can be named: the ones on the circle, with their other names
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
}  # laid out like the major keys: the letters in the middle row, the sharps above and the flats below
NUMERAL_CHOICES: list[str] = list(
    NUMERALS,
)  # the six chords of a key that are on the circle: capitals are major, small letters minor


@register
class CircleOfFifths(Exercise):
    """
    Questions on the circle of fifths: a relative major, a relative minor, or the Roman numeral of a chord.

    Examples
    --------
    >>> q = CircleOfFifths().generate(random.Random(3))
    >>> q.circle is not None and q.answer in q.choices
    True
    """

    name = "Circle of Fifths"
    category = "Scales & keys"
    description = "Find relative keys and the chords of a key on the circle of fifths."
    par_seconds = 7.0
    has_sound = False

    def settings_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The kinds of question in force.

        Examples
        --------
        >>> CircleOfFifths().settings_signature().startswith("[")
        True
        """
        return signature(settings.circle)

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML, with a paragraph for each kind of question that is switched on.

        Examples
        --------
        >>> "circle of fifths" in CircleOfFifths().instructions()
        True
        """
        kinds = settings.circle.active_questions()
        text = [
            (
                "<b>Circle of Fifths</b><br>This is the circle of fifths. The outer ring has the major keys, with C at the "
                "top and a fifth higher at each step clockwise. The inner ring has their relative minors, which have the "
                "same key signature: A minor sits under C major. Each question lights one cell and leaves its answer blank. "
                "A right answer lights the cell, writes its name and shows the key signature on the staff in the middle. A "
                "wrong one flashes the cell red, striped, so you can try again."
            ),
        ]
        if "major" in kinds:
            text.append("<b>Relative major.</b> A minor key is shown. Press the name of its relative major.")
        if "minor" in kinds:
            text.append("<b>Relative minor.</b> A major key is shown. Press the name of its relative minor.")
        if "numeral" in kinds:
            text.append(
                "<b>Roman numerals.</b> A key is in the middle, with its staff, and its six chords that are on the circle "
                "are lit: the major chords I, IV and V on the outer ring, and the minor chords ii, iii and vi on the inner "
                "ring. (There is a seventh chord, vii°, which is diminished, and has no place on the circle.) Press the "
                "numeral of the chord asked about. Capitals are major chords and small letters are minor ones. A right "
                "answer shows the numerals of all six chords.",
            )
        text.append(
            "Some keys have two names, such as B and C♭ or G♯m and A♭m. For those you press both names, in either order. "
            "Press the letter of a key, Shift and the letter for a sharp, or Ctrl and the letter for a flat. A numeral is "
            "on the number keys.",
        )
        return "<br><br>".join(text)

    def generate(self, rng: random.Random) -> Question:
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
        >>> q = CircleOfFifths().generate(random.Random(5))
        >>> q.circle_kind, q.prompt
        ('minor', 'Which minor key is the relative minor of F major?')
        >>> settings.circle.questions = set(settings.CIRCLE_QUESTIONS)
        """
        kind = rng.choice(settings.circle.active_questions())
        if kind == "numeral":
            return self._numeral_question(rng)
        place = rng.randrange(len(MAJORS))
        return self._minor_question(place) if kind == "minor" else self._major_question(place)

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
            The minor key is shown; the answer is its major. A key with two names needs both.

        Examples
        --------
        >>> # noinspection PyProtectedMember
        >>> q = CircleOfFifths._major_question(5)
        >>> q.answer, q.required, q.circle_ring
        ('B', ('B', 'C♭'), 'outer')
        >>> # noinspection PyProtectedMember
        >>> CircleOfFifths._major_question(3).required  # one name: nothing more to press
        ()
        """
        names = MAJORS[place]
        main, double = names[0], len(names) > 1
        both = " Press both of its names." if double else ""
        return Question(
            f"Which major key is the relative major of {display_minor(place)}?{both}",
            choices=list(MAJOR_CHOICES),
            answer=main,
            required=names if double else (),
            grid=dict(MAJOR_GRID),
            circle=place,
            circle_kind="major",
            circle_ring="outer",
            caption=f"{MINORS[place][0][:-1]} minor",
            explanation=(
                f"{display_major(place)} and {display_minor(place)} have the same key signature: "
                f"{format_key_signature(SIGNATURES[place])}. A relative minor starts on the sixth note of the major."
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
            The major key is shown; the answer is its minor. A key with two names needs both.

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
            f"Which minor key is the relative minor of {display_major(place)}?{both}",
            choices=list(MINOR_CHOICES),
            answer=main,
            required=names if double else (),
            grid=dict(MINOR_GRID),
            circle=place,
            circle_kind="minor",
            circle_ring="inner",
            caption=f"{MAJORS[place][0]} major",
            explanation=(
                f"{display_major(place)} and {display_minor(place)} have the same key signature: "
                f"{format_key_signature(SIGNATURES[place])}. A relative minor starts on the sixth note of the major."
            ),
        )

    @staticmethod
    def _numeral_question(rng: random.Random) -> Question:
        """
        Ask for the Roman numeral of one of the six chords of a key that are on the circle.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            A key is shown, with its six chords lit; the answer is the numeral of one of them.

        Examples
        --------
        >>> # noinspection PyProtectedMember
        >>> q = CircleOfFifths._numeral_question(random.Random(2))
        >>> q.circle_kind, q.circle_key is not None, q.answer in NUMERAL_CHOICES
        ('numeral', True, True)
        """
        key = rng.randrange(len(MAJORS))
        (ring, place), numeral = rng.choice(list(cells_of_key(key).items()))
        chords = numeral_chords(key)
        tonic = MAJORS[key][0]
        return Question(
            f"In {tonic} major, which Roman numeral is the chord {chords[numeral]}?",
            choices=list(NUMERAL_CHOICES),
            answer=numeral,
            circle=place,
            circle_kind="numeral",
            circle_ring=ring,
            circle_key=key,
            caption=f"{tonic} major",
            explanation=f"In {tonic} major: " + ", ".join(f"{n} {chords[n]}" for n in NUMERALS) + ".",
        )


@register
class ChordQualities(Exercise):
    """
    Identify the quality of a triad or seventh chord in root position.

    Examples
    --------
    >>> q = ChordQualities().generate(random.Random(9))
    >>> len(q.staff[0]) in (3, 4) and q.answer in q.choices
    True
    """

    name = "Chord Quality"
    category = "Chords"
    description = "Identify triads and seventh chords in root position."
    par_seconds = 6.0

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
            "<b>Chord Quality</b><br>A chord is shown in root position. Press its type. Check the size of the "
            "intervals stacked above the lowest note to tell the types apart. You can press an answer's number instead "
            "of the button: 1 is the first."
        )

    def generate(self, rng: random.Random) -> Question:
        """
        Make a chord in root position whose quality is to be named.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            The chord drawn as one stack of notes, with its type (such as 'minor 7th') as the answer.

        Examples
        --------
        >>> q = ChordQualities().generate(random.Random(10))
        >>> q.answer in CHORDS
        True
        """
        clef = rng.choice(("treble", "bass"))
        quality = rng.choice(list(CHORDS))
        root = _random_note(rng, clef=clef, accidentals=True)
        lo, hi = CLEF_RANGES[clef]
        chord = build(root, intervals=CHORDS[quality])
        if any(abs(n.accidental) > 1 for n in chord) or chord[-1].diatonic > hi.diatonic + 3:
            return self.generate(rng)
        choices = pick_distractors(
            quality,
            pool=list(CHORDS),
            n=4,
            rng=rng,
        )
        expl = f"{root.name} {quality}: " + " ".join(n.name for n in chord)
        return Question(
            "",
            choices=choices,
            answer=quality,
            staff=[chord],
            clef=clef,
            explanation=expl,
        )


# Where the lowest and highest note of an arpeggio may sit on each clef (up to two ledger lines either side of the staff).
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
class ArpeggioNames(Exercise):
    """
    Name the type and the inversion of a broken chord.

    Examples
    --------
    >>> q = ArpeggioNames().generate(random.Random(11))
    >>> q.octaves is not None and len(q.staff) >= 4
    True
    """

    name = "Arpeggio Identification"
    category = "Chords"
    description = "Name the type and the inversion of a broken chord."
    par_seconds = 9.0

    def settings_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The clefs, chord types, inversions and key signatures in force.

        Examples
        --------
        >>> ArpeggioNames().settings_signature().startswith("[")
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
            "<b>Arpeggio Identification</b><br>A chord is played one note at a time, rising from its lowest note to "
            "the same note an octave higher. Press its type, then its inversion. The type is on the number keys, 1 for the "
            "first, and the inversion is on the home row: A for the first, S for the second and so on.<br><br>"
            "Find the chord's root by looking for the notes a third apart. The inversion is which chord tone is "
            "lowest: the root (root position), the third (1st inversion), the fifth (2nd inversion) or the seventh "
            "(3rd inversion, seventh chords only).<br><br>"
            "Use the sliders button to choose the clefs, the types of arpeggio, the inversions and key signatures."
        )

    def generate(self, rng: random.Random) -> Question:
        """
        Make an arpeggio on one of the chosen clefs, in a chosen position.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            The arpeggio's notes one after another on a staff; the answer is the chord type and inversion, such as
            'major · 1st inversion'.

        Raises
        ------
        RuntimeError
            If no arpeggio fits the chosen clefs, chord types and inversions.

        Examples
        --------
        >>> q = ArpeggioNames().generate(random.Random(12))
        >>> " · " in q.answer
        True
        """
        cfg = settings.arpeggio
        for _ in range(500):
            chord_type = rng.choice(cfg.active_types())
            inversion = rng.choice(cfg.inversions_for(chord_type))
            clef = rng.choice(cfg.active_clefs())
            key = rng.choice(cfg.active_keys()) if cfg.key_signature else 0
            root = Note(4, letter=rng.randrange(7), accidental=rng.choice((-1, 0, 1)))
            if (root.letter, root.accidental) in (
                (2, 1),
                (6, 1),
                (0, -1),
                (3, -1),
            ):  # E♯ B♯ C♭ F♭ are not worth asking
                continue
            notes = arpeggio(root, intervals=CHORDS[chord_type], inversion=inversion)
            if any(abs(n.accidental) > 1 for n in notes):  # no double sharps or flats
                continue
            low, high = (n.diatonic for n in ARPEGGIO_WINDOWS[clef])
            fits = [s for s in range(-28, 29, 7) if notes[0].diatonic + s >= low and notes[-1].diatonic + s <= high]
            if not fits:
                continue
            shift = rng.choice(fits) // 7
            notes = [Note(n.octave + shift, letter=n.letter, accidental=n.accidental) for n in notes]
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
            0 for root position, 1 for the first inversion and so on. Keyword-only.
        root : Note
            The root of the chord. Keyword-only.
        notes : list of Note
            The arpeggio's notes, already moved to the right octave. Keyword-only.
        clef : str
            The clef to draw on. Keyword-only.
        key : int
            The key signature to draw. Keyword-only.
        cfg : ArpeggioSettings
            The settings, which decide which types and inversions have buttons. Keyword-only.

        Returns
        -------
        Question
            The notes drawn one after another, with a row of type buttons and a row of inversion buttons.

        Examples
        --------
        >>> cfg_ = settings.ArpeggioSettings()
        >>> notes_ = arpeggio(Note.parse("C4"), intervals=CHORDS["major"])
        >>> # noinspection PyProtectedMember
        >>> q = ArpeggioNames._question("major", inversion=0, root=Note.parse("C4"), notes=notes_, clef="treble", key=0, cfg=cfg_)
        >>> q.answer
        'major · root position'
        """
        joiner = " \u00b7 "
        types = cfg.active_types()
        inversions = sorted({i for t in types for i in cfg.inversions_for(t)})
        answer = f"{chord_type}{joiner}{INVERSION_NAMES[inversion]}"
        grid = {t: divmod(i, 5) for i, t in enumerate(types)} if len(types) > 5 else None  # two rows once there are many
        expl = f"{root.name} {chord_type}, {INVERSION_NAMES[inversion]}: " + " ".join(n.name for n in notes)
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


# Black keys: pitch class -> (letter, accidental) for the sharp name and for the flat name.
_BLACK_KEY_NAMES = {
    1: ((0, 1), (1, -1)),
    3: ((1, 1), (2, -1)),
    6: ((3, 1), (4, -1)),
    8: ((4, 1), (5, -1)),
    10: ((5, 1), (6, -1)),
}
_WHITE_KEY_LETTER = {
    0: 0,
    2: 1,
    4: 2,
    5: 3,
    7: 4,
    9: 5,
    11: 6,
}


def _key_tonic(count: int) -> Note:
    """
    Return the tonic of a major key.

    Parameters
    ----------
    count : int
        Sharps (positive) or flats (negative) in the key signature, from -7 to 7.

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
    return Note(4, letter="CDEFGAB".index(name[0]), accidental=1 if "♯" in name else -1 if "♭" in name else 0)


def _key_spellings(
    pc: int,
    *,
    count: int | None,
) -> list[tuple[int, int]]:
    """
    Return the names that are correct for a piano key in a key signature.

    Notes of the key keep the spelling the key gives them (the F key is E♯ in C♯ major). Other white keys use their natural
    name. Other black keys are spelled with sharps in a sharp key and flats in a flat key; with no signature (or none given)
    either name is right.

    Parameters
    ----------
    pc : int
        The key's pitch class, 0 for C up to 11 for B.
    count : int or None
        The key signature: sharps if positive, flats if negative, 0 for none, or None for no key signature shown. Keyword-only.

    Returns
    -------
    list of tuple of (int, int)
        The correct (letter, accidental) pairs, most preferred first.

    Examples
    --------
    >>> _key_spellings(6, count=None)  # a black key with no signature: F♯ or G♭
    [(3, 1), (4, -1)]
    >>> _key_spellings(6, count=-2)  # in B♭ major it is not in the key, so a flat key spells it with a flat
    [(4, -1)]
    >>> _key_spellings(0, count=None)
    [(0, 0)]
    """
    diatonic = {}
    if count is not None:
        diatonic = {n.pitch_class: (n.letter, n.accidental) for n in build(_key_tonic(count), intervals=SCALES["Major (Ionian)"])}
    if pc in diatonic:
        return [diatonic[pc]]
    if pc in _WHITE_KEY_LETTER:
        return [(_WHITE_KEY_LETTER[pc], 0)]
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
    Return the note that sounds as a MIDI number when written with a given letter name.

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
    >>> str(_spelled(61, letter=1, accidental=-1))  # MIDI 61 written as D♭
    'D♭4'
    >>> str(_spelled(59, letter=0, accidental=-1))  # MIDI 59 written as C♭
    'C♭4'
    """
    return Note((midi - accidental - NATURAL_SEMITONES[letter]) // 12 - 1, letter=letter, accidental=accidental)


@register
class KeyboardNotes(Exercise):
    """
    Name the highlighted key on a piano keyboard.

    Examples
    --------
    >>> q = KeyboardNotes().generate(random.Random(13))
    >>> q.keyboard is not None and q.answer in q.choices
    True
    """

    name = "Keyboard Identification"
    category = "Notation"
    description = "Name the highlighted key on a piano keyboard."
    par_seconds = 3.0

    def settings_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The keyboard range, black keys, octave and key signature settings, and the naming in force.

        Examples
        --------
        >>> KeyboardNotes().settings_signature().startswith("[")
        True
        """
        return signature(settings.keyboard, settings.note_names.naming)

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML, with paragraphs added for the octave and key signature settings that are on.

        Examples
        --------
        >>> "highlighted" in KeyboardNotes().instructions()
        True
        """
        cfg = settings.keyboard
        text = [
            (
                "<b>Keyboard Identification</b><br>One key on the keyboard is highlighted. Press the button with its name, "
                "or type its name on the keyboard: the letter for a natural, Shift and the letter for a sharp, Ctrl and "
                "the letter for a flat."
            ),
        ]
        if cfg.require_octave:
            text.append(
                "Choose its octave too, from the row below, or type its number. Octaves count up from C, so middle C is the "
                "C in octave 4.",
            )
        if cfg.key_signature:
            text.append(
                "A key signature is shown above the keyboard. Name the key the way that signature spells it. Only "
                "that spelling counts, so F♯ and G♭ are not interchangeable. A black key that is not in the key "
                "is spelled with sharps in a sharp key and with flats in a flat key.",
            )
        else:
            text.append("Black keys have two names, such as C♯ and D♭. Either one is accepted.")
        return "<br><br>".join(text)

    def generate(self, rng: random.Random) -> Question:
        """
        Make a keyboard with one key highlighted.

        Parameters
        ----------
        rng : random.Random
            The random number generator.

        Returns
        -------
        Question
            The keyboard, a grid of name buttons (and a row of octave buttons if octaves are asked), and the key's name as
            the answer, with the other spelling of a black key accepted.

        Examples
        --------
        >>> q = KeyboardNotes().generate(random.Random(14))
        >>> # noinspection PyUnresolvedReferences
        >>> q.keyboard_range[0] <= q.keyboard.midi <= q.keyboard_range[1]
        True
        """
        cfg = settings.keyboard
        naming = settings.note_names.naming
        lo, hi = sorted((cfg.low, cfg.high))
        candidates = [m for m in range(lo, hi + 1) if cfg.black_keys or m % 12 in _WHITE_KEY_LETTER] or [lo]
        count = rng.choice(cfg.active_keys()) if cfg.key_signature else None
        midi = rng.choice(candidates)

        spelled = [_spelled(midi, letter=letter, accidental=acc) for letter, acc in _key_spellings(midi % 12, count=count)]
        key = spelled[0]  # the key as the signature spells it (also what plays when you answer correctly)
        names = [spell(n, naming=naming) for n in spelled]
        answer, accept = names[0], tuple(names[1:])
        octaves = None
        if cfg.require_octave:
            octaves = [
                str(o)
                for o in sorted(
                    {
                        _spelled(m, letter=letter, accidental=accidental).octave
                        for m in candidates
                        for letter, accidental in _key_spellings(m % 12, count=count)[:1]  # the first spelling of each
                    },
                )
            ]
            answer, accept = f"{names[0]}{spelled[0].octave}", tuple(f"{n}{sp.octave}" for n, sp in zip(names[1:], spelled[1:]))

        if len(spelled) > 1:
            explanation = f"{names[0]} and {names[1]} are the same black key."
        elif count is not None:
            # noinspection PyTypeChecker
            in_key = midi % 12 in {n.pitch_class for n in build(_key_tonic(count), intervals=SCALES["Major (Ionian)"])}
            # noinspection PyTypeChecker
            explanation = f"In {MAJOR_KEYS[count]} major ({format_key_signature(count)}) this key is called {names[0]}."
            if not in_key and midi % 12 not in _WHITE_KEY_LETTER:
                # noinspection PyTypeChecker
                explanation += f" It is not in the key, so it is spelled with {'sharps' if count > 0 else 'flats'}."
        else:
            explanation = ""

        # One button per name: sharps on the top row, naturals in the middle, flats below, a column per letter.
        # A key signature can need any spelling (E♯, C♭ ...), so it gets the full set.
        grid, choices = {}, []
        for letter in range(7):
            n = spell(Note(4, letter=letter), naming=naming)
            choices.append(n)
            grid[n] = (1, letter)
        if cfg.key_signature:
            extra = [(letter, acc, 0 if acc > 0 else 2) for letter in range(7) for acc in (1, -1)]
        elif cfg.black_keys:
            extra = [
                (letter, acc, row)
                for (sharp, flat) in _BLACK_KEY_NAMES.values()
                for (letter, acc), row in ((sharp, 0), (flat, 2))
            ]
        else:
            extra = []
        for letter, acc, row in extra:
            n = spell(Note(4, letter=letter, accidental=acc), naming=naming)
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
            keyboard_range=(lo, hi),
            octaves=octaves,
            key=count or 0,
            key_staff=cfg.key_signature,
        )


@register
class NoteConstruction(Exercise):
    """
    Place a named note on the staff.

    Examples
    --------
    >>> q = NoteConstruction().generate(random.Random(15))
    >>> q.construct is not None and q.prompt.startswith("Place ")
    True
    """

    name = "Note Construction"
    category = "Notation"
    description = "Place the named note on the staff."
    par_seconds = 6.0

    def settings_signature(self) -> str:
        """
        Return what identifies the settings that shape these questions.

        Returns
        -------
        str
            The clefs, accidentals and key signature settings, and the naming in force.

        Examples
        --------
        >>> NoteConstruction().settings_signature().startswith("[")
        True
        """
        return signature(settings.construction, settings.note_names.naming)

    def instructions(self) -> str:
        """
        Return the help text for the exercise.

        Returns
        -------
        str
            Simple HTML, with paragraphs added for the key signature and accidental settings that are on.

        Examples
        --------
        >>> "Click the staff" in NoteConstruction().instructions()
        True
        """
        cfg = settings.construction
        text = [
            (
                "<b>Note Construction</b><br>A note name is shown. Click the staff where that note belongs. The octave "
                "counts: the number says which C-to-B you mean, and middle C is C4. On a grand staff, click the upper "
                "staff for notes from middle C up and the lower staff for the notes below it."
            ),
        ]
        if cfg.key_signature:
            text.append(
                "A key signature is drawn at the start of the staff. It already applies to every note of that "
                "letter, so in G major you place F♯ on the F line with no sign. A note that the key does not "
                "give you needs its own sign.",
            )
        if cfg.accidentals:
            text.append(
                "To give a note its own sign, choose ♯, ♮ or ♭ first, then click the staff. You can also right "
                "click the staff to step through them. ♮ cancels a sharp or flat from the key signature. Only the "
                "exact spelling counts, so G♯ is not A♭.",
            )
        text.append(
            "You can do all of this without the mouse. The Up and Down arrows (or the Higher and Lower buttons) move the "
            "note a line or space, and Page Up and Page Down (or the Octave buttons) an octave. Typing a letter from A to G "
            "jumps to the nearest note with that name. Press Return (or Place note) to place it."
            + (" The Left and Right arrows, or the keys + - and 0, choose a sign." if cfg.accidentals else ""),
        )
        text.append("A wrong click shows the note you placed so you can adjust and try again.")
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
            A prompt such as 'Place F♯4 on the staff.'; the answer is the note's name, and `construct` is the note to place.

        Examples
        --------
        >>> q = NoteConstruction().generate(random.Random(16))
        >>> q.answer in q.prompt
        True
        """
        cfg = settings.construction
        clef = rng.choice(cfg.active_clefs())
        lo, hi = settings.DEFAULT_RANGES[clef]
        count = rng.choice(cfg.active_keys()) if cfg.key_signature else 0
        diatonic = rng.randint(lo, hi)
        implied = key_accidental(diatonic % 7, count=count)  # what the key signature already does to this letter
        accidental = implied
        if cfg.accidentals and rng.random() < (0.4 if cfg.key_signature else 0.5):
            accidental = rng.choice([a for a in (-1, 0, 1) if a != implied])  # a sign that differs from the key
        note = Note.from_diatonic(diatonic, accidental=accidental)
        name = f"{spell(note, naming=settings.note_names.naming)}{note.octave}"
        explanation = ""
        if cfg.key_signature and count:
            key_name = f"{MAJOR_KEYS[count]} major ({format_key_signature(count)})"
            word = {1: "sharp", -1: "flat", 0: "natural"}
            if accidental == implied and implied:
                explanation = f"In {key_name} the key signature already makes this a {word[implied]}, so it needs no sign."
            elif accidental != implied:
                explanation = f"In {key_name} this note needs its own {word[accidental]} sign."
        return Question(
            f"Place {name} on the staff.",
            choices=[],
            answer=name,
            clef=clef,
            construct=note,
            accidentals=cfg.accidentals,
            key=count,
            explanation=explanation,
        )
