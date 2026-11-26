---
title: alto.ui.database_page
parent: api
package: alto.ui
api_components: [{"title": "AnswerList", "url": "/api/alto.ui.database_page/class-answerlist/"}, {"title": "DatabasePage", "url": "/api/alto.ui.database_page/class-databasepage/"}, {"title": "QuestionTexts", "url": "/api/alto.ui.database_page/class-questiontexts/"}, {"title": "RowsModel", "url": "/api/alto.ui.database_page/class-rowsmodel/"}, {"title": "answer_cells", "url": "/api/alto.ui.database_page/function-answer_cells/"}, {"title": "open_preview", "url": "/api/alto.ui.database_page/function-open_preview/"}]
permalink: /api/alto.ui.database_page/
---
{% raw %}
A read-only look at what is stored: every answer, every question's
record, and the profiles.

## Classes

- [`RowsModel`](class-rowsmodel/) — Rows of (text shown, value to sort by) cells, as a table model. Numbers are right-aligned.
- [`QuestionTexts`](class-questiontexts/) — Describes stored questions in words, remembering each one so it is worked out only once.
- [`AnswerList`](class-answerlist/) — A table of answers that sorts when a heading is clicked and opens the question behind a row on a double click.
- [`DatabasePage`](class-databasepage/) — The tables behind the app.

## Functions

- [`answer_cells`](function-answer_cells/) — Turn answers read from the database into the cells of a table, and the hidden details of each row.
- [`open_preview`](function-open_preview/) — Show the question behind a row of an answers table, if its record is still stored.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> len(
...     _when(0.0)[0]
... )  # a timestamp as 'YYYY-MM-DD HH:MM:SS'
19
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"rowsmodel": "class-rowsmodel/", "rowsmodelrowcount": "class-rowsmodel/#rowsmodelrowcount", "rowsmodelcolumncount": "class-rowsmodel/#rowsmodelcolumncount", "rowsmodeldata": "class-rowsmodel/#rowsmodeldata", "rowsmodelheaderdata": "class-rowsmodel/#rowsmodelheaderdata", "questiontexts": "class-questiontexts/", "answer_cells": "function-answer_cells/", "open_preview": "function-open_preview/", "answerlist": "class-answerlist/", "answerlistshow_answers": "class-answerlist/#answerlistshow_answers", "databasepage": "class-databasepage/", "databasepageshow_table": "class-databasepage/#databasepageshow_table"}</script>
{% include api-fragments.html %}
