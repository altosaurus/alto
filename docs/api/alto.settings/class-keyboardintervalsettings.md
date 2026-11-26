---
title: KeyboardIntervalSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-keyboardintervalsettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyboardIntervalSettings(
    low: int = KEYBOARD_DEFAULT[0],
    high: int = KEYBOARD_DEFAULT[1],
    intervals: set[int] = field(default_factory=lambda: set(range(1, 13))),
    all_interval_buttons: bool = False,
    compact_buttons: bool = False,
    button_count: int = 6,
)
```

{% endraw %}{% include api-source.html name="KeyboardIntervalSettings" line=1011 %}{% raw %}

</div>

The keyboard range and interval distances used for keyboard interval
identification.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `low` | `int` | The lowest key, as a MIDI number. Keyword-only. |
| `high` | `int` | The highest key, inclusive. Keyword-only. |
| `intervals` | `set of int` | Selected distances in half steps, up to the full piano span. Keyword-only. |
| `button_count` | `int, default 6` | Maximum answer buttons in limited mode. Keyword-only. |
| `compact_buttons` | `bool, default False` | Answer with separate quality-letter and interval-number buttons. Keyword-only. |
| `all_interval_buttons` | `bool, default False` | Show a fixed answer button for every selected interval instead of a limited number of choices. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardIntervalSettings().bounds()
(48, 72)
```

## KeyboardIntervalSettings.answer_button_limit

<div class="api-signature" markdown="1">

```python
def answer_button_limit() -> int
```

{% endraw %}{% include api-source.html name="KeyboardIntervalSettings.answer_button_limit" line=1048 %}{% raw %}

</div>

Return the requested count within the supported range of 1 to 87
buttons.

**Returns**

| Type | Description |
| --- | --- |
| `int` | The bounded maximum number of answer buttons in limited mode. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardIntervalSettings().answer_button_limit()
6
>>> KeyboardIntervalSettings(
...     button_count=0
... ).answer_button_limit()
1
```

## KeyboardIntervalSettings.bounds

<div class="api-signature" markdown="1">

```python
def bounds() -> tuple[int, int]
```

{% endraw %}{% include api-source.html name="KeyboardIntervalSettings.bounds" line=1070 %}{% raw %}

</div>

Return a piano range containing at least two distinct keys.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (int, int)` | Sorted bounds within the full piano range, widened by one key if necessary. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardIntervalSettings(
...     low=60, high=60
... ).bounds()
(60, 61)
```

## KeyboardIntervalSettings.active_intervals

<div class="api-signature" markdown="1">

```python
def active_intervals() -> list[int]
```

{% endraw %}{% include api-source.html name="KeyboardIntervalSettings.active_intervals" line=1098 %}{% raw %}

</div>

Return selected interval distances that fit the keyboard range.

**Returns**

| Type | Description |
| --- | --- |
| `list of int` | Sorted positive distances that fit; empty if none are selected. Invalid nonempty selections use a minor second. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyboardIntervalSettings(
...     low=60, high=64, intervals={3, 4, 12}
... ).active_intervals()
[3, 4]
>>> KeyboardIntervalSettings(
...     intervals=set()
... ).active_intervals()
[]
```
{% endraw %}
