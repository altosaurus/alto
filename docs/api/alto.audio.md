---
title: alto.audio
parent: api
package: alto
permalink: /api/alto.audio/
---
{% raw %}
Note playback: recorded instrument samples (University of Iowa), with pitch-shifting for missing notes.

`Sounds` plays notes through Qt's `QSoundEffect`, one effect per note, created the first time it is needed. A note with
no recording is made by shifting the nearest recording (or, for the piano outside its sampled range, by synthesis).
Instrument previews render the phrase as one cached clip, with fixed spacing between its notes.
The module-level `sounds` is the one the interface uses.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [inst.label for inst in INSTRUMENTS][:2]
['Piano', 'Flute']
>>> Sounds().instrument
'piano'
```

## synth_piano

```python
def synth_piano(
    midi: int,
    *,
    duration: float = 1.6,
) -> np.ndarray
```

Synthesize a piano note, for notes outside the recorded range.

An additive model: stretched partials, a decay for each partial, a detuned string pair, and a hammer thump.

**Parameters**

- `midi` (*int*): The MIDI note number. The same number always gives the same sound.
- `duration` (*float, default 1.6*): How long the note lasts, in seconds. Keyword-only.

**Returns**

- *numpy.ndarray*: Mono samples at `SAMPLE_RATE`, scaled so the loudest is 0.8.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> samples = synth_piano(60, duration=0.1)
>>> len(samples)
4410
>>> round(float(np.max(np.abs(samples))), 1)
0.8
```

## Instrument

```python
Instrument(
    key: str,
    *,
    label: str,
    folder: str,
    gain: float = 1.0,
    sustained: bool = False,
    family: str = '',
    variant: str = '',
    damped: bool = False,
    samples: tuple[tuple[int, Path], ...] = (),
    pack_name: str = '',
    kind: str = '',
)
```

An instrument that notes can be played on, and where its recordings are.

**Attributes**

- `key` (*str*): A short identifier used in settings and file names.
- `label` (*str*): The name shown in the interface. Keyword-only.
- `folder` (*str*): Under `assets/`: "piano" or "samples/<key>". File names are MIDI note numbers. Keyword-only.
- `gain` (*float, default 1.0*): The level relative to the piano. Keyword-only.
- `sustained` (*bool, default False*): True for bowed and blown instruments, whose notes end when the next one begins; struck and plucked ones ring on. Keyword-only.
- `damped` (*bool, default False*): True for an instrument whose notes are stopped by a damper when the key is let go, played without the pedal: the piano. Each note ends as the next one begins, as it does when the fingers move from key to key, instead of ringing on over the following notes as if the pedal were down. Keyword-only.
- `family` (*str, default ""*): Instruments that are ways of playing the same instrument share a family (the viola: arco and pizzicato). Keyword-only.
- `variant` (*str, default ""*): Which way of playing it, within the family. Keyword-only.
- `samples` (*tuple of (int, Path), default ()*): Pairs of MIDI pitches and local recording paths supplied by an installed instrument pack. Keyword-only.
- `pack_name` (*str, default ""*): Display name of the plugin that supplies the recordings. Keyword-only.
- `kind` (*str, default ""*): What sort of instrument it is, such as "harpsichord", so that other sounds of the same sort can be offered together. Built-in instruments use their family or name. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Instrument("flute", label="Flute", folder="samples/flute", sustained=True).gain
1.0
>>> INSTRUMENT_BY_KEY["piano"].damped, INSTRUMENT_BY_KEY["marimba"].damped
(True, False)
```

### Instrument.kind_name

```python
@property
def kind_name() -> str
```

Name what sort of instrument this is, in lowercase.

**Returns**

- *str*: The plugin's ``kind``, or the built-in family, or the instrument's label.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> INSTRUMENT_BY_KEY["viola_bowed"].kind_name, INSTRUMENT_BY_KEY["flute"].kind_name
('viola', 'flute')
```

### Instrument.picker_group

```python
@property
def picker_group() -> str
```

Identify the instrument's entry in the sound picker.

**Returns**

- *str*: The pack-qualified key for a plugin sound, or the built-in family or label.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> INSTRUMENT_BY_KEY["viola_bowed"].picker_group
'Viola'
```

### Instrument.playback_volume

```python
def playback_volume(level: float = 1.0) -> float
```

Return the output volume for a note or clip played on this instrument.

**Parameters**

- `level` (*float, default 1.0*): Relative amplitude. Simultaneous notes can request a lower level for each voice.

**Returns**

- *float*: Linear Qt volume between zero and one, including the instrument's gain.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> INSTRUMENT_BY_KEY["flute"].playback_volume()
0.85
```

## instrument_groups

```python
def instrument_groups() -> list[tuple[str, list[Instrument]]]
```

Return the instruments as they are listed for choosing.

Ways of playing one instrument share a single entry.

**Returns**

- *list of tuple of (str, list of Instrument)*: Each entry's picker group and its instruments, in the order listed.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [name for name, _ in instrument_groups()]
['Piano', 'Flute', 'French Horn', 'Viola', 'Marimba', 'Vibraphone']
>>> [inst_.variant for inst_ in dict(instrument_groups())["Viola"]]
['Arco', 'Pizzicato']
```

## read_wav

```python
def read_wav(path: Path) -> tuple[np.ndarray, int]
```

Read a mono 16-bit WAV file.

**Parameters**

- `path` (*Path*): The file.

**Returns**

- *tuple of (numpy.ndarray, int)*: The samples as floats from -1 to 1, and the sample rate in hertz.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> import tempfile
>>> path_ = Path(tempfile.mkdtemp()) / "silence.wav"
>>> _ = path_.write_bytes(to_wav_bytes(np.zeros(10)))
>>> samples, rate = read_wav(path_)
>>> len(samples), rate
(10, 44100)
```

## shift_pitch

```python
def shift_pitch(
    samples: np.ndarray,
    *,
    semitones: float,
) -> np.ndarray
```

Change the pitch of samples by resampling them.

It also changes the length, which is fine for a few semitones.

**Parameters**

- `samples` (*numpy.ndarray*): Mono samples.
- `semitones` (*float*): How far to shift; positive is higher. Keyword-only.

**Returns**

- *numpy.ndarray*: The resampled samples, shorter when shifted up and longer when shifted down.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(shift_pitch(np.zeros(100), semitones=12))  # an octave up: half as long
50
```

## to_wav_bytes

```python
def to_wav_bytes(
    samples: np.ndarray,
    *,
    rate: int = SAMPLE_RATE,
) -> bytes
```

Encode samples as a mono 16-bit WAV file in memory.

**Parameters**

- `samples` (*numpy.ndarray*): Mono samples from -1 to 1.
- `rate` (*int, default SAMPLE_RATE*): The sample rate in hertz. Keyword-only.

**Returns**

- *bytes*: The contents of a WAV file.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> to_wav_bytes(np.zeros(10))[:4]
b'RIFF'
```

## write_file_atomically

```python
def write_file_atomically(
    path: Path,
    *,
    data: bytes,
) -> None
```

Write a file so that nothing ever reads it half written, even another copy of Alto writing the same file.

The bytes go to a file of the writer's own first and then replace the file in one step.

**Parameters**

- `path` (*Path*): The file.
- `data` (*bytes*): What it holds. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> folder = Path(tempfile.mkdtemp())
>>> write_file_atomically(folder / "note.wav", data=b"RIFF")
>>> (folder / "note.wav").read_bytes(), [p.name for p in folder.iterdir()]
(b'RIFF', ['note.wav'])
```

## Sounds

```python
Sounds()
```

A lazy cache of notes played through `QSoundEffect`, in the chosen instrument.

**Attributes**

- `enabled` (*bool*): False while the app is muted.
- `instrument` (*str*): The key of the instrument in use, a key of `INSTRUMENT_BY_KEY`.
- `FADE_MS` (*int*): How quickly a sustained note dies away when the next one begins, in milliseconds.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> s = Sounds()
>>> s.enabled, s.instrument
(True, 'piano')
>>> s.enabled = False  # muted: nothing below makes a sound
>>> s.play_midi(60)
```

**Constructor**

Create a player with the piano chosen and sound on.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Sounds().instrument
'piano'
```

### Sounds.recordings

```python
def recordings(inst: Instrument) -> dict[int, Path]
```

Return the notes an instrument has a recording for on disk.

**Parameters**

- `inst` (*Instrument*): The instrument.

**Returns**

- *dict of int to Path*: MIDI note number to its sample file.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> 60 in Sounds().recordings(INSTRUMENT_BY_KEY["piano"])
True
```

### Sounds.note_duration_ms

```python
def note_duration_ms(
    midi: int,
    *,
    instrument: str | None = None,
) -> int
```

Read the playback length of a note for synchronized instrument animations.

**Parameters**

- `midi` (*int*): Sounding MIDI pitch.
- `instrument` (*str or None*): Pack sound key, or None for the learner's selected sound.

**Returns**

- *int*: Duration in milliseconds, using the usual feedback interval if the WAV is unavailable.

**Examples**

```text
A one-second sample has the same 1000 ms feedback interval when muted.
```

### Sounds.play_midi

```python
def play_midi(
    midi: int,
    *,
    volume: float = 1.0,
    instrument: str | None = None,
    force: bool = False,
    release_previous: bool = True,
) -> None
```

Play a note in the chosen instrument (or another one).

A sustained instrument (bowed or blown) ends the notes still sounding first, as a player would, and so does a damped
one (the piano, played without the pedal), unless `release_previous` is False, which is for the notes of a chord
that start together. Nothing plays while muted unless
`force` is set. A failure to play is reported but never raised, so audio can never break an exercise.

**Parameters**

- `midi` (*int*): The MIDI note number.
- `volume` (*float, default 1.0*): The level from 0 to 1, before the instrument's own gain. Keyword-only.
- `instrument` (*str or None, default None*): The key of the instrument to use instead of the chosen one. Keyword-only.
- `force` (*bool, default False*): Play even while muted, for previews. Keyword-only.
- `release_previous` (*bool, default True*): End the sustained or damped notes still ringing first. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> s = Sounds()
>>> s.enabled = False
>>> s.play_midi(60)  # muted: returns at once
>>> Sounds().play_midi(60)  # doctest: +SKIP
```

### Sounds.stop_all

```python
def stop_all() -> None
```

Silence every note at once, and cancel any fade-outs underway.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Sounds().stop_all()
```

### Sounds.preview

```python
def preview(
    key: str,
    *,
    midis: Iterable[int],
    step_ms: int = 300,
) -> None
```

Play notes one after another in an instrument, even while muted, to hear what it sounds like.

The phrase is rendered as one audio clip, so first-use loading cannot change the spacing between notes.
Starting a preview silences the one before it.

**Parameters**

- `key` (*str*): The key of the instrument.
- `midis` (*iterable of int*): The MIDI notes to play, in order. Keyword-only.
- `step_ms` (*int, default 300*): The time between notes, in milliseconds. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sounds.preview("flute", midis=[60, 64, 67])  # doctest: +SKIP
```

### Sounds.play_notes

```python
def play_notes(
    columns: Iterable[Sequence[Note]],
    *,
    gap_ms: int = DEFAULT_NOTE_GAP_MS,
    warmup: bool = False,
    force: bool = False,
    instrument: str | None = None,
    on_step: Callable[[int | None], object] | None = None,
) -> None
```

Play staff columns left to right, evenly spaced.

The notes within a column sound together, a little quieter the more there are.

**Parameters**

- `instrument` (*str or None*): Instrument key for this playback, or None for the learner’s selection.
- `force` (*bool*): Play even when exercise audio is muted.
- `warmup` (*bool*): Silently initialize audio streams before starting playback.
- `columns` (*iterable of sequence of Note*): The columns of notes, as drawn on a staff.
- `gap_ms` (*int, default 450*): The time between columns, in milliseconds. Keyword-only.
- `on_step` (*callable or None, default None*): Called with the index of each column as it starts, and with None when the last has had its time. It is called while muted too, so a display can follow the music with the sound off. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> s = Sounds()
>>> s.enabled = False
>>> s.play_notes([[Note.parse("C4"), Note.parse("E4"), Note.parse("G4")]])  # muted: nothing sounds
```

### Sounds.stop_sample

```python
def stop_sample(on_step: Callable[[int | None], object]) -> None
```

Stop a displayed sample if it still owns playback.

**Parameters**

- `on_step` (*callable*): The display callback originally passed to play_sample.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Sounds().stop_sample(print)
```

### Sounds.play_sample

```python
def play_sample(
    columns: Sequence[Sequence[Note]],
    *,
    gap_ms: int,
    on_step: Callable[[int | None], object],
    force: bool = False,
    instrument: str | None = None,
    warmup: bool = False,
) -> None
```

Play a displayed sample and report the sounding column until it ends or is interrupted.

**Parameters**

- `columns` (*sequence of sequence of Note*): Written notes in playback order, with simultaneous notes grouped together.
- `gap_ms` (*int*): Time between column onsets in milliseconds.
- `on_step` (*callable*): Receives each sounding column index and None to clear the display.
- `instrument` (*str or None*): Instrument key for this playback, or None for the learner’s selection.
- `force` (*bool*): Audition the sample even when exercise audio is muted.
- `warmup` (*bool*): Prepare the audio streams before the first note.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> player = Sounds()
>>> player.enabled = False
>>> player.play_sample([[Note.parse("C4")]], gap_ms=300, on_step=print)
0
>>> player.stop_sample(print)
None
```

### Sounds.play_correct

```python
def play_correct(streak: int) -> None
```

Play a note that climbs the C major scale (C5 to C6) as the streak grows, then wraps.

**Parameters**

- `streak` (*int*): How many right answers in a row; 1 plays C5.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> s = Sounds()
>>> s.enabled = False
>>> s.play_correct(3)  # muted: nothing sounds
```
{% endraw %}
