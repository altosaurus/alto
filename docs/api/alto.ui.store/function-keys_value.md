---
title: keys_value
parent: alto.ui.store
api_module: alto.ui.store
package: alto.ui
permalink: /api/alto.ui.store/function-keys_value/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def keys_value(
    settings: QSettings,
    *,
    key: str,
) -> set[int]
```

{% endraw %}{% include api-source.html name="keys_value" line=377 %}{% raw %}

</div>

Read a saved set of key signatures, each a number of sharps
(positive) or flats (negative) up to seven.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `settings` | `QSettings` | The settings to read. |
| `key` | `str` | The setting's name. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `set of int` | The saved key signatures that exist; empty if nothing usable is saved. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> settings_.setValue(
...     "demo/keys", "-2,0,9,x,3"
... )
>>> sorted(
...     keys_value(settings_, key="demo/keys")
... )
[-2, 0, 3]
>>> settings_.remove("demo")
```
{% endraw %}
