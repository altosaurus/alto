---
title: MeterButton
parent: alto.ui.meter_staff
api_module: alto.ui.meter_staff
package: alto.ui
permalink: /api/alto.ui.meter_staff/class-meterbutton/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
MeterButton(
    text: str,
    *,
    meter: tuple[int, int],
)
```

{% endraw %}{% include api-source.html name="MeterButton" line=110 %}{% raw %}

</div>

Bases: `QPushButton`

Draw a stacked time signature in a standard answer button.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MeterButton("12/8", meter=(12, 8)).accessibleName()
'12/8'
```

**Constructor**

Keep the plain signature as the text and accessible name.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | The time signature written with a slash. |
| `meter` | `tuple of int` | The numerator and denominator to engrave. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MeterButton("3/4", meter=(3, 4)).text()
'3/4'
```

## MeterButton.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="MeterButton.paintEvent" line=140 %}{% raw %}

</div>

Draw the styled button chrome and engrave its label.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QPaintEvent` | The paint request. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MeterButton("6/8", meter=(6, 8)).grab().isNull()
False
```
{% endraw %}
