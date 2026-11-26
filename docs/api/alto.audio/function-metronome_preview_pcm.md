---
title: metronome_preview_pcm
parent: alto.audio
api_module: alto.audio
package: alto
permalink: /api/alto.audio/function-metronome_preview_pcm/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
@lru_cache(maxsize=len(METRONOME_CLICKS))
def metronome_preview_pcm(key: str) -> tuple[bytes, int]
```

{% endraw %}{% include api-source.html name="metronome_preview_pcm" line=704 %}{% raw %}

</div>

Return the four beats used for playback and the spectrum display.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The bundled click to repeat at 120 BPM. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of bytes and int` | Mono 16-bit PCM frames and their sample rate in hertz. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pcm, rate = metronome_preview_pcm("high-pip")
>>> len(pcm) > 3 * rate
True
```
{% endraw %}
