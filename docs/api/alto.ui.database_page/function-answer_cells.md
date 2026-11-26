---
title: answer_cells
parent: alto.ui.database_page
api_module: alto.ui.database_page
package: alto.ui
permalink: /api/alto.ui.database_page/function-answer_cells/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def answer_cells(
    rows: Sequence[sqlite3.Row],
    *,
    names: dict[str, str],
    texts: QuestionTexts,
) -> _AnswerPage
```

{% endraw %}{% include api-source.html name="answer_cells" line=432 %}{% raw %}

</div>

Turn answers read from the database into the cells of a table, and
the hidden details of each row.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rows` | `sequence of sqlite3.Row` | Answers, as `Database.attempt_rows` returns them. |
| `names` | `dict of str to str` | The title of each exercise, by class name. Keyword-only. |
| `texts` | `QuestionTexts` | Describes each question in words. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of (list, list of dict)` | The cells, in the order of `ANSWER_HEADERS`, and for each row the exercise, the stored question and the lines the question preview shows about the answer. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.learning import Database
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> db.add_attempt(
...     ada.id,
...     exercise="NoteNames",
...     item_key="k",
...     attempt_no=1,
...     answer="C",
...     correct=True,
...     duration_ms=2500,
...     answered_at=1000.0,
... )
>>> table, hidden = answer_cells(
...     db.attempt_rows(ada.id),
...     names={
...         "NoteNames": "Note Identification"
...     },
...     texts=QuestionTexts(),
... )
>>> [text for text, _ in table[0]][1:]
['Note Identification', '(no longer stored)', 'C', 'Right', '1',
'2.5 s', '—']
>>> hidden[0]["exercise"]
'NoteNames'
```
{% endraw %}
