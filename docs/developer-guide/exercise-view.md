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

Start in `MainWindow.open_exercise()`. On the first visit, the selected tile supplies the exercise class, `NoteNames`. The window creates an ExercisePage for the exercise and active learner. The page creates an ExerciseController that owns the selected exercise. The screen uses that exercise to build its components. The controller connects practice inputs and updates before it publishes the first question for the view to draw. [MainWindow.open_exercise]({{ '/api/alto.ui.main_window/class-mainwindow/#mainwindowopen_exercise' | relative_url }}) · [ExerciseController.next_question]({{ '/api/alto.ui.exercise_controller/class-exercisecontroller/#exercisecontrollernext_question' | relative_url }})

### ExerciseView components

Open **Exercise settings** with the sliders button. In the constructor, each assignment names a component of the screen. Follow the assignment, or its factory method, to see how the component is configured. The main area stacks the toolbar, question view, and answer controls on the left, and the settings pane opens on the right. The numbers below match the screenshot. Select a line number beside an excerpt to open that line on GitHub.

{% include component-shot.html screen="exercise-view-anatomy" labels=true width=982 height=614 alt="Note Identification with the staff on the left, the exercise toolbar above it, letter-name answer controls below it, and the settings pane open on the right." %}

#### 1. Staff

`ExerciseController.question` holds the question being graded. The controller sends it to the screen, where `QuestionView.displayed_question` records what was drawn. If the review queue is empty, the controller clears its question and the question view displays the queue message. `QuestionView.prompt` shows instructions and retry messages above the music. Questions with an instruction printed on the staff usually hide this label. For Note Identification, `QuestionView` mounts a staff and draws the written pitches, clef, key signature, and note value. A keyboard question can show the keys alongside a key signature. Construction questions select an editor for placing notes, clefs, scales, or signatures. Consecutive questions that use the same display reuse its widget. During calendar practice, QuestionView also places the review interval beside the staff or below the keyboard. [QuestionView]({{ '/api/alto.ui.question_view/class-questionview/' | relative_url }})

{% include exercise-view-source.html name="staff" %}

The staff stores the pitches in columns, sizes itself to fit the music, and requests a repaint. On the next paint event, Qt gives the staff a chance to draw the paper, staff lines, clef, and note. [Staff update]({{ '/api/alto.ui.staff/class-staffwidget/#staffwidgetshow_notes' | relative_url }}) · [Paint event]({{ '/api/alto.ui.staff/class-staffwidget/#staffwidgetpaintevent' | relative_url }})

#### 2. Toolbar

`ExerciseView` creates an `ExerciseToolbar` and places it above the staff. The toolbar owns the score, help button, and exercise tools. It shows the book button when the exercise has a reference and the MIDI selector when the exercise supports MIDI on Linux. Clicking the sliders button tells the view to open or close the settings pane. [ExerciseToolbar]({{ '/api/alto.ui.exercise_toolbar/class-exercisetoolbar/' | relative_url }})

{% include exercise-view-source.html name="toolbar" %}

#### 3. Answer controls

The numbered region shows the answer controls inside `view.control_area`. In Note Identification the answer row displays one button per letter. The same area shows review ratings during manual self-grading and the **Next** button when the learner advances manually. When the review queue is empty, the button reads **Check again**. The controller listens to the answer controls. Clicking a letter sends its value for grading. With **Octave** enabled, the controller collects the note name and octave in either order and grades the pair once. Each new question replaces the choices and their keyboard shortcuts. [ControlArea]({{ '/api/alto.ui.control_area/class-controlarea/' | relative_url }}) · [AnswerControls]({{ '/api/alto.ui.answer_controls/class-answercontrols/' | relative_url }}) · [Answer submission]({{ '/api/alto.ui.exercise_controller/class-exercisecontroller/#exercisecontrollersubmit_choice' | relative_url }})

{% include exercise-view-source.html name="answer" %}

Construction questions can ask the learner to place an answer in the music. The active control is available as `view.question_view.editor`. For example, a Key Signature Construction question requests a fork for choosing the number of sharps or flats. The question view creates it on demand and resets it for the next key signature. [KeyFork]({{ '/api/alto.ui.key_fork/class-keyfork/' | relative_url }})

For construction questions, the same answer area displays its `PlacementControls` row. In Scale Construction, **Place note** enters each note and **Answer** submits the completed scale. In Beat Construction, marking the first beat enables **Undo** and **Answer**. The Answer button asks QuestionView to read its active editor. The controller connects each submission to its matching grading method. [PlacementControls]({{ '/api/alto.ui.placement_controls/class-placementcontrols/' | relative_url }})

#### 4. Settings pane

The page asks the settings panel factory for the controls that belong to the active exercise. For Note Identification, the factory chooses the panel that builds the **Clefs**, **Range**, and other note-name settings. [Settings panel factory]({{ '/api/alto.ui.settings_panel/function-settings_panel_for/' | relative_url }}) · [Note Identification settings panel]({{ '/api/alto.ui.settings_panel/class-notenamesettingspanel/' | relative_url }})

{% include exercise-view-source.html name="panel" %}

The view places the panel in a `SidePane`, which stays hidden until the learner opens it. The toolbar toggle animates the pane’s width. Restyling the panel redraws the question’s keyboard and circle. [SidePane]({{ '/api/alto.ui.side_pane/class-sidepane/' | relative_url }}) Changing a question option, such as the clef, asks the controller for a new question.

{% include exercise-view-source.html name="signals" %}

### Practice responsibilities

| Component | Responsibility |
|---|---|
| ExerciseView | Displays a supplied question, renders progress and feedback, and reports visibility changes. |
| ExercisePage | Assembles the screen and connects playback and application events when the main window opens an exercise. |
| ExerciseController | Selects questions, grades submissions, records attempts with the learner, and manages retries, ratings, and advance timers. It owns the feedback fades and cancels them when the question changes. |
| RatingControls | Shows the interval above each manual grade button and sends the selected rating to the controller. |
| PracticeSession | Computes the next score, streak, and attempt count. The view receives the resulting snapshot. |
| ExerciseFeedback | Plays the answer and sends each sounding column to the view. When playback ends, it tells the controller that feedback is complete. |

To inspect the layout with a known question, create an ExerciseView and pass the question to its display method. To test grading, send the same answer directly to an ExerciseController. The running page connects those two paths. [Display API]({{ '/api/alto.ui.exercise_view/class-exerciseview/' | relative_url }}) · [Controller API]({{ '/api/alto.ui.exercise_controller/class-exercisecontroller/' | relative_url }}) · [Playback API]({{ '/api/alto.ui.exercise_feedback/class-exercisefeedback/' | relative_url }})

### Question selection

Inside the controller’s `next_question()`, follow `q = self._pick_question()`. With a profile open, this calls `Learner.pick()`. The profile’s scheduler decides which eligible question to show, so a question can be a review of a note the learner has seen before. To trace a freshly generated note, follow `ChoiceExercise.generate()` into `NoteNames.make_question()`. It chooses a pitch within the enabled clef and range, spells it in the question key, and selects the staff signature independently. `NoteNames._question_for()` turns that pitch into a `Question` with both the notation and the accepted answer. [Learner.pick]({{ '/api/alto.learning.learner/class-learner/#learnerpick' | relative_url }}) · [NoteNames.make_question]({{ '/api/alto.exercises.library/class-notenames/#notenamesmake_question' | relative_url }})

To see how that one object drives the screen, put a breakpoint on `self.displayed_question = q` in `alto/ui/question_view.py`. The controller has already started the response timer and reset the attempt count. Inspect the question in your debugger.

```python
str(q.staff[0][0])  # The written pitch, for example "C4"
q.clef, q.key  # How to draw and read the staff
q.choices, q.answer  # The button labels and the expected answer
q.octaves  # None while Octave is off
```

For middle C with letter names, `q.answer` is `"C"`. Step to the end of `ExerciseView.show_question()` and compare the live widgets with the question you inspected above. With the settings shown, all three expressions should return `True`. [Question fields]({{ '/api/alto.exercises.base/class-question/' | relative_url }})

```python
self.question_view.staff.columns == q.staff
[button.text() for button in self.control_area.answers.buttons] == q.choices
self.settings_panel.parentWidget() is self.settings_pane
```

## An answer from click to feedback

Set a breakpoint in `ExerciseController.submit_choice()` and click the name of the note you see. The button passes its choice string to the controller, which calls `q.check(choice)`. For the middle C example, clicking **C** succeeds. The staff drawing has already done its job by this point. The comparison uses the answer stored in the question. [ExerciseController.submit_choice]({{ '/api/alto.ui.exercise_controller/class-exercisecontroller/#exercisecontrollersubmit_choice' | relative_url }}) · [Question.check]({{ '/api/alto.exercises.base/class-question/#questioncheck' | relative_url }})

Step into `ExerciseController.record()`. The controller asks `PracticeSession.after_attempt()` for the updated attempt count, score, and retry decision. With an active profile, the controller also passes the attempt number, submitted answer, and elapsed time to the learner. Try a wrong answer and then a correct retry in ordinary practice. The history shows two attempts, and the score shows one missed question. [PracticeSession]({{ '/api/alto.learning.practice_session/class-practicesession/' | relative_url }}) · [Learner.record]({{ '/api/alto.learning.learner/class-learner/#learnerrecord' | relative_url }})

A correct answer finishes the question. ExerciseFeedback plays the answer through StaffPlayback. Each onset tells the view which column to highlight. The controller publishes the updated session for the toolbar and advances according to the selected **Next Question** setting. Try a wrong button on another question. It flashes red. Inspect `view.session` to see whether that miss finished the question. In ordinary ASRS or ARTS practice you can try another button on the same note. In shuffle mode the miss ends that turn. With SM-2 or FSRS, the scheduler brings the missed card back for review. [Practice modes]({{ '/practice/' | relative_url }})

## A two-part answer

Open the gear and turn on **Octave** while a note is on screen. Watch for a new question and a second row of buttons. Here’s what happens between the switch and the next answer:

1. `NoteNameSettingsPanel` receives the toggle. Its inherited `_octave_toggled()` in `alto/ui/settings_menu.py` sets `cfg.require_octave`, saves the settings, and emits `changed`. The controller connects that signal to its next-question method.
2. Inspect `q.answer` and `q.octaves` at the same breakpoint as before. For a question showing middle C, the expected answer is now `"C4"`. The exercise fills `q.octaves` from the enabled clefs’ pitch ranges. The view sees that second set of choices and presents both rows.
3. Select the octave first. The button stays selected and the score stays put. Now select the note name. Once both parts are present, the controller combines them in name–octave order and checks the result. Both parts form one submission. A wrong pair records one failed attempt and flashes both selections. [NoteNameSettingsPanel]({{ '/api/alto.ui.settings_panel/class-notenamesettingspanel/' | relative_url }})

## Question material and feedback settings

| Change in Exercise settings | What to observe |
|---|---|
| Under **Clefs**, leave only **Bass** selected. | The replacement question uses the bass clef. New pitches come from its configured **Range**. With **Octave** on, the offered octaves come from that range too. |
| Under **Buttons**, choose **Limited** and reduce **Button count**. | `ChoiceExercise.limit_buttons()` samples the other choices while keeping the correct answer available. With **Octave** on, the limit applies separately to names and octaves. |
| Under **Next Question**, choose **Wait** before answering. | The current question stays in place when you change this setting. The controller applies this choice when grading the answer. **Wait** leaves **Next** for you to press, **After Animation** advances when feedback finishes, and **Immediately** advances while the answer audio can continue. With calendar self-grading enabled, you choose a rating to advance. |

If the wrong notes are being asked, inspect the settings and the `Question` returned by `_pick_question()`. If that object is right but the wrong controls appear, follow `ExerciseView.show_question()`. If the view accepts an unexpected answer, inspect the choice passed to `q.check()`. [ChoiceExercise.limit_buttons]({{ '/api/alto.exercises.base/class-choiceexercise/#choiceexerciselimit_buttons' | relative_url }})
