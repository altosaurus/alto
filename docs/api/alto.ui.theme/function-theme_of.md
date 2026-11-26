---
title: theme_of
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/function-theme_of/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def theme_of(
    colors: dict[str, str],
    *,
    dark: bool,
    key: str = '',
    family: str = '',
    label: str = '',
    note: str = '',
) -> CustomTheme
```

{% endraw %}{% include api-source.html name="theme_of" line=728 %}{% raw %}

</div>

Build a custom theme from its saved or preview colors.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `colors` | `dict of str to str` | A color for every part, as "#rrggbb". |
| `dark` | `bool` | True if it is the dark version. Keyword-only. |
| `key` | `str` | Saved theme identifier, or empty for a preview. |
| `family` | `str` | Identifier shared by the light and dark versions. |
| `label` | `str` | Name displayed in settings. |
| `note` | `str` | Description displayed with the theme. |

**Returns**

| Type | Description |
| --- | --- |
| `CustomTheme` | The theme with the supplied colors and identifiers. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> theme_of(
...     {part: "#102030" for part in PARTS},
...     dark=True,
... ).window
'#102030'
```
{% endraw %}
