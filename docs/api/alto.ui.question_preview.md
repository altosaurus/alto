---
title: alto.ui.question_preview
parent: api
package: alto.ui
api_components: [{"title": "QuestionPreview", "url": "/api/alto.ui.question_preview/class-questionpreview/"}]
permalink: /api/alto.ui.question_preview/
---
{% raw %}
A popup showing a stored question the way the exercise showed it, with
its answer.

## Classes

- [`QuestionPreview`](class-questionpreview/) — A question as it appeared (the notes on the staff, or the highlighted key), then what the answer is.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> question = Question(
...     "Name the note.",
...     choices=["C", "D"],
...     answer="C",
... )
>>> QuestionPreview(
...     "Note Identification", question=question
... ).windowTitle()
'Note Identification'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"questionpreview": "class-questionpreview/"}</script>
{% include api-fragments.html %}
