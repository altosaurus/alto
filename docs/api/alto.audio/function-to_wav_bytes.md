---
title: to_wav_bytes
parent: alto.audio
api_module: alto.audio
package: alto
permalink: /api/alto.audio/function-to_wav_bytes/
---
{% raw %}
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

| Parameter | Type | Description |
| --- | --- | --- |
| `samples` | `iterable of float` | Mono samples from -1 to 1; anything beyond is clipped. |
| `rate` | `int, default SAMPLE_RATE` | The sample rate in hertz. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `bytes` | The contents of a WAV file. |

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
{% endraw %}
