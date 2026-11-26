---
title: start_handoff
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/function-start_handoff/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def start_handoff(
    prepared: Prepared,
    *,
    target: Target,
    pid: int | None = None,
    log: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> None
```

{% endraw %}{% include api-source.html name="start_handoff" line=782 %}{% raw %}

</div>

Start the program that installs the update, and return at once so
that Alto can quit.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `prepared` | `Prepared` | The checked update. |
| `target` | `Target` | The copy that is replaced. |
| `pid` | `int or None, default None` | The process to wait for, which is Alto; this one if None. Keyword-only. |
| `log` | `Path or None, default None` | Where the Linux helper writes; `log_path()` if None. Keyword-only. |
| `environ` | `Mapping or None, default None` | The environment to start from; this program's if None. Keyword-only. |

**Raises**

- *UpdateError*: If the update is missing what the system needs.
{% endraw %}
