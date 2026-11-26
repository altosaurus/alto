---
title: save_bool
parent: alto.ui.store
api_module: alto.ui.store
package: alto.ui
permalink: /api/alto.ui.store/function-save_bool/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def save_bool(
    settings: QSettings,
    *,
    key: str,
    value: bool,
) -> None
```

{% endraw %}{% include api-source.html name="save_bool" line=234 %}{% raw %}

</div>

Save a switch as the text "true" or "false", the form `bool_value`
reads.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `settings` | `QSettings` | The settings to write. |
| `key` | `str` | The setting's name. Keyword-only. |
| `value` | `bool` | The switch. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> save_bool(
...     settings_, key="demo/on", value=False
... )
>>> settings_.value("demo/on")
'false'
>>> settings_.remove("demo")
```
{% endraw %}
