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

```python
def card_fields(
    question: Question,
    *,
    folder: Path,
    exercise: Exercise,
) -> list[str]
```

Render an exercise as a reveal-and-grade card.

**Returns**

- *list of str*: The prompt, illustrations, answer, and explanation fields as HTML.

## AnkiExporter

```python
AnkiExporter(
    learner: Learner | None,
    *,
    reviews: dict[str, list[Review]],
    selected: str = '',
    parent: QWidget | None = None,
)
```

Bases: `QDialog`

Select exercise decks, preview cards, and export an Anki package.

**Constructor**

Build the deck navigation, card preview, and private exercise
settings.

### AnkiExporter.changeEvent

```python
def changeEvent(event: QEvent) -> None
```

Refresh palette-dependent artwork when Qt applies a new theme.

### AnkiExporter.reject

```python
def reject() -> None
```

Keep the export process alive until the destination dialog can
close.

## ExporterSession

```python
ExporterSession()
```

Manage a modeless Qt window with its own exercise settings and Qt
settings store.

**Constructor**

Start with no exporter open.

### ExporterSession.open

```python
def open(
    learner: Learner | None,
    *,
    selected: str,
) -> None
```

Raise the existing exporter or spawn a window for the active
profile.

**Parameters**

- `learner` (*Learner or None*): Active profile whose review dates and practice limits are available.
- `selected` (*str*): Class name of the exercise to select when opening.

**Raises**

- *OSError*: If the system cannot start the exporter.

### ExporterSession.sync_theme

```python
def sync_theme(key: str) -> None
```

Forward the selected palette and any custom colors to an open
exporter.

### ExporterSession.close

```python
def close() -> None
```

Close the command pipe so the exporter can finish its current
write and exit normally.
{% endraw %}
