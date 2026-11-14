---
title: alto.ui.exercise_view
parent: api
package: alto.ui
order: 23
permalink: /api/alto.ui.exercise_view/
---
{% raw %}
The exercise screen: a question, its answer buttons, the score, and a pane of settings that slides in from the right.

One `ExerciseView` works for every exercise. It asks the exercise (or, with a profile, the learner) for the next
`Question`, shows it as a staff, a keyboard or text, offers the answer buttons, and records each answer.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> view = ExerciseView(NoteNames(), rng=random.Random(1))
>>> # noinspection PyUnresolvedReferences
>>> view.question.answer in [button.text() for button in view.buttons]
True
```

## choice_keys

```python
def choice_keys(choices: list[str]) -> list[str]
```

Choose a key for each answer button, so that every answer can be given from the keyboard.

Nine answers or fewer take the digits 1 to 9. More than that, as on the piano keyboard, take the notes' own names: the
letter for a natural, Shift and the letter for a sharp, Ctrl and the letter for a flat. A minor key, such as F♯m, is
typed the same way as the major key of its name. Any other long list takes 1 to 9
and then 0, and the rest can be reached with Tab.

**Parameters**

- `choices` (*list of str*): The answers, in the order of their buttons.

**Returns**

- *list of str*: A key for each answer, such as "3" or "Shift+C"; "" for an answer that has none.

**Examples**

```pycon
>>> choice_keys(["major", "minor", "diminished"])
['1', '2', '3']
>>> choice_keys(list("CDEFGAB") + ["C♯", "B♭"] + ["F♯"])
['C', 'D', 'E', 'F', 'G', 'A', 'B', 'Shift+C', 'Ctrl+B', 'Shift+F']
>>> choice_keys([str(n) for n in range(12)])[8:]
['9', '0', '', '']
```

## second_row_keys

```python
def second_row_keys(
    first: list[str],
    *,
    labels: list[str],
) -> list[str]
```

Choose a key for each button of the second row of a two-part answer, such as the octave or the inversion.

They must not be keys that the first row has. When the first row uses the digits the second row takes the home row,
A S D F and so on; when the first row uses letters (the notes' names) it takes the digits, and an octave that is a single
digit takes that digit.

**Parameters**

- `first` (*list of str*): The keys of the first row, as `choice_keys` chose them.
- `labels` (*list of str*): The text of each button of the second row. Keyword-only.

**Returns**

- *list of str*: A key for each button; "" for one that has none.

**Examples**

```pycon
>>> second_row_keys(["1", "2", "3"], labels=["root position", "1st inversion"])
['A', 'S']
>>> second_row_keys(["C", "Shift+C"], labels=["3", "4", "5"])
['3', '4', '5']
```

## note_name

```python
def note_name(note: Note) -> str
```

Return a note's name as it is written, with its octave: F♯4.

**Parameters**

- `note` (*Note*): The note.

**Returns**

- *str*: The name in the naming the app is set to, then the octave number.

**Examples**

```pycon
>>> note_name(Note.parse("F#4"))
'F♯4'
```

## note_words

```python
def note_words(note: Note) -> str
```

Return a note's name in words, for a screen reader: "F sharp 4".

**Parameters**

- `note` (*Note*): The note.

**Returns**

- *str*: The letter, then "sharp", "flat" or "natural" if it has a sign, then the octave number.

**Examples**

```pycon
>>> note_words(Note.parse("F#4")), note_words(Note.parse("Bb3")), note_words(Note.parse("C4"))
('F sharp 4', 'B flat 3', 'C 4')
```

## ExerciseView

```python
ExerciseView(
    exercise: Exercise,
    *,
    rng: random.Random | None = None,
    parent: QWidget | None = None,
    learner: Learner | None = None,
)
```

Bases: `QWidget`

The screen for practising one exercise.

**Attributes**

- `PANE_WIDTH` (*int*): The width of the settings pane when it is open, in pixels.
- `REFERENCE_WIDTH` (*int*): The width of the reference pane when it is open, in pixels.
- `exercise` (*Exercise*): The exercise being practised.
- `learner` (*Learner or None*): Records every answer and chooses what to ask next; None asks at random.
- `rng` (*random.Random*): The random number generator for new questions.
- `correct` (*int*): Questions answered right first time.
- `total` (*int*): Questions answered.
- `streak` (*int*): Right answers in a row.
- `question` (*Question or None*): The question on screen.
- `answered` (*bool*): True once the question has been answered right.
- `missed` (*bool*): True once the question has been answered wrong, so it no longer counts towards the score.
- `buttons` (*list of QPushButton*): The answer buttons on screen.
- `settings_panel` (*QWidget or None*): The exercise's settings, or None for an exercise with none.
- `staff` (*StaffWidget*): Shows the notes of a question.
- `keyboard` (*KeyboardWidget*): Shows the key of a keyboard question.
- `input_staff` (*StaffInput*): The staff to click, for "place this note" questions.
- `scale_input` (*ScaleInput*): The staff to click, for "place the notes of this scale" questions.
- `fork` (*KeyFork*): The fork to pick a key signature on, for "build this key signature" questions.
- `answer_button` (*QPushButton*): Hands in what was built with the fork or placed on the scale staff.
- `book_btn` (*QToolButton or None*): Opens the exercise's reference in a pane on the right; None for an exercise that has none.
- `reference_pane` (*QFrame or None*): The pane that holds the reference.
- `lesson_requested` (*Signal*): Emitted with a lesson's key when the reference pane's lesson button is pressed.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> view = ExerciseView(NoteNames(), rng=random.Random(1))
>>> view.score.text()
'0/0 (–)   streak 0'
```

**Constructor**

Build the screen and show the first question.

**Parameters**

- `exercise` (*Exercise*): The exercise to practise.
- `rng` (*random.Random or None, default None*): The random number generator; a fresh one if None. Keyword-only.
- `parent` (*QWidget or None, default None*): The widget that owns the screen. Keyword-only.
- `learner` (*Learner or None, default None*): Where to record answers and what to ask next; None asks at random and records nothing. Keyword-only.

**Constructor examples**

```pycon
>>> from alto.exercises.library import KeySignatures
>>> view = ExerciseView(KeySignatures(), rng=random.Random(2))
>>> view.settings_panel is not None  # the exercise has settings behind the gear button
True
```

### ExerciseView.next_question

```python
def next_question() -> None
```

Show the next question: its staff, keyboard or text, and a fresh set of answer buttons.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> view = ExerciseView(NoteNames(), rng=random.Random(1))
>>> view.next_question()
>>> # noinspection PyUnresolvedReferences
>>> view.answered, len(view.buttons) == len(view.question.choices)
(False, True)
```

### ExerciseView.submit

```python
def submit(
    choice: str,
    *,
    button: QPushButton,
) -> None
```

Check an answer chosen with a button.

A right answer is scored, fades green, plays (unless the exercise is silent) and moves on after a moment; a wrong one
fades red and its button is switched off, so another can be tried.

**Parameters**

- `choice` (*str*): The text of the button that was pressed.
- `button` (*QPushButton*): The button. Nothing happens if it is switched off. Keyword-only.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> sounds.enabled = False
>>> view = ExerciseView(NoteNames(), rng=random.Random(1))
>>> question = view.question
>>> # noinspection PyUnresolvedReferences
>>> wrong = next(b for b in view.buttons if b.text() != question.answer)
>>> view.submit(wrong.text(), button=wrong)
>>> view.missed, wrong.isEnabled()
(True, False)
>>> # noinspection PyUnresolvedReferences
>>> right = next(b for b in view.buttons if b.text() == question.answer)
>>> # noinspection PyUnresolvedReferences
>>> view.submit(question.answer, button=right)
>>> view.answered
True
>>> view._advance.stop()
>>> sounds.enabled = True
```
{% endraw %}
