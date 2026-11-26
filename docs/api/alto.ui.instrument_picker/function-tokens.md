---
title: tokens
parent: alto.ui.instrument_picker
api_module: alto.ui.instrument_picker
package: alto.ui
permalink: /api/alto.ui.instrument_picker/function-tokens/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def tokens(widget: QWidget) -> dict[str, str]
```

{% endraw %}{% include api-source.html name="tokens" line=139 %}{% raw %}

</div>

Return the summary page's colors.

All are mixed from the system palette so they follow its light or
dark theme.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `widget` | `QWidget` | The widget whose palette to use. |

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to str` | Color name to '#rrggbb': accent, accent_soft, muted, line, panel and well, and for each of good, warn and bad a text color and a soft background (such as good and good_soft). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> colors = tokens(QWidget())
>>> sorted(colors)[:3]
['accent', 'accent_soft', 'bad']
>>> colors["panel"].startswith("#")
True
```
{% endraw %}
