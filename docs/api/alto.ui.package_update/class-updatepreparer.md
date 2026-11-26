---
title: UpdatePreparer
parent: alto.ui.package_update
api_module: alto.ui.package_update
package: alto.ui
permalink: /api/alto.ui.package_update/class-updatepreparer/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
UpdatePreparer(parent: QObject | None = None)
```

{% endraw %}{% include api-source.html name="UpdatePreparer" line=96 %}{% raw %}

</div>

Bases: `QObject`

Download and check an update on another thread, and report how it
goes through signals.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `status` | `Signal` | Emitted with what is being done ("Checking the signature…"). |
| `progress` | `Signal` | Emitted with the bytes received so far and the total (0 if it is not known), while the file downloads. |
| `done` | `Signal` | Emitted once at the end, with 0 if the update is ready (see `prepared`) or 1 if it failed, and the reason. Nothing is emitted if the person canceled. |
| `prepared` | `Prepared or None` | The checked update, once it is ready. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> UpdatePreparer().prepared is None
True
```

**Constructor**

Make a preparer that has not started.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QObject or None, default None` | The object that owns it. |

## UpdatePreparer.start

<div class="api-signature" markdown="1">

```python
def start(
    *,
    release: Release,
    target: Target,
    work: Path,
    keys: tuple[str, ...],
) -> None
```

{% endraw %}{% include api-source.html name="UpdatePreparer.start" line=144 %}{% raw %}

</div>

Start downloading and checking.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `release` | `Release` | The release to install. |
| `target` | `Target` | The copy that will be replaced. |
| `work` | `Path` | An empty folder to work in. |
| `keys` | `tuple of str` | The public keys (base64) a signature may be made with. |

## UpdatePreparer.cancel

<div class="api-signature" markdown="1">

```python
def cancel() -> None
```

{% endraw %}{% include api-source.html name="UpdatePreparer.cancel" line=180 %}{% raw %}

</div>

Stop, at the next chance, and say nothing more.

## UpdatePreparer.is_canceled

<div class="api-signature" markdown="1">

```python
def is_canceled() -> bool
```

{% endraw %}{% include api-source.html name="UpdatePreparer.is_canceled" line=184 %}{% raw %}

</div>

Say whether the person has canceled.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True once `cancel` has been called. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> UpdatePreparer().is_canceled()
False
```
{% endraw %}
