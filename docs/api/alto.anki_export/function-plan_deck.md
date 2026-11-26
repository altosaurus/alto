---
title: plan_deck
parent: alto.anki_export
api_module: alto.anki_export
package: alto
permalink: /api/alto.anki_export/function-plan_deck/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def plan_deck(selection: DeckSelection) -> PlannedDeck
```

{% endraw %}{% include api-source.html name="plan_deck" line=242 %}{% raw %}

</div>

Select the exact cards to count in the summary and write to the
package.

**Returns**

| Type | Description |
| --- | --- |
| `PlannedDeck` | Eligible cards in export order, with reviewed cards first. |
{% endraw %}
