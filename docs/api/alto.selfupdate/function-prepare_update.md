---
title: prepare_update
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/function-prepare_update/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def prepare_update(
    release: updates.Release,
    *,
    target: Target,
    work: Path,
    keys: tuple[str, ...],
    machine: str,
    base: str = updates.DOWNLOAD_BASE,
    status: Callable[[str], None],
    progress: Callable[[int, int], None],
    canceled: Callable[[], bool],
) -> Prepared
```

{% endraw %}{% include api-source.html name="prepare_update" line=435 %}{% raw %}

</div>

Download a release for this copy and check it: its signed list of
checksums, then the file against its listed hash.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `release` | `updates.Release` | The release to install. |
| `target` | `Target` | The copy that will be replaced. |
| `work` | `Path` | An empty folder to work in. |
| `keys` | `tuple of str` | The public keys (base64) a signature may be made with. Keyword-only. |
| `machine` | `str` | The processor, as `platform.machine()` says it. Keyword-only. |
| `base` | `str, default updates.DOWNLOAD_BASE` | Where the release keeps its files. Keyword-only. |
| `status` | `Callable` | Called with what is being done, in words for the person. Keyword-only. |
| `progress` | `Callable` | Called with the bytes received so far and the total, while the file downloads. Keyword-only. |
| `canceled` | `Callable` | Asked now and then; True stops. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Prepared` | The checked update, ready to be handed over. |

**Raises**

- *UpdateError*: If anything is missing or does not check out. Nothing is installed.
- *UpdateCanceled*: If `canceled` said so.
{% endraw %}
