---
title: ClefReferencePanel
parent: alto.ui.reference
api_module: alto.ui.reference
package: alto.ui
permalink: /api/alto.ui.reference/class-clefreferencepanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ClefReferencePanel(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="ClefReferencePanel" line=636 %}{% raw %}

</div>

Bases: `QWidget`

The reference for the clefs: how they are made, and a picture of
each with where its symbol goes.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `lesson_button` | `QPushButton` | Opens the lesson on the clefs. |
| `lesson_requested` | `Signal` | Emitted with the key of the lesson to open when that button is pressed. |
| `rows` | `dict of str to QLabel` | The words beside the picture of each clef, by clef. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = ClefReferencePanel()
>>> "C clef" in panel.rows[
...     "mezzo"
... ].text() and "bottom line" in panel.rows[
...     "french"
... ].text()
True
```

**Constructor**

Build the panel: the lesson button, a line of explanation and a
row for each clef.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(ClefReferencePanel().rows) == len(
...     settings.CLEF_BASICS_CLEFS
... )
True
```
{% endraw %}
