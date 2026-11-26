---
title: RangeEditor
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/class-rangeeditor/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
RangeEditor(
    key: str,
    *,
    low: int,
    high: int,
    limits: tuple[int, int] | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="RangeEditor" line=211 %}{% raw %}

</div>

Bases: `QWidget`

A staff showing the lowest and highest note asked for a clef.

Arrows on the left move the lower bound, arrows on the right move
the upper bound.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `edited` | `Signal` | Emitted with the clef key, the lowest note and the highest note (as staff steps) after a change. |
| `key` | `str` | The clef. |
| `low` | `int` | The lowest note asked, as a staff step (`Note.diatonic`). |
| `high` | `int` | The highest note asked. |
| `limits` | `tuple of (int, int)` | The furthest the bounds may go. |
| `staff` | `StaffWidget` | Shows the two notes. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> editor = RangeEditor(
...     "treble", low=28, high=34
... )
>>> editor.caption_text.text()
'<b>C4 – B4</b>'
```

**Constructor**

Build the editor for a clef's range.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The clef, a key of `RANGE_LIMITS`. |
| `low` | `int` | The lowest note asked, as a staff step. Keyword-only. |
| `high` | `int` | The highest note asked. Keyword-only. |
| `limits` | `tuple of (int, int) or None, default None` | The furthest the bounds may go, as staff steps; None for the clef's usual limits. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns the editor. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> RangeEditor(
...     "bass", low=14, high=28
... ).limits == settings.RANGE_LIMITS["bass"]
True
>>> RangeEditor(
...     "alto", low=21, high=30, limits=(21, 30)
... ).limits
(21, 30)
```
{% endraw %}
