---
title: alto.ui.exercise_view
parent: api
package: alto.ui
api_components: [{"title": "ExerciseView", "url": "/api/alto.ui.exercise_view/class-exerciseview/"}, {"title": "choice_keys", "url": "/api/alto.ui.exercise_view/function-choice_keys/"}, {"title": "note_name", "url": "/api/alto.ui.exercise_view/function-note_name/"}, {"title": "note_words", "url": "/api/alto.ui.exercise_view/function-note_words/"}, {"title": "second_row_keys", "url": "/api/alto.ui.exercise_view/function-second_row_keys/"}]
permalink: /api/alto.ui.exercise_view/
---
{% raw %}
The exercise screen: a question, its answer buttons, the score, and a
pane of settings that slides in from the right.

## Classes

- [`ExerciseView`](class-exerciseview/) — The screen for practicing one exercise.

## Functions

- [`choice_keys`](function-choice_keys/) — Choose a key for each answer button, so that every answer can be given from the keyboard.
- [`second_row_keys`](function-second_row_keys/) — Choose a key for each button of the second row of a two-part answer, such as the octave or the inversion.
- [`note_name`](function-note_name/) — Return a note's name as it is written, with its octave: F♯4.
- [`note_words`](function-note_words/) — Return a note's name in words, for a screen reader: "F sharp 4".

<details markdown="1">
<summary>Module notes and examples</summary>

One `ExerciseView` works for every exercise. It asks the exercise (or,
with a profile, the learner) for the next
`Question`, shows it as a staff, a keyboard or text, offers the answer
buttons, and records each answer.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> view = ExerciseView(
...     NoteNames(), rng=random.Random(1)
... )
>>> # noinspection PyUnresolvedReferences
>>> view.question.answer in [
...     button.text() for button in view.buttons
... ]
True
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"choice_keys": "function-choice_keys/", "second_row_keys": "function-second_row_keys/", "note_name": "function-note_name/", "note_words": "function-note_words/", "exerciseview": "class-exerciseview/", "exerciseviewhideevent": "class-exerciseview/#exerciseviewhideevent", "exerciseviewshowevent": "class-exerciseview/#exerciseviewshowevent", "exerciseviewsettings_state": "class-exerciseview/#exerciseviewsettings_state", "exerciseviewrestore_settings_state": "class-exerciseview/#exerciseviewrestore_settings_state", "exerciseviewscheduling_changed": "class-exerciseview/#exerciseviewscheduling_changed", "exerciseviewnext_question": "class-exerciseview/#exerciseviewnext_question", "exercisevieweventfilter": "class-exerciseview/#exercisevieweventfilter", "exerciseviewsubmit": "class-exerciseview/#exerciseviewsubmit"}</script>
{% include api-fragments.html %}
