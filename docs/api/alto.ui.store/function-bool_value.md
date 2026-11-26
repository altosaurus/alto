---
title: bool_value
parent: alto.ui.store
api_module: alto.ui.store
package: alto.ui
permalink: /api/alto.ui.store/function-bool_value/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def bool_value(
    settings: QSettings,
    *,
    key: str,
    default: bool,
) -> bool
```

{% endraw %}{% include api-source.html name="bool_value" line=180 %}{% raw %}

</div>

Read a switch saved as the text "true" or "false".

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `settings` | `QSettings` | The settings to read. |
| `key` | `str` | The setting's name. Keyword-only. |
| `default` | `bool` | What to return if nothing is saved, or if the saved text is neither "true" nor "false". Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | The saved switch. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> save_bool(
...     settings_, key="demo/on", value=True
... )
>>> (
...     bool_value(
...         settings_,
...         key="demo/on",
...         default=False,
...     ),
...     bool_value(
...         settings_,
...         key="demo/missing",
...         default=True,
...     ),
... )
(True, True)
>>> settings_.setValue("demo/on", "FALSE")
>>> bool_value(
...     settings_, key="demo/on", default=True
... )
False
>>> settings_.remove("demo")
```
{% endraw %}
