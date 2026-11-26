---
title: Instrument
parent: alto.audio
api_module: alto.audio
package: alto
permalink: /api/alto.audio/class-instrument/
---
{% raw %}
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

| Attribute | Type | Description |
| --- | --- | --- |
| `key` | `str` | A short identifier used in settings and file names. |
| `label` | `str` | The name shown in the interface. Keyword-only. |
| `folder` | `str` | Under `assets/`: "piano" or "samples/<key>". File names are MIDI note numbers. Keyword-only. |
| `gain` | `float, default 1.0` | The level relative to the piano. Keyword-only. |
| `sustained` | `bool, default False` | True for bowed and blown instruments, whose notes end when the next one begins; struck and plucked ones ring on. Keyword-only. |
| `damped` | `bool, default False` | True for an instrument whose notes are stopped by a damper when the key is let go, played without the pedal: the piano. Each note ends as the next one begins, as it does when the fingers move from key to key, instead of ringing on over the following notes as if the pedal were down. Keyword-only. |
| `family` | `str, default ""` | Instruments that are ways of playing the same instrument share a family (the viola: arco and pizzicato). Keyword-only. |
| `variant` | `str, default ""` | Which way of playing it, within the family. Keyword-only. |
| `samples` | `tuple of (int, Path), default ()` | Pairs of MIDI pitches and local recording paths supplied by an installed instrument pack. Keyword-only. |
| `pack_name` | `str, default ""` | Display name of the plugin that supplies the recordings. Keyword-only. |
| `kind` | `str, default ""` | What sort of instrument it is, such as "harpsichord", so that other sounds of the same sort can be offered together. Built-in instruments use their family or name. Keyword-only. |

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

## Instrument.kind_name

<div class="api-signature" markdown="1">

```python
@property
def kind_name() -> str
```

{% endraw %}{% include api-source.html name="Instrument.kind_name" line=250 %}{% raw %}

</div>

Name what sort of instrument this is, in lowercase.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The plugin's ``kind``, or the built-in family, or the instrument's label. |

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

## Instrument.picker_group

<div class="api-signature" markdown="1">

```python
@property
def picker_group() -> str
```

{% endraw %}{% include api-source.html name="Instrument.picker_group" line=273 %}{% raw %}

</div>

Identify the instrument's entry in the sound picker.

**Returns**

| Type | Description |
| --- | --- |
| `str` | The pack-qualified key for a plugin sound, or the built-in family or label. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> INSTRUMENT_BY_KEY[
...     "viola_bowed"
... ].picker_group
'Viola'
```

## Instrument.playback_volume

<div class="api-signature" markdown="1">

```python
def playback_volume(level: float = 1.0) -> float
```

{% endraw %}{% include api-source.html name="Instrument.playback_volume" line=292 %}{% raw %}

</div>

Return the output volume for a note or clip played on this
instrument.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `level` | `float, default 1.0` | Relative amplitude. Simultaneous notes can request a lower level for each voice. |

**Returns**

| Type | Description |
| --- | --- |
| `float` | Linear Qt volume between zero and one, including the instrument's gain. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> INSTRUMENT_BY_KEY["flute"].playback_volume()
0.85
```
{% endraw %}
