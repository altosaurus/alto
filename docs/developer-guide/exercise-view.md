---
title: Exercise view
parent: developer-guide
order: 2
myst:
  all_links_external: true
permalink: /developer-guide/exercise-view/
---
Open **Note Identification** from the exercise catalog. You’ll follow one written note from the exercise that chooses it to the button that grades it. Then you’ll turn on **Octave** and watch the same view switch to a two-part answer. For the first pass, open the **Exercise settings** gear, choose **Answer Type → Letters (C D E)**, and leave **Octave** off.

{% include component-shot.html screen="note-identification" width=1100 height=720 alt="Note Identification with the written question on the staff and its answer buttons below." %}

## The first question

{% include first-question-c4.html %}

Start in `MainWindow.open_exercise()`. On the first visit, the selected tile supplies the exercise class, `NoteNames`. The window constructs `ExerciseView(cls(), learner=self.learner)`. The view builds its staff, controls, and settings pane, then calls `next_question()`. [MainWindow.open_exercise]({{ '/api/alto.ui.main_window/class-mainwindow/#mainwindowopen_exercise' | relative_url }}) · [ExerciseView.next_question]({{ '/api/alto.ui.exercise_view/class-exerciseview/#exerciseviewnext_question' | relative_url }})

### ExerciseView components

Open **Exercise settings** with the sliders button. The view stacks the toolbar, staff, and answer controls on the left and opens the settings pane on the right. The numbers below match the screenshot. Select a line number beside an excerpt to open that line on GitHub.

{% include component-shot.html screen="exercise-view-anatomy" labels=true width=982 height=614 alt="Note Identification with the staff on the left, the exercise toolbar above it, letter-name answer controls below it, and the settings pane open on the right." %}

#### 1. Staff

The view creates the staff once and adds it to the music area. Each new question reuses that widget and supplies the pitches to draw, along with their clef, key signature, and note value.

{% include exercise-view-source.html name="staff" %}

The staff stores the pitches in columns, sizes itself to fit the music, and requests a repaint. On the next paint event, Qt gives the staff a chance to draw the paper, staff lines, clef, and note. [Staff update]({{ '/api/alto.ui.staff/class-staffwidget/#staffwidgetshow_notes' | relative_url }}) · [Paint event]({{ '/api/alto.ui.staff/class-staffwidget/#staffwidgetpaintevent' | relative_url }})

#### 2. Toolbar

`ExerciseView._build_toolbar()` builds a horizontal row for the score, help button, and exercise tools. The constructor adds that row above the staff. The stretch after **Back to lesson** pushes the score and remaining controls to the right. The sliders button opens and closes the settings pane.

{% include exercise-view-source.html name="toolbar" %}

#### 3. Answer controls

The view starts with an empty grid below the staff. For each question, it clears the previous buttons and adds one per letter choice. Each button remembers its own letter and submits it as soon as the learner clicks. The question supplies the grid positions when it needs a particular layout. [Answer button]({{ '/api/alto.ui.degree_text/class-degreebutton/' | relative_url }}) · [Answer submission]({{ '/api/alto.ui.exercise_view/class-exerciseview/#exerciseviewsubmit' | relative_url }})

{% include exercise-view-source.html name="answer" %}

#### 4. Settings pane

The view asks the settings panel factory for the controls that belong to the active exercise. For Note Identification, the factory chooses the panel that builds the **Clefs**, **Range**, and other note-name settings. [Settings panel factory]({{ '/api/alto.ui.settings_panel/function-settings_panel_for/' | relative_url }}) · [Note Identification settings panel]({{ '/api/alto.ui.settings_panel/class-notenamesettingspanel/' | relative_url }})

{% include exercise-view-source.html name="panel" %}

The constructor places the panel inside a frame to the right of the main area and hides it until the learner opens it. The toolbar toggle animates the frame’s width. Changing a question option, such as the clef, tells the view to show a new question using that selection.

{% include exercise-view-source.html name="signals" %}

### Question selection

Inside `next_question()`, follow `q = self._pick_question()`. With a profile open, this calls `Learner.pick()`. The profile’s scheduler decides which eligible question to show, so a question can be a review of a note the learner has seen before. To trace a freshly generated note, follow `ChoiceExercise.generate()` into `NoteNames.make_question()`. It chooses a pitch within the enabled clef and range, spells it in the question key, and selects the staff signature independently. `NoteNames._question_for()` turns that pitch into a `Question` with both the notation and the accepted answer. [Learner.pick]({{ '/api/alto.learning.learner/class-learner/#learnerpick' | relative_url }}) · [NoteNames.make_question]({{ '/api/alto.exercises.library/class-notenames/#notenamesmake_question' | relative_url }})

To see how that one object drives the screen, put a breakpoint on `self.question = q` in `alto/ui/exercise_view.py`. A few lines below, the view clears the attempt count and starts the response timer. Inspect these expressions in your debugger:

```python
str(q.staff[0][0])  # The written pitch, for example "C4"
q.clef, q.key  # How to draw and read the staff
q.choices, q.answer  # The button labels and the expected answer
q.octaves  # None while Octave is off
```

For middle C with letter names, `q.answer` is `"C"`. Step to the end of `next_question()` and compare the live widgets with the question you inspected above. With the settings shown, all three expressions should return `True`. [Question fields]({{ '/api/alto.exercises.base/class-question/' | relative_url }})

```python
self.staff.columns == q.staff
[button.text() for button in self.buttons] == q.choices
self.settings_panel.parentWidget() is self.pane
```

## An answer from click to feedback

Set a breakpoint in `ExerciseView.submit()` and click the name of the note you see. The button passes its choice string to `submit()`, which calls `q.check(choice)`. For the middle C example, clicking **C** succeeds. The staff drawing has already done its job by this point. The comparison uses the answer stored in the question. [ExerciseView.submit]({{ '/api/alto.ui.exercise_view/class-exerciseview/#exerciseviewsubmit' | relative_url }}) · [Question.check]({{ '/api/alto.exercises.base/class-question/#questioncheck' | relative_url }})

Step into `_record()`. The view asks `PracticeSession.after_attempt()` for the updated attempt count, score, and retry decision. With an active profile, the view also passes the attempt number, submitted answer, and elapsed time to the learner. Try a wrong answer and then a correct retry in ordinary practice. The history shows two attempts, and the score shows one missed question. [PracticeSession]({{ '/api/alto.learning.practice_session/class-practicesession/' | relative_url }}) · [Learner.record]({{ '/api/alto.learning.learner/class-learner/#learnerrecord' | relative_url }})

A correct answer finishes the question. The view plays the note when sound is on. Try a wrong button on another question. It flashes red, and the view reads the session’s decision. In ordinary ASRS or ARTS practice you can try another button on the same note. In shuffle mode the miss ends that turn. With SM-2 or FSRS, the scheduler brings the missed card back for review. [Practice modes]({{ '/practice/' | relative_url }})

## A two-part answer

Open the gear and turn on **Octave** while a note is on screen. Watch for a new question and a second row of buttons. Here’s what happens between the switch and the next answer:

1. `NoteNameSettingsPanel` receives the toggle. Its inherited `_octave_toggled()` in `alto/ui/settings_menu.py` sets `cfg.require_octave`, saves the settings, and emits `changed`. The view connected this signal to `next_question()` when it built the pane.
2. Inspect `q.answer` and `q.octaves` at the same breakpoint as before. For a question showing middle C, the expected answer is now `"C4"`. The exercise fills `q.octaves` from the enabled clefs’ pitch ranges. The view sees that second set of choices and wires both rows to `_pick()`.
3. Select the octave first. The button stays selected and the score stays put. Now select the note name. Once both parts are present, `_submit_pair()` combines them in name–octave order and checks the result. A correct pair goes through `submit()`. A wrong pair records one failed attempt and flashes both selections. [NoteNameSettingsPanel]({{ '/api/alto.ui.settings_panel/class-notenamesettingspanel/' | relative_url }})

## Question material and feedback settings

| Change in Exercise settings | What to observe |
|---|---|
| Under **Clefs**, leave only **Bass** selected. | The replacement question uses the bass clef. New pitches come from its configured **Range**. With **Octave** on, the offered octaves come from that range too. |
| Under **Buttons**, choose **Limited** and reduce **Button count**. | `ChoiceExercise.limit_buttons()` samples the other choices while keeping the correct answer available. With **Octave** on, the limit applies separately to names and octaves. |
| Under **Next Question**, choose **Wait** before answering. | The current question stays in place when you change this setting. On a correct answer, `_finish_answer()` reads the saved mode. **Wait** leaves **Next** for you to press, **After Animation** advances when feedback finishes, and **Immediately** advances while the answer audio can continue. With calendar self-grading enabled, you choose a rating to advance. |

If the wrong notes are being asked, inspect the settings and the `Question` returned by `_pick_question()`. If that object is right but the wrong controls appear, follow `next_question()`. If the view accepts an unexpected answer, inspect the choice passed to `q.check()`. [ChoiceExercise.limit_buttons]({{ '/api/alto.exercises.base/class-choiceexercise/#choiceexerciselimit_buttons' | relative_url }})
