---
title: read_wav
parent: alto.audio
api_module: alto.audio
package: alto
permalink: /api/alto.audio/function-read_wav/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_wav(path: Path) -> tuple[list[float], int]
```

{% endraw %}{% include api-source.html name="read_wav" line=465 %}{% raw %}

</div>

Read a mono 16-bit WAV file.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `path` | `Path` | The file. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (list of float, int)` | The samples as floats from -1 to 1, and the sample rate in hertz. |

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
{% endraw %}
