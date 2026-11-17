---
title: alto.ui.glossary
parent: api
package: alto.ui
order: 34
permalink: /api/alto.ui.glossary/
---
{% raw %}
A searchable glossary of the notation terms used in Alto.

## GlossaryPage

```python
GlossaryPage()
```

Bases: `QWidget`

Display definitions and links beside a searchable term list.

**Constructor**

Build the glossary and select its first term.

### GlossaryPage.hideEvent

```python
def hideEvent(event: QHideEvent) -> None
```

End the example when leaving the glossary.

**Parameters**

- `event` (*QHideEvent*): The notification that the glossary has been hidden.
{% endraw %}
