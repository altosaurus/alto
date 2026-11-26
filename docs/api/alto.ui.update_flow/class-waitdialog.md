---
title: WaitDialog
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/class-waitdialog/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
WaitDialog(
    parent: QWidget | None,
    *,
    text: str,
)
```

{% endraw %}{% include api-source.html name="WaitDialog" line=395 %}{% raw %}

</div>

Bases: `QDialog`

A small window with a bar that keeps moving and a Cancel button,
shown while something is asked for.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `ended` | `bool` | Whether the asking has ended, by an answer, a failure or a cancel. |
| `canceled` | `bool` | Whether the person canceled it. |

**Constructor**

Build the window.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None` | The window it belongs to. |
| `text` | `str` | What is being asked for. Keyword-only. |

## WaitDialog.reject

<div class="api-signature" markdown="1">

```python
def reject() -> None
```

{% endraw %}{% include api-source.html name="WaitDialog.reject" line=439 %}{% raw %}

</div>

Cancel the asking.
{% endraw %}
