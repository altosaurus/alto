---
title: text_value
parent: alto.ui.store
api_module: alto.ui.store
package: alto.ui
permalink: /api/alto.ui.store/function-text_value/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def text_value(
    settings: QSettings,
    *,
    key: str,
    default: str,
) -> str
```

{% endraw %}{% include api-source.html name="text_value" line=134 %}{% raw %}

</div>

Read a saved setting as text.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `settings` | `QSettings` | The settings to read. |
| `key` | `str` | The setting's name. Keyword-only. |
| `default` | `str` | What to return if nothing is saved. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The saved text, or `default` if there is none (or it is not text). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> settings_.setValue("demo/name", "viola")
>>> text_value(
...     settings_,
...     key="demo/name",
...     default="piano",
... )
'viola'
>>> text_value(
...     settings_,
...     key="demo/missing",
...     default="piano",
... )
'piano'
>>> settings_.remove("demo")
```
{% endraw %}
