---
title: choices_value
parent: alto.ui.store
api_module: alto.ui.store
package: alto.ui
permalink: /api/alto.ui.store/function-choices_value/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def choices_value(
    settings: QSettings,
    *,
    key: str,
    allowed: Iterable[str],
    separator: str = ',',
) -> set[str]
```

{% endraw %}{% include api-source.html name="choices_value" line=325 %}{% raw %}

</div>

Read a saved set of choices, keeping only the ones that are still
offered.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `settings` | `QSettings` | The settings to read. |
| `key` | `str` | The setting's name. Keyword-only. |
| `allowed` | `iterable of str` | The choices that exist now. Keyword-only. |
| `separator` | `str, default ","` | What separates the choices in the saved text. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `set of str` | The saved choices that are allowed; empty if nothing is saved or none of them exists any more. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_ = store()
>>> settings_.setValue(
...     "demo/clefs", "treble,gone,bass"
... )
>>> sorted(
...     choices_value(
...         settings_,
...         key="demo/clefs",
...         allowed=("treble", "bass", "alto"),
...     )
... )
['bass', 'treble']
>>> settings_.remove("demo")
```
{% endraw %}
