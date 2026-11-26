---
title: choice_keys
parent: alto.ui.exercise_view
api_module: alto.ui.exercise_view
package: alto.ui
permalink: /api/alto.ui.exercise_view/function-choice_keys/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def choice_keys(choices: list[str]) -> list[str]
```

{% endraw %}{% include api-source.html name="choice_keys" line=182 %}{% raw %}

</div>

Choose a key for each answer button, so that every answer can be
given from the keyboard.

Nine answers or fewer take the digits 1 to 9. More than that, as on
the piano keyboard, take the notes' own names: the
letter for a natural, Shift and the letter for a sharp, Ctrl and the
letter for a flat. A minor key, such as F♯m, is
typed the same way as the major key of its name. Any other long list
takes 1 to 9
and then 0, and the rest can be reached with Tab. Scale-degree banks
use the degree digit, with Shift for a sharp,
Ctrl for a flat, and Alt added for double alterations.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `choices` | `list of str` | The answers, in the order of their buttons. |

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | A key for each answer, such as "3" or "Shift+C"; "" for an answer that has none. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> choice_keys(
...     ["major", "minor", "diminished"]
... )
['1', '2', '3']
>>> choice_keys(
...     list("CDEFGAB") + ["C♯", "B♭"] + ["F♯"]
... )
['C', 'D', 'E', 'F', 'G', 'A', 'B', 'Shift+C', 'Ctrl+B', 'Shift+F']
>>> choice_keys([str(n) for n in range(12)])[8:]
['9', '0', '', '']
```
{% endraw %}
