---
title: alto.learning.calendar
parent: api
package: alto.learning
api_components: [{"title": "CalendarPractice", "url": "/api/alto.learning.calendar/class-calendarpractice/"}, {"title": "ReviewInterval", "url": "/api/alto.learning.calendar/class-reviewinterval/"}]
permalink: /api/alto.learning.calendar/
---
{% raw %}
Daily exercise queues for SM-2 and FSRS.

## Classes

- [`ReviewInterval`](class-reviewinterval/) — A preview of one rating for a card in its current scheduling state.
- [`CalendarPractice`](class-calendarpractice/) — Prepare daily exercise queues and store each scheduler's review dates.

<details markdown="1">
<summary>Module notes and examples</summary>

The scheduler controls when an introduced card is due. Each exercise
supplies new
questions under its current settings. Counting a prepared question does
not introduce it.

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"reviewinterval": "class-reviewinterval/", "reviewintervalduration": "class-reviewinterval/#reviewintervalduration", "calendarpractice": "class-calendarpractice/", "calendarpracticeinherit_schedules": "class-calendarpractice/#calendarpracticeinherit_schedules", "calendarpracticelimits": "class-calendarpractice/#calendarpracticelimits", "calendarpracticeoverrides": "class-calendarpractice/#calendarpracticeoverrides", "calendarpracticeset_limits": "class-calendarpractice/#calendarpracticeset_limits", "calendarpracticereset_limits": "class-calendarpractice/#calendarpracticereset_limits", "calendarpracticequeue": "class-calendarpractice/#calendarpracticequeue", "calendarpracticecounts": "class-calendarpractice/#calendarpracticecounts", "calendarpracticetile_counts": "class-calendarpractice/#calendarpracticetile_counts", "calendarpracticestudy_counts": "class-calendarpractice/#calendarpracticestudy_counts", "calendarpracticetake": "class-calendarpractice/#calendarpracticetake", "calendarpracticetake_or_wait": "class-calendarpractice/#calendarpracticetake_or_wait", "calendarpracticeintroduce": "class-calendarpractice/#calendarpracticeintroduce", "calendarpracticecorrect_interval": "class-calendarpractice/#calendarpracticecorrect_interval", "calendarpracticepassing_intervals": "class-calendarpractice/#calendarpracticepassing_intervals", "calendarpracticegrade": "class-calendarpractice/#calendarpracticegrade"}</script>
{% include api-fragments.html %}
