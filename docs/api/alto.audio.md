---
title: alto.audio
parent: api
package: alto
permalink: /api/alto.audio/
---
{% raw %}
Note playback: recorded instrument samples (University of Iowa), with
pitch-shifting for missing notes.

`Sounds` plays notes through Qt's `QSoundEffect`, one effect per note,
created the first time it is needed. A note with
no recording is made by shifting the nearest recording (or, for the
piano outside its sampled range, by synthesis).
Instrument previews render the phrase as one cached clip to preserve
its rhythm from the first playback.
The module-level `sounds` is the one the interface uses.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [inst.label for inst in INSTRUMENTS][:2]
['Piano', 'Flute']
>>> Sounds().instrument
'piano'
```

## synth_piano

<div class="api-signature" markdown="1">

```python
def synth_piano(
    midi: int,
    *,
    duration: float = 1.6,
) -> list[float]
```

{% endraw %}{% include api-source.html name="synth_piano" line=65 %}{% raw %}

</div>

Synthesize a piano note, for notes outside the recorded range.

An additive model: stretched partials, a decay for each partial, a
detuned string pair, and a hammer thump. Each partial
is a decaying sine made by rotating a complex number one sample at a
time, which needs no sine or exponential per sample.

**Parameters**

- `midi` (*int*): The MIDI note number. The same number always gives the same sound.
- `duration` (*float, default 1.6*): How long the note lasts, in seconds. Keyword-only.

**Returns**

- *list of float*: Mono samples at `SAMPLE_RATE`, scaled so the loudest is 0.8.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> samples = synth_piano(60, duration=0.1)
>>> len(samples)
4410
>>> round(max(abs(s) for s in samples), 1)
0.8
```

## Instrument

<div class="api-signature" markdown="1">

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

{% endraw %}{% include api-source.html name="Instrument" line=163 %}{% raw %}

</div>

An instrument that notes can be played on, and where its recordings
are.

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
```

### Instrument.kind_name

<div class="api-signature" markdown="1">

```python
@property
def kind_name() -> str
```

{% endraw %}{% include api-source.html name="Instrument.kind_name" line=250 %}{% raw %}

</div>

Name what sort of instrument this is, in lowercase.

**Returns**

- *str*: The plugin's ``kind``, or the built-in family, or the instrument's label.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     INSTRUMENT_BY_KEY[
...         "viola_bowed"
...     ].kind_name,
...     INSTRUMENT_BY_KEY["flute"].kind_name,
... )
('viola', 'flute')
```

### Instrument.picker_group

<div class="api-signature" markdown="1">

```python
@property
def picker_group() -> str
```

{% endraw %}{% include api-source.html name="Instrument.picker_group" line=273 %}{% raw %}

</div>

Identify the instrument's entry in the sound picker.

**Returns**

- *str*: The pack-qualified key for a plugin sound, or the built-in family or label.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> INSTRUMENT_BY_KEY[
...     "viola_bowed"
... ].picker_group
'Viola'
```

### Instrument.playback_volume

<div class="api-signature" markdown="1">

```python
def playback_volume(level: float = 1.0) -> float
```

{% endraw %}{% include api-source.html name="Instrument.playback_volume" line=292 %}{% raw %}

</div>

Return the output volume for a note or clip played on this
instrument.

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

<div class="api-signature" markdown="1">

```python
def instrument_groups() -> list[tuple[str, list[Instrument]]]
```

{% endraw %}{% include api-source.html name="instrument_groups" line=371 %}{% raw %}

</div>

Return the instruments as they are listed for choosing.

Ways of playing one instrument share a single entry.

**Returns**

- *list of tuple of (str, list of Instrument)*: Each entry's picker group and its instruments, in the order listed.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [name for name, _ in instrument_groups()]
['Piano', 'Flute', 'French Horn', 'Viola', 'Marimba', 'Vibraphone']
>>> [
...     inst_.variant
...     for inst_ in dict(instrument_groups())[
...         "Viola"
...     ]
... ]
['Arco', 'Pizzicato']
```

## read_wav

<div class="api-signature" markdown="1">

```python
def read_wav(path: Path) -> tuple[list[float], int]
```

{% endraw %}{% include api-source.html name="read_wav" line=465 %}{% raw %}

</div>

Read a mono 16-bit WAV file.

**Parameters**

- `path` (*Path*): The file.

**Returns**

- *tuple of (list of float, int)*: The samples as floats from -1 to 1, and the sample rate in hertz.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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
```

## shift_pitch

<div class="api-signature" markdown="1">

```python
def shift_pitch(
    samples: Sequence[float],
    *,
    semitones: float,
) -> list[float]
```

{% endraw %}{% include api-source.html name="shift_pitch" line=546 %}{% raw %}

</div>

Change the pitch of samples by resampling them.

It also changes the length, which is fine for a few semitones.

**Parameters**

- `samples` (*sequence of float*): Mono samples.
- `semitones` (*float*): How far to shift; positive is higher. Keyword-only.

**Returns**

- *list of float*: The resampled samples, shorter when shifted up and longer when shifted down.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(
...     shift_pitch([0.0] * 100, semitones=12)
... )  # an octave up: half as long
50
```

## to_wav_bytes

<div class="api-signature" markdown="1">

```python
def to_wav_bytes(
    samples: Iterable[float],
    *,
    rate: int = SAMPLE_RATE,
) -> bytes
```

{% endraw %}{% include api-source.html name="to_wav_bytes" line=581 %}{% raw %}

</div>

Encode samples as a mono 16-bit WAV file in memory.

**Parameters**

- `samples` (*iterable of float*): Mono samples from -1 to 1; anything beyond is clipped.
- `rate` (*int, default SAMPLE_RATE*): The sample rate in hertz. Keyword-only.

**Returns**

- *bytes*: The contents of a WAV file.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
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
```

## write_file_atomically

<div class="api-signature" markdown="1">

```python
def write_file_atomically(
    path: Path,
    *,
    data: bytes,
) -> None
```

{% endraw %}{% include api-source.html name="write_file_atomically" line=636 %}{% raw %}

</div>

Write a file so that nothing ever reads it half written, even
another copy of Alto writing the same file.

The bytes go to a file of the writer's own first and then replace
the file in one step.

**Parameters**

- `path` (*Path*): The file.
- `data` (*bytes*): What it holds. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> folder = Path(tempfile.mkdtemp())
>>> write_file_atomically(
...     folder / "note.wav", data=b"RIFF"
... )
>>> (
...     (folder / "note.wav").read_bytes(),
...     [p.name for p in folder.iterdir()],
... )
(b'RIFF', ['note.wav'])
```

## metronome_preview_pcm

<div class="api-signature" markdown="1">

```python
@lru_cache(maxsize=len(METRONOME_CLICKS))
def metronome_preview_pcm(key: str) -> tuple[bytes, int]
```

{% endraw %}{% include api-source.html name="metronome_preview_pcm" line=704 %}{% raw %}

</div>

Return the four beats used for playback and the spectrum display.

**Parameters**

- `key` (*str*): The bundled click to repeat at 120 BPM.

**Returns**

- *tuple of bytes and int*: Mono 16-bit PCM frames and their sample rate in hertz.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pcm, rate = metronome_preview_pcm("high-pip")
>>> len(pcm) > 3 * rate
True
```

## Sounds

<div class="api-signature" markdown="1">

```python
Sounds()
```

{% endraw %}{% include api-source.html name="Sounds" line=783 %}{% raw %}

</div>

Bases: `QObject`

A lazy cache of notes played through `QSoundEffect`, in the chosen
instrument.

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

<div class="api-signature" markdown="1">

```python
def recordings(inst: Instrument) -> dict[int, Path]
```

{% endraw %}{% include api-source.html name="Sounds.recordings" line=883 %}{% raw %}

</div>

Return the notes an instrument has a recording for on disk.

**Parameters**

- `inst` (*Instrument*): The instrument.

**Returns**

- *dict of int to Path*: MIDI note number to its sample file.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> 60 in Sounds().recordings(
...     INSTRUMENT_BY_KEY["piano"]
... )
True
```

### Sounds.unrecorded

<div class="api-signature" markdown="1">

```python
def unrecorded(instrument: str | None = None) -> list[int]
```

{% endraw %}{% include api-source.html name="Sounds.unrecorded" line=985 %}{% raw %}

</div>

List the notes within an instrument's recorded range that have
no recording of their own, nearest middle C first.

Each is made the first time it plays, by shifting the nearest
recording. `alto.ui.warmup` makes them ahead of time with
`prepare`, so that even a first play is quick.

**Parameters**

- `instrument` (*str or None, default None*): The instrument's key, or None for the current one.

**Returns**

- *list of int*: MIDI note numbers.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> notes = Sounds().unrecorded(
...     "piano"
... )  # the piano is recorded every third semitone
>>> notes[:2], 60 in notes, len(notes)
([61, 59], False, 58)
```

### Sounds.prepare

<div class="api-signature" markdown="1">

```python
def prepare(
    midi: int,
    *,
    instrument: str | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="Sounds.prepare" line=1027 %}{% raw %}

</div>

Make the file a note plays, if it has no recording and was not
made before, so that its first play is quick.

**Parameters**

- `midi` (*int*): The MIDI note number.
- `instrument` (*str or None, default None*): The instrument's key, or None for the current one. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Sounds().prepare(61, instrument="piano")
```

### Sounds.note_duration_ms

<div class="api-signature" markdown="1">

```python
def note_duration_ms(
    midi: int,
    *,
    instrument: str | None = None,
) -> int
```

{% endraw %}{% include api-source.html name="Sounds.note_duration_ms" line=1113 %}{% raw %}

</div>

Read the playback length of a note for synchronized instrument
animations.

**Parameters**

- `midi` (*int*): Sounding MIDI pitch.
- `instrument` (*str or None*): Pack sound key, or None for the learner's selected sound.

**Returns**

- *int*: Duration in milliseconds, using the usual feedback interval if the WAV is unavailable.

**Examples**

```text
A one-second sample has the same 1000 ms feedback interval when
muted.
```

### Sounds.play_midi

<div class="api-signature" markdown="1">

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

{% endraw %}{% include api-source.html name="Sounds.play_midi" line=1242 %}{% raw %}

</div>

Play a note in the chosen instrument (or another one).

A sustained instrument (bowed or blown) ends the notes still
sounding first, as a player would, and so does a damped
one (the piano, played without the pedal), unless
`release_previous` is False, which is for the notes of a chord
that start together. Nothing plays while muted unless
`force` is set. A failure to play is reported but never raised,
so audio can never break an exercise.

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

### Sounds.play_metronome_click

<div class="api-signature" markdown="1">

```python
def play_metronome_click(
    *,
    force: bool = False,
) -> None
```

{% endraw %}{% include api-source.html name="Sounds.play_metronome_click" line=1308 %}{% raw %}

</div>

Play one beat with the selected click sound.

**Parameters**

- `force` (*bool, default False*): Play even when muted for an explicit settings preview.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> player = Sounds()
>>> player.enabled = False
>>> player.play_metronome_click()
```

### Sounds.preview_metronome

<div class="api-signature" markdown="1">

```python
def preview_metronome(key: str) -> None
```

{% endraw %}{% include api-source.html name="Sounds.preview_metronome" line=1335 %}{% raw %}

</div>

Play four evenly spaced clicks at 120 BPM, even while muted.

Render one clip so loading the sound cannot delay later beats.

**Parameters**

- `key` (*str*): The bundled click to audition.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sounds.preview_metronome("low-pip")  # doctest: +SKIP
```

### Sounds.stop_metronome_preview

<div class="api-signature" markdown="1">

```python
def stop_metronome_preview() -> None
```

{% endraw %}{% include api-source.html name="Sounds.stop_metronome_preview" line=1394 %}{% raw %}

</div>

End the four-click audition when leaving the preview.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sounds.stop_metronome_preview()
```

### Sounds.stop_all

<div class="api-signature" markdown="1">

```python
def stop_all() -> None
```

{% endraw %}{% include api-source.html name="Sounds.stop_all" line=1405 %}{% raw %}

</div>

Silence every note at once, and cancel any fade-outs underway.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Sounds().stop_all()
```

### Sounds.preview

<div class="api-signature" markdown="1">

```python
def preview(
    key: str,
    *,
    midis: Iterable[int | None],
    step_ms: int | tuple[int, ...] = 300,
    beat_ms: int | None = None,
    force: bool = True,
    on_step: Callable[[int | None], object] | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="Sounds.preview" line=1581 %}{% raw %}

</div>

Play notes one after another in an instrument, even while muted,
to hear what it sounds like.

The phrase is rendered as one audio clip, so first-use loading
cannot change the spacing between notes.
Starting a preview silences the one before it.

**Parameters**

- `key` (*str*): The key of the instrument.
- `midis` (*iterable of int or None*): MIDI pitches in order, with None for a rest. Keyword-only.
- `step_ms` (*int or tuple of int, default 300*): Duration in milliseconds for every note, or one per note.
- `beat_ms` (*int or None*): Add the selected metronome sound at this interval in milliseconds. Omit for an unaccompanied preview.
- `force` (*bool, default True*): Play even when muted. False follows the sound setting while keeping the visual timing.
- `on_step` (*callable or None*): Highlight each onset. Clear on completion or interruption.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sounds.preview(
...     "flute", midis=[60, 64, 67]
... )  # doctest: +SKIP
```

### Sounds.play_rhythm

<div class="api-signature" markdown="1">

```python
def play_rhythm(
    step_ms: tuple[int, ...],
    *,
    levels: tuple[float, ...],
    force: bool = False,
    on_step: Callable[[int | None], object],
) -> None
```

{% endraw %}{% include api-source.html name="Sounds.play_rhythm" line=1786 %}{% raw %}

</div>

Play one metronome click per written onset, observing rests.

**Parameters**

- `step_ms` (*tuple of int*): Length of each note or rest in milliseconds.
- `levels` (*tuple of float*): Click volume from zero (rest) to one for each step.
- `force` (*bool*): Allow an explicit audition while muted.
- `on_step` (*callable*): Highlight notes and rests, then clear after the last step.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sounds.play_rhythm(
...     (600, 600), levels=(1.0, 0.0), on_step=print,
... )  # doctest: +SKIP
```

### Sounds.play_notes

<div class="api-signature" markdown="1">

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

{% endraw %}{% include api-source.html name="Sounds.play_notes" line=2134 %}{% raw %}

</div>

Play staff columns left to right, evenly spaced.

The notes within a column sound together, a little quieter the
more there are.

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
>>> s.play_notes(
...     [
...         [
...             Note.parse("C4"),
...             Note.parse("E4"),
...             Note.parse("G4"),
...         ]
...     ]
... )  # muted: nothing sounds
```

### Sounds.stop_sample

<div class="api-signature" markdown="1">

```python
def stop_sample(on_step: Callable[[int | None], object]) -> None
```

{% endraw %}{% include api-source.html name="Sounds.stop_sample" line=2219 %}{% raw %}

</div>

Stop a displayed sample if it still owns playback.

**Parameters**

- `on_step` (*callable*): The display callback originally passed to play_sample.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Sounds().stop_sample(print)
```

### Sounds.play_sample

<div class="api-signature" markdown="1">

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

{% endraw %}{% include api-source.html name="Sounds.play_sample" line=2235 %}{% raw %}

</div>

Play a displayed sample and report the sounding column until it
ends or is interrupted.

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
>>> player.play_sample(
...     [[Note.parse("C4")]],
...     gap_ms=300,
...     on_step=print,
... )
0
>>> player.stop_sample(print)
None
```

### Sounds.play_correct

<div class="api-signature" markdown="1">

```python
def play_correct(streak: int) -> None
```

{% endraw %}{% include api-source.html name="Sounds.play_correct" line=2311 %}{% raw %}

</div>

Play a note that climbs the C major scale (C5 to C6) as the
streak grows, then wraps.

**Parameters**

- `streak` (*int*): How many right answers in a row; 1 plays C5.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> s = Sounds()
>>> s.enabled = False
>>> s.play_correct(3)  # muted: nothing sounds
```
{% endraw %}
