"""
Load and save each exercise's settings.

The settings themselves are plain dataclasses in `alto.settings`, one
shared object per exercise. The functions here read them
from the saved preferences when Alto starts (`load_exercise_settings`)
and write them back when a settings panel changes them.
Values saved by older versions are converted, and anything saved that is
not valid any more is ignored.

Examples
--------
>>> load_note_names()
>>> settings.note_names.naming in NAMINGS
True
"""

from __future__ import annotations

from alto import settings
from alto.audio import INSTRUMENT_BY_KEY
from alto.circle_schemes import (
    DEFAULT_SCHEME,
    PRESETS,
    dump_customs,
    load_customs,
)
from alto.exercises.base import REGISTRY, ChoiceExercise
from alto.exercises.packs import PackExercise
from alto.settings import (
    CLEFS,
    DEFAULT_RANGES,
    MAX_DIATONIC,
    MIN_DIATONIC,
    NAMINGS,
    NOTE_VALUES,
    RANGE_LIMITS,
)
from alto.ui.store import (
    bool_value,
    choices_value,
    int_value,
    joined,
    keys_value,
    list_value,
    save_bool,
    store,
    text_value,
)


def load_note_names() -> None:
    """
    Load the saved note identification settings into the shared settings
    object.

    Settings saved by an older version, which had a switch between the
    grand staff and single clefs, are converted. Anything
    in the saved data that is not valid is ignored.

    Examples
    --------
    >>> cfg_ = settings.note_names
    >>> cfg_.clefs = {"alto"}
    >>> save_note_names()
    >>> cfg_.clefs = {"treble"}
    >>> load_note_names()
    >>> cfg_.clefs
    {'alto'}
    >>> cfg_.clefs = {"treble", "bass"}
    >>> save_note_names()
    """
    s = store()
    cfg = settings.note_names
    if s.value("noteNames/clefs") is not None:
        cfg.clefs = choices_value(
            s,
            key="noteNames/clefs",
            allowed=settings.RANGE_KEYS,
        )
    if (
        s.value("noteNames/mode") == "grand"
        # an older version had a switch between the grand staff and
        # single
        # clefs
    ):
        cfg.clefs = {"grand"}
    s.remove("noteNames/mode")
    cfg.minor_keys = keys_value(s, key="noteNames/minorKeys")
    cfg.key_signatures = keys_value(s, key="noteNames/keys")
    if not (cfg.key_signatures or cfg.minor_keys):
        cfg.key_signatures = {0}
    if list_value(s, key="noteNames/values"):
        cfg.note_values = choices_value(
            s,
            key="noteNames/values",
            allowed=NOTE_VALUES,
        ) or {"whole"}
    naming = text_value(s, key="noteNames/naming", default=cfg.naming)
    cfg.naming = naming if naming in NAMINGS else "letters"
    cfg.scale_answer = bool_value(
        s,
        key="noteNames/scaleAnswer",
        default=False,
    )
    # Older note questions used the question key on the staff. Scale
    # answers used a blank staff regardless of their question key.
    cfg.staff_keys = keys_value(s, key="noteNames/staffKeys") or (
        {0} if cfg.scale_answer else cfg.key_signatures | cfg.minor_keys
    )
    cfg.scale_keys = keys_value(s, key="noteNames/scaleKeys")
    cfg.scale_minor_keys = keys_value(s, key="noteNames/scaleMinorKeys")
    if not (cfg.scale_keys or cfg.scale_minor_keys):
        cfg.scale_keys = set(range(-7, 8))
    if not s.contains("noteNames/minorKeys") and bool_value(
        s,
        key="noteNames/minorDegrees",
        default=False,
    ):
        cfg.minor_keys, cfg.key_signatures = cfg.key_signatures, set()
    cfg.accidentals = bool_value(s, key="noteNames/accidentals", default=False)
    cfg.require_octave = bool_value(
        s,
        key="noteNames/requireOctave",
        default=False,
    )
    cfg.ranges = {}
    for item in list_value(
        s,
        key="noteNames/ranges",
    ):  # e.g. "treble:31-33,bass:14-28"
        try:
            key, span = item.split(":")
            lo, hi = (int(x) for x in span.split("-"))
        except ValueError:
            continue
        if key in DEFAULT_RANGES and MIN_DIATONIC <= lo <= hi <= MAX_DIATONIC:
            cfg.ranges[key] = (lo, hi)


def save_note_names() -> None:
    """
    Save the note identification settings.

    Examples
    --------
    >>> cfg_ = settings.note_names
    >>> cfg_.naming = "solfege"
    >>> save_note_names()
    >>> str(store().value("noteNames/naming"))
    'solfege'
    >>> cfg_.naming = "letters"
    >>> save_note_names()
    """
    s = store()
    cfg = settings.note_names
    s.setValue(
        "noteNames/clefs",
        joined(c for c in settings.RANGE_KEYS if c in cfg.clefs),
    )
    s.setValue("noteNames/keys", joined(sorted(cfg.key_signatures)))
    save_bool(s, key="noteNames/scaleAnswer", value=cfg.scale_answer)
    s.setValue("noteNames/staffKeys", joined(sorted(cfg.staff_keys) or [0]))
    s.setValue("noteNames/minorKeys", joined(sorted(cfg.minor_keys)))
    s.setValue(
        "noteNames/scaleMinorKeys",
        joined(sorted(cfg.scale_minor_keys)),
    )
    s.setValue("noteNames/scaleKeys", joined(sorted(cfg.scale_keys)))
    s.setValue("noteNames/values", joined(cfg.active_values()))
    if not s.contains("keyboard/naming"):
        # Freeze the old shared choice before the staff changes it.
        previous = text_value(s, key="noteNames/naming", default="letters")
        s.setValue("keyboard/naming", previous)
    s.setValue("noteNames/naming", cfg.naming)
    s.remove("noteNames/minorDegrees")
    save_bool(s, key="noteNames/accidentals", value=cfg.accidentals)
    save_bool(s, key="noteNames/requireOctave", value=cfg.require_octave)
    s.setValue(
        "noteNames/ranges",
        ",".join(f"{k}:{lo}-{hi}" for k, (lo, hi) in cfg.ranges.items()),
    )


def load_keyboard() -> None:
    """
    Load the saved keyboard exercise settings into the shared settings
    object.

    A saved range that is not a valid span of keys, or a key list with
    nothing usable in it, is ignored.

    Examples
    --------
    >>> cfg_ = settings.keyboard
    >>> cfg_.require_octave = True
    >>> save_keyboard()
    >>> cfg_.require_octave = False
    >>> load_keyboard()
    >>> cfg_.require_octave
    True
    >>> cfg_.require_octave = False
    >>> save_keyboard()
    """
    saved_settings = store()
    cfg = settings.keyboard
    key = "keyboard/naming"
    if not saved_settings.contains(key):
        key = "noteNames/naming"  # older profiles shared this choice
    naming = text_value(saved_settings, key=key, default="letters")
    cfg.naming = naming if naming in NAMINGS else "letters"
    cfg.black_keys = bool_value(
        saved_settings,
        key="keyboard/blackKeys",
        default=True,
    )
    cfg.require_octave = bool_value(
        saved_settings,
        key="keyboard/requireOctave",
        default=False,
    )
    try:
        low = int_value(saved_settings, key="keyboard/low", default=cfg.low)
        high = int_value(saved_settings, key="keyboard/high", default=cfg.high)
    except (TypeError, ValueError):
        return
    first, last = settings.KEYBOARD_FULL
    if first <= low <= high <= last:
        cfg.low, cfg.high = low, high
    cfg.key_signature = bool_value(
        saved_settings,
        key="keyboard/keySignature",
        default=False,
    )
    cfg.keys = keys_value(saved_settings, key="keyboard/keys") or cfg.keys


def save_keyboard() -> None:
    """
    Save the keyboard exercise settings.

    Examples
    --------
    >>> cfg_ = settings.keyboard
    >>> save_keyboard()
    >>> int(
    ...     store().value("keyboard/low")
    ... ) == cfg_.low
    True
    """
    saved_settings = store()
    cfg = settings.keyboard
    saved_settings.setValue("keyboard/naming", cfg.naming)
    save_bool(saved_settings, key="keyboard/blackKeys", value=cfg.black_keys)
    save_bool(
        saved_settings,
        key="keyboard/requireOctave",
        value=cfg.require_octave,
    )
    saved_settings.setValue("keyboard/low", cfg.low)
    saved_settings.setValue("keyboard/high", cfg.high)
    save_bool(
        saved_settings,
        key="keyboard/keySignature",
        value=cfg.key_signature,
    )
    saved_settings.setValue("keyboard/keys", joined(cfg.active_keys()))


def load_keyboard_intervals() -> None:
    """
    Load keyboard interval settings, ignoring invalid values and
    intervals that cannot fit.

    Examples
    --------
    >>> load_keyboard_intervals()
    >>> settings.keyboard_intervals.bounds()[
    ...     0
    ... ] < settings.keyboard_intervals.bounds()[1]
    True
    """
    saved = store()
    cfg = settings.keyboard_intervals
    defaults = settings.KeyboardIntervalSettings()
    try:
        low = int_value(
            saved,
            key="keyboardIntervals/low",
            default=defaults.low,
        )
        high = int_value(
            saved,
            key="keyboardIntervals/high",
            default=defaults.high,
        )
    except (TypeError, ValueError):
        low, high = defaults.bounds()
    first, last = settings.KEYBOARD_FULL
    cfg.low, cfg.high = (
        (low, high) if first <= low < high <= last else defaults.bounds()
    )
    selected = text_value(
        saved,
        key="keyboardIntervals/intervals",
        default=joined(range(1, 13)),
    )
    cfg.intervals = {
        int(value)
        for value in selected.split(",")
        if value.isdecimal() and 1 <= int(value) <= last - first
    }
    if not cfg.intervals and selected.strip():
        cfg.intervals = {1}
    cfg.intervals = set(cfg.active_intervals())
    cfg.compact_buttons = bool_value(
        saved,
        key="keyboardIntervals/compactButtons",
        default=False,
    )
    cfg.all_interval_buttons = bool_value(
        saved,
        key="keyboardIntervals/allButtons",
        default=False,
    )
    try:
        cfg.button_count = int_value(
            saved,
            key="keyboardIntervals/buttonCount",
            default=6,
        )
    except (TypeError, ValueError):
        cfg.button_count = 6
    cfg.button_count = cfg.answer_button_limit()


def save_keyboard_intervals(cfg: settings.KeyboardIntervalSettings) -> None:
    """
    Save the keyboard interval range and selected distances.

    Parameters
    ----------
    cfg : KeyboardIntervalSettings
        The settings to save.

    Examples
    --------
    >>> save_keyboard_intervals(
    ...     settings.KeyboardIntervalSettings()
    ... )
    >>> int(store().value("keyboardIntervals/low"))
    48
    """
    saved = store()
    low, high = cfg.bounds()
    saved.setValue("keyboardIntervals/low", low)
    saved.setValue("keyboardIntervals/high", high)
    saved.setValue(
        "keyboardIntervals/intervals",
        joined(cfg.active_intervals()),
    )
    save_bool(
        saved,
        key="keyboardIntervals/compactButtons",
        value=cfg.compact_buttons,
    )
    save_bool(
        saved,
        key="keyboardIntervals/allButtons",
        value=cfg.all_interval_buttons,
    )
    saved.setValue("keyboardIntervals/buttonCount", cfg.answer_button_limit())


def load_construction() -> None:
    """
    Load the saved note construction settings into the shared settings
    object.

    Examples
    --------
    >>> store().setValue(
    ...     "construction/accidentals", "true"
    ... )
    >>> load_construction()
    >>> settings.construction.accidentals
    False
    """
    saved_settings = store()
    cfg = settings.construction
    cfg.clefs = (
        choices_value(
            saved_settings,
            key="construction/clefs",
            allowed=settings.RANGE_KEYS,
        )
        or cfg.clefs
    )
    cfg.question_type = (
        "notes"
        if text_value(
            saved_settings,
            key="construction/questionType",
            default="scale",
        )
        == "notes"
        else "scale"
    )
    degrees = list_value(saved_settings, key="construction/degrees")
    cfg.degrees = {n for n in range(1, 8) if str(n) in degrees} or set(
        range(1, 8),
    )
    cfg.octave = bool_value(
        saved_settings,
        key="construction/octave",
        default=True,
    )
    cfg.accidentals = False  # ignore the retired setting in existing profiles
    mode = text_value(
        saved_settings,
        key="construction/keyMode",
        default="major",
    )
    cfg.major = mode != "minor"
    cfg.minor = mode in {"minor", "both"}
    cfg.staff_keys = keys_value(
        saved_settings,
        key="construction/staffKeys",
    ) or {0}
    cfg.key_signature = True
    used_signatures = bool_value(
        saved_settings,
        key="construction/keySignature",
        default=False,
    )
    cfg.keys = keys_value(saved_settings, key="construction/keys") or cfg.keys
    cfg.minor_keys = (
        keys_value(saved_settings, key="construction/minorKeys") or None
    )
    if not used_signatures:
        cfg.keys = {0}
        cfg.minor_keys = {0}


def save_construction(cfg: settings.ConstructionSettings) -> None:
    """
    Save the note construction settings.

    Parameters
    ----------
    cfg : ConstructionSettings
        The settings to save.

    Examples
    --------
    >>> settings.construction.degrees = {1, 3}
    >>> save_construction(settings.construction)
    >>> str(store().value("construction/degrees"))
    '1,3'
    >>> settings.construction.degrees = set(
    ...     range(1, 8)
    ... )
    >>> save_construction(settings.construction)
    """
    saved_settings = store()
    saved_settings.setValue(
        "construction/clefs",
        joined(c for c in settings.RANGE_KEYS if c in cfg.clefs),
    )
    saved_settings.setValue("construction/keySignature", "true")
    saved_settings.setValue("construction/questionType", cfg.question_type)
    saved_settings.setValue(
        "construction/degrees",
        joined(sorted(cfg.degrees)),
    )
    save_bool(saved_settings, key="construction/octave", value=cfg.octave)
    saved_settings.setValue(
        "construction/staffKeys",
        joined(sorted(cfg.staff_keys or {0})),
    )
    saved_settings.setValue(
        "construction/keyMode",
        ("both" if cfg.major else "minor") if cfg.minor else "major",
    )
    saved_settings.setValue("construction/keys", joined(cfg.active_keys()))
    saved_settings.setValue(
        "construction/minorKeys",
        joined(sorted(cfg.minor_keys or cfg.keys)),
    )


def load_arpeggio() -> None:
    """
    Load the saved arpeggio settings into the shared settings object.

    Anything in the saved data that is not valid is ignored, and a list
    with nothing valid in it leaves the setting as it was.

    Examples
    --------
    >>> store().setValue("arpeggio/types", "major")
    >>> load_arpeggio()
    >>> settings.arpeggio.types
    {'major'}
    >>> settings.arpeggio.types = {
    ...     "major",
    ...     "minor",
    ...     "dominant 7th",
    ...     "diminished 7th",
    ... }
    >>> store().setValue(
    ...     "arpeggio/types",
    ...     ",".join(
    ...         settings.arpeggio.active_types()
    ...     ),
    ... )
    """
    saved_settings = store()
    cfg = settings.arpeggio
    cfg.clefs = (
        choices_value(saved_settings, key="arpeggio/clefs", allowed=CLEFS)
        or cfg.clefs
    )
    cfg.types = (
        choices_value(
            saved_settings,
            key="arpeggio/types",
            allowed=settings.ARPEGGIO_TYPES,
        )
        or cfg.types
    )
    inversions = list_value(saved_settings, key="arpeggio/inversions")
    cfg.inversions = {
        int(i)
        for i in inversions
        if i.isdigit() and int(i) in settings.INVERSIONS
    } or cfg.inversions
    cfg.key_signature = bool_value(
        saved_settings,
        key="arpeggio/keySignature",
        default=False,
    )
    cfg.keys = keys_value(saved_settings, key="arpeggio/keys") or cfg.keys


def save_arpeggio(cfg: settings.ArpeggioSettings) -> None:
    """
    Save the arpeggio settings.

    Parameters
    ----------
    cfg : ArpeggioSettings
        The settings to save.

    Examples
    --------
    >>> save_arpeggio(settings.arpeggio)
    >>> str(
    ...     store().value("arpeggio/clefs")
    ... ) == ",".join(
    ...     settings.arpeggio.active_clefs()
    ... )
    True
    """
    saved_settings = store()
    saved_settings.setValue("arpeggio/clefs", joined(cfg.active_clefs()))
    saved_settings.setValue("arpeggio/types", joined(cfg.active_types()))
    saved_settings.setValue(
        "arpeggio/inversions",
        joined(cfg.active_inversions()),
    )
    save_bool(
        saved_settings,
        key="arpeggio/keySignature",
        value=cfg.key_signature,
    )
    saved_settings.setValue("arpeggio/keys", joined(cfg.active_keys()))


def load_intervals(
    cfg: settings.IntervalSettings | None = None,
    *,
    prefix: str = "intervals",
) -> None:
    """
    Restore the saved staff interval options, keeping valid choices and
    per-clef ranges.

    Parameters
    ----------
    cfg : IntervalSettings or None
        Settings to populate. Defaults to Interval Identification.
    prefix : str
        Independent settings-store group for the exercise.

    Examples
    --------
    >>> load_intervals()
    >>> bool(settings.intervals.active_clefs())
    True
    """
    saved = store()
    cfg = settings.intervals if cfg is None else cfg
    defaults = settings.IntervalSettings()
    cfg.clefs = (
        choices_value(
            saved,
            key=f"{prefix}/clefs",
            allowed=settings.RANGE_KEYS,
        )
        or defaults.clefs
    )
    cfg.note_values = choices_value(
        saved,
        key=f"{prefix}/values",
        allowed=NOTE_VALUES,
    ) or {"whole"}
    cfg.displays = (
        choices_value(
            saved,
            key=f"{prefix}/display",
            allowed=settings.INTERVAL_DISPLAYS,
        )
        or defaults.displays
    )
    cfg.directions = (
        choices_value(
            saved,
            key=f"{prefix}/direction",
            allowed=settings.MELODIC_DIRECTIONS,
        )
        or defaults.directions
    )
    quality = text_value(
        saved,
        key=f"{prefix}/quality",
        default=defaults.quality_mode,
    )
    if (
        quality == "false"
    ):  # Older versions saved the Quality switch as "true" or "false".
        quality = "interval"
    cfg.quality_mode = (
        quality
        if quality in settings.INTERVAL_QUALITY_MODES
        else defaults.quality_mode
    )
    if prefix == "intervals":
        cfg.inversions = bool_value(
            saved,
            key=f"{prefix}/inversions",
            default=False,
        )
        cfg.consonance = bool_value(
            saved,
            key=f"{prefix}/consonance",
            default=False,
        )
    cfg.button_mode = (
        "all"
        if text_value(saved, key=f"{prefix}/buttonMode", default="limited")
        == "all"
        else "limited"
    )
    try:
        cfg.button_count = max(
            2,
            min(10, int_value(saved, key=f"{prefix}/buttonCount", default=6)),
        )
    except ValueError:
        cfg.button_count = defaults.button_count
    cfg.staff_keys = keys_value(saved, key=f"{prefix}/staffKeys") or {0}
    signs = list_value(saved, key=f"{prefix}/accidentals")
    cfg.accidentals = {
        sign for sign in settings.INTERVAL_ACCIDENTALS if str(sign) in signs
    } or defaults.accidentals
    names = text_value(
        saved,
        key=f"{prefix}/intervals",
        default=joined(defaults.intervals),
    )
    cfg.intervals = set(names.split(",")) & settings.WRITTEN_INTERVALS.keys()
    cfg.ranges = {}
    for clef, (minimum, maximum) in RANGE_LIMITS.items():
        bounds = list_value(saved, key=f"{prefix}/range/{clef}")
        if len(bounds) == 2 and all(value.isdecimal() for value in bounds):
            low, high = map(int, bounds)
            if minimum <= low <= high <= maximum:
                cfg.ranges[clef] = (low, high)


def _load_key_settings(
    cfg: settings.KeySignatureSettings,
    *,
    prefix: str,
) -> None:
    """
    Load the saved clefs, scales and key signatures of a key exercise
    into its settings.

    Anything in the saved data that is not valid is ignored, and a list
    with nothing valid in it leaves the setting as it was.

    Parameters
    ----------
    cfg : KeySignatureSettings
        The settings to fill.
    prefix : str
        What the exercise's saved settings are filed under, such as
        "keySignatures". Keyword-only.

    Examples
    --------
    >>> loaded = settings.KeySignatureSettings()
    >>> store().setValue(
    ...     "doctestKeys/keys", "-2,5,99"
    ... )
    >>> _load_key_settings(
    ...     loaded, prefix="doctestKeys"
    ... )
    >>> sorted(loaded.keys)
    [-2, 5]
    >>> store().remove("doctestKeys")
    """
    saved_settings = store()
    cfg.clefs = (
        choices_value(saved_settings, key=f"{prefix}/clefs", allowed=CLEFS)
        or cfg.clefs
    )
    cfg.modes = (
        choices_value(
            saved_settings,
            key=f"{prefix}/modes",
            allowed=settings.KEY_MODES,
            separator="|",
        )
        or cfg.modes
    )
    keys = list_value(saved_settings, key=f"{prefix}/keys")
    cfg.keys = keys_value(saved_settings, key=f"{prefix}/keys") or cfg.keys
    if isinstance(
        cfg,
        (
            settings.ScaleConstructionSettings,
            settings.ScaleIdentificationSettings,
        ),
    ):
        minor_key = f"{prefix}/minorKeys"
        if saved_settings.contains(minor_key):
            cfg.minor_keys = keys_value(saved_settings, key=minor_key)
            if (
                saved_settings.contains(f"{prefix}/keys")
                and not keys
                and cfg.minor_keys
            ):
                cfg.keys = set()
        else:
            cfg.minor_keys = None
    if isinstance(cfg, settings.ScaleConstructionSettings):
        cfg.steps = bool_value(
            saved_settings,
            key=f"{prefix}/steps",
            default=False,
        )
        cfg.octave = bool_value(
            saved_settings,
            key=f"{prefix}/octave",
            default=False,
        )
    if isinstance(
        cfg,
        (
            settings.ScaleConstructionSettings,
            settings.ScaleIdentificationSettings,
        ),
    ):
        if isinstance(cfg, settings.ScaleIdentificationSettings):
            question_type = text_value(
                saved_settings,
                key=f"{prefix}/questionType",
                default="combined",
            )
            cfg.question_type = (
                question_type
                if question_type in {"mode", "key"}
                else "combined"
            )
            cfg.button_mode = (
                "all"
                if text_value(
                    saved_settings,
                    key=f"{prefix}/buttonMode",
                    default="limited",
                )
                == "all"
                else "limited"
            )
            cfg.button_count = max(
                2,
                min(
                    10,
                    int_value(
                        saved_settings,
                        key=f"{prefix}/buttonCount",
                        default=6,
                    ),
                ),
            )
        motion = text_value(
            saved_settings,
            key=f"{prefix}/motion",
            default="ascending",
        )
        cfg.motion = (
            motion if motion in {"ascending", "descending"} else "ascending"
        )
        cfg.staff_keys = (
            keys_value(saved_settings, key=f"{prefix}/staffKeys")
            or cfg.staff_keys
        )


def save_key_settings(
    cfg: settings.KeySignatureSettings,
    *,
    prefix: str,
) -> None:
    """
    Save the settings of a key exercise: its clefs, scales and key
    signatures, and the options of the kind of exercise it is.

    Parameters
    ----------
    cfg : KeySignatureSettings
        The settings to save; the scale and Order of Keys exercises save
        their own options too.
    prefix : str
        What the exercise's saved settings are filed under, such as
        "keySignatures". Keyword-only.

    Examples
    --------
    >>> saved_ = settings.ScaleConstructionSettings(
    ...     modes={"Major (Ionian)", "Dorian"},
    ...     steps=True,
    ... )
    >>> save_key_settings(
    ...     saved_, prefix="doctestScales"
    ... )
    >>> loaded_ = (
    ...     settings.ScaleConstructionSettings()
    ... )
    >>> _load_key_settings(
    ...     loaded_, prefix="doctestScales"
    ... )
    >>> sorted(loaded_.modes), loaded_.steps
    (['Dorian', 'Major (Ionian)'], True)
    >>> store().remove("doctestScales")
    """
    saved_settings = store()
    saved_settings.setValue(f"{prefix}/clefs", joined(cfg.active_clefs()))
    saved_settings.setValue(
        f"{prefix}/modes",
        joined(cfg.active_modes(), separator="|"),
    )
    keys = cfg.active_keys()
    if (
        isinstance(
            cfg,
            (
                settings.ScaleConstructionSettings,
                settings.ScaleIdentificationSettings,
            ),
        )
        and cfg.minor_keys is not None
    ):
        keys = sorted(cfg.keys)
        saved_settings.setValue(
            f"{prefix}/minorKeys",
            joined(sorted(cfg.minor_keys)),
        )
    saved_settings.setValue(f"{prefix}/keys", joined(keys))
    if isinstance(cfg, settings.OrderOfKeysSettings):
        saved_settings.setValue(
            f"{prefix}/startingAccidentals",
            joined(sorted(cfg.starting_accidentals)),
        )
    if isinstance(cfg, settings.ScaleConstructionSettings):
        save_bool(saved_settings, key=f"{prefix}/steps", value=cfg.steps)
        save_bool(saved_settings, key=f"{prefix}/octave", value=cfg.octave)
    if isinstance(
        cfg,
        (
            settings.ScaleConstructionSettings,
            settings.ScaleIdentificationSettings,
        ),
    ):
        saved_settings.setValue(f"{prefix}/motion", cfg.motion)
        saved_settings.setValue(
            f"{prefix}/staffKeys",
            joined(cfg.active_staff_keys()),
        )
    if isinstance(cfg, settings.ScaleIdentificationSettings):
        saved_settings.setValue(f"{prefix}/questionType", cfg.question_type)
        saved_settings.setValue(f"{prefix}/buttonMode", cfg.button_mode)
        saved_settings.setValue(f"{prefix}/buttonCount", cfg.button_count)


def load_key_signatures() -> None:
    """
    Load the saved key signature identification settings into the shared
    settings object.

    Anything in the saved data that is not valid is ignored, and a list
    with nothing valid in it leaves the setting as it was.

    Examples
    --------
    >>> store().setValue(
    ...     "keySignatures/clefs", "alto"
    ... )
    >>> load_key_signatures()
    >>> settings.key_signatures.clefs
    {'alto'}
    >>> settings.key_signatures.clefs = {
    ...     "treble",
    ...     "bass",
    ... }
    >>> store().setValue(
    ...     "keySignatures/clefs", "treble,bass"
    ... )
    """
    _load_key_settings(settings.key_signatures, prefix="keySignatures")


def load_key_construction() -> None:
    """
    Load the saved key signature construction settings into the shared
    settings object.

    Anything in the saved data that is not valid is ignored, and a list
    with nothing valid in it leaves the setting as it was.

    Examples
    --------
    >>> store().setValue(
    ...     "keyConstruction/keys", "-3,4"
    ... )
    >>> load_key_construction()
    >>> settings.key_construction.active_keys()
    [-3, 4]
    >>> settings.key_construction.keys = set(
    ...     range(-7, 8)
    ... )
    >>> store().remove("keyConstruction")
    """
    _load_key_settings(settings.key_construction, prefix="keyConstruction")


def load_order_of_keys() -> None:
    """
    Restore the clefs, scales, and key signatures selected for Order of
    Keys.

    Examples
    --------
    >>> load_order_of_keys()
    """
    cfg = settings.order_of_keys
    _load_key_settings(cfg, prefix="orderOfKeys")
    saved = list_value(store(), key="orderOfKeys/startingAccidentals")
    cfg.starting_accidentals = {
        n for n in cfg.available_starts() if str(n) in saved
    } or {0}


def load_scale_identification() -> None:
    """
    Load the saved scale identification options independently of scale
    construction.

    Examples
    --------
    >>> load_scale_identification()
    >>> settings.scale_identification.active_staff_keys()
    [0]
    """
    _load_key_settings(
        settings.scale_identification,
        prefix="scaleIdentification",
    )


def load_scale_construction() -> None:
    """
    Load the saved scale construction settings into the shared settings
    object.

    Anything in the saved data that is not valid is ignored, and a list
    with nothing valid in it leaves the setting as it was.

    Examples
    --------
    >>> store().setValue(
    ...     "scaleConstruction/keys", "1,-1"
    ... )
    >>> store().setValue(
    ...     "scaleConstruction/steps", "true"
    ... )
    >>> store().setValue(
    ...     "scaleConstruction/octave", "true"
    ... )
    >>> load_scale_construction()
    >>> (
    ...     settings.scale_construction.active_keys(),
    ...     settings.scale_construction.steps,
    ...     settings.scale_construction.octave,
    ... )
    ([-1, 1], True, True)
    >>> (
    ...     settings.scale_construction.keys,
    ...     settings.scale_construction.steps,
    ... ) = set(range(-7, 8)), False
    >>> settings.scale_construction.octave = False
    >>> store().remove("scaleConstruction")
    """
    _load_key_settings(settings.scale_construction, prefix="scaleConstruction")


def saved_notation_terms() -> set[str]:
    """
    Read the last nonempty selection of notation terms.

    Returns
    -------
    set of str
        The saved terms that still exist, or all terms for a new
        profile.

    Examples
    --------
    Switching Select none off restores these checkboxes.
    """
    terms = settings.NOTATION_TERMS
    return choices_value(
        store(),
        key="notationIdentification/terms",
        allowed=terms,
    ) or set(terms)


def load_notation_terms() -> None:
    """
    Restore the question type and term selection, defaulting to Answer
    Button and all terms.

    Examples
    --------
    >>> load_notation_terms()
    >>> bool(settings.notation.terms)
    True
    """
    kind = text_value(
        store(),
        key="notationIdentification/questionType",
        default="button",
    )
    settings.notation.question_type = (
        kind if kind in settings.NOTATION_QUESTION_TYPES else "button"
    )
    none = bool_value(
        store(),
        key="notationIdentification/selectNone",
        default=False,
    )
    settings.notation.terms = set() if none else saved_notation_terms()


def load_clef_basics() -> None:
    """
    Load the saved clef basics settings into the shared settings object.

    Anything in the saved data that is not a clef or a kind of question
    is ignored, and a list with no clef in it leaves the
    setting as it was.

    Examples
    --------
    >>> store().setValue(
    ...     "clefBasics/clefs", "alto,subbass,flute"
    ... )
    >>> store().setValue(
    ...     "clefBasics/type", "identification"
    ... )
    >>> load_clef_basics()
    >>> (
    ...     settings.clef_basics.active_clefs(),
    ...     settings.clef_basics.question_type,
    ... )
    (['alto', 'subbass'], 'identification')
    >>> (
    ...     settings.clef_basics.clefs,
    ...     settings.clef_basics.question_type,
    ... ) = (
    ...     {"treble", "bass"},
    ...     "construction",
    ... )
    >>> store().remove("clefBasics")
    """
    clefs = choices_value(
        store(),
        key="clefBasics/clefs",
        allowed=settings.CLEF_BASICS_CLEFS,
    )
    settings.clef_basics.clefs = clefs or settings.clef_basics.clefs
    kind = text_value(store(), key="clefBasics/type", default="")
    if kind in settings.CLEF_QUESTION_TYPES:
        settings.clef_basics.question_type = kind


def save_clef_basics(cfg: settings.ClefBasicsSettings) -> None:
    """
    Save clef basics settings, the form `load_clef_basics` reads.

    Parameters
    ----------
    cfg : ClefBasicsSettings
        The settings to save.

    Examples
    --------
    >>> save_clef_basics(
    ...     settings.ClefBasicsSettings(
    ...         clefs={"french", "treble"},
    ...         question_type="identification",
    ...     )
    ... )
    >>> (
    ...     str(store().value("clefBasics/clefs")),
    ...     str(store().value("clefBasics/type")),
    ... )
    ('treble,french', 'identification')
    >>> store().remove("clefBasics")
    """
    saved = store()
    saved.setValue("clefBasics/clefs", joined(cfg.active_clefs()))
    saved.setValue("clefBasics/type", cfg.question_type)


def load_circle() -> None:
    """
    Load the saved circle of fifths settings into the shared settings
    object.

    Anything in the saved data that is not valid is ignored, and a list
    with nothing valid in it leaves the setting as it was. A
    saved color scheme that no longer exists (it was deleted, or comes
    from a newer Alto) leaves the default.

    Examples
    --------
    >>> store().setValue(
    ...     "circle/questions", "numeral,nonsense"
    ... )
    >>> store().setValue(
    ...     "circle/scheme", "midnight"
    ... )
    >>> load_circle()
    >>> (
    ...     settings.circle.questions,
    ...     settings.circle.scheme,
    ... )
    ({'numeral'}, 'midnight')
    >>> settings.circle.questions = set(
    ...     settings.CIRCLE_QUESTIONS
    ... )
    >>> settings.circle.scheme = DEFAULT_SCHEME
    >>> store().remove("circle")
    """
    saved_settings = store()
    questions = choices_value(
        saved_settings,
        key="circle/questions",
        allowed=settings.CIRCLE_QUESTIONS,
    )
    settings.circle.questions = questions or settings.circle.questions
    settings.circle.customs = load_customs(
        text_value(saved_settings, key="circle/customSchemes", default="[]"),
    )
    wanted = text_value(
        saved_settings,
        key="circle/scheme",
        default=DEFAULT_SCHEME,
    )
    if (
        wanted == "colour-blind"
    ):  # Migrate the preset key saved by earlier versions.
        wanted = "color-blind"
    elif wanted == "chequer":
        wanted = "checker"
    known = set(PRESETS) | {record["id"] for record in settings.circle.customs}
    settings.circle.scheme = wanted if wanted in known else DEFAULT_SCHEME


def save_circle(cfg: settings.CircleSettings) -> None:
    """
    Save the circle of fifths settings.

    Parameters
    ----------
    cfg : CircleSettings
        The settings to save.

    Examples
    --------
    >>> save_circle(
    ...     settings.CircleSettings(scheme="ink")
    ... )
    >>> store().value("circle/scheme")
    'ink'
    >>> store().remove("circle")
    """
    saved_settings = store()
    saved_settings.setValue("circle/questions", joined(cfg.active_questions()))
    saved_settings.setValue("circle/scheme", cfg.scheme)
    saved_settings.setValue("circle/customSchemes", dump_customs(cfg.customs))


def load_pack_options() -> None:
    """
    Restore the options learners chose for each plugin exercise that
    offers settings.

    Anything in the saved data that is not valid is ignored.

    Examples
    --------
    >>> load_pack_options()
    """
    saved = store()
    for cls in REGISTRY:
        if not issubclass(cls, PackExercise) or not cls.controls:
            continue
        chosen = cls.options()
        prefix = f"packExercises/{cls.__name__}"
        picked = text_value(saved, key=f"{prefix}/sound", default="")
        # An old "true" or "false", or a sound that is no longer
        # installed, means the plugin's own.
        chosen.sound = picked if picked in INSTRUMENT_BY_KEY else None
        chosen.accidentals = bool_value(
            saved,
            key=f"{prefix}/accidentals",
            default=False,
        )
        chosen.require_octave = bool_value(
            saved,
            key=f"{prefix}/octave",
            default=False,
        )
        if cls.range_clef:
            low, high = cls.span
            try:
                first, last = (
                    int(part)
                    for part in text_value(
                        saved,
                        key=f"{prefix}/range",
                        default="",
                    ).split("-")
                )
            except ValueError:
                first, last = low, high
            chosen.ranges[cls.range_clef] = (
                (first, last) if low <= first <= last <= high else (low, high)
            )
        if cls.spec.get("type") == "keyboard-intervals":
            chosen.keys = None
            try:
                first, last = (
                    int(part)
                    for part in text_value(
                        saved,
                        key=f"{prefix}/keys",
                        default="",
                    ).split("-")
                )
            except ValueError:
                pass
            else:
                if cls.key_span[0] <= first < last <= cls.key_span[1]:
                    chosen.keys = (first, last)
            chosen.intervals = (
                frozenset(
                    choices_value(
                        saved,
                        key=f"{prefix}/intervals",
                        allowed=cls.interval_names,
                    ),
                )
                or None
            )
            boards = choices_value(
                saved,
                key=f"{prefix}/manuals",
                allowed=cls.manual_names,
                separator="|",
            )
            chosen.manuals = frozenset(boards) or None


def save_pack_options(name: str) -> None:
    """
    Save the options chosen for one plugin exercise.

    Parameters
    ----------
    name : str
        The exercise's class name.

    Examples
    --------
    >>> save_pack_options("pack.nothing.here")
    """
    chosen = settings.pack_exercises.get(name)
    if chosen is None:
        return
    saved = store()
    prefix = f"packExercises/{name}"
    saved.setValue(f"{prefix}/sound", chosen.sound or "")
    save_bool(saved, key=f"{prefix}/accidentals", value=chosen.accidentals)
    save_bool(saved, key=f"{prefix}/octave", value=chosen.require_octave)
    for low, high in chosen.ranges.values():
        saved.setValue(f"{prefix}/range", f"{low}-{high}")
    saved.setValue(
        f"{prefix}/keys",
        "" if chosen.keys is None else f"{chosen.keys[0]}-{chosen.keys[1]}",
    )
    saved.setValue(
        f"{prefix}/intervals",
        "" if chosen.intervals is None else joined(sorted(chosen.intervals)),
    )
    saved.setValue(
        f"{prefix}/manuals",
        ""
        if chosen.manuals is None
        else joined(sorted(chosen.manuals), separator="|"),
    )


def load_choice_buttons() -> None:
    """
    Restore the independent button preferences for each multiple-choice
    exercise.

    Examples
    --------
    >>> load_choice_buttons()
    >>> from alto.exercises.library import NoteNames
    >>> NoteNames.button_settings().button_mode in {
    ...     "all",
    ...     "limited",
    ... }
    True
    """
    saved = store()
    for cls in REGISTRY:
        if not issubclass(cls, ChoiceExercise):
            continue
        cfg = cls.button_settings()
        prefix = f"answerButtons/{cls.__name__}"
        mode = "limited" if cls.default_limit else "all"
        value = text_value(saved, key=f"{prefix}/mode", default=mode)
        cfg.button_mode = value if value in ("all", "limited") else mode
        try:
            cfg.button_count = max(
                2,
                min(
                    10,
                    int_value(
                        saved,
                        key=f"{prefix}/count",
                        default=cls.default_limit or 6,
                    ),
                ),
            )
        except ValueError:
            cfg.button_count = cls.default_limit or 6


def load_exercise_settings() -> None:
    """
    Load the saved exercise options before creating a practice or export
    settings panel.

    Examples
    --------
    >>> load_exercise_settings()
    """
    load_choice_buttons()
    saved = store()
    component = text_value(
        saved,
        key="beatIdentification/rhythmComponent",
        default="Time signature",
    )
    settings.beat_rhythm_component = (
        component
        if component in settings.BEAT_RHYTHM_COMPONENTS
        else "Time signature"
    )
    for prefix, default in settings.DEFAULT_BEAT_NOTE_TYPES.items():
        settings.beat_tuplets[prefix] = bool_value(
            saved,
            key=f"{prefix}/tuplets",
            default=False,
        )
        settings.beat_note_types[prefix] = (
            choices_value(
                saved,
                key=f"{prefix}/noteTypes",
                allowed=settings.BEAT_NOTE_TYPES,
            )
            or default.copy()
        )
    shared_signs = (
        choices_value(
            saved,
            key="rythmicEquations/operators",
            allowed=settings.RHYTHM_OPERATORS,
        )
        or settings.DEFAULT_RHYTHM_OPERATORS
    )
    for side, default in (("left", 1), ("right", 0)):
        signs = choices_value(
            saved,
            key=f"rythmicEquations/{side}Signs",
            allowed=settings.RHYTHM_OPERATORS,
        )
        setattr(settings, f"rhythm_{side}_signs", signs or shared_signs.copy())
        try:
            count = int_value(
                saved,
                key=f"rythmicEquations/{side}Operators",
                default=default,
            )
        except (ValueError, OverflowError):
            count = default
        setattr(
            settings,
            f"rhythm_{side}_operators",
            max(0, min(settings.MAX_RHYTHM_OPERATORS, count)),
        )
    settings.rhythm_answer_types = choices_value(
        saved,
        key="rythmicEquations/answerTypes",
        allowed=settings.RHYTHM_ANSWER_TYPES,
    ) or {"symbol"}
    settings.rhythm_parentheses = bool_value(
        saved,
        key="rythmicEquations/parentheses",
        default=False,
    )
    settings.rhythm_ties = bool_value(
        saved,
        key="rythmicEquations/ties",
        default=False,
    )
    settings.rhythm_beams = bool_value(
        saved,
        key="rythmicEquations/beams",
        default=False,
    )
    settings.rhythm_symbols = choices_value(
        saved,
        key="rythmicEquations/symbols",
        allowed=settings.RHYTHM_DURATIONS,
    ) or (settings.DEFAULT_RHYTHM_SYMBOLS.copy())
    load_note_names()
    load_intervals()
    load_intervals(
        settings.interval_construction,
        prefix="intervalConstruction",
    )
    load_keyboard()
    load_keyboard_intervals()
    load_construction()
    load_arpeggio()
    load_key_signatures()
    load_key_construction()
    load_order_of_keys()
    load_circle()
    load_clef_basics()
    load_notation_terms()
    load_pack_options()
    load_scale_construction()
    load_scale_identification()
