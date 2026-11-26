---
title: clean_environment
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/function-clean_environment/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def clean_environment(env: Mapping[str, str]) -> dict[str, str]
```

{% endraw %}{% include api-source.html name="clean_environment" line=591 %}{% raw %}

</div>

Undo what PyInstaller did to the environment, for a program that
this one starts.

A packaged program puts its own libraries first on the library path,
which would make the system's `sh`, `tar` and the next
Alto load them. PyInstaller keeps the original in
`LD_LIBRARY_PATH_ORIG`, and asks a program that restarts itself to
reset
what it passed on. The desktop's start-up token is for this launch
only, so it is dropped too.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `env` | `Mapping` | The environment of this program. |

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to str` | The environment to give the other. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> clean_environment(
...     {
...         "LD_LIBRARY_PATH": "/app/lib",
...         "LD_LIBRARY_PATH_ORIG": "/usr/lib",
...         "_PYI_ARCHIVE_FILE": "x",
...     }
... )
{'LD_LIBRARY_PATH': '/usr/lib', 'PYINSTALLER_RESET_ENVIRONMENT':
'1'}
>>> clean_environment(
...     {
...         "LD_LIBRARY_PATH": "/app/lib",
...         "LD_LIBRARY_PATH_ORIG": "",
...     }
... )
{'PYINSTALLER_RESET_ENVIRONMENT': '1'}
>>> clean_environment({"HOME": "/home/me"})
{'HOME': '/home/me', 'PYINSTALLER_RESET_ENVIRONMENT': '1'}
```
{% endraw %}
