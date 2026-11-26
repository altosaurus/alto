---
title: install_command
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-install_command/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def install_command(
    source: Source,
    *,
    uv: str,
    tag: str | None = None,
) -> tuple[str, list[str]]
```

{% endraw %}{% include api-source.html name="install_command" line=487 %}{% raw %}

</div>

Give the command that installs Alto over the installed copy: a
release, or the newest commit of the address.

`uv tool install --force` is used rather than `uv tool upgrade`,
because an upgrade stays on the tag or branch the copy was
installed from, and a copy that follows a release must be able to
move to the main branch and back.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `source` | `Source` | Where the running copy came from. |
| `uv` | `str` | The path of the `uv` program. Keyword-only. |
| `tag` | `str or None, default None` | The release to install, such as "v0.1.0"; the address's default branch if None. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of str and list of str` | The program and its arguments. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> here = Source(
...     "https://example.org/alto.git",
...     commit="abc1234",
... )
>>> install_command(here, uv="uv", tag="v0.1.0")
('uv', ['tool', 'install', '--force', 'git+https://example.org/alto.git@v0.1.0'])
>>> install_command(here, uv="uv")
('uv', ['tool', 'install', '--force', 'git+https://example.org/alto.git'])
```
{% endraw %}
