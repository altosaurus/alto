---
title: alto.ui.score_excerpt
parent: api
package: alto.ui
permalink: /api/alto.ui.score_excerpt/
---
{% raw %}
Paint the engraved score and locate symbols from a pixel map made from
the same SVG.

## ScoreExcerpt

```python
ScoreExcerpt(excerpt: Excerpt)
```

The score artwork and its per-pixel index into the excerpt's target
list.

**Constructor**

Read the SVG and its aligned 16-bit hit map.

### ScoreExcerpt.music_rect

```python
def music_rect(paper: QRectF) -> QRectF
```

Fit the music inside its paper, leaving one line for the source
credit.

**Returns**

- *QRectF*: Destination rectangle shared by display and pointer hit testing.

### ScoreExcerpt.component_at

```python
def component_at(
    point: QPoint,
    *,
    rect: QRectF,
) -> tuple[str, int] | None
```

Look up the visible ink under a point in the scaled engraving.

**Returns**

- *tuple or None*: Term and marker index, or None on blank paper.

### ScoreExcerpt.paint

```python
def paint(
    painter: QPainter,
    *,
    paper: QRectF,
    index: int | None,
    color: QColor,
) -> None
```

Draw the excerpt and its attribution at the current paper size.

## score_artwork

```python
@lru_cache(maxsize=4)
def score_artwork(excerpt: Excerpt) -> ScoreExcerpt
```

Load the music and hit map once per recently viewed passage.

**Returns**

- *ScoreExcerpt*: The passage artwork.
{% endraw %}
