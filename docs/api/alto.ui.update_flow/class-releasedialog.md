---
title: ReleaseDialog
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/class-releasedialog/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ReleaseDialog(parent: QWidget | None)
```

{% endraw %}{% include api-source.html name="ReleaseDialog" line=751 %}{% raw %}

</div>

Bases: `WaitDialog`

A waiting window while GitHub is asked for the latest release.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `release` | `Release or None` | The latest release, once it is known; None if it could not be found out. |
| `error` | `str` | What went wrong, if there is no release. |
| `fetcher` | `ReleaseFetcher` | What does the asking. |

**Constructor**

Build the window; it asks nothing until `run` is called.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None` | The window it belongs to. |

## ReleaseDialog.run

<div class="api-signature" markdown="1">

```python
def run() -> None
```

{% endraw %}{% include api-source.html name="ReleaseDialog.run" line=781 %}{% raw %}

</div>

Ask, showing the window until there is an answer.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> # noinspection PyTypeChecker
>>> ReleaseDialog(None).canceled
False
```
{% endraw %}
