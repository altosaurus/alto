---
title: shift_pitch
parent: alto.audio
api_module: alto.audio
package: alto
permalink: /api/alto.audio/function-shift_pitch/
---
{% raw %}
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

| Parameter | Type | Description |
| --- | --- | --- |
| `samples` | `sequence of float` | Mono samples. |
| `semitones` | `float` | How far to shift; positive is higher. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `list of float` | The resampled samples, shorter when shifted up and longer when shifted down. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(
...     shift_pitch([0.0] * 100, semitones=12)
... )  # an octave up: half as long
50
```
{% endraw %}
