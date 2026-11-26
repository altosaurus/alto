---
title: parse_ls_remote
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-parse_ls_remote/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def parse_ls_remote(text: str) -> str | None
```

{% endraw %}{% include api-source.html name="parse_ls_remote" line=536 %}{% raw %}

</div>

Read the commit id out of what `git ls-remote` printed.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | The output: a line for each ref, each a commit id, a tab and the ref's name. |

**Returns**

| Type | Description |
| --- | --- |
| `str or None` | The commit id on the first line, or None if there is none (the ref does not exist, or git printed an error). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> parse_ls_remote(
...     "b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe\tHEAD\n"
... )
'b6e2091ba08f6b79dcf293d1a77d86f7a812d4fe'
>>> (
...     parse_ls_remote("") is None,
...     parse_ls_remote(
...         "fatal: repository not found"
...     )
...     is None,
... )
(True, True)
```
{% endraw %}
