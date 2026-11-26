---
title: AnswerList
parent: alto.ui.database_page
api_module: alto.ui.database_page
package: alto.ui
permalink: /api/alto.ui.database_page/class-answerlist/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
AnswerList(
    *,
    names: dict[str, str],
    learner: Learner | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="AnswerList" line=803 %}{% raw %}

</div>

Bases: `QTableView`

A table of answers that sorts when a heading is clicked and opens
the question behind a row on a double click.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `proxy` | `QSortFilterProxyModel` | Sorts the rows by the values in `SORT_ROLE`. |
| `model_` | `RowsModel or None` | The rows being shown; None until `show_answers` is called. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> table = AnswerList(names={})
>>> table.show_answers([])
>>> table.proxy.rowCount()
0
```

**Constructor**

Create an empty table.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `names` | `dict of str to str` | The title of each exercise, by class name. Keyword-only. |
| `learner` | `Learner or None, default None` | The active profile for question statistics. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns the table. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> AnswerList(names={}).isSortingEnabled()
True
```

## AnswerList.show_answers

<div class="api-signature" markdown="1">

```python
def show_answers(rows: Sequence[sqlite3.Row]) -> None
```

{% endraw %}{% include api-source.html name="AnswerList.show_answers" line=872 %}{% raw %}

</div>

Show answers, newest first.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rows` | `sequence of sqlite3.Row` | Answers, as `Database.attempt_rows` returns them. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> table = AnswerList(names={})
>>> table.show_answers([])
>>> assert table.model_ is not None
>>> table.model_.headers[:2]
['When', 'Exercise']
```
{% endraw %}
