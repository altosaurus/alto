---
title: KeyboardSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-keyboardsettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyboardSettings(
    black_keys: bool = True,
    *,
    naming: str = 'letters',
    require_octave: bool = False,
    low: int = KEYBOARD_DEFAULT[0],
    high: int = KEYBOARD_DEFAULT[1],
    key_signature: bool = False,
    keys: set[int] = field(default_factory=lambda: {-3, -2, -1, 0, 1, 2, 3}),
)
```

{% endraw %}{% include api-source.html name="KeyboardSettings" line=884 %}{% raw %}

</div>

Bases: `KeyChoice`

The settings of the keyboard identification exercise.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `naming` | `str, default "letters"` | Naming system for the highlighted key. Keyword-only. |
| `black_keys` | `bool, default True` | Also ask the black keys, answered by either enharmonic name. |
| `require_octave` | `bool, default False` | The answer must include the octave number as well. Keyword-only. |
| `low` | `int` | The lowest key asked, as a MIDI number. Keyword-only. |
| `high` | `int` | The highest key asked, as a MIDI number, inclusive. Keyword-only. |
| `key_signature` | `bool, default False` | Show a key signature, and require the name that fits it (no enharmonic spelling). Keyword-only. |
| `keys` | `set of int` | The key signatures to draw from, as sharps (positive) or flats (negative). Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = KeyboardSettings()
>>> key_name(cfg.low), key_name(cfg.high)
('C3', 'C5')
```
{% endraw %}
