---
title: write_file_atomically
parent: alto.audio
api_module: alto.audio
package: alto
permalink: /api/alto.audio/function-write_file_atomically/
---
{% raw %}
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

| Parameter | Type | Description |
| --- | --- | --- |
| `path` | `Path` | The file. |
| `data` | `bytes` | What it holds. Keyword-only. |

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
{% endraw %}
