---
title: Staff
parent: alto.lessons.base
api_module: alto.lessons.base
package: alto.lessons
permalink: /api/alto.lessons.base/class-staff/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Staff(
    clef: str,
    note: str = '',
    caption: str = '',
    key: int = 0,
)
```

{% endraw %}{% include api-source.html name="Staff" line=174 %}{% raw %}

</div>

A staff to show beside the words of a step: a clef, and perhaps a
note, with a line of words under it.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `clef` | `str` | The clef to draw, any of `alto.settings.CLEF_BASICS_CLEFS`. |
| `note` | `str` | A note to write on the staff, such as "C4"; empty for none. Only the seven clefs that have a lowest line for notes can have one, not the French violin and subbass clefs. |
| `caption` | `str` | The words under the staff. |
| `key` | `int` | Sharps (positive) or flats (negative) after the clef. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Staff(
...     clef="alto",
...     note="C4",
...     caption="Alto clef",
... ).note
'C4'
```
{% endraw %}
