---
title: clef_choice_page
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/function-clef_choice_page/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def clef_choice_page(
    choices: Iterable[str],
    *,
    selected: set[str],
    edited: Callable[[], object],
    back: Callable[[], object],
    title: str = 'Clefs',
    hint: str = 'One of the checked clefs is picked at random.',
) -> tuple[dict[str, QCheckBox], QWidget]
```

{% endraw %}{% include api-source.html name="clef_choice_page" line=775 %}{% raw %}

</div>

Build the "Clefs" page that every exercise with a choice of clefs
shares.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `choices` | `iterable of str` | The clefs to offer, from `settings.RANGE_KEYS`; "grand" is left out of exercises that cannot use the grand staff. |
| `selected` | `set of str` | The clefs that start checked. Keyword-only. |
| `edited` | `callable` | Called whenever a box is checked or unchecked. Keyword-only. |
| `back` | `callable` | Called when the Back button is clicked. Keyword-only. |
| `title` | `str, default "Clefs"` | The page's title. Keyword-only. |
| `hint` | `str, default "One of the checked clefs is picked at random."` | The gray line above the list. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to QCheckBox` | The checkbox of each clef offered. |
| `QWidget` | The page, with its title. The last checked clef cannot be unchecked. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> checked = []
>>> boxes_, page_ = clef_choice_page(
...     ("treble", "bass"),
...     selected={"bass"},
...     edited=lambda: checked.append(1),
...     back=lambda: None,
... )
>>> boxes_[
...     "bass"
... ].isEnabled()  # it is the only one checked, so it stays checked
False
>>> boxes_["treble"].setChecked(True)
>>> (
...     sorted(
...         c
...         for c, ticked_box in boxes_.items()
...         if ticked_box.isChecked()
...     ),
...     checked,
... )
(['bass', 'treble'], [1])
```
{% endraw %}
