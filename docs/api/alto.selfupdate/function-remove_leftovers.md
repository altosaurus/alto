---
title: remove_leftovers
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/function-remove_leftovers/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def remove_leftovers(
    *,
    older_than: float = 86400.0,
    now: float | None = None,
    root: Path | None = None,
) -> int
```

{% endraw %}{% include api-source.html name="remove_leftovers" line=894 %}{% raw %}

</div>

Remove the temporary folders of earlier updates that were never
cleaned up, such as a Windows installer that was run and left.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `older_than` | `float, default 86400.0` | How old, in seconds, a folder must be. Keyword-only. |
| `now` | `float or None, default None` | The time to measure from; the clock's if None. Keyword-only. |
| `root` | `Path or None, default None` | The folder to look in; the system's temporary folder if None. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | How many folders were removed. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> remove_leftovers(
...     root=Path("/no/such/folder")
... )
0
```
{% endraw %}
