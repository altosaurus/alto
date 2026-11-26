---
title: keyboard_key_staff
parent: alto.ui.staff
api_module: alto.ui.staff
package: alto.ui
permalink: /api/alto.ui.staff/function-keyboard_key_staff/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def keyboard_key_staff() -> StaffWidget
```

{% endraw %}{% include api-source.html name="keyboard_key_staff" line=2633 %}{% raw %}

</div>

Build the compact key signature shown above a keyboard question.

**Returns**

| Type | Description |
| --- | --- |
| `StaffWidget` | A fixed-width staff sized for the signature. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keyboard_key_staff().width() == px(210)
True
```
{% endraw %}
