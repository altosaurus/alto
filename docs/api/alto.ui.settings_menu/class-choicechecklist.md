---
title: ChoiceChecklist
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/class-choicechecklist/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ChoiceChecklist(
    groups: list[tuple[str, list[tuple[object, str]]]],
    *,
    selected: set,
    allow_empty: bool = False,
    positions: Mapping[object, tuple[int, int]] | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ChoiceChecklist" line=2721 %}{% raw %}

</div>

Bases: `QWidget`

Checkboxes for a list of choices, optionally under headings and
allowing an empty selection.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `changed` | `Signal` | Emitted after a box is checked or unchecked. |
| `allow_empty` | `bool` | Whether all choices may be unchecked. |
| `boxes` | `dict` | The checkbox of each choice, by its key. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> groups = [
...     (
...         "Triads",
...         [
...             ("major", "Major"),
...             ("minor", "Minor"),
...         ],
...     ),
...     ("", [("x", "Other")]),
... ]
>>> checklist = ChoiceChecklist(
...     groups, selected={"major"}
... )
>>> checklist.selected()
{'major'}
```

**Constructor**

Build the checklist.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `groups` | `list of tuple of (str, list of tuple of (object, str))` | The headings and, under each, the choices as (key, label); an empty heading shows none. |
| `selected` | `set` | The keys to check initially. Keyword-only. |
| `allow_empty` | `bool, default False` | Allow all choices to be unchecked. Keyword-only. |
| `positions` | `mapping or None, default None` | Optional (row, column) for each key within its group. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> checklist = ChoiceChecklist(
...     [("", [(0, "Root"), (1, "1st")])],
...     selected={0},
... )
>>> # noinspection PyTypeChecker
>>> sorted(checklist.boxes)
[0, 1]
```

## ChoiceChecklist.selected

<div class="api-signature" markdown="1">

```python
def selected() -> set
```

{% endraw %}{% include api-source.html name="ChoiceChecklist.selected" line=2828 %}{% raw %}

</div>

Return the checked choices.

**Returns**

| Type | Description |
| --- | --- |
| `set` | The keys of the checked boxes. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ChoiceChecklist(
...     [("", [(0, "Root"), (1, "1st")])],
...     selected={0, 1},
... ).selected()
{0, 1}
```
{% endraw %}
