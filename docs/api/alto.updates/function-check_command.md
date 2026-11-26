---
title: check_command
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-check_command/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def check_command(
    source: Source,
    *,
    git: str,
) -> tuple[str, list[str]]
```

{% endraw %}{% include api-source.html name="check_command" line=452 %}{% raw %}

</div>

Give the command that asks the address Alto came from for the commit
at the end of a branch or tag.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `source` | `Source` | Where the running copy came from. |
| `git` | `str` | The path of the `git` program. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of str and list of str` | The program and its arguments. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> check_command(
...     Source(
...         "https://example.org/a.git",
...         commit="abc1234",
...     ),
...     git="git",
... )
('git', ['ls-remote', 'https://example.org/a.git', 'HEAD'])
```
{% endraw %}
