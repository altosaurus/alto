---
title: alto.exercises.base
parent: api
package: alto.exercises
api_components: [{"title": "ButtonSettings", "url": "/api/alto.exercises.base/class-buttonsettings/"}, {"title": "ChoiceExercise", "url": "/api/alto.exercises.base/class-choiceexercise/"}, {"title": "Exercise", "url": "/api/alto.exercises.base/class-exercise/"}, {"title": "FingerboardPosition", "url": "/api/alto.exercises.base/class-fingerboardposition/"}, {"title": "PicturePosition", "url": "/api/alto.exercises.base/class-pictureposition/"}, {"title": "Question", "url": "/api/alto.exercises.base/class-question/"}, {"title": "note_from", "url": "/api/alto.exercises.base/function-note_from/"}, {"title": "pick_distractors", "url": "/api/alto.exercises.base/function-pick_distractors/"}, {"title": "register", "url": "/api/alto.exercises.base/function-register/"}, {"title": "signature", "url": "/api/alto.exercises.base/function-signature/"}]
permalink: /api/alto.exercises.base/
---
{% raw %}
Exercise framework. Register a ChoiceExercise for button answers or an
Exercise for construction tasks.

## Classes

- [`FingerboardPosition`](class-fingerboardposition/) — A written pitch on one string, with the tuning needed to redraw it.
- [`PicturePosition`](class-pictureposition/) — A pack-owned image and a marked location in its original pixels.
- [`Question`](class-question/) — One question, with what to show for it and which answer is right.
- [`Exercise`](class-exercise/) — What every exercise provides: its name, how it makes questions and how long a good answer takes.
- [`ButtonSettings`](class-buttonsettings/) — An exercise’s choice of answer layout and maximum number of buttons per group.
- [`ChoiceExercise`](class-choiceexercise/) — A button-answer exercise with its own standard Buttons submenu.

## Functions

- [`note_from`](function-note_from/) — Rebuild a note from stored data.
- [`signature`](function-signature/) — Describe the exercise settings in force, so a stored question is only asked again under the settings it was made for.
- [`register`](function-register/) — Add an exercise to `REGISTRY`, next to the others of its category.
- [`pick_distractors`](function-pick_distractors/) — Choose wrong answers to offer alongside the right one, and shuffle them all.

<details markdown="1">
<summary>Module notes and examples</summary>

An `Exercise` makes `Question` objects. The `Question` says what to show
(a staff, a keyboard or only text), which
buttons to offer and which answer is right. The exercise screen and the
scheduler work with those two classes only, so
a new exercise needs no new interface code.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> question = Question(
...     "Name this note.",
...     choices=["C", "D", "E"],
...     answer="D",
... )
>>> question.check("D"), question.check("E")
(True, False)
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"fingerboardposition": "class-fingerboardposition/", "pictureposition": "class-pictureposition/", "question": "class-question/", "questioncheck_placed": "class-question/#questioncheck_placed", "questionsounding_columns": "class-question/#questionsounding_columns", "questionplacement_columns": "class-question/#questionplacement_columns", "questioncheck_scale": "class-question/#questioncheck_scale", "questioncheck_steps": "class-question/#questioncheck_steps", "questioncheck_built": "class-question/#questioncheck_built", "questionplaces_sequence": "class-question/#questionplaces_sequence", "questioncheck": "class-question/#questioncheck", "questioncomplete": "class-question/#questioncomplete", "questionitem_key": "class-question/#questionitem_key", "questionto_dict": "class-question/#questionto_dict", "questionfrom_dict": "class-question/#questionfrom_dict", "note_from": "function-note_from/", "signature": "function-signature/", "exercise": "class-exercise/", "exercisesound_instrument": "class-exercise/#exercisesound_instrument", "exercisesettings_signature": "class-exercise/#exercisesettings_signature", "exercisecard_prompt": "class-exercise/#exercisecard_prompt", "exercisecard_groups": "class-exercise/#exercisecard_groups", "exercisecard_count": "class-exercise/#exercisecard_count", "exercisedaily_candidates": "class-exercise/#exercisedaily_candidates", "exercisereview_question": "class-exercise/#exercisereview_question", "exerciserefresh": "class-exercise/#exerciserefresh", "exerciseinstructions": "class-exercise/#exerciseinstructions", "exercisegenerate": "class-exercise/#exercisegenerate", "buttonsettings": "class-buttonsettings/", "choiceexercise": "class-choiceexercise/", "choiceexercisebutton_settings": "class-choiceexercise/#choiceexercisebutton_settings", "choiceexercisesettings_signature": "class-choiceexercise/#choiceexercisesettings_signature", "choiceexercisepractice_signature": "class-choiceexercise/#choiceexercisepractice_signature", "choiceexercisegenerate": "class-choiceexercise/#choiceexercisegenerate", "choiceexerciselimit_buttons": "class-choiceexercise/#choiceexerciselimit_buttons", "choiceexercisemake_question": "class-choiceexercise/#choiceexercisemake_question", "register": "function-register/", "pick_distractors": "function-pick_distractors/"}</script>
{% include api-fragments.html %}
