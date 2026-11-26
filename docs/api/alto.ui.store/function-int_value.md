---
title: int_value
parent: alto.ui.store
api_module: alto.ui.store
package: alto.ui
permalink: /api/alto.ui.store/function-int_value/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def int_value(
    settings: QSettings,
    *,
    key: str,
    default: int,
) -> int
```

{% endraw %}{% include api-source.html name="int_value" line=77 %}{% raw %}

</div>

Read an integer setting.

`QSettings` hands back whatever was saved, which may be a number or
its text.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `settings` | `QSettings` | The settings to read. |
| `key` | `str` | The setting's name. Keyword-only. |
| `default` | `int` | What to return if nothing is saved. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `int` | The saved value, or `default` if there is none (or it is not a number, text or similar). |

**Raises**

- *ValueError*: If the saved text is not a whole number.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> settings_.setValue("demo/count", "42")
>>> int_value(
...     settings_, key="demo/count", default=0
... )
42
>>> int_value(
...     settings_, key="demo/missing", default=7
... )
7
>>> settings_.setValue("demo/count", "many")
>>> int_value(
...     settings_, key="demo/count", default=0
... )
Traceback (most recent call last):
    ...
ValueError: invalid literal for int() with base 10: 'many'
>>> settings_.remove("demo")
```
{% endraw %}
