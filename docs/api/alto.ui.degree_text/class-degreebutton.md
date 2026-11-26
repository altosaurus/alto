---
title: DegreeButton
parent: alto.ui.degree_text
api_module: alto.ui.degree_text
package: alto.ui
permalink: /api/alto.ui.degree_text/class-degreebutton/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class DegreeButton(QPushButton)
```

{% endraw %}{% include api-source.html name="DegreeButton" line=182 %}{% raw %}

</div>

An answer button that draws scale-degree carets directly above the
digits.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> DegreeButton("2̂").text()
'2̂'
```

## DegreeButton.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="DegreeButton.paintEvent" line=193 %}{% raw %}

</div>

Keep the native button appearance and position degree accents
explicitly.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QPaintEvent` | The paint request. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> DegreeButton("2̂").grab().isNull()
False
```
{% endraw %}
