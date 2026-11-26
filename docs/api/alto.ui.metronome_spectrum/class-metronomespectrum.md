---
title: MetronomeSpectrum
parent: alto.ui.metronome_spectrum
api_module: alto.ui.metronome_spectrum
package: alto.ui
permalink: /api/alto.ui.metronome_spectrum/class-metronomespectrum/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
MetronomeSpectrum()
```

{% endraw %}{% include api-source.html name="MetronomeSpectrum" line=91 %}{% raw %}

</div>

Bases: `QWidget`

Show a smooth frequency curve that rises with each click.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MetronomeSpectrum().accessibleName()
'Metronome spectrum'
```

**Constructor**

Create the level display at rest.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> display = MetronomeSpectrum()
```

## MetronomeSpectrum.set_sound

<div class="api-signature" markdown="1">

```python
def set_sound(key: str) -> None
```

{% endraw %}{% include api-source.html name="MetronomeSpectrum.set_sound" line=122 %}{% raw %}

</div>

Load the levels for the selected sound.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The sound selected in the list. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MetronomeSpectrum().set_sound("pencil-click")
```

## MetronomeSpectrum.set_playing

<div class="api-signature" markdown="1">

```python
def set_playing(playing: bool) -> None
```

{% endraw %}{% include api-source.html name="MetronomeSpectrum.set_playing" line=152 %}{% raw %}

</div>

Follow the audio backend's playback state.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `playing` | `bool` | Whether the loaded preview is playing. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MetronomeSpectrum().set_playing(False)
```

## MetronomeSpectrum.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="MetronomeSpectrum.paintEvent" line=175 %}{% raw %}

</div>

Draw a continuous curve through the current spectrum.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QPaintEvent` | The requested paint region. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MetronomeSpectrum().grab().isNull()
False
```
{% endraw %}
