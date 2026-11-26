---
title: ExporterSession
parent: alto.ui.anki_exporter
api_module: alto.ui.anki_exporter
package: alto.ui
permalink: /api/alto.ui.anki_exporter/class-exportersession/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ExporterSession()
```

{% endraw %}{% include api-source.html name="ExporterSession" line=1168 %}{% raw %}

</div>

Manage a modeless Qt window with its own exercise settings and Qt
settings store.

**Constructor**

Start with no exporter open.

## ExporterSession.open

<div class="api-signature" markdown="1">

```python
def open(
    learner: Learner | None,
    *,
    selected: str,
) -> None
```

{% endraw %}{% include api-source.html name="ExporterSession.open" line=1179 %}{% raw %}

</div>

Raise the existing exporter or spawn a window for the active
profile.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `learner` | `Learner or None` | Active profile whose review dates and practice limits are available. |
| `selected` | `str` | Class name of the exercise to select when opening. |

**Raises**

- *OSError*: If the system cannot start the exporter.

## ExporterSession.sync_theme

<div class="api-signature" markdown="1">

```python
def sync_theme(key: str) -> None
```

{% endraw %}{% include api-source.html name="ExporterSession.sync_theme" line=1252 %}{% raw %}

</div>

Forward the selected palette and any custom colors to an open
exporter.

## ExporterSession.close

<div class="api-signature" markdown="1">

```python
def close() -> None
```

{% endraw %}{% include api-source.html name="ExporterSession.close" line=1269 %}{% raw %}

</div>

Close the command pipe so the exporter can finish its current
write and exit normally.
{% endraw %}
