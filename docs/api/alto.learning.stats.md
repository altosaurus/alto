---
title: alto.learning.stats
parent: api
package: alto.learning
api_components: [{"title": "Bucket", "url": "/api/alto.learning.stats/class-bucket/"}, {"title": "ExerciseStats", "url": "/api/alto.learning.stats/class-exercisestats/"}, {"title": "HardQuestion", "url": "/api/alto.learning.stats/class-hardquestion/"}, {"title": "Stats", "url": "/api/alto.learning.stats/class-stats/"}, {"title": "collect", "url": "/api/alto.learning.stats/function-collect/"}, {"title": "daily_counts", "url": "/api/alto.learning.stats/function-daily_counts/"}, {"title": "describe", "url": "/api/alto.learning.stats/function-describe/"}, {"title": "period_end", "url": "/api/alto.learning.stats/function-period_end/"}]
permalink: /api/alto.learning.stats/
---
{% raw %}
Numbers and series for the statistics screen, worked out from the
answers in the database. Pure Python, no Qt.

## Classes

- [`Bucket`](class-bucket/) — The answers given in one period (an hour, day, week or month), for the charts.
- [`ExerciseStats`](class-exercisestats/) — How practice is going on one exercise.
- [`HardQuestion`](class-hardquestion/) — A question that needs practice, for the list on the statistics screen.
- [`Stats`](class-stats/) — Everything the statistics screen shows.

## Functions

- [`period_end`](function-period_end/) — Return the moment a chart period ends, which is when the next one begins.
- [`describe`](function-describe/) — Return a short line saying what a question was, for the list of questions that need practice.
- [`daily_counts`](function-daily_counts/) — Return how many questions were answered on each day, for the review heatmap.
- [`collect`](function-collect/) — Work out everything the statistics screen shows.

<details markdown="1">
<summary>Module notes and examples</summary>

A "question" here is one showing of a question, scored by its first
answer: it is right if that answer was right.
Later attempts at the same showing show up as extra attempts per
question, not as extra questions.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> for i, ok in enumerate((True, True, False)):
...     db.add_attempt(
...         ada.id,
...         exercise="NoteNames",
...         item_key=str(i),
...         attempt_no=1,
...         answer="C",
...         correct=ok,
...         duration_ms=2000,
...         answered_at=1000.0 + i,
...     )
>>> stats = collect(
...     db, profile_ids=[ada.id], now=1010.0
... )
>>> stats.questions, stats.first_right
(3, 2)
>>> # noinspection PyTypeChecker
>>> round(stats.accuracy)
67
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"bucket": "class-bucket/", "bucketaccuracy": "class-bucket/#bucketaccuracy", "bucketmedian_seconds": "class-bucket/#bucketmedian_seconds", "exercisestats": "class-exercisestats/", "hardquestion": "class-hardquestion/", "stats": "class-stats/", "statsaccuracy": "class-stats/#statsaccuracy", "statsattempts_per_question": "class-stats/#statsattempts_per_question", "period_end": "function-period_end/", "describe": "function-describe/", "daily_counts": "function-daily_counts/", "collect": "function-collect/"}</script>
{% include api-fragments.html %}
