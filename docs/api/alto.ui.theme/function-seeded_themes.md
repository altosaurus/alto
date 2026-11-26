---
title: seeded_themes
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-seeded_themes/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def seeded_themes(seed: tuple[str, str, str, float, float, float, float]) -> tuple[CustomTheme, CustomTheme]
```

{% endraw %}{% include api-source.html name="seeded_themes" line=264 %}{% raw %}

</div>

Make the light and the dark theme of a seed: neutrals tinted by one
hue, and an accent of another.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `seed` | `tuple` | The key, name and note, then the neutral hue and saturation and the accent hue and saturation. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (CustomTheme, CustomTheme)` | The light theme and the dark theme. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> pale, deep = seeded_themes(SEEDS[0])
>>> pale.key, deep.key, pale.dark, deep.dark
('parchment', 'parchment_dark', False, True)
```
{% endraw %}
