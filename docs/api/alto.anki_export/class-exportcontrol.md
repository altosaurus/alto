---
title: ExportControl
parent: alto.anki_export
api_module: alto.anki_export
package: alto
permalink: /api/alto.anki_export/class-exportcontrol/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ExportControl()
```

{% endraw %}{% include api-source.html name="ExportControl" line=311 %}{% raw %}

</div>

Coordinate a cancellation decision with the final replacement of the
destination.

**Constructor**

Start with a pending export and an untouched destination.

## ExportControl.confirm_cancel

<div class="api-signature" markdown="1">

```python
def confirm_cancel(confirm: Callable[[], bool]) -> bool
```

{% endraw %}{% include api-source.html name="ExportControl.confirm_cancel" line=323 %}{% raw %}

</div>

Reserve the destination until the user decides whether to
cancel.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if cancellation was confirmed before the package was saved. |

## ExportControl.check

<div class="api-signature" markdown="1">

```python
def check() -> None
```

{% endraw %}{% include api-source.html name="ExportControl.check" line=340 %}{% raw %}

</div>

Stop work and unwind temporary files after confirmed
cancellation.

**Raises**

- *CancelledError*: When the user has confirmed cancellation.

## ExportControl.publish

<div class="api-signature" markdown="1">

```python
def publish(
    package: Path,
    *,
    destination: Path,
) -> None
```

{% endraw %}{% include api-source.html name="ExportControl.publish" line=353 %}{% raw %}

</div>

Replace the destination only while cancellation is excluded.
{% endraw %}
