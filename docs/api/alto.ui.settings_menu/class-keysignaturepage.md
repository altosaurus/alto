---
title: KeySignaturePage
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/class-keysignaturepage/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
KeySignaturePage(
    enabled: bool,
    *,
    selected: set[int],
    allow_empty: bool = False,
    key_names: dict[int, str] | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="KeySignaturePage" line=2522 %}{% raw %}

</div>

Bases: `QWidget`

The key signature sub-page: a switch for using key signatures at
all, and the keys to draw from.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `changed` | `Signal` | Emitted after the switch or a key is changed. |
| `switch_row` | `ToggleRow` | The "Use key signatures" switch. |
| `checklist` | `KeyChecklist` | The keys; only enabled while the switch is on. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = KeySignaturePage(
...     True, selected={0, 1}
... )
>>> page.enabled(), page.selected() == {0, 1}
(True, True)
```

**Constructor**

Build the page.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `enabled` | `bool` | Whether key signatures are on. |
| `selected` | `set of int` | The key signatures to check initially. Keyword-only. |
| `allow_empty` | `bool, default False` | Allow every key to be unchecked. Keyword-only. |
| `key_names` | `dict of int to str or None, default None` | Key names to display beside the signature diagrams. With None, show only diagrams. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns it. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = KeySignaturePage(False, selected={0})
>>> page.checklist.isEnabled()
False
```

## KeySignaturePage.enabled

<div class="api-signature" markdown="1">

```python
def enabled() -> bool
```

{% endraw %}{% include api-source.html name="KeySignaturePage.enabled" line=2600 %}{% raw %}

</div>

Report whether key signatures are switched on.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True if the switch is on. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignaturePage(
...     True, selected={0}
... ).enabled()
True
```

## KeySignaturePage.selected

<div class="api-signature" markdown="1">

```python
def selected() -> set[int]
```

{% endraw %}{% include api-source.html name="KeySignaturePage.selected" line=2618 %}{% raw %}

</div>

Return the checked key signatures.

**Returns**

| Type | Description |
| --- | --- |
| `set of int` | Sharps if positive, flats if negative. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> KeySignaturePage(
...     True, selected={-2, 0}
... ).selected() == {-2, 0}
True
```
{% endraw %}
