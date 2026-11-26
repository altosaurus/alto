---
title: download
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/function-download/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def download(
    url: str,
    *,
    destination: Path,
    allowed: str,
    max_bytes: int,
    progress: Callable[[int, int], None],
    canceled: Callable[[], bool],
    seconds: int = 30,
) -> str
```

{% endraw %}{% include api-source.html name="download" line=241 %}{% raw %}

</div>

Fetch a file, checking the address, the size and the connection, and
give its SHA-256 hash.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `url` | `str` | The address. It must start with `allowed`. |
| `destination` | `Path` | Where to write the file. Nothing is left there if the download fails or is canceled. Keyword-only. |
| `allowed` | `str` | What the address must start with, which is where a release keeps its files. Keyword-only. |
| `max_bytes` | `int` | The most to accept, by the size the server states and by what actually arrives. Keyword-only. |
| `progress` | `Callable` | Called with the bytes received so far and the size the server states (0 if it does not say). Keyword-only. |
| `canceled` | `Callable` | Asked now and then; True stops the download. Keyword-only. |
| `seconds` | `int, default 30` | How long to wait for the server at a time. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The SHA-256 hash of what was written, in hexadecimal. |

**Raises**

- *UpdateError*: If the address is not allowed, the file is too large, the connection is not secure, or the download fails.
- *UpdateCanceled*: If `canceled` said so.
{% endraw %}
