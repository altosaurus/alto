---
title: score_artwork
parent: alto.ui.score_excerpt
api_module: alto.ui.score_excerpt
package: alto.ui
permalink: /api/alto.ui.score_excerpt/function-score_artwork/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
@lru_cache(maxsize=4)
def score_artwork(excerpt: Excerpt) -> ScoreExcerpt
```

{% endraw %}{% include api-source.html name="score_artwork" line=182 %}{% raw %}

</div>

Load the music and hit map once per recently viewed passage.

**Returns**

| Type | Description |
| --- | --- |
| `ScoreExcerpt` | The passage artwork. |
{% endraw %}
