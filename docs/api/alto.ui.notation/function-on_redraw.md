---
title: on_redraw
parent: alto.ui.notation
api_module: alto.ui.notation
package: alto.ui
permalink: /api/alto.ui.notation/function-on_redraw/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def on_redraw(hook: Callable[[], None]) -> None
```

{% endraw %}{% include api-source.html name="on_redraw" line=299 %}{% raw %}

</div>

Register a function to call whenever the notation style changes.

The staff widgets live in a module that imports this one, so they
register themselves here instead of being found by
this module.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `hook` | `Callable` | A function with no arguments that repaints what depends on the style. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> calls = []
>>> def repaint() -> None:
...     calls.append(1)
>>> on_redraw(repaint)
>>> _redraw()
>>> calls
[1]
>>> _redraw_hooks.remove(repaint)
```
{% endraw %}
