---
title: CustomTheme
parent: alto.ui.theme
api_module: alto.ui.theme
package: alto.ui
permalink: /api/alto.ui.theme/class-customtheme/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
CustomTheme(
    key: str,
    family: str,
    label: str,
    note: str,
    dark: bool,
    window: str,
    panel: str,
    ink: str,
    muted: str,
    line: str,
    accent: str,
    track: str,
)
```

{% endraw %}{% include api-source.html name="CustomTheme" line=40 %}{% raw %}

</div>

A theme with colors of its own.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `key` | `str` | What it is saved as. |
| `family` | `str` | The key of the light version of the theme, which its dark version shares. |
| `label` | `str` | What the settings call it. |
| `note` | `str` | A short line about it, shown under its picture. |
| `dark` | `bool` | True if it is a dark theme, so that Qt draws its own parts (such as the title bar) to match. |
| `window` | `str` | The color of the window. |
| `panel` | `str` | The color of lists, boxes and buttons. |
| `ink` | `str` | The color of text. |
| `muted` | `str` | The color of quiet text. |
| `line` | `str` | The color of outlines. |
| `accent` | `str` | The color of what is chosen, and of links. |
| `track` | `str` | The color of the track behind a switch or a slider, a little off the window's own. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     CUSTOM_THEMES[0].key,
...     CUSTOM_THEMES[0].dark,
...     len(CUSTOM_THEMES),
... )
('studio', False, 50)
```
{% endraw %}
