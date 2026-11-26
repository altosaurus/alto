---
title: GlossaryPage
parent: alto.ui.glossary
api_module: alto.ui.glossary
package: alto.ui
permalink: /api/alto.ui.glossary/class-glossarypage/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
GlossaryPage()
```

{% endraw %}{% include api-source.html name="GlossaryPage" line=1381 %}{% raw %}

</div>

Bases: `QWidget`

Display definitions and links beside a searchable term list.

**Constructor**

Build the glossary and select its first term.

## GlossaryPage.hideEvent

<div class="api-signature" markdown="1">

```python
def hideEvent(event: QHideEvent) -> None
```

{% endraw %}{% include api-source.html name="GlossaryPage.hideEvent" line=1768 %}{% raw %}

</div>

End the example when leaving the glossary.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QHideEvent` | The notification that the glossary has been hidden. |
{% endraw %}
