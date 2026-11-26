---
title: ScaleIdentificationSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-scaleidentificationsettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ScaleIdentificationSettings(
    *,
    question_type: str = 'combined',
    button_mode: str = 'limited',
    button_count: int = 6,
    minor_keys: set[int] | None = None,
    motion: str = 'ascending',
    staff_keys: set[int] = field(default_factory=lambda: {0}),
)
```

{% endraw %}{% include api-source.html name="ScaleIdentificationSettings" line=1530 %}{% raw %}

</div>

Bases: `KeySignatureSettings`

Choose the clefs, scale types and independent staff and scale key
signatures for identification.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `staff_keys` | `set of int` | Signatures drawn on the staff, independently of the scale's own signature. Keyword-only. |
| `motion` | `str, default "ascending"` | Direction of the scale, "ascending" or "descending". Keyword-only. |
| `button_mode` | `str, default "limited"` | Show a limited set of complete answers or separate tonic and mode buttons in "all" mode. Keyword-only. |
| `button_count` | `int, default 6` | Maximum number of answer buttons in limited mode. Keyword-only. |
| `question_type` | `str, default "combined"` | Ask for the mode, the tonic (key), or both. Keyword-only. |
| `minor_keys` | `set of int or None` | Signatures for natural minor. None uses the shared key selection. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = ScaleIdentificationSettings(
...     keys={2}, staff_keys={-3}
... )
>>> cfg.active_keys(), cfg.active_staff_keys()
([2], [-3])
```

## ScaleIdentificationSettings.active_staff_keys

<div class="api-signature" markdown="1">

```python
def active_staff_keys() -> list[int]
```

{% endraw %}{% include api-source.html name="ScaleIdentificationSettings.active_staff_keys" line=1575 %}{% raw %}

</div>

Return the selected staff signatures, falling back to no
signature.

**Returns**

| Type | Description |
| --- | --- |
| `list of int` | Signature counts in ascending order. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleIdentificationSettings(
...     staff_keys=set()
... ).active_staff_keys()
[0]
```
{% endraw %}
