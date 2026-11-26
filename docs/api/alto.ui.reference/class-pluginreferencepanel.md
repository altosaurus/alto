---
title: PluginReferencePanel
parent: alto.ui.reference
api_module: alto.ui.reference
package: alto.ui
permalink: /api/alto.ui.reference/class-pluginreferencepanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PluginReferencePanel(
    exercise: Exercise,
    *,
    lessons: list[Lesson],
)
```

{% endraw %}{% include api-source.html name="PluginReferencePanel" line=947 %}{% raw %}

</div>

Bases: `QWidget`

What a plugin's exercise offers to look up: what it asks, and a
button for each lesson that teaches it.

**Constructor**

Show the exercise's description and a button for each lesson
that goes with it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `exercise` | `Exercise` | The plugin's exercise whose reference was opened. |
| `lessons` | `list of Lesson` | At least one lesson that names the exercise as practice, or that the exercise names. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> demo = Lesson(
...     key="pack.d.l",
...     title="Parts",
...     about="",
...     summary="",
...     category="D",
...     steps=(),
...     exercise="x",
... )
>>> PluginReferencePanel(
...     NoteNames(), lessons=[demo]
... ).lesson_buttons[0].text()
'New to this? Take the lesson: Parts  →'
```
{% endraw %}
