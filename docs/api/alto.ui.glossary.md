---
title: alto.ui.glossary
parent: api
package: alto.ui
permalink: /api/alto.ui.glossary/
---
{% raw %}
A searchable glossary of the notation terms used in Alto.

## GlossaryPage

<div class="api-signature" markdown="1">

```python
GlossaryPage()
```

{% endraw %}{% include api-source.html name="GlossaryPage" line=1356 %}{% raw %}

</div>

Bases: `QWidget`

Display definitions and links beside a searchable term list.

**Constructor**

Build the glossary and select its first term.

### GlossaryPage.hideEvent

<div class="api-signature" markdown="1">

```python
def hideEvent(event: QHideEvent) -> None
```

{% endraw %}{% include api-source.html name="GlossaryPage.hideEvent" line=1743 %}{% raw %}

</div>

End the example when leaving the glossary.

**Parameters**

- `event` (*QHideEvent*): The notification that the glossary has been hidden.
{% endraw %}
