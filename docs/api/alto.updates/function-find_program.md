---
title: find_program
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-find_program/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def find_program(
    name: str,
    *,
    home: Path | None = None,
) -> str | None
```

{% endraw %}{% include api-source.html name="find_program" line=412 %}{% raw %}

</div>

Find a program to run, also in the places the installers put them,
which a program started from the dock may not search.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `name` | `str` | The program's name, such as "git" or "uv". |
| `home` | `Path or None, default None` | The home folder to look in besides the search path; the user's own if None. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str or None` | Its path, or None if it is nowhere to be found. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> find_program(
...     "no-such-program-anywhere"
... ) is None
True
```
{% endraw %}
