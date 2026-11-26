---
title: AnkiExporter
parent: alto.ui.anki_exporter
api_module: alto.ui.anki_exporter
package: alto.ui
permalink: /api/alto.ui.anki_exporter/class-ankiexporter/
---
{% raw %}
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

{% endraw %}{% include api-source.html name="AnkiExporter" line=830 %}{% raw %}

</div>

Bases: `QDialog`

Select exercise decks, preview cards, and export an Anki package.

**Constructor**

Build the deck navigation, card preview, and private exercise
settings.

## AnkiExporter.changeEvent

<div class="api-signature" markdown="1">

```python
def changeEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="AnkiExporter.changeEvent" line=1006 %}{% raw %}

</div>

Refresh palette-dependent artwork when Qt applies a new theme.

## AnkiExporter.reject

<div class="api-signature" markdown="1">

```python
def reject() -> None
```

{% endraw %}{% include api-source.html name="AnkiExporter.reject" line=1156 %}{% raw %}

</div>

Keep the export process alive until the destination dialog can
close.
{% endraw %}
