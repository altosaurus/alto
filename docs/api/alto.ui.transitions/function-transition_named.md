---
title: transition_named
parent: alto.ui.transitions
api_module: alto.ui.transitions
package: alto.ui
permalink: /api/alto.ui.transitions/function-transition_named/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def transition_named(key: str) -> Transition
```

{% endraw %}{% include api-source.html name="transition_named" line=1487 %}{% raw %}

</div>

Find a transition by its key.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The key. |

**Returns**

| Type | Description |
| --- | --- |
| `Transition` | The transition, or the default one if there is none with that key. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     transition_named("flip").label,
...     transition_named("nonsense").key,
... )
('Flip', 'cascade')
```
{% endraw %}
