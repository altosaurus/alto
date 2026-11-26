---
title: ReferencePanel
parent: alto.ui.reference
api_module: alto.ui.reference
package: alto.ui
permalink: /api/alto.ui.reference/class-referencepanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ReferencePanel(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="ReferencePanel" line=512 %}{% raw %}

</div>

Bases: `QWidget`

The reference for the circle of fifths: a short description, the
circle to explore, and what the picked key means.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `circle` | `ExplorableCircle` | The circle to pick a key on. |
| `explanation` | `QLabel` | The text under the circle, which follows the pick. |
| `lesson_button` | `QPushButton` | Opens the lesson on the circle of fifths. |
| `lesson_requested` | `Signal` | Emitted with the key of the lesson to open when that button is pressed. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = ReferencePanel()
>>> panel.circle.select("outer", place=1)
>>> "<b>G major</b>" in panel.explanation.text()
True
```

**Constructor**

Build the panel with nothing picked.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = ReferencePanel()
>>> panel.explanation.text() == ""
False
```
{% endraw %}
