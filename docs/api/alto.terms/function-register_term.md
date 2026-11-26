---
title: register_term
parent: alto.terms
api_module: alto.terms
package: alto
permalink: /api/alto.terms/function-register_term/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def register_term(entry: PluginTerm) -> None
```

{% endraw %}{% include api-source.html name="register_term" line=106 %}{% raw %}

</div>

Add a plugin's glossary entry.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `entry` | `PluginTerm` | The entry. |

**Raises**

- *ValueError*: If another plugin already supplies the same term.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> register_term(
...     PluginTerm(
...         name="bridge",
...         pack="Demo",
...         definition="It lifts the strings.",
...     )
... )
>>> register_term(
...     PluginTerm(
...         name="bridge",
...         pack="Other",
...         definition="Again.",
...     )
... )
Traceback (most recent call last):
...
ValueError: The term bridge is already supplied by Demo.
>>> _ = PLUGIN_TERMS.pop("bridge")
```
{% endraw %}
