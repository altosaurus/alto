---
title: Exercise view
parent: developer-guide
order: 2
permalink: /developer-guide/exercise-view/
---
Open **Note Identification** from the exercise catalog. You’ll follow one written note from the exercise that chooses it to the button that grades it. Then you’ll turn on **Octave** and watch the same view switch to a two-part answer. For the first pass, open the **Exercise settings** gear, choose **Note names → Letters (C D E)**, and leave **Octave** off.

{% include component-shot.html screen="note-identification" width=1100 height=720 alt="Note Identification with the written question on the staff and its answer buttons below." %}

## The first question

{% include first-question-c4.html %}

Start in `MainWindow.open_exercise()`. On the first visit, the selected tile supplies the exercise class, `NoteNames`. The window constructs `ExerciseView(cls(), learner=self.learner)`. The view builds its staff, controls, and settings pane, then calls `next_question()`. [MainWindow.open_exercise]({{ '/api/alto.ui.main_window/#mainwindowopen_exercise' | relative_url }}) · [ExerciseView.next_question]({{ '/api/alto.ui.exercise_view/#exerciseviewnext_question' | relative_url }})

### ExerciseView components

Open **Exercise settings** with the sliders button to see the layout below. The capture shows just `ExerciseView`. In its constructor, `outer = QHBoxLayout(self)` puts the main exercise area on the left and the settings frame on the right. Inside the main area, a vertical layout orders the toolbar, music, and answer controls.

{% include component-shot.html screen="exercise-view-anatomy" labels=true width=982 height=614 alt="Note Identification with the staff on the left, the exercise toolbar above it, letter-name answer controls below it, and the settings pane open on the right." %}

1. **Staff.** In `ExerciseView.__init__()`, find `self.staff = StaffWidget(max_step=MAX_STEP)`. The constructor adds this widget to `self._music_layout`. When a question arrives, `next_question()` passes its pitches, clef, key, and note value to `self.staff.show_notes(...)`. Follow that call into `StaffWidget`: it stores the pitches in `self.columns`, fits the widget to the music, and calls `update()`. On the next paint event, `paintEvent()` opens a `QPainter` and calls `_draw_score()` to draw the paper, staff lines, clef, and note. [StaffWidget.show_notes]({{ '/api/alto.ui.staff/#staffwidgetshow_notes' | relative_url }}) · [StaffWidget.paintEvent]({{ '/api/alto.ui.staff/#staffwidgetpaintevent' | relative_url }})
2. **Toolbar.** Find `top = QHBoxLayout()` in the view constructor. It adds the score label, help, and other exercise tools, then places this row at the top of the main area with `lay.addLayout(top)`. The sliders button is `self.gear`, a checkable `QToolButton`. Its `toggled` signal opens or closes the pane labeled **4**. [ExerciseView constructor]({{ '/api/alto.ui.exercise_view/#exerciseview' | relative_url }})
3. **Answer controls.** The constructor creates an empty grid, `self.choice_box`. In `next_question()`, find `for i, c in enumerate(q.choices)`. For the letter names shown here, each iteration creates a `DegreeButton(c)`, connects its click to `self.submit(choice, button=btn)`, and inserts the button at the row and column from `q.grid`. With **Octave** off, clicking a letter submits it immediately. On the next question the view retires the old buttons and fills the grid again. [DegreeButton]({{ '/api/alto.ui.degree_text/#degreebutton' | relative_url }}) · [ExerciseView.submit]({{ '/api/alto.ui.exercise_view/#exerciseviewsubmit' | relative_url }})
4. **Settings pane.** Follow `settings_panel_for(exercise, learner=self.learner)` into `settings_panel.py`. For `NoteNames`, the factory selects `NoteNameSettingsPanel(settings.note_names)`. Its constructor builds the settings menu and rows such as **Clefs** and **Range**. Back in the view, `pane_lay.addWidget(self.settings_panel, 1)` puts that panel inside `self.pane`, an initially hidden `QFrame`. When the sliders button is checked, `_toggle_pane()` shows the frame and animates its maximum width. Changing a question option emits `changed`, which the view connects to `next_question()`. [Settings panel factory]({{ '/api/alto.ui.settings_panel/#settings_panel_for' | relative_url }}) · [NoteNameSettingsPanel]({{ '/api/alto.ui.settings_panel/#notenamesettingspanel' | relative_url }})

### Question selection

Inside `next_question()`, follow `q = self._pick_question()`. With a profile open, this calls `Learner.pick()`. The profile’s scheduler decides which eligible question to show, so a question can be a review of a note the learner has seen before. To trace a freshly generated note, follow `ChoiceExercise.generate()` into `NoteNames.make_question()`. It chooses a clef, key signature, and note value from the enabled settings, then draws a pitch within that clef’s range. `NoteNames._question_for()` turns that pitch into a `Question` with both the notation and the accepted answer. [Learner.pick]({{ '/api/alto.learning.learner/#learnerpick' | relative_url }}) · [NoteNames.make_question]({{ '/api/alto.exercises.library/#notenamesmake_question' | relative_url }})

To see how that one object drives the screen, put a breakpoint on `self.question = q` in `alto/ui/exercise_view.py`. A few lines below, the view clears the attempt count and starts the response timer. Inspect these expressions in your debugger:

```python
str(q.staff[0][0])  # The written pitch, for example "C4"
q.clef, q.key  # How to draw and read the staff
q.choices, q.answer  # The button labels and the expected answer
q.octaves  # None while Octave is off
```

For middle C with letter names, `q.answer` is `"C"`. Step to the end of `next_question()` and compare the live widgets with the question you inspected above. With the settings shown, all three expressions should return `True`. [Question fields]({{ '/api/alto.exercises.base/#question' | relative_url }})

```python
self.staff.columns == q.staff
[button.text() for button in self.buttons] == q.choices
self.settings_panel.parentWidget() is self.pane
```

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
