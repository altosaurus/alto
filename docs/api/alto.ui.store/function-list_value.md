---
title: list_value
parent: alto.ui.store
api_module: alto.ui.store
package: alto.ui
permalink: /api/alto.ui.store/function-list_value/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def list_value(
    settings: QSettings,
    *,
    key: str,
    separator: str = ',',
) -> list[str]
```

{% endraw %}{% include api-source.html name="list_value" line=266 %}{% raw %}

</div>

Read a saved list of words, such as "treble,bass".

`QSettings` may hand back text that contains commas as a list of its
parts, so both forms are read.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `settings` | `QSettings` | The settings to read. |
| `key` | `str` | The setting's name. Keyword-only. |
| `separator` | `str, default ","` | What separates the words in the saved text. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | The words in their saved order, without empty ones; empty if nothing is saved. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> settings_.setValue(
...     "demo/clefs", "treble,,bass"
... )
>>> (
...     list_value(settings_, key="demo/clefs"),
...     list_value(
...         settings_, key="demo/missing"
...     ),
... )
(['treble', 'bass'], [])
>>> settings_.setValue(
...     "demo/modes", ["major|minor"]
... )
>>> list_value(
...     settings_,
...     key="demo/modes",
...     separator="|",
... )
['major', 'minor']
>>> settings_.remove("demo")
```
{% endraw %}
