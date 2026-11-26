---
title: ignore_progress
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/function-ignore_progress/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def ignore_progress(
    done: int,
    total: int,
) -> None
```

{% endraw %}{% include api-source.html name="ignore_progress" line=416 %}{% raw %}

</div>

Take a note of progress and do nothing with it, for a download whose
progress nobody watches.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `done` | `int` | The bytes received so far. |
| `total` | `int` | The total the server states. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ignore_progress(1, 2)
```
{% endraw %}
