---
title: DailyReleaseCheck
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/class-dailyreleasecheck/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
DailyReleaseCheck(window: MainWindow)
```

{% endraw %}{% include api-source.html name="DailyReleaseCheck" line=628 %}{% raw %}

</div>

Bases: `QTimer`

Check for published releases in the background and honor the
learner’s reminder choice at the exercise grid.

**Examples**

```text
Reopening Alto on the same afternoon reuses the previous check time.
```

**Constructor**

Schedule the first check after the startup window has opened.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `window` | `MainWindow` | The window that owns the timer and presents upgrade offers. |

**Constructor examples**

```text
Source checkouts continue to use Git for updates.
```
{% endraw %}
