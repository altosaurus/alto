---
title: KeySignatureSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-keysignaturesettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeySignatureSettings(
    *,
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    modes: set[str] = field(default_factory=lambda: {'Major (Ionian)', 'Natural minor (Aeolian)'}),
    keys: set[int] = field(default_factory=lambda: set(range(-7, 8))),
)
```

{% endraw %}{% include api-source.html name="KeySignatureSettings" line=1401 %}{% raw %}

</div>

Bases: `ClefChoice, KeyChoice`

The settings of the key signature identification exercise.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `clefs` | `set of str` | The clefs a signature is drawn on, any of `CLEFS`. Keyword-only. |
| `modes` | `set of str` | The scales to ask about, from `KEY_MODES`. Keyword-only. |
| `keys` | `set of int` | The key signatures asked, as sharps (positive) or flats (negative). Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = KeySignatureSettings()
>>> cfg.active_clefs(), len(cfg.active_keys())
(['treble', 'bass'], 15)
```

## KeySignatureSettings.active_modes

<div class="api-signature" markdown="1">

```python
def active_modes() -> list[str]
```

{% endraw %}{% include api-source.html name="KeySignatureSettings.active_modes" line=1433 %}{% raw %}

</div>

Return the scales to ask about, in the order of `KEY_MODES`.

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | The chosen modes, or major if none are chosen. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignatureSettings().active_modes()
['Major (Ionian)', 'Natural minor (Aeolian)']
```
{% endraw %}
