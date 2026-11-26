---
title: DegreeCheckBox
parent: alto.ui.degree_text
api_module: alto.ui.degree_text
package: alto.ui
permalink: /api/alto.ui.degree_text/class-degreecheckbox/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class DegreeCheckBox(QCheckBox)
```

{% endraw %}{% include api-source.html name="DegreeCheckBox" line=230 %}{% raw %}

</div>

Draw the scale degree caret centered above the checkbox label's
digit.

## DegreeCheckBox.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="DegreeCheckBox.paintEvent" line=236 %}{% raw %}

</div>

Paint the native checkbox and use the shared scale degree
renderer for its label.
{% endraw %}
