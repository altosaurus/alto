---
title: CheckDialog
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/class-checkdialog/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
CheckDialog(
    parent: QWidget | None,
    *,
    source: Source,
    git: str,
)
```

{% endraw %}{% include api-source.html name="CheckDialog" line=454 %}{% raw %}

</div>

Bases: `WaitDialog`

A waiting window while the address Alto came from is asked for the
newest commit of its main branch.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `commit` | `str` | The newest commit, once it is known; empty if it could not be found out. |
| `error` | `str` | What went wrong, if there is no commit. |
| `runner` | `CommandRunner` | The program that does the asking. |

**Constructor**

Build the window; it asks nothing until `run` is called.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None` | The window it belongs to. |
| `source` | `Source` | Where the running copy of Alto came from. Keyword-only. |
| `git` | `str` | The path of the `git` program. Keyword-only. |

## CheckDialog.run

<div class="api-signature" markdown="1">

```python
def run() -> None
```

{% endraw %}{% include api-source.html name="CheckDialog.run" line=496 %}{% raw %}

</div>

Ask, showing the window until there is an answer.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> # noinspection PyTypeChecker
>>> CheckDialog(
...     None,
...     source=Source(
...         "https://example.org/a.git",
...         commit="abc1234",
...     ),
...     git="git",
... ).canceled
False
```
{% endraw %}
