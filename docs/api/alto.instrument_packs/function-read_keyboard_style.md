---
title: read_keyboard_style
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/function-read_keyboard_style/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def read_keyboard_style(
    value: object,
    *,
    where: str,
) -> PackKeyboardStyle | None
```

{% endraw %}{% include api-source.html name="read_keyboard_style" line=219 %}{% raw %}

</div>

Validate the optional look of an instrument's keyboards.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `value` | `object` | The instrument's ``keyboard_style`` entry, an object, or None. |
| `where` | `str` | The instrument's qualified key, used in messages. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `PackKeyboardStyle or None` | The style, or None to draw the keyboards in the learner's own keyboard style. |

**Raises**

- *ValueError*: If a field is unknown, or a color or number is invalid.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_keyboard_style(
...     None, where="pack.v.va"
... ) is None
True
>>> # noinspection PyUnresolvedReferences
>>> read_keyboard_style(
...     {
...         "cap": "#eee3c8",
...         "white": ["#2a211c", "#120d0a"],
...     },
...     where="pack.v.va",
... ).colors[1]
('white', ('#2a211c', '#120d0a'))
```
{% endraw %}
