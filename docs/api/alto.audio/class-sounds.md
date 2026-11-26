---
title: Sounds
parent: alto.audio
api_module: alto.audio
package: alto
permalink: /api/alto.audio/class-sounds/
---
{% raw %}
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

| Attribute | Type | Description |
| --- | --- | --- |
| `enabled` | `bool` | False while the app is muted. |
| `instrument` | `str` | The key of the instrument in use, a key of `INSTRUMENT_BY_KEY`. |
| `FADE_MS` | `int` | How quickly a sustained note dies away when the next one begins, in milliseconds. |

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

## Sounds.recordings

<div class="api-signature" markdown="1">

```python
def recordings(inst: Instrument) -> dict[int, Path]
```

{% endraw %}{% include api-source.html name="Sounds.recordings" line=883 %}{% raw %}

</div>

Return the notes an instrument has a recording for on disk.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `inst` | `Instrument` | The instrument. |

**Returns**

| Type | Description |
| --- | --- |
| `dict of int to Path` | MIDI note number to its sample file. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> 60 in Sounds().recordings(
...     INSTRUMENT_BY_KEY["piano"]
... )
True
```

## Sounds.unrecorded

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

| Parameter | Type | Description |
| --- | --- | --- |
| `instrument` | `str or None, default None` | The instrument's key, or None for the current one. |

**Returns**

| Type | Description |
| --- | --- |
| `list of int` | MIDI note numbers. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> notes = Sounds().unrecorded(
...     "piano"
... )  # the piano is recorded every third semitone
>>> notes[:2], 60 in notes, len(notes)
([61, 59], False, 58)
```

## Sounds.prepare

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

| Parameter | Type | Description |
| --- | --- | --- |
| `midi` | `int` | The MIDI note number. |
| `instrument` | `str or None, default None` | The instrument's key, or None for the current one. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Sounds().prepare(61, instrument="piano")
```

## Sounds.note_duration_ms

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

| Parameter | Type | Description |
| --- | --- | --- |
| `midi` | `int` | Sounding MIDI pitch. |
| `instrument` | `str or None` | Pack sound key, or None for the learner's selected sound. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | Duration in milliseconds, using the usual feedback interval if the WAV is unavailable. |

**Examples**

```text
A one-second sample has the same 1000 ms feedback interval when
muted.
```

## Sounds.play_midi

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

| Parameter | Type | Description |
| --- | --- | --- |
| `midi` | `int` | The MIDI note number. |
| `volume` | `float, default 1.0` | The level from 0 to 1, before the instrument's own gain. Keyword-only. |
| `instrument` | `str or None, default None` | The key of the instrument to use instead of the chosen one. Keyword-only. |
| `force` | `bool, default False` | Play even while muted, for previews. Keyword-only. |
| `release_previous` | `bool, default True` | End the sustained or damped notes still ringing first. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> s = Sounds()
>>> s.enabled = False
>>> s.play_midi(60)  # muted: returns at once
>>> Sounds().play_midi(60)  # doctest: +SKIP
```

## Sounds.play_metronome_click

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

| Parameter | Type | Description |
| --- | --- | --- |
| `force` | `bool, default False` | Play even when muted for an explicit settings preview. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> player = Sounds()
>>> player.enabled = False
>>> player.play_metronome_click()
```

## Sounds.preview_metronome

<div class="api-signature" markdown="1">

```python
def preview_metronome(key: str) -> None
```

{% endraw %}{% include api-source.html name="Sounds.preview_metronome" line=1335 %}{% raw %}

</div>

Play four evenly spaced clicks at 120 BPM, even while muted.

Render one clip so loading the sound cannot delay later beats.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The bundled click to audition. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sounds.preview_metronome("low-pip")  # doctest: +SKIP
```

## Sounds.stop_metronome_preview

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

## Sounds.stop_all

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

## Sounds.preview

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

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The key of the instrument. |
| `midis` | `iterable of int or None` | MIDI pitches in order, with None for a rest. Keyword-only. |
| `step_ms` | `int or tuple of int, default 300` | Duration in milliseconds for every note, or one per note. |
| `beat_ms` | `int or None` | Add the selected metronome sound at this interval in milliseconds. Omit for an unaccompanied preview. |
| `force` | `bool, default True` | Play even when muted. False follows the sound setting while keeping the visual timing. |
| `on_step` | `callable or None` | Highlight each onset. Clear on completion or interruption. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sounds.preview(
...     "flute", midis=[60, 64, 67]
... )  # doctest: +SKIP
```

## Sounds.play_rhythm

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

| Parameter | Type | Description |
| --- | --- | --- |
| `step_ms` | `tuple of int` | Length of each note or rest in milliseconds. |
| `levels` | `tuple of float` | Click volume from zero (rest) to one for each step. |
| `force` | `bool` | Allow an explicit audition while muted. |
| `on_step` | `callable` | Highlight notes and rests, then clear after the last step. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sounds.play_rhythm(
...     (600, 600), levels=(1.0, 0.0), on_step=print,
... )  # doctest: +SKIP
```

## Sounds.play_notes

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

{% endraw %}{% include api-source.html name="Sounds.play_notes" line=2135 %}{% raw %}

</div>

Play staff columns left to right, evenly spaced.

The notes within a column sound together, a little quieter the
more there are.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `instrument` | `str or None` | Instrument key for this playback, or None for the learner’s selection. |
| `force` | `bool` | Play even when exercise audio is muted. |
| `warmup` | `bool` | Silently initialize audio streams before starting playback. |
| `columns` | `iterable of sequence of Note` | The columns of notes, as drawn on a staff. |
| `gap_ms` | `int, default 450` | The time between columns, in milliseconds. Keyword-only. |
| `on_step` | `callable or None, default None` | Called with the index of each column as it starts, and with None when the last has had its time. It is called while muted too, so a display can follow the music with the sound off. Keyword-only. |

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

## Sounds.stop_sample

<div class="api-signature" markdown="1">

```python
def stop_sample(on_step: Callable[[int | None], object]) -> None
```

{% endraw %}{% include api-source.html name="Sounds.stop_sample" line=2220 %}{% raw %}

</div>

Stop a displayed sample if it still owns playback.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `on_step` | `callable` | The display callback originally passed to play_sample. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Sounds().stop_sample(print)
```

## Sounds.play_sample

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

{% endraw %}{% include api-source.html name="Sounds.play_sample" line=2236 %}{% raw %}

</div>

Play a displayed sample and report the sounding column until it
ends or is interrupted.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `columns` | `sequence of sequence of Note` | Written notes in playback order, with simultaneous notes grouped together. |
| `gap_ms` | `int` | Time between column onsets in milliseconds. |
| `on_step` | `callable` | Receives each sounding column index and None to clear the display. |
| `instrument` | `str or None` | Instrument key for this playback, or None for the learner’s selection. |
| `force` | `bool` | Audition the sample even when exercise audio is muted. |
| `warmup` | `bool` | Prepare the audio streams before the first note. |

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

## Sounds.play_correct

<div class="api-signature" markdown="1">

```python
def play_correct(streak: int) -> None
```

{% endraw %}{% include api-source.html name="Sounds.play_correct" line=2312 %}{% raw %}

</div>

Play a note that climbs the C major scale (C5 to C6) as the
streak grows, then wraps.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `streak` | `int` | How many right answers in a row; 1 plays C5. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> s = Sounds()
>>> s.enabled = False
>>> s.play_correct(3)  # muted: nothing sounds
```
{% endraw %}
