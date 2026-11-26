---
title: KeyChecklist
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/class-keychecklist/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeyChecklist(
    selected: set[int],
    *,
    allow_empty: bool = False,
    counts_only: bool = False,
    key_names: dict[int, str] | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeyChecklist" line=2344 %}{% raw %}

</div>

Bases: `QWidget`

Checkboxes for the 15 major keys, flats on the left and sharps on
the right.

At least one stays checked. Each is labeled with a picture of its
signature.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `changed` | `Signal` | Emitted after a box is checked or unchecked. |
| `boxes` | `dict of int to QCheckBox` | The checkbox of each key signature, from -7 (seven flats) to 7 (seven sharps). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyChecklist({0, 2}).selected() == {0, 2}
True
```

**Constructor**

Build the checklist.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `selected` | `set of int` | The key signatures to check initially. |
| `allow_empty` | `bool, default False` | Allow every key to be unchecked. Keyword-only. |
| `counts_only` | `bool, default False` | Label each box with its accidental count instead of drawing a signature. Keyword-only. |
| `key_names` | `dict of int to str or None, default None` | Key names to display beside the signature diagrams. With None, show only diagrams. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(KeyChecklist({0}).boxes)
15
```

## KeyChecklist.selected

<div class="api-signature" markdown="1">

```python
def selected() -> set[int]
```

{% endraw %}{% include api-source.html name="KeyChecklist.selected" line=2486 %}{% raw %}

</div>

Return the checked key signatures.

**Returns**

| Type | Description |
| --- | --- |
| `set of int` | Sharps if positive, flats if negative. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeyChecklist({-3, 1}).selected() == {-3, 1}
True
```
{% endraw %}
