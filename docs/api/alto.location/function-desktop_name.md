---
title: desktop_name
parent: alto.location
api_module: alto.location
package: alto
permalink: /api/alto.location/function-desktop_name/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def desktop_name(
    *,
    environ: Mapping[str, str] = os.environ,
) -> str
```

{% endraw %}{% include api-source.html name="desktop_name" line=137 %}{% raw %}

</div>

Give the name the desktop uses to match Alto's window to its menu
entry, and so to its icon in the dock.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `environ` | `mapping of str to str` | The environment to read. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | "alto", or "alto-dev" when `ALTO_HOME` keeps a second copy apart, so that the two copies are separate in the dock. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     desktop_name(environ={}),
...     desktop_name(
...         environ={
...             "ALTO_HOME": "/tmp/alto-dev"
...         }
...     ),
... )
('alto', 'alto-dev')
```
{% endraw %}
