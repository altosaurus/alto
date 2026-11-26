---
title: profile_reviews
parent: alto.anki_export
api_module: alto.anki_export
package: alto
permalink: /api/alto.anki_export/function-profile_reviews/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def profile_reviews(learner: Learner) -> dict[str, list[Review]]
```

{% endraw %}{% include api-source.html name="profile_reviews" line=75 %}{% raw %}

</div>

Read this profile's graded calendar cards in due order.

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to list of Review` | Scheduled questions grouped by exercise class name. |
{% endraw %}
