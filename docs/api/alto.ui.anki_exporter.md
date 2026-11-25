---
title: alto.ui.anki_exporter
parent: api
package: alto.ui
permalink: /api/alto.ui.anki_exporter/
---
{% raw %}
Modeless Anki deck exporter using Alto's exercise controls and music
engraving.

## card_fields

<div class="api-signature" markdown="1">

```python
def card_fields(
    question: Question,
    *,
    folder: Path,
    exercise: Exercise,
) -> list[str]
```

{% endraw %}{% include api-source.html name="card_fields" line=130 %}{% raw %}

</div>

Render an exercise as a reveal-and-grade card.

**Returns**

- *list of str*: The prompt, illustrations, answer, and explanation fields as HTML.

## AnkiExporter

<div class="api-signature" markdown="1">

```python
AnkiExporter(
    learner: Learner | None,
    *,
    reviews: dict[str, list[Review]],
    selected: str = '',
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="AnkiExporter" line=796 %}{% raw %}

</div>

Bases: `QDialog`

Select exercise decks, preview cards, and export an Anki package.

**Constructor**

Build the deck navigation, card preview, and private exercise
settings.

### AnkiExporter.changeEvent

<div class="api-signature" markdown="1">

```python
def changeEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="AnkiExporter.changeEvent" line=972 %}{% raw %}

</div>

Refresh palette-dependent artwork when Qt applies a new theme.

### AnkiExporter.reject

<div class="api-signature" markdown="1">

```python
def reject() -> None
```

{% endraw %}{% include api-source.html name="AnkiExporter.reject" line=1122 %}{% raw %}

</div>

Keep the export process alive until the destination dialog can
close.

## ExporterSession

<div class="api-signature" markdown="1">

```python
ExporterSession()
```

{% endraw %}{% include api-source.html name="ExporterSession" line=1134 %}{% raw %}

</div>

Manage a modeless Qt window with its own exercise settings and Qt
settings store.

**Constructor**

Start with no exporter open.

### ExporterSession.open

<div class="api-signature" markdown="1">

```python
def open(
    learner: Learner | None,
    *,
    selected: str,
) -> None
```

{% endraw %}{% include api-source.html name="ExporterSession.open" line=1145 %}{% raw %}

</div>

Raise the existing exporter or spawn a window for the active
profile.

**Parameters**

- `learner` (*Learner or None*): Active profile whose review dates and practice limits are available.
- `selected` (*str*): Class name of the exercise to select when opening.

**Raises**

- *OSError*: If the system cannot start the exporter.

### ExporterSession.sync_theme

<div class="api-signature" markdown="1">

```python
def sync_theme(key: str) -> None
```

{% endraw %}{% include api-source.html name="ExporterSession.sync_theme" line=1218 %}{% raw %}

</div>

Forward the selected palette and any custom colors to an open
exporter.

### ExporterSession.close

<div class="api-signature" markdown="1">

```python
def close() -> None
```

{% endraw %}{% include api-source.html name="ExporterSession.close" line=1235 %}{% raw %}

</div>

Close the command pipe so the exporter can finish its current
write and exit normally.
{% endraw %}
