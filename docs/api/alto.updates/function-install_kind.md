---
title: install_kind
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-install_kind/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def install_kind(
    source: Source | None,
    *,
    tool: bool,
    frozen: bool,
) -> InstallKind
```

{% endraw %}{% include api-source.html name="install_kind" line=319 %}{% raw %}

</div>

Decide what kind of copy of Alto this is.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `source` | `Source or None` | Where it was installed from, if it was installed from a git address. |
| `tool` | `bool` | Whether it runs from an environment that `uv tool` made. Keyword-only. |
| `frozen` | `bool` | Whether it is a packaged build. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `InstallKind` | The kind. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> here = Source(
...     "https://example.org/a.git",
...     commit="abc1234",
... )
>>> install_kind(
...     here, tool=True, frozen=False
... ).name
'SCRIPT'
>>> (
...     install_kind(
...         here, tool=False, frozen=False
...     ).name,
...     install_kind(
...         None, tool=False, frozen=False
...     ).name,
... )
('OTHER', 'SOURCE')
>>> install_kind(
...     None, tool=False, frozen=True
... ).name
'PACKAGE'
```
{% endraw %}
