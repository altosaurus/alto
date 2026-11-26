---
title: KeyConstructionSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-keyconstructionsettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyConstructionSettings()
```

{% endraw %}{% include api-source.html name="KeyConstructionSettings" line=1502 %}{% raw %}

</div>

Bases: `KeySignatureSettings`

The settings of the key signature construction exercise: the same
choices as key signature identification.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `clefs` | `set of str` | The clefs the blank staff is drawn in, any of `CLEFS`. Keyword-only. |
| `modes` | `set of str` | The scales to ask for, from `KEY_MODES`. Keyword-only. |
| `keys` | `set of int` | The key signatures to build, as sharps (positive) or flats (negative). Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = KeyConstructionSettings(keys={-2})
>>> cfg.active_keys(), cfg.active_modes()
([-2], ['Major (Ionian)', 'Natural minor (Aeolian)'])
```
{% endraw %}
