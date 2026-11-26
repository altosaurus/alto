---
title: alto.learning.scheduler
parent: api
package: alto.learning
api_components: [{"title": "arts_priority", "url": "/api/alto.learning.scheduler/function-arts_priority/"}, {"title": "choose", "url": "/api/alto.learning.scheduler/function-choose/"}, {"title": "speed_term", "url": "/api/alto.learning.scheduler/function-speed_term/"}, {"title": "update_strain", "url": "/api/alto.learning.scheduler/function-update_strain/"}, {"title": "weight", "url": "/api/alto.learning.scheduler/function-weight/"}]
permalink: /api/alto.learning.scheduler/
---
{% raw %}
How a question's history turns into how soon it comes back. Pure Python,
no database and no Qt.

## Functions

- [`arts_priority`](function-arts_priority/) — Score a previously answered item for Adaptive Response-Time-based Sequencing.
- [`speed_term`](function-speed_term/) — Return the strain change for how long the first answer took.
- [`update_strain`](function-update_strain/) — Return the question's strain after one more answer.
- [`weight`](function-weight/) — Return how likely a question is to be picked, relative to the others.
- [`choose`](function-choose/) — Pick one option at random, in proportion to its weight.

<details markdown="1">
<summary>Module notes and examples</summary>

Every question carries a *strain*: how much practice it needs. A new
question starts at NEW_STRAIN. Each answer moves
it, and the chance of being asked is exp(WEIGHT_SLOPE * strain), so
strained questions come back sooner and more
often while well-known ones fade into the background.

* A wrong answer adds WRONG_PENALTY, so every extra attempt pushes the
question further up.
* A right answer on the first try takes CORRECT_REWARD off. A right
answer after misses earns only RETRY_REWARD.
* The first answer's speed, against the exercise's `par_seconds`, adds
or removes strain on top: very quick
  answers take off up to FAST_BONUS, and slow ones add up to
  SLOW_PENALTY.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> strain = update_strain(
...     NEW_STRAIN,
...     correct=False,
...     attempt_no=1,
...     seconds=4.0,
...     par_seconds=4.0,
... )
>>> strain  # a miss pushes the question up
3.0
>>> update_strain(
...     strain,
...     correct=True,
...     attempt_no=2,
...     seconds=2.0,
...     par_seconds=4.0,
... )  # a retry earns little
2.8
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"arts_priority": "function-arts_priority/", "speed_term": "function-speed_term/", "update_strain": "function-update_strain/", "weight": "function-weight/", "choose": "function-choose/"}</script>
{% include api-fragments.html %}
