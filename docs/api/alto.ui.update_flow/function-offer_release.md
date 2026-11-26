---
title: offer_release
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/function-offer_release/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def offer_release(
    parent: QWidget,
    *,
    release: Release,
    kind: InstallKind,
    source: Source | None,
    installed: str,
    restart: Callable[[], None],
    quit_app: Callable[[], None],
) -> None
```

{% endraw %}{% include api-source.html name="offer_release" line=1121 %}{% raw %}

</div>

Ask whether to upgrade using the installation's supported update
path.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget` | Window that owns the upgrade prompt. |
| `release` | `Release` | Published release to offer. |
| `kind` | `InstallKind` | Installation type. |
| `source` | `Source or None` | Repository used by a script installation. |
| `installed` | `str` | Current version. |
| `restart` | `Callable` | Restart a script installation after upgrading. |
| `quit_app` | `Callable` | Close a packaged copy after handing off to its installer. |

**Examples**

```text
A manual check can offer a version the learner previously declined.
```
{% endraw %}
