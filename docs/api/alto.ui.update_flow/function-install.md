---
title: install
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/function-install/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def install(
    parent: QWidget,
    *,
    source: Source,
    tag: str | None,
    restart: Callable[[], None],
) -> None
```

{% endraw %}{% include api-source.html name="install" line=1282 %}{% raw %}

</div>

Install a release, or the newest commit of the main branch, showing
the progress, and restart if it worked.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget` | The window the progress is shown over. |
| `source` | `Source` | Where the running copy came from. Keyword-only. |
| `tag` | `str or None` | The release to install, such as "v0.1.0"; None for the newest commit of the main branch. Keyword-only. |
| `restart` | `Callable` | What to do after a successful update. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> install  # doctest: +SKIP
```
{% endraw %}
