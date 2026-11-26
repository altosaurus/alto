---
title: ScoreExcerpt
parent: alto.ui.score_excerpt
api_module: alto.ui.score_excerpt
package: alto.ui
permalink: /api/alto.ui.score_excerpt/class-scoreexcerpt/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ScoreExcerpt(excerpt: Excerpt)
```

{% endraw %}{% include api-source.html name="ScoreExcerpt" line=19 %}{% raw %}

</div>

The score artwork and its per-pixel index into the excerpt's target
list.

**Constructor**

Read the SVG and its aligned 16-bit hit map.

## ScoreExcerpt.music_rect

<div class="api-signature" markdown="1">

```python
def music_rect(paper: QRectF) -> QRectF
```

{% endraw %}{% include api-source.html name="ScoreExcerpt.music_rect" line=46 %}{% raw %}

</div>

Fit the music inside its paper, leaving one line for the source
credit.

**Returns**

| Type | Description |
| --- | --- |
| `QRectF` | Destination rectangle shared by display and pointer hit testing. |

## ScoreExcerpt.component_at

<div class="api-signature" markdown="1">

```python
def component_at(
    point: QPoint,
    *,
    rect: QRectF,
) -> tuple[str, int] | None
```

{% endraw %}{% include api-source.html name="ScoreExcerpt.component_at" line=64 %}{% raw %}

</div>

Look up the visible ink under a point in the scaled engraving.

**Returns**

| Type | Description |
| --- | --- |
| `tuple or None` | Term and marker index, or None on blank paper. |

## ScoreExcerpt.paint

<div class="api-signature" markdown="1">

```python
def paint(
    painter: QPainter,
    *,
    paper: QRectF,
    index: int | None,
    color: QColor,
) -> None
```

{% endraw %}{% include api-source.html name="ScoreExcerpt.paint" line=96 %}{% raw %}

</div>

Draw the excerpt and its attribution at the current paper size.
{% endraw %}
