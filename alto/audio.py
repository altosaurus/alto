"""
Note playback: recorded instrument samples (University of Iowa), with
pitch-shifting for missing notes.

`Sounds` plays notes through Qt's `QSoundEffect`, one effect per note,
created the first time it is needed. A note with
no recording is made by shifting the nearest recording (or, for the
piano outside its sampled range, by synthesis).
Instrument previews render the phrase as one cached clip, with fixed
spacing between its notes.
The module-level `sounds` is the one the interface uses.

Examples
--------
>>> [inst.label for inst in INSTRUMENTS][:2]
['Piano', 'Flute']
>>> Sounds().instrument
'piano'
"""

from __future__ import annotations

import array
import hashlib
import io
import math
import operator
import os
import random
import tempfile
import time
import wave
from collections.abc import (
    Callable,
    Iterable,
    Sequence,
)
from dataclasses import (
    KW_ONLY,
    dataclass,
)
from pathlib import Path

from PySide6.QtCore import (
    QPropertyAnimation,
    QTimer,
    QUrl,
)
from PySide6.QtMultimedia import (
    QSoundEffect,
)

from alto.theory.pitch import Note

SAMPLE_RATE = 44100
DEFAULT_NOTE_GAP_MS = 450
MELODIC_INTERVAL_GAP_MS = 500


def synth_piano(
    midi: int,
    *,
    duration: float = 1.6,
) -> list[float]:
    """
    Synthesize a piano note, for notes outside the recorded range.

    An additive model: stretched partials, a decay for each partial, a
    detuned string pair, and a hammer thump. Each partial
    is a decaying sine made by rotating a complex number one sample at a
    time, which needs no sine or exponential per sample.

    Parameters
    ----------
    midi : int
        The MIDI note number. The same number always gives the same
        sound.
    duration : float, default 1.6
        How long the note lasts, in seconds. Keyword-only.

    Returns
    -------
    list of float
        Mono samples at `SAMPLE_RATE`, scaled so the loudest is 0.8.

    Examples
    --------
    >>> samples = synth_piano(60, duration=0.1)
    >>> len(samples)
    4410
    >>> round(max(abs(s) for s in samples), 1)
    0.8
    """
    rng = random.Random(midi)  # deterministic per note
    f0 = 440.0 * 2 ** ((midi - 69) / 12)
    count = int(SAMPLE_RATE * duration)
    inharm = (
        0.00008 * (1 + max(0, 60 - midi) / 24) ** 2
        if midi < 60
        else 0.0002 * (midi - 55) / 10
    )
    out = [0.0] * count
    for n in range(1, 17):
        f = n * f0 * math.sqrt(1 + inharm * n * n)
        if f > 12000:
            break
        amp = 1.0 / n**1.15
        if n % 7 == 0:  # strike-point comb: hammer hits ~1/7 along the string
            amp *= 0.3
        decay = (
            2.2 + 1.1 * n + (midi - 60) * 0.03
        )  # higher partials/notes die faster
        # two slightly detuned strings give the characteristic shimmer;
        # one hammer strikes both, so they start in phase
        phase = rng.uniform(0, 2 * math.pi)
        for detune in (-0.0008, 0.0008):
            step = 2 * math.pi * f * (1 + detune) / SAMPLE_RATE
            turn = complex(math.cos(step), math.sin(step)) * math.exp(
                -decay / SAMPLE_RATE,
            )
            z = amp * 0.5 * complex(math.cos(phase), math.sin(phase))
            for k in range(count):
                out[k] += z.imag
                z *= turn
    # soft attack, then a quick dip into the long sustain, and a fade
    # out to avoid a click
    for k in range(count):
        t = k / SAMPLE_RATE
        out[k] *= (
            (1 - math.exp(-t / 0.002))
            * (0.65 + 0.35 * math.exp(-t / 0.25))
            * min(1.0, (duration - t) / 0.05)
        )
    # hammer thump: a very short noise burst, smoothed by a 24-sample
    # moving average
    thump_count = min(count, int(0.02 * SAMPLE_RATE))
    noise = [rng.gauss(0.0, 1.0) for _ in range(thump_count)]
    totals = [0.0]
    for value in noise:
        totals.append(totals[-1] + value)
    level = 0.25 * (1.0 / (1 + (midi - 40) / 30))
    for k in range(thump_count):
        smooth = (
            totals[min(thump_count, k + 12)] - totals[max(0, k - 12)]
        ) / 24
        t = k / SAMPLE_RATE
        out[k] += (
            level
            * smooth
            * math.exp(-k / (0.004 * SAMPLE_RATE))
            * min(1.0, (duration - t) / 0.05)
        )
    peak = max((abs(value) for value in out), default=0.0) or 1.0
    return [value / peak * 0.8 for value in out]


@dataclass(frozen=True)
class Instrument:
    """
    An instrument that notes can be played on, and where its recordings
    are.

    Attributes
    ----------
    key : str
        A short identifier used in settings and file names.
    label : str
        The name shown in the interface. Keyword-only.
    folder : str
        Under `assets/`: "piano" or "samples/<key>". File names are MIDI
        note numbers. Keyword-only.
    gain : float, default 1.0
        The level relative to the piano. Keyword-only.
    sustained : bool, default False
        True for bowed and blown instruments, whose notes end when the
        next one begins; struck and plucked ones ring on.
        Keyword-only.
    damped : bool, default False
        True for an instrument whose notes are stopped by a damper when
        the key is let go, played without the pedal: the
        piano. Each note ends as the next one begins, as it does when
        the fingers move from key to key, instead of ringing
        on over the following notes as if the pedal were down.
        Keyword-only.
    family : str, default ""
        Instruments that are ways of playing the same instrument share a
        family (the viola: arco and pizzicato).
        Keyword-only.
    variant : str, default ""
        Which way of playing it, within the family. Keyword-only.
    samples : tuple of (int, Path), default ()
        Pairs of MIDI pitches and local recording paths supplied by an
        installed instrument pack. Keyword-only.
    pack_name : str, default ""
        Display name of the plugin that supplies the recordings.
        Keyword-only.
    kind : str, default ""
        What sort of instrument it is, such as "harpsichord", so that
        other sounds of the same sort can be offered together.
        Built-in instruments use their family or name. Keyword-only.

    Examples
    --------
    >>> Instrument(
    ...     "flute",
    ...     label="Flute",
    ...     folder="samples/flute",
    ...     sustained=True,
    ... ).gain
    1.0
    >>> (
    ...     INSTRUMENT_BY_KEY["piano"].damped,
    ...     INSTRUMENT_BY_KEY["marimba"].damped,
    ... )
    (True, False)
    """

    key: str
    _: KW_ONLY
    label: str
    # under assets/: "piano" or "samples/<key>"; file names are MIDI
    # note numbers
    folder: str
    gain: float = 1.0  # level relative to the piano
    # bowed and blown notes end when the next one begins; struck and
    # plucked ones ring on
    sustained: bool = False
    # instruments that are ways of playing the same instrument share a
    # family (the viola: arco, pizzicato)
    family: str = ""
    variant: str = ""  # which way of playing it, within the family
    # a damper stops each note as the next begins, as on a piano played
    # without the pedal
    damped: bool = False
    samples: tuple[
        tuple[int, Path],
        ...,
    ] = ()  # Explicit pitch-to-file map supplied by a pack.
    pack_name: str = ""
    # what sort of instrument it is, so sounds of the same sort can be
    # offered together
    kind: str = ""

    @property
    def kind_name(self) -> str:
        """
        Name what sort of instrument this is, in lowercase.

        Returns
        -------
        str
            The plugin's ``kind``, or the built-in family, or the
            instrument's label.

        Examples
        --------
        >>> (
        ...     INSTRUMENT_BY_KEY[
        ...         "viola_bowed"
        ...     ].kind_name,
        ...     INSTRUMENT_BY_KEY["flute"].kind_name,
        ... )
        ('viola', 'flute')
        """
        return (self.kind or self.family or self.label).lower()

    @property
    def picker_group(self) -> str:
        """
        Identify the instrument's entry in the sound picker.

        Returns
        -------
        str
            The pack-qualified key for a plugin sound, or the built-in
            family or label.

        Examples
        --------
        >>> INSTRUMENT_BY_KEY[
        ...     "viola_bowed"
        ... ].picker_group
        'Viola'
        """
        return self.key if self.pack_name else self.family or self.label

    def playback_volume(self, level: float = 1.0) -> float:
        """
        Return the output volume for a note or clip played on this
        instrument.

        Parameters
        ----------
        level : float, default 1.0
            Relative amplitude. Simultaneous notes can request a lower
            level for each voice.

        Returns
        -------
        float
            Linear Qt volume between zero and one, including the
            instrument's gain.

        Examples
        --------
        >>> INSTRUMENT_BY_KEY["flute"].playback_volume()
        0.85
        """
        return max(0.0, min(1.0, level * self.gain))


INSTRUMENTS = (
    Instrument(
        "piano",
        label="Piano",
        folder="piano",
        damped=True,
    ),
    Instrument(
        "flute",
        label="Flute",
        folder="samples/flute",
        gain=0.85,
        sustained=True,
    ),
    Instrument(
        "horn",
        label="French Horn",
        folder="samples/horn",
        gain=0.85,
        sustained=True,
    ),
    Instrument(
        "viola_bowed",
        label="Viola (Arco)",
        folder="samples/viola_bowed",
        gain=0.85,
        sustained=True,
        family="Viola",
        variant="Arco",
    ),
    Instrument(
        "viola_plucked",
        label="Viola (Pizzicato)",
        folder="samples/viola_plucked",
        gain=0.85,
        family="Viola",
        variant="Pizzicato",
    ),
    Instrument(
        "marimba",
        label="Marimba",
        folder="samples/marimba",
        gain=0.85,
    ),
    Instrument(
        "vibraphone",
        label="Vibraphone",
        folder="samples/vibraphone",
        gain=0.85,
    ),
)
INSTRUMENT_BY_KEY = {i.key: i for i in INSTRUMENTS}


def instrument_groups() -> list[tuple[str, list[Instrument]]]:
    """
    Return the instruments as they are listed for choosing.

    Ways of playing one instrument share a single entry.

    Returns
    -------
    list of tuple of (str, list of Instrument)
        Each entry's picker group and its instruments, in the order
        listed.

    Examples
    --------
    >>> [name for name, _ in instrument_groups()]
    ['Piano', 'Flute', 'French Horn', 'Viola', 'Marimba', 'Vibraphone']
    >>> [
    ...     inst_.variant
    ...     for inst_ in dict(instrument_groups())[
    ...         "Viola"
    ...     ]
    ... ]
    ['Arco', 'Pizzicato']
    """
    groups: dict[str, list[Instrument]] = {}
    for inst in INSTRUMENT_BY_KEY.values():
        groups.setdefault(inst.picker_group, []).append(inst)
    return list(groups.items())


def _pcm(data: bytes) -> array.array[int]:
    """
    Read 16-bit samples as Python's `wave` module hands them over: in
    the computer's own byte order.

    WAV files store samples little-endian, and `wave` swaps the bytes
    itself on a big-endian computer, both when it reads frames
    and when it writes them, so the samples here never need swapping.

    Parameters
    ----------
    data : bytes
        The samples, two bytes each, as `wave.Wave_read.readframes`
        returns them.

    Returns
    -------
    array.array of int
        The samples, from -32768 to 32767.

    Examples
    --------
    >>> list(
    ...     _pcm(
    ...         array.array("h", [1, -1]).tobytes()
    ...     )
    ... )
    [1, -1]
    """
    samples = array.array("h")
    samples.frombytes(data)
    return samples


def _frame_rate(path: Path) -> int:
    """
    Read the sample rate of a WAV file without reading its samples.

    Parameters
    ----------
    path : Path
        The file.

    Returns
    -------
    int
        Samples per second.

    Examples
    --------
    >>> import tempfile
    >>> path_ = (
    ...     Path(tempfile.mkdtemp()) / "quiet.wav"
    ... )
    >>> _ = path_.write_bytes(
    ...     to_wav_bytes([0.0], rate=22050)
    ... )
    >>> _frame_rate(path_)
    22050
    """
    with wave.open(str(path)) as w:
        return w.getframerate()


def read_wav(path: Path) -> tuple[list[float], int]:
    """
    Read a mono 16-bit WAV file.

    Parameters
    ----------
    path : Path
        The file.

    Returns
    -------
    tuple of (list of float, int)
        The samples as floats from -1 to 1, and the sample rate in
        hertz.

    Examples
    --------
    >>> import tempfile
    >>> path_ = (
    ...     Path(tempfile.mkdtemp()) / "silence.wav"
    ... )
    >>> _ = path_.write_bytes(
    ...     to_wav_bytes([0.0] * 10)
    ... )
    >>> samples, rate = read_wav(path_)
    >>> len(samples), rate
    (10, 44100)
    """
    with wave.open(str(path)) as w:
        frames, rate = w.readframes(w.getnframes()), w.getframerate()
    return [value / 32768 for value in _pcm(frames)], rate


def _interpolate(
    samples: Sequence[float],
    *,
    step: float,
    count: int,
) -> list[float]:
    """
    Read samples at evenly spaced fractional positions, drawing straight
    lines between neighbors.

    Positions past the last sample give the last sample, as
    `numpy.interp` does.

    Parameters
    ----------
    samples : sequence of float
        Mono samples.
    step : float
        The distance between positions, in samples. Keyword-only.
    count : int
        How many positions, starting at 0. Keyword-only.

    Returns
    -------
    list of float
        The values at the positions.

    Examples
    --------
    >>> _interpolate(
    ...     [0.0, 1.0, 0.0], step=0.5, count=6
    ... )
    [0.0, 0.5, 1.0, 0.5, 0.0, 0.0]
    """
    last = len(samples) - 1
    inside = min(
        count,
        max(0, math.ceil(last / step)),
    )  # the positions that fall before the last sample
    out = [
        (a := samples[i := int(x := k * step)])
        + (samples[i + 1] - a) * (x - i)
        for k in range(inside)
    ]
    out.extend([samples[last]] * (count - inside))
    return out


def shift_pitch(
    samples: Sequence[float],
    *,
    semitones: float,
) -> list[float]:
    """
    Change the pitch of samples by resampling them.

    It also changes the length, which is fine for a few semitones.

    Parameters
    ----------
    samples : sequence of float
        Mono samples.
    semitones : float
        How far to shift; positive is higher. Keyword-only.

    Returns
    -------
    list of float
        The resampled samples, shorter when shifted up and longer when
        shifted down.

    Examples
    --------
    >>> len(
    ...     shift_pitch([0.0] * 100, semitones=12)
    ... )  # an octave up: half as long
    50
    """
    ratio = 2 ** (semitones / 12)
    count = max(0, math.ceil((len(samples) - 1) / ratio))
    return _interpolate(samples, step=ratio, count=count)


def to_wav_bytes(
    samples: Iterable[float],
    *,
    rate: int = SAMPLE_RATE,
) -> bytes:
    """
    Encode samples as a mono 16-bit WAV file in memory.

    Parameters
    ----------
    samples : iterable of float
        Mono samples from -1 to 1; anything beyond is clipped.
    rate : int, default SAMPLE_RATE
        The sample rate in hertz. Keyword-only.

    Returns
    -------
    bytes
        The contents of a WAV file.

    Examples
    --------
    >>> to_wav_bytes([0.0] * 10)[:4]
    b'RIFF'
    >>> import tempfile
    >>> clipped = (
    ...     Path(tempfile.mkdtemp()) / "clipped.wav"
    ... )
    >>> _ = clipped.write_bytes(
    ...     to_wav_bytes([2.0, -3.0, 0.5])
    ... )
    >>> [
    ...     round(value, 3)
    ...     for value in read_wav(clipped)[0]
    ... ]  # beyond full scale is clipped
    [1.0, -1.0, 0.5]
    """
    values = list(samples)
    if values and (min(values) < -1.0 or max(values) > 1.0):
        values = [
            -1.0 if value < -1.0 else min(value, 1.0) for value in values
        ]
    pcm = array.array(
        "h",
        [int(value * 32767) for value in values],
    )  # wave writes them little-endian, swapping if need be
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


def write_file_atomically(
    path: Path,
    *,
    data: bytes,
) -> None:
    """
    Write a file so that nothing ever reads it half written, even
    another copy of Alto writing the same file.

    The bytes go to a file of the writer's own first and then replace
    the file in one step.

    Parameters
    ----------
    path : Path
        The file.
    data : bytes
        What it holds. Keyword-only.

    Examples
    --------
    >>> folder = Path(tempfile.mkdtemp())
    >>> write_file_atomically(
    ...     folder / "note.wav", data=b"RIFF"
    ... )
    >>> (
    ...     (folder / "note.wav").read_bytes(),
    ...     [p.name for p in folder.iterdir()],
    ... )
    (b'RIFF', ['note.wav'])
    """
    partial = path.with_name(f".{path.name}.{os.getpid()}.part")
    partial.write_bytes(data)
    partial.replace(path)


ASSETS = Path(__file__).parent / "assets"
ASSET_DIR = ASSETS / "piano"


class Sounds:
    """
    A lazy cache of notes played through `QSoundEffect`, in the chosen
    instrument.

    Attributes
    ----------
    enabled : bool
        False while the app is muted.
    instrument : str
        The key of the instrument in use, a key of `INSTRUMENT_BY_KEY`.
    FADE_MS : int
        How quickly a sustained note dies away when the next one begins,
        in milliseconds.

    Examples
    --------
    >>> s = Sounds()
    >>> s.enabled, s.instrument
    (True, 'piano')
    >>> s.enabled = False  # muted: nothing below makes a sound
    >>> s.play_midi(60)
    """

    def __init__(self) -> None:
        """
        Create a player with the piano chosen and sound on.

        Examples
        --------
        >>> Sounds().instrument
        'piano'
        """
        self.enabled = True
        self.instrument = "piano"  # key into INSTRUMENT_BY_KEY
        self._effects = {}
        self._preview_effects: dict[
            tuple[str, tuple[int, ...], int],
            QSoundEffect,
        ] = {}
        # sustained and damped notes that may still be sounding, to
        # release when the next begins
        self._sounding: list = []
        self._fades: dict = {}  # running fade-outs, by effect
        # which sequence of notes is current, so that an older one stops
        # when a new one starts
        self._sequence_run = 0
        self._sample_step: Callable[[int | None], object] | None = None
        self._sample_files: dict[str, dict[int, Path]] = {}
        self._dir = Path(tempfile.gettempdir()) / "alto_sounds"

    def _samples(self, inst: Instrument) -> dict[int, Path]:
        """
        Find the recorded notes an instrument has on disk.

        Parameters
        ----------
        inst : Instrument
            The instrument.

        Returns
        -------
        dict of int to Path
            MIDI note number to its sample file. The folder is read once
            and the result is remembered.

        Examples
        --------
        >>> piano = Sounds()._samples(
        ...     INSTRUMENT_BY_KEY["piano"]
        ... )
        >>> 60 in piano and piano[60].suffix
        '.wav'
        """
        if inst.samples:
            return dict(inst.samples)
        found = self._sample_files.get(inst.key)
        if found is None:
            folder = ASSETS / inst.folder
            found = {
                int(p.stem): p
                for p in folder.glob("*.wav")
                if p.stem.isdigit()
            }
            self._sample_files[inst.key] = found
        return found

    def recordings(self, inst: Instrument) -> dict[int, Path]:
        """
        Return the notes an instrument has a recording for on disk.

        Parameters
        ----------
        inst : Instrument
            The instrument.

        Returns
        -------
        dict of int to Path
            MIDI note number to its sample file.

        Examples
        --------
        >>> 60 in Sounds().recordings(
        ...     INSTRUMENT_BY_KEY["piano"]
        ... )
        True
        """
        return self._samples(inst)

    def _note_file(
        self,
        inst: Instrument,
        *,
        midi: int,
    ) -> Path:
        """
        Return a WAV file for a note.

        The recording if there is one, otherwise the nearest recording
        pitch-shifted (or a synthesized piano note outside the
        piano's sampled range). Made files are kept in a temporary
        folder.

        Parameters
        ----------
        inst : Instrument
            The instrument.
        midi : int
            The MIDI note number. Keyword-only.

        Returns
        -------
        Path
            The file to play.

        Examples
        --------
        >>> Sounds()._note_file(
        ...     INSTRUMENT_BY_KEY["piano"], midi=60
        ... ).suffix
        '.wav'
        """
        samples = self._samples(inst)
        if midi in samples:
            return samples[midi]
        self._dir.mkdir(exist_ok=True)
        source: Path | None = None
        semitones = 0
        if samples:
            nearest = min(samples, key=lambda m: abs(m - midi))
            if inst.key != "piano" or abs(nearest - midi) <= 2:
                source, semitones = samples[nearest], midi - nearest
        if source is not None:
            stat = source.stat()
            # A pack update can replace a recording under the same name,
            # so the made file is named after the recording's state.
            identity: tuple[object, ...] = (
                "shift",
                str(source),
                stat.st_size,
                stat.st_mtime_ns,
                semitones,
            )
        else:  # the piano outside its sampled range
            identity = ("synth-2", midi)
        path = self._dir / (
            f"{inst.key}"
            "_"
            f"{midi}"
            "_"
            f"{hashlib.sha256(repr(identity).encode()).hexdigest()[:16]}"
            ".wav"
        )
        if path.exists():
            return path
        if source is not None:
            audio, rate = read_wav(source)
            write_file_atomically(
                path,
                data=to_wav_bytes(
                    shift_pitch(audio, semitones=semitones),
                    rate=rate,
                ),
            )
        else:
            write_file_atomically(path, data=to_wav_bytes(synth_piano(midi)))
        return path

    def unrecorded(self, instrument: str | None = None) -> list[int]:
        """
        List the notes within an instrument's recorded range that have
        no recording of their own, nearest middle C first.

        Each is made the first time it plays, by shifting the nearest
        recording. `alto.ui.warmup` makes them ahead of time with
        `prepare`, so that even a first play is quick.

        Parameters
        ----------
        instrument : str or None, default None
            The instrument's key, or None for the current one.

        Returns
        -------
        list of int
            MIDI note numbers.

        Examples
        --------
        >>> notes = Sounds().unrecorded(
        ...     "piano"
        ... )  # the piano is recorded every third semitone
        >>> notes[:2], 60 in notes, len(notes)
        ([61, 59], False, 58)
        """
        recorded = self.recordings(
            INSTRUMENT_BY_KEY.get(
                instrument or self.instrument,
                INSTRUMENTS[0],
            ),
        )
        if not recorded:
            return []
        missing = [
            midi
            for midi in range(min(recorded), max(recorded) + 1)
            if midi not in recorded
        ]
        return sorted(missing, key=lambda midi: (abs(midi - 60), -midi))

    def prepare(self, midi: int, *, instrument: str | None = None) -> None:
        """
        Make the file a note plays, if it has no recording and was not
        made before, so that its first play is quick.

        Parameters
        ----------
        midi : int
            The MIDI note number.
        instrument : str or None, default None
            The instrument's key, or None for the current one.
            Keyword-only.

        Examples
        --------
        >>> Sounds().prepare(61, instrument="piano")
        """
        self._note_file(
            INSTRUMENT_BY_KEY.get(
                instrument or self.instrument,
                INSTRUMENTS[0],
            ),
            midi=midi,
        )

    def _at_sample_rate(self, path: Path) -> Path:
        """
        Return a recording at `SAMPLE_RATE`, converting it once and
        keeping the result for later previews.

        Parameters
        ----------
        path : Path
            A mono 16-bit WAV file.

        Returns
        -------
        Path
            The file itself if it is already at `SAMPLE_RATE`, otherwise
            a converted copy in the temporary folder.

        Examples
        --------
        >>> piano = Sounds()._note_file(
        ...     INSTRUMENT_BY_KEY["piano"], midi=60
        ... )
        >>> Sounds()._at_sample_rate(piano) == piano
        True
        """
        with wave.open(str(path)) as w:
            rate, total = w.getframerate(), w.getnframes()
        if rate == SAMPLE_RATE:
            return path
        stat = path.stat()
        identity = (
            "rate",
            str(path),
            stat.st_size,
            stat.st_mtime_ns,
            SAMPLE_RATE,
        )
        converted = self._dir / (
            "rate_"
            f"{hashlib.sha256(repr(identity).encode()).hexdigest()[:16]}"
            ".wav"
        )
        if not converted.exists():
            samples, _rate = read_wav(path)
            step = (
                rate / SAMPLE_RATE
                # read at 0, step, 2 * step, ... to the end, drawing
                # straight lines between samples
            )
            self._dir.mkdir(parents=True, exist_ok=True)
            write_file_atomically(
                converted,
                data=to_wav_bytes(
                    _interpolate(
                        samples,
                        step=step,
                        count=math.ceil(total / step),
                    ),
                ),
            )
        return converted

    def note_duration_ms(
        self,
        midi: int,
        *,
        instrument: str | None = None,
    ) -> int:
        """
        Read the playback length of a note for synchronized instrument
        animations.

        Parameters
        ----------
        midi : int
            Sounding MIDI pitch.
        instrument : str or None
            Pack sound key, or None for the learner's selected sound.

        Returns
        -------
        int
            Duration in milliseconds, using the usual feedback interval
            if the WAV is unavailable.

        Examples
        --------
        A one-second sample has the same 1000 ms feedback interval when
        muted.
        """
        inst = INSTRUMENT_BY_KEY.get(
            instrument or self.instrument,
            INSTRUMENTS[0],
        )
        try:
            with wave.open(
                str(self._note_file(inst, midi=midi)),
                "rb",
            ) as recording:
                return max(
                    1,
                    round(
                        1000
                        * recording.getnframes()
                        / recording.getframerate(),
                    ),
                )
        except (OSError, EOFError, wave.Error, ValueError, ZeroDivisionError):
            return DEFAULT_NOTE_GAP_MS

    FADE_MS = (
        70  # how quickly a sustained note dies away when the next one begins
    )

    def _effect(
        self,
        inst: Instrument,
        *,
        midi: int,
    ) -> QSoundEffect:
        """
        Return the sound effect for a note, creating it the first time
        it is needed.

        Parameters
        ----------
        inst : Instrument
            The instrument.
        midi : int
            The MIDI note number. Keyword-only.

        Returns
        -------
        QSoundEffect
            The loaded effect, which can be played again and again.

        Examples
        --------
        >>> effect = Sounds()._effect(
        ...     INSTRUMENT_BY_KEY["piano"], midi=60
        ... )  # doctest: +SKIP
        """
        key = (inst.key, midi)
        fx = self._effects.get(key)
        if fx is None:
            fx = QSoundEffect()
            fx.setSource(
                QUrl.fromLocalFile(str(self._note_file(inst, midi=midi))),
            )
            self._effects[key] = fx
        return fx

    def _release(self, fx: QSoundEffect) -> None:
        """
        Let a sustained note die away quickly instead of cutting it off.

        Parameters
        ----------
        fx : QSoundEffect
            The effect that is sounding.

        Examples
        --------
        >>> from PySide6.QtMultimedia import (
        ...     QSoundEffect,
        ... )
        >>> effect = QSoundEffect()  # doctest: +SKIP
        >>> # noinspection PyProtectedMember
        >>> sounds._release(effect)  # doctest: +SKIP
        """
        fade = QPropertyAnimation(fx, b"volume")
        fade.setDuration(self.FADE_MS)
        fade.setStartValue(fx.volume())
        fade.setEndValue(0.0)
        fade.finished.connect(fx.stop)
        self._fades[id(fx)] = fade
        fade.start()

    def _release_sounding(self) -> None:
        """
        End the sustained and damped notes that are still ringing.

        Examples
        --------
        >>> # nothing is ringing: nothing happens
        >>> Sounds()._release_sounding()
        """
        sounding, self._sounding = self._sounding, []
        for fx in sounding:
            self._release(fx)

    def play_midi(
        self,
        midi: int,
        *,
        volume: float = 1.0,
        instrument: str | None = None,
        force: bool = False,
        release_previous: bool = True,
    ) -> None:
        """
        Play a note in the chosen instrument (or another one).

        A sustained instrument (bowed or blown) ends the notes still
        sounding first, as a player would, and so does a damped
        one (the piano, played without the pedal), unless
        `release_previous` is False, which is for the notes of a chord
        that start together. Nothing plays while muted unless
        `force` is set. A failure to play is reported but never raised,
        so audio can never break an exercise.

        Parameters
        ----------
        midi : int
            The MIDI note number.
        volume : float, default 1.0
            The level from 0 to 1, before the instrument's own gain.
            Keyword-only.
        instrument : str or None, default None
            The key of the instrument to use instead of the chosen one.
            Keyword-only.
        force : bool, default False
            Play even while muted, for previews. Keyword-only.
        release_previous : bool, default True
            End the sustained or damped notes still ringing first.
            Keyword-only.

        Examples
        --------
        >>> s = Sounds()
        >>> s.enabled = False
        >>> s.play_midi(60)  # muted: returns at once
        >>> Sounds().play_midi(60)  # doctest: +SKIP
        """
        if not (self.enabled or force):
            return
        try:
            inst = INSTRUMENT_BY_KEY.get(
                instrument or self.instrument,
                INSTRUMENTS[0],
            )
            if (inst.sustained or inst.damped) and release_previous:
                self._release_sounding()
            fx = self._effect(inst, midi=midi)
            fade = self._fades.pop(
                id(fx),
                None,
            )  # this note may have been released a moment ago
            if fade is not None:
                fade.stop()
            fx.setVolume(inst.playback_volume(volume))
            fx.play()
            if inst.sustained or inst.damped:
                self._sounding.append(fx)
        except Exception as exc:  # audio must never break an exercise
            print(f"audio unavailable: {exc}")

    def stop_all(self) -> None:
        """
        Silence every note at once, and cancel any fade-outs underway.

        Examples
        --------
        >>> Sounds().stop_all()
        """
        self._interrupt_sequence()
        for fade in self._fades.values():
            fade.stop()
        self._fades.clear()
        self._sounding = []
        for fx in self._effects.values():
            if fx.isPlaying():
                fx.setVolume(0.0)
                fx.stop()
        for fx in self._preview_effects.values():
            fx.stop()

    def _preview_file(
        self,
        inst: Instrument,
        *,
        midis: tuple[int, ...],
        step_ms: int,
        tail_ms: int = 0,
    ) -> Path:
        """
        Render a preview as one WAV file with note onsets a fixed number
        of samples apart.

        The notes are mixed as 16-bit integers at the rate their
        recordings share, so no sample is converted or resampled:
        Python's own C code does the adding, and only each note's short
        fade-out is worked out sample by sample. Recordings at
        different rates are first converted to `SAMPLE_RATE`, once. The
        clip is kept, named after everything it is made from,
        including the state of a pack's recordings, so playing the same
        phrase again costs nothing.

        Parameters
        ----------
        inst : Instrument
            The instrument whose recordings to use.
        midis : tuple of int
            The notes in playback order. Keyword-only.
        step_ms : int
            The interval between note onsets in milliseconds.
            Keyword-only.
        tail_ms : int, default 0
            Extra sustain for the last note, in milliseconds.
            Keyword-only.

        Returns
        -------
        pathlib.Path
            A cached mono WAV file containing the phrase.

        Examples
        --------
        >>> Sounds()._preview_file(
        ...     INSTRUMENT_BY_KEY["piano"],
        ...     midis=(74, 75, 72, 71),
        ...     step_ms=300,
        ... ).suffix
        '.wav'
        """
        # A pack update can replace the recordings under the same
        # instrument key, so their state is part of the clip's name.
        recordings = tuple(
            (str(source), (stat := source.stat()).st_size, stat.st_mtime_ns)
            for _midi, source in inst.samples
        )
        identity = repr(
            (
                "integer-mix",
                inst.key,
                midis,
                step_ms,
                self.FADE_MS,
                tail_ms,
                recordings,
            ),
        ).encode()
        path = (
            self._dir / f"preview_{hashlib.sha256(identity).hexdigest()}.wav"
        )
        if path.exists():
            return path
        files = [self._note_file(inst, midi=midi) for midi in midis]
        rates = {_frame_rate(file) for file in files}
        if len(rates) > 1:
            files = [self._at_sample_rate(file) for file in files]
        rate = rates.pop() if len(rates) == 1 else SAMPLE_RATE
        gap = max(1, round(rate * step_ms / 1000))
        fade = max(1, round(rate * self.FADE_MS / 1000))
        extra = round(rate * tail_ms / 1000)
        notes = []
        for index, file in enumerate(files):
            hold = gap + (extra if index == len(files) - 1 else 0)
            with wave.open(str(file)) as w:
                pcm = _pcm(w.readframes(min(w.getnframes(), hold + fade)))
            tail = max(0, len(pcm) - hold)
            for k in range(
                tail,
            ):  # fade from full to silent over the tail, ending at 0
                pcm[hold + k] = int(
                    pcm[hold + k]
                    * (1.0 - k / (tail - 1) if tail > 1 else 1.0),
                )
            notes.append(pcm)
        length = max(
            (i * gap + len(pcm) for i, pcm in enumerate(notes)),
            default=0,
        )
        # Short recordings still need the full final beat for displays
        # that follow the output clock.
        phrase = [0] * max(length, len(files) * gap + extra)
        for i, pcm in enumerate(notes):
            start, end = i * gap, i * gap + len(pcm)
            phrase[start:end] = map(operator.add, phrase[start:end], pcm)
        if phrase and (min(phrase) < -32768 or max(phrase) > 32767):
            phrase = [
                -32768 if value < -32768 else min(value, 32767)
                for value in phrase
            ]
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(array.array("h", phrase).tobytes())
        self._dir.mkdir(parents=True, exist_ok=True)
        write_file_atomically(path, data=buf.getvalue())
        return path

    def preview(
        self,
        key: str,
        *,
        midis: Iterable[int],
        step_ms: int = 300,
    ) -> None:
        """
        Play notes one after another in an instrument, even while muted,
        to hear what it sounds like.

        The phrase is rendered as one audio clip, so first-use loading
        cannot change the spacing between notes.
        Starting a preview silences the one before it.

        Parameters
        ----------
        key : str
            The key of the instrument.
        midis : iterable of int
            The MIDI notes to play, in order. Keyword-only.
        step_ms : int, default 300
            The time between notes, in milliseconds. Keyword-only.

        Examples
        --------
        >>> sounds.preview(
        ...     "flute", midis=[60, 64, 67]
        ... )  # doctest: +SKIP
        """
        self.stop_all()
        notes = tuple(midis)
        if not notes:
            return
        try:
            inst = INSTRUMENT_BY_KEY[key]
            cache_key = (key, notes, step_ms)
            effect = self._preview_effects.get(cache_key)
            if effect is None:
                path = self._preview_file(inst, midis=notes, step_ms=step_ms)
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(str(path)))
                self._preview_effects[cache_key] = effect
            effect.setVolume(inst.playback_volume())
            effect.play()
        except (
            Exception
        ) as exc:  # audio must never break the instrument picker
            print(f"audio unavailable: {exc}")

    def _play_column(
        self,
        midis: Iterable[int],
        *,
        volume: float,
        key: str | None = None,
        force: bool = False,
    ) -> None:
        """
        Start the notes of one column together, first ending any
        sustained or damped notes still ringing.

        Parameters
        ----------
        midis : iterable of int
            The MIDI notes to sound together.
        volume : float
            The level for each, from 0 to 1. Keyword-only.
        key : str or None, default None
            The instrument's key; the chosen instrument if None.
            Keyword-only.
        force : bool, default False
            Play even while muted. Keyword-only.

        Examples
        --------
        >>> s = Sounds()
        >>> s.enabled = False
        >>> s._play_column(
        ...     [60, 64, 67], volume=1.0
        ... )  # muted: nothing sounds
        """
        inst = INSTRUMENT_BY_KEY.get(key or self.instrument, INSTRUMENTS[0])
        if (inst.sustained or inst.damped) and (self.enabled or force):
            self._release_sounding()
        for midi in midis:
            self.play_midi(
                midi,
                volume=volume,
                instrument=key,
                force=force,
                release_previous=False,
            )

    def _play_sequence(
        self,
        key: str,
        *,
        steps: list[tuple[list[int], float]],
        gap_ms: int,
        force: bool = False,
        warmup: bool = False,
        on_step: Callable[[int | None], object] | None = None,
    ) -> None:
        """
        Play steps one after another, a fixed time apart.

        The rhythm has to be even, so the notes are loaded first (making
        a sound effect the first time it is needed takes long
        enough to hold up the next note), and each step is scheduled
        only once the one before it has been started. A pause
        while the sound system starts therefore delays the rest instead
        of making them sound together. Starting a sequence
        cancels the steps still waiting from an earlier one.

        Parameters
        ----------
        warmup : bool
            Silently initialize audio streams before starting playback.
        key : str
            The instrument's key.
        steps : list of tuple of (list of int, float)
            For each step, the MIDI notes of its column and their
            volume. Keyword-only.
        gap_ms : int
            The time from the start of one step to the start of the
            next, in milliseconds. Keyword-only.
        force : bool, default False
            Play even while muted. Keyword-only.
        on_step : callable or None, default None
            Called with the index of each step as it starts, and with
            None one gap after the last one, so that the caller can
            show which note is sounding. While muted the steps are still
            walked through, on the same timing, so the display
            does not depend on the sound. Not called for a sequence that
            a newer one has replaced. Keyword-only.

        Examples
        --------
        >>> s = Sounds()
        >>> s.enabled = False
        >>> s._play_sequence(
        ...     "piano", steps=[([60], 1.0)], gap_ms=300
        ... )  # muted: only cancels any earlier sequence
        >>> s._sequence_run
        1

        """
        self._interrupt_sequence()
        run = self._sequence_run
        for effect in self._preview_effects.values():
            effect.stop()
        if not steps:
            return
        if not (self.enabled or force):
            if on_step is not None:
                self._walk(
                    len(steps),
                    gap_ms=gap_ms,
                    run=run,
                    on_step=on_step,
                )
            return
        try:
            inst = INSTRUMENT_BY_KEY[key]
            effects = [
                self._effect(inst, midi=m) for midis, _ in steps for m in midis
            ]
        except Exception as exc:  # audio must never break an exercise
            print(f"audio unavailable: {exc}")
            if on_step is not None:
                self._walk(len(steps), gap_ms=gap_ms, run=run, on_step=on_step)
            return
        deadline = time.monotonic() + 1.0
        primed = not warmup

        def loading() -> bool:
            """
            Report whether any of the sequence's sound effects is still
            loading.

            Returns
            -------
            bool
                True while at least one effect has not finished loading.

            Examples
            --------
            >>> loading()  # doctest: +SKIP
            False
            """
            # noinspection PyNoneFunctionAssignment
            return any(
                getattr(fx, "status", lambda: None)()
                == QSoundEffect.Status.Loading
                for fx in effects
            )

        def step(i: int) -> None:
            """
            Play one step of the sequence and schedule the next.

            Parameters
            ----------
            i : int
                The index of the step. Nothing happens if a newer
                sequence has started since this one was scheduled.

            Examples
            --------
            >>> step(0)  # doctest: +SKIP
            """
            if run != self._sequence_run:
                return
            midis, volume = steps[i]
            self._play_column(
                midis,
                volume=volume,
                key=key,
                force=force,
            )
            if on_step is not None:
                on_step(i)
            if (
                i + 1 < len(steps)
                # the next one is due a full gap after this one has
                # started,
                # however long that took
            ):
                QTimer.singleShot(gap_ms, lambda: step(i + 1))
            elif on_step is not None:
                finish = on_step
                QTimer.singleShot(
                    gap_ms,
                    lambda: run == self._sequence_run and finish(None),
                )  # the last note has had its time

        def wait() -> None:
            """
            Wait for the effects to load, for at most a second, then
            start the first step.

            Examples
            --------
            >>> wait()  # doctest: +SKIP
            """
            nonlocal primed
            if run != self._sequence_run:
                return
            if loading() and time.monotonic() < deadline:
                QTimer.singleShot(10, wait)
            elif not primed:
                # Loading the sample does not open its audio stream.
                # Start each stream silently first,
                # so backend initialization cannot delay the first
                # audible notes independently.
                primed = True
                for effect in effects:
                    effect.setVolume(0.0)
                    effect.play()
                QTimer.singleShot(150, wait)
            else:
                if warmup:
                    for effect in effects:
                        effect.stop()
                step(0)

        wait()

    def _walk(
        self,
        count: int,
        *,
        gap_ms: int,
        run: int,
        on_step: Callable[[int | None], object],
    ) -> None:
        """
        Go through the steps of a sequence without a sound, on the same
        timing, telling the caller each one.

        Parameters
        ----------
        count : int
            How many steps there are.
        gap_ms : int
            The time from the start of one step to the start of the
            next, in milliseconds. Keyword-only.
        run : int
            Which sequence this is; the walk stops if a newer one has
            started. Keyword-only.
        on_step : callable
            Called with each step's index, and with None one gap after
            the last. Keyword-only.

        Examples
        --------
        >>> s = Sounds()
        >>> seen = []
        >>> s._walk(
        ...     1,
        ...     gap_ms=10,
        ...     run=s._sequence_run,
        ...     on_step=seen.append,
        ... )
        >>> seen
        [0]
        """
        started = time.monotonic()

        def step(i: int) -> None:
            """
            Report one step and schedule the next.

            Parameters
            ----------
            i : int
                The index of the step; `count` means the end.

            Examples
            --------
            >>> step(0)  # doctest: +SKIP
            """
            if run != self._sequence_run:
                return
            on_step(i if i < count else None)
            if i < count:
                delay = max(
                    1,
                    round(
                        (started + (i + 1) * gap_ms / 1000 - time.monotonic())
                        * 1000,
                    ),
                )
                QTimer.singleShot(delay, lambda: step(i + 1))

        step(0)

    def play_notes(
        self,
        columns: Iterable[Sequence[Note]],
        *,
        gap_ms: int = DEFAULT_NOTE_GAP_MS,
        warmup: bool = False,
        force: bool = False,
        instrument: str | None = None,
        on_step: Callable[[int | None], object] | None = None,
    ) -> None:
        """
        Play staff columns left to right, evenly spaced.

        The notes within a column sound together, a little quieter the
        more there are.

        Parameters
        ----------
        instrument : str or None
            Instrument key for this playback, or None for the learner’s
            selection.
        force : bool
            Play even when exercise audio is muted.
        warmup : bool
            Silently initialize audio streams before starting playback.
        columns : iterable of sequence of Note
            The columns of notes, as drawn on a staff.
        gap_ms : int, default 450
            The time between columns, in milliseconds. Keyword-only.
        on_step : callable or None, default None
            Called with the index of each column as it starts, and with
            None when the last has had its time. It is called
            while muted too, so a display can follow the music with the
            sound off. Keyword-only.

        Examples
        --------
        >>> s = Sounds()
        >>> s.enabled = False
        >>> s.play_notes(
        ...     [
        ...         [
        ...             Note.parse("C4"),
        ...             Note.parse("E4"),
        ...             Note.parse("G4"),
        ...         ]
        ...     ]
        ... )  # muted: nothing sounds

        """
        self._play_sequence(
            instrument or self.instrument,
            steps=[
                (
                    [n.midi for n in col],
                    min(1.0, 1.4 / max(1, len(col)) ** 0.5),
                )
                for col in columns
            ],
            gap_ms=gap_ms,
            warmup=warmup,
            force=force,
            on_step=on_step,
        )

    def _interrupt_sequence(self) -> None:
        """
        Invalidate scheduled steps and clear the highlighted note in an
        interrupted sample.

        Examples
        --------
        >>> player = Sounds()
        >>> player._interrupt_sequence()
        >>> player._sequence_run
        1
        """
        self._sequence_run += 1
        previous, self._sample_step = self._sample_step, None
        if previous is not None:
            previous(None)

    def stop_sample(self, on_step: Callable[[int | None], object]) -> None:
        """
        Stop a displayed sample if it still owns playback.

        Parameters
        ----------
        on_step : callable
            The display callback originally passed to play_sample.

        Examples
        --------
        >>> Sounds().stop_sample(print)
        """
        if self._sample_step == on_step:
            self.stop_all()

    def play_sample(
        self,
        columns: Sequence[Sequence[Note]],
        *,
        gap_ms: int,
        on_step: Callable[[int | None], object],
        force: bool = False,
        instrument: str | None = None,
        warmup: bool = False,
    ) -> None:
        """
        Play a displayed sample and report the sounding column until it
        ends or is interrupted.

        Parameters
        ----------
        columns : sequence of sequence of Note
            Written notes in playback order, with simultaneous notes
            grouped together.
        gap_ms : int
            Time between column onsets in milliseconds.
        on_step : callable
            Receives each sounding column index and None to clear the
            display.
        instrument : str or None
            Instrument key for this playback, or None for the learner’s
            selection.
        force : bool
            Audition the sample even when exercise audio is muted.
        warmup : bool
            Prepare the audio streams before the first note.

        Examples
        --------
        >>> player = Sounds()
        >>> player.enabled = False
        >>> player.play_sample(
        ...     [[Note.parse("C4")]],
        ...     gap_ms=300,
        ...     on_step=print,
        ... )
        0
        >>> player.stop_sample(print)
        None
        """
        if not columns:
            return

        def show(index: int | None) -> None:
            """
            Update the display and release it after its final note.

            Parameters
            ----------
            index : int or None
                Column that started, or None after the last column.

            Examples
            --------
            >>> show(None)  # doctest: +SKIP
            """
            if index is None:
                self._sample_step = None
            on_step(index)

        self.stop_all()
        self.play_notes(
            columns,
            gap_ms=gap_ms,
            on_step=show,
            force=force,
            warmup=warmup,
            instrument=instrument,
        )
        self._sample_step = on_step

    def play_correct(self, streak: int) -> None:
        """
        Play a note that climbs the C major scale (C5 to C6) as the
        streak grows, then wraps.

        Parameters
        ----------
        streak : int
            How many right answers in a row; 1 plays C5.

        Examples
        --------
        >>> s = Sounds()
        >>> s.enabled = False
        >>> s.play_correct(3)  # muted: nothing sounds
        """
        scale = (
            72,
            74,
            76,
            77,
            79,
            81,
            83,
            84,
        )
        self.play_midi(scale[(max(streak, 1) - 1) % len(scale)])


sounds = Sounds()
