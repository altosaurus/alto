---
title: PackageUpdateDialog
parent: alto.ui.package_update
api_module: alto.ui.package_update
package: alto.ui
permalink: /api/alto.ui.package_update/class-packageupdatedialog/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PackageUpdateDialog(
    parent: QWidget | None,
    *,
    release: Release,
    target: Target,
)
```

{% endraw %}{% include api-source.html name="PackageUpdateDialog" line=327 %}{% raw %}

</div>

Bases: `QDialog`

The window that downloads and checks an update for a packaged copy,
and then says what happens next.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `status` | `QLabel` | What is happening. |
| `bar` | `QProgressBar` | The progress of the download; a bar that keeps moving while the size is not known. |
| `button` | `QPushButton` | Cancel while the update is being prepared, then OK if it is ready or Close if it failed. |
| `ended` | `bool` | Whether the preparing has ended, ready, failed or canceled. |
| `ready` | `bool` | Whether the update is downloaded and checked. |
| `canceled` | `bool` | Whether the person canceled. |
| `error` | `str` | Why it failed, if it did. |
| `preparer` | `UpdatePreparer` | What does the work. |

**Constructor**

Build the window; nothing is downloaded until `run` is called.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None` | The window it belongs to. |
| `release` | `Release` | The release to install. Keyword-only. |
| `target` | `Target` | The copy that will be replaced. Keyword-only. |

## PackageUpdateDialog.run

<div class="api-signature" markdown="1">

```python
def run() -> Prepared | None
```

{% endraw %}{% include api-source.html name="PackageUpdateDialog.run" line=397 %}{% raw %}

</div>

Download and check the update, showing the window until the
person has read how it went.

**Returns**

| Type | Description |
| --- | --- |
| `Prepared or None` | The update, if it is ready and OK was pressed; None if it failed or was canceled, in which case nothing is left behind. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> here = Target(
...     "linux", folder=Path("/x"), prefix=None
... )
>>> # noinspection PyTypeChecker
>>> PackageUpdateDialog(
...     None,
...     release=Release(
...         "0.1.0", tag="v0.1.0", url=""
...     ),
...     target=here,
... ).ready
False
```

## PackageUpdateDialog.reject

<div class="api-signature" markdown="1">

```python
def reject() -> None
```

{% endraw %}{% include api-source.html name="PackageUpdateDialog.reject" line=439 %}{% raw %}

</div>

Close the window; before the update is ready that cancels it.
{% endraw %}
