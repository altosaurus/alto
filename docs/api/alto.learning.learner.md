---
title: alto.learning.learner
parent: api
package: alto.learning
api_components: [{"title": "Learner", "url": "/api/alto.learning.learner/class-learner/"}, {"title": "PracticeComplete", "url": "/api/alto.learning.learner/class-practicecomplete/"}]
permalink: /api/alto.learning.learner/
---
{% raw %}
Ties the profile, the database and the scheduler together for the
exercise screen.

## Classes

- [`PracticeComplete`](class-practicecomplete/) — The current exercise has no scheduled cards available.
- [`Learner`](class-learner/) — Chooses what a profile is asked next and records how it was answered.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> db = Database()
>>> learner = Learner(
...     db, profile=db.add_profile("Ada")
... )
>>> question = learner.pick(
...     NoteNames(), rng=random.Random(1)
... )
>>> question.answer in question.choices
True
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"practicecomplete": "class-practicecomplete/", "learner": "class-learner/", "learnerset_profile": "class-learner/#learnerset_profile", "learnermode": "class-learner/#learnermode", "learnerself_grading": "class-learner/#learnerself_grading", "learnerresponse_times": "class-learner/#learnerresponse_times", "learnerset_speed_thresholds": "class-learner/#learnerset_speed_thresholds", "learnerset_self_grading": "class-learner/#learnerset_self_grading", "learnerset_mode": "class-learner/#learnerset_mode", "learnerpick": "class-learner/#learnerpick", "learnerrecord": "class-learner/#learnerrecord"}</script>
{% include api-fragments.html %}
