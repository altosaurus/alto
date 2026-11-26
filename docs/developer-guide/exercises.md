---
title: Exercises
parent: developer-guide
order: 2.5
permalink: /developer-guide/exercises/
---
Every exercise in Alto’s catalog inherits from `Exercise`. To trace how a new question is made, start with its class in the tree. A direct subclass implements `generate(rng)`. A subclass of `ChoiceExercise` inherits that method and supplies the musical task in `make_question(rng)`.

## Exercise class tree

Each line connects a subclass to its immediate parent. The links open the class definitions in the API reference. Where the catalog uses a different name, it appears beside the class.

- [`Exercise`]({{ '/api/alto.exercises.base/class-exercise/' | relative_url }})
  - [`ChoiceExercise`]({{ '/api/alto.exercises.base/class-choiceexercise/' | relative_url }})
    - [`ArpeggioNames`]({{ '/api/alto.exercises.library/class-arpeggionames/' | relative_url }}) · Arpeggio Identification
    - [`BeatIdentification`]({{ '/api/alto.exercises.library/class-beatidentification/' | relative_url }}) · Beat Identification
    - [`ChordQualities`]({{ '/api/alto.exercises.library/class-chordqualities/' | relative_url }}) · Chord Quality
    - [`CircleOfFifths`]({{ '/api/alto.exercises.library/class-circleoffifths/' | relative_url }}) · Circle of Fifths
    - [`ClefBasics`]({{ '/api/alto.exercises.library/class-clefbasics/' | relative_url }}) · Clef Basics
    - [`KeyboardNotes`]({{ '/api/alto.exercises.library/class-keyboardnotes/' | relative_url }}) · Keyboard Note Identification
    - [`KeySignatures`]({{ '/api/alto.exercises.library/class-keysignatures/' | relative_url }}) · Key Signature Identification
    - [`NotationIdentification`]({{ '/api/alto.exercises.library/class-notationidentification/' | relative_url }}) · Notation Identification
    - [`NoteNames`]({{ '/api/alto.exercises.library/class-notenames/' | relative_url }}) · Note Identification
    - [`RythmicEquations`]({{ '/api/alto.exercises.library/class-rythmicequations/' | relative_url }}) · Rythmic Equations
    - [`PackExercise`]({{ '/api/alto.exercises.packs/class-packexercise/' | relative_url }})
      - One class per installed pack exercise, such as `pack.viola.first-position` (Viola Note Identification)
  - [`BeatConstruction`]({{ '/api/alto.exercises.library/class-beatconstruction/' | relative_url }}) · Beat Construction
  - [`IntervalConstruction`]({{ '/api/alto.exercises.library/class-intervalconstruction/' | relative_url }}) · Interval Construction
  - [`IntervalNames`]({{ '/api/alto.exercises.library/class-intervalnames/' | relative_url }}) · Interval Identification
  - [`KeyboardIntervals`]({{ '/api/alto.exercises.library/class-keyboardintervals/' | relative_url }}) · Keyboard Interval Identification
  - [`KeySignatureConstruction`]({{ '/api/alto.exercises.library/class-keysignatureconstruction/' | relative_url }}) · Key Signature Construction
  - [`NoteConstruction`]({{ '/api/alto.exercises.library/class-noteconstruction/' | relative_url }}) · Note Construction
  - [`OrderOfKeys`]({{ '/api/alto.exercises.library/class-orderofkeys/' | relative_url }}) · Order of Keys
  - [`ScaleConstruction`]({{ '/api/alto.exercises.library/class-scaleconstruction/' | relative_url }}) · Scale Construction
  - [`ScaleIdentification`]({{ '/api/alto.exercises.library/class-scaleidentification/' | relative_url }}) · Scale Identification
{: .exercise-tree }

## Question generation

**Shared behavior.** `Exercise` defines the catalog metadata and the contract for generating a `Question`. It also provides defaults for instructions, finding distinct practice items, and reviewing saved questions. The `Question` carries the prompt, the expected answer, and the data needed to display it. `ExerciseView` is the Qt widget that presents the question and handles learner input. [Question API]({{ '/api/alto.exercises.base/class-question/' | relative_url }}) · [Exercise view walkthrough]({{ '/developer-guide/exercise-view/' | relative_url }})

**Answer choices.** In Beat Identification, `make_question()` writes two measures, sets the correct meter, and supplies the eligible answer labels. The inherited `ChoiceExercise.generate()` then calls `limit_buttons()`. With **Limited** selected, it samples distractors while keeping the choices needed for a correct answer. Each exercise class has its own button settings. [ChoiceExercise.generate]({{ '/api/alto.exercises.base/class-choiceexercise/#choiceexercisegenerate' | relative_url }})

**Constructed answers.** In Beat Construction, `generate()` supplies the rhythm and the meter. The learner marks beat positions in both measures. Note, Interval, and Scale Construction likewise ask the learner to place notes. Key Signature Construction uses the sharp/flat fork, while Order of Keys asks for the position of each accidental. These exercises inherit directly from `Exercise`. Their editing and submission buttons operate on the answer the learner is building.

## Exceptions to the button pattern

Three built-ins accept button answers and implement their own choice layouts directly on `Exercise`. When changing one of these layouts, start in the exercise’s own generator.

| Exercise | How it builds the choices |
| --- | --- |
| Interval Identification (`IntervalNames`) | The written-interval generator builds the answer pool for the active question, such as interval number, quality, or consonance. Interval Construction shares this generator for its staff material. |
| Keyboard Interval Identification (`KeyboardIntervals`) | The generator finds intervals that fit the keyboard range. Its compact layout splits quality and number into separate groups and accepts alternative spellings. |
| Scale Identification (`ScaleIdentification`) | The generator can ask for the tonic, the mode, or both. For a combined question, **All** offers separate tonic and mode groups, while **Limited** offers complete scale names. |

Two `ChoiceExercise` subclasses also accept input on the staff. **Clef Basics** offers answer buttons for identification and asks the learner to place a clef in construction mode. **Notation Identification** can ask the learner to name a highlighted marking or click a named feature in the music. In their staff-input modes, both classes return a question with an empty `choices` list.

## Registration and instrument packs

Importing `alto.exercises` loads `library.py`, where `@register` adds each built-in class to `REGISTRY` alongside others in its catalog category. The catalog can therefore show Beat Identification and Beat Construction together under **Rhythm** even though they have different immediate parents. For a new built-in with answer choices, start with `ChoiceExercise.make_question()`. For a new placement exercise, start with `Exercise.generate()`. [Adding an exercise]({{ '/development/#adding-an-exercise' | relative_url }})

Instrument packs join the same tree at runtime. For example, the viola pack declares **Viola Note Identification** in `pack.json`. `read_pack()` creates the class `pack.viola.first-position` with `PackExercise` as its parent. `load_packs()` registers that class in the same catalog. The generated class inherits card selection from `PackExercise` and button limiting from `ChoiceExercise`. [Pack loader API]({{ '/api/alto.exercises.packs/function-read_pack/' | relative_url }}) · [Plugin manifest]({{ '/plugins/api/' | relative_url }})
