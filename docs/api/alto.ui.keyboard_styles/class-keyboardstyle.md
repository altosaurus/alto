---
title: KeyboardStyle
parent: alto.ui.keyboard_styles
api_module: alto.ui.keyboard_styles
package: alto.ui
permalink: /api/alto.ui.keyboard_styles/class-keyboardstyle/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyboardStyle(
    key: str,
    *,
    label: str,
    note: str,
    white: tuple[str, str],
    white_edge: str,
    black: tuple[str, str],
    black_edge: str,
    case: str | None = DEFAULT_CASE,
    felt: str | None = None,
    cap: str | None = None,
    narrow: float = 1.0,
    gap: float = 1.0,
    rail: float = 8.0,
    thick: bool = False,
    hue: bool = False,
    glow: bool = False,
    ink: bool = False,
    knobs: bool = False,
    reverse_below: int | None = None,
    dot: str | None = None,
    round: float = 7.0,
)
```

{% endraw %}{% include api-source.html name="KeyboardStyle" line=40 %}{% raw %}

</div>

How a keyboard looks: the colors of the keys and the case, and a few
details of the drawing.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `key` | `str` | The identifier saved in the settings. |
| `label` | `str` | The name shown in the interface. Keyword-only. |
| `note` | `str` | A few words on what it is modeled on. Keyword-only. |
| `white` | `tuple of (str, str)` | The natural keys' color at the top and at the bottom. Keyword-only. |
| `white_edge` | `str` | The outline color of the natural keys. Keyword-only. |
| `black` | `tuple of (str, str)` | The sharps' color at the top and at the bottom. Keyword-only. |
| `black_edge` | `str` | The outline color of the sharps. Keyword-only. |
| `case` | `str or None` | The body around the keys; None draws no body. Keyword-only. |
| `felt` | `str or None` | A strip of felt under the fallboard. Keyword-only. |
| `cap` | `str or None` | A bone cap on top of each sharp. Keyword-only. |
| `narrow` | `float, default 1.0` | How wide the sharps are, compared with a piano's. Keyword-only. |
| `gap` | `float, default 1.0` | Pixels between neighboring naturals. Keyword-only. |
| `rail` | `float, default 8.0` | The height of the strip above the keys. Keyword-only. |
| `thick` | `bool, default False` | Heavy outlines. Keyword-only. |
| `hue` | `bool, default False` | Color each key by its note name. Keyword-only. |
| `glow` | `bool, default False` | A soft halo around the outlines. Keyword-only. |
| `ink` | `bool, default False` | Hatched sharps, like an engraving. Keyword-only. |
| `knobs` | `bool, default False` | A row of organ stop knobs in the strip above the keys. Keyword-only. |
| `reverse_below` | `int or None` | Keys under this MIDI number swap colors (an organ's preset keys). Keyword-only. |
| `dot` | `str or None` | The color of a dot that marks every C. Keyword-only. |
| `round` | `float, default 7.0` | The most the lower corners of a natural are rounded, in pixels. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> style = BY_KEY["modern"]
>>> style.label, style.case
('Modern piano', '#0d0d0f')
```
{% endraw %}
