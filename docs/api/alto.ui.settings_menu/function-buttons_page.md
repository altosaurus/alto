---
title: buttons_page
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/function-buttons_page/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def buttons_page(
    cfg: ButtonSettings | settings.IntervalSettings | settings.ScaleIdentificationSettings,
    *,
    changed: Callable[[], None],
    back: Callable[[], None],
) -> QWidget
```

{% endraw %}{% include api-source.html name="buttons_page" line=2870 %}{% raw %}

</div>

Build the shared Limited and All answer-button submenu.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `ButtonSettings or IntervalSettings` | The exercise that owns the button mode and count. |
| `changed` | `callable` | Save and apply an edit. |
| `back` | `callable` | Return to the exercise settings menu. |

**Returns**

| Type | Description |
| --- | --- |
| `QWidget` | The Buttons page with the count picker below Limited. |

**Examples**

```text
Choosing All hides the count picker and retains its last value.
```
{% endraw %}
