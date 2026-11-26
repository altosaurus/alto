---
title: second_row_keys
parent: alto.ui.exercise_view
api_module: alto.ui.exercise_view
package: alto.ui
permalink: /api/alto.ui.exercise_view/function-second_row_keys/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def second_row_keys(
    first: list[str],
    *,
    labels: list[str],
) -> list[str]
```

{% endraw %}{% include api-source.html name="second_row_keys" line=270 %}{% raw %}

</div>

Choose a key for each button of the second row of a two-part answer,
such as the octave or the inversion.

They must not be keys that the first row has. When the first row
uses the digits the second row takes the home row,
A S D F and so on; when the first row uses letters (the notes'
names) it takes the digits, and an octave that is a single
digit takes that digit.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `first` | `list of str` | The keys of the first row, as `choice_keys` chose them. |
| `labels` | `list of str` | The text of each button of the second row. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | A key for each button; "" for one that has none. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> second_row_keys(
...     ["1", "2", "3"],
...     labels=[
...         "root position",
...         "1st inversion",
...     ],
... )
['A', 'S']
>>> second_row_keys(
...     ["C", "Shift+C"], labels=["3", "4", "5"]
... )
['3', '4', '5']
```
{% endraw %}
