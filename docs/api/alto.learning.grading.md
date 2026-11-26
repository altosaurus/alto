---
title: alto.learning.grading
parent: api
package: alto.learning
api_components: [{"title": "Sm2State", "url": "/api/alto.learning.grading/class-sm2state/"}, {"title": "inherited_state", "url": "/api/alto.learning.grading/function-inherited_state/"}, {"title": "read_fsrs_card", "url": "/api/alto.learning.grading/function-read_fsrs_card/"}, {"title": "review_options", "url": "/api/alto.learning.grading/function-review_options/"}]
permalink: /api/alto.learning.grading/
---
{% raw %}
Answer-button intervals for Anki's default SM-2 and FSRS-6 deck
settings.

## Classes

- [`Sm2State`](class-sm2state/) — SM-2 learning step, review history, and actual delay for the current presentation.

## Functions

- [`inherited_state`](function-inherited_state/) — Translate one saved calendar schedule into the other scheduler's initial state.
- [`read_fsrs_card`](function-read_fsrs_card/) — Restore a saved FSRS card or start one for the question.
- [`review_options`](function-review_options/) — Calculate a consistent set of answer-button intervals from one scheduling state.
{% endraw %}

<script type="application/json" id="api-fragments">{"sm2state": "class-sm2state/", "sm2stateread": "class-sm2state/#sm2stateread", "inherited_state": "function-inherited_state/", "read_fsrs_card": "function-read_fsrs_card/", "review_options": "function-review_options/"}</script>
{% include api-fragments.html %}
