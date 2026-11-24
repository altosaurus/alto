---
title: Exercise view
parent: developer-guide
order: 2
permalink: /developer-guide/exercise-view/
---
Open **Note Identification** from the exercise catalog. You’ll follow one written note from the exercise that chooses it to the button that grades it. Then you’ll turn on **Octave** and watch the same view switch to a two-part answer. For the first pass, open the **Exercise settings** gear, choose **Note names → Letters (C D E)**, and leave **Octave** off.

{% include component-shot.html screen="note-identification" width=1100 height=720 alt="Note Identification with the written question on the staff and its answer buttons below." %}

## The first question

Start in `MainWindow.open_exercise()`. On the first visit, the selected tile supplies the exercise class, `NoteNames`. The window constructs `ExerciseView(cls(), learner=self.learner)`. The view builds its staff, controls, and settings pane, then calls `next_question()`. [MainWindow.open_exercise]({{ '/api/alto.ui.main_window/#mainwindowopen_exercise' | relative_url }}) · [ExerciseView.next_question]({{ '/api/alto.ui.exercise_view/#exerciseviewnext_question' | relative_url }})

Inside `next_question()`, follow `q = self._pick_question()`. With a profile open, this calls `Learner.pick()`. The profile’s scheduler decides which eligible question to show, so a question can be a review of a note the learner has seen before. To trace a freshly generated note, follow `ChoiceExercise.generate()` into `NoteNames.make_question()`. It chooses a clef, key signature, and note value from the enabled settings, then draws a pitch within that clef’s range. `NoteNames._question_for()` turns that pitch into a `Question` with both the notation and the accepted answer. [Learner.pick]({{ '/api/alto.learning.learner/#learnerpick' | relative_url }}) · [NoteNames.make_question]({{ '/api/alto.exercises.library/#notenamesmake_question' | relative_url }})

To see how that one object drives the screen, put a breakpoint on `self.question = q` in `alto/ui/exercise_view.py`. Inspect these expressions in your debugger:

```python
str(q.staff[0][0])  # The written pitch, for example "C4"
q.clef, q.key  # How to draw and read the staff
q.choices, q.answer  # The button labels and the expected answer
q.octaves  # None while Octave is off
```

For middle C with letter names, `q.answer` is `"C"`. Continue through `next_question()` to `self.staff.show_notes(...)`, which draws the question, then to the loop over `q.choices`, which creates the buttons. The view also clears the previous attempt count and starts the response timer. [Question fields]({{ '/api/alto.exercises.base/#question' | relative_url }})

## An answer from click to feedback

Set a breakpoint in `ExerciseView.submit()` and click the name of the note you see. The button passes its choice string to `submit()`, which calls `q.check(choice)`. For the middle C example, clicking **C** succeeds. The staff drawing has already done its job by this point. The comparison uses the answer stored in the question. [ExerciseView.submit]({{ '/api/alto.ui.exercise_view/#exerciseviewsubmit' | relative_url }}) · [Question.check]({{ '/api/alto.exercises.base/#questioncheck' | relative_url }})

Step into `_record()`. It increments the attempt number and passes the question, submitted answer, correctness, and elapsed time to `Learner.record()` for the active profile. Every graded attempt goes into the history. Only the first attempt on this showing counts toward the view’s score and streak. [Learner.record]({{ '/api/alto.learning.learner/#learnerrecord' | relative_url }})

A correct answer reaches `_finish_answer()`, which marks it answered and plays the note when sound is on. Try a wrong button on another question. It flashes red, and `_after_miss()` consults the practice mode. In ordinary ASRS or ARTS practice you can try another button on the same note. With SM-2 or FSRS, the scheduler brings the missed card back for review. [Practice modes]({{ '/practice/' | relative_url }})

## A two-part answer

Open the gear and turn on **Octave** while a note is on screen. Watch for a new question and a second row of buttons. Here’s what happens between the switch and the next answer:

1. `NoteNameSettingsPanel` receives the toggle. Its inherited `_octave_toggled()` in `alto/ui/settings_menu.py` sets `cfg.require_octave`, saves the settings, and emits `changed`. The view connected this signal to `next_question()` when it built the pane.
2. Inspect `q.answer` and `q.octaves` at the same breakpoint as before. For a question showing middle C, the expected answer is now `"C4"`. The exercise fills `q.octaves` from the enabled clefs’ pitch ranges. The view sees that second set of choices and wires both rows to `_pick()`.
3. Select the octave first. The button stays selected and the score stays put. Now select the note name. Once both parts are present, `_submit_pair()` combines them in name–octave order and checks the result. A correct pair goes through `submit()`. A wrong pair records one failed attempt and flashes both selections. [NoteNameSettingsPanel]({{ '/api/alto.ui.settings_panel/#notenamesettingspanel' | relative_url }})

## Question material and feedback settings

| Change in Exercise settings | What to observe |
|---|---|
| Under **Clefs**, leave only **Bass** selected. | The replacement question uses the bass clef. New pitches come from its configured **Range**. With **Octave** on, the offered octaves come from that range too. |
| Under **Buttons**, choose **Limited** and reduce **Button count**. | `ChoiceExercise.limit_buttons()` samples the other choices while keeping the correct answer available. With **Octave** on, the limit applies separately to names and octaves. |
| Under **Next Question**, choose **Wait** before answering. | The current question stays in place when you change this setting. On a correct answer, `_finish_answer()` reads the saved mode. **Wait** leaves **Next** for you to press, **After Animation** advances when feedback finishes, and **Immediately** advances while the answer audio can continue. With calendar self-grading enabled, you choose a rating to advance. |

If the wrong notes are being asked, inspect the settings and the `Question` returned by `_pick_question()`. If that object is right but the wrong controls appear, follow `next_question()`. If the view accepts an unexpected answer, inspect the choice passed to `q.check()`. [ChoiceExercise.limit_buttons]({{ '/api/alto.exercises.base/#choiceexerciselimit_buttons' | relative_url }})
