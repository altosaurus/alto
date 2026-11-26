---
title: self_update_target
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/function-self_update_target/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def self_update_target(
    *,
    executable: Path | None = None,
    system: str | None = None,
) -> Target | None
```

{% endraw %}{% include api-source.html name="self_update_target" line=177 %}{% raw %}

</div>

Say whether the running copy can replace itself, and if so where it
is.

On Linux a copy can if it was put in `<prefix>/opt/alto` by
`install.sh`, which links `<prefix>/bin/alto` to it; a folder that
someone unpacked and ran from cannot. On Windows a copy can if the
installer made it, which leaves `unins000.exe` beside it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `executable` | `Path or None, default None` | The running program; the one that is running if None. Keyword-only. |
| `system` | `str or None, default None` | "linux" or "windows"; this computer's if None. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Target or None` | Where the copy is, or None if it cannot replace itself. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> self_update_target(
...     executable=Path("/usr/bin/python3"),
...     system="linux",
... ) is None
True
>>> self_update_target(
...     executable=Path("/nowhere/alto.exe"),
...     system="windows",
... ) is None
True
```
{% endraw %}
