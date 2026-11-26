---
title: synth_piano
parent: alto.audio
api_module: alto.audio
package: alto
permalink: /api/alto.audio/function-synth_piano/
---
{% raw %}
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

| Parameter | Type | Description |
| --- | --- | --- |
| `midi` | `int` | The MIDI note number. The same number always gives the same sound. |
| `duration` | `float, default 1.6` | How long the note lasts, in seconds. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `list of float` | Mono samples at `SAMPLE_RATE`, scaled so the loudest is 0.8. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> samples = synth_piano(60, duration=0.1)
>>> len(samples)
4410
>>> round(max(abs(s) for s in samples), 1)
0.8
```
{% endraw %}
