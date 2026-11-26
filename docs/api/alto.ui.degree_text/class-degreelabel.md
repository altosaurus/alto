---
title: DegreeLabel
parent: alto.ui.degree_text
api_module: alto.ui.degree_text
package: alto.ui
permalink: /api/alto.ui.degree_text/class-degreelabel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class DegreeLabel(QLabel)
```

{% endraw %}{% include api-source.html name="DegreeLabel" line=270 %}{% raw %}

</div>

A plain-text label with explicitly positioned scale-degree carets.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> DegreeLabel("Note to place: 2̂ / 4").text()
'Note to place: 2̂ / 4'
```

## DegreeLabel.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="DegreeLabel.paintEvent" line=280 %}{% raw %}

</div>

Paint degree labels with carets centered above their numbers.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QPaintEvent` | The paint request. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> DegreeLabel("2̂").grab().isNull()
False
```
{% endraw %}
