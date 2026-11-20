---
title: alto.learning.learner
parent: api
package: alto.learning
permalink: /api/alto.learning.learner/
---
{% raw %}
Ties the profile, the database and the scheduler together for the exercise screen.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> db = Database()
>>> learner = Learner(db, profile=db.add_profile("Ada"))
>>> question = learner.pick(NoteNames(), rng=random.Random(1))
>>> question.answer in question.choices
True
```

## PracticeComplete

```python
PracticeComplete(retry_at: float | None = None)
```

Bases: `Exception`

The current exercise has no scheduled cards available.

**Examples**

```pycon
>>> issubclass(PracticeComplete, Exception)
True
```

**Constructor**

Carry the next missed card's due time to the exercise screen.

**Parameters**

- `retry_at` (*float or None*): Scheduled timestamp, or None when practice is finished for now.

**Constructor examples**

```pycon
>>> PracticeComplete().retry_at is None
True
```

## Learner

```python
Learner(
    db: Database,
    *,
    profile: Profile,
)
```

Chooses what a profile is asked next and records how it was answered.

**Attributes**

- `FRESH` (*int*): How many new questions are generated for each pick, alongside the ones asked before.
- `db` (*Database*): Where answers and what is known about each question are stored.
- `profile` (*Profile*): Whose answers these are.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> db = Database()
>>> learner = Learner(db, profile=db.add_profile("Ada"))
>>> rng = random.Random(2)
>>> question = learner.pick(NoteNames(), rng=rng)
>>> learner.record(NoteNames(), question=question, answer=question.answer, correct=True, attempt_no=1, seconds=2.5)
>>> db.count_attempts(learner.profile.id)
1
```

**Constructor**

Create a learner for one profile.

**Parameters**

- `db` (*Database*): The database to read and write.
- `profile` (*Profile*): The profile that is practicing. Keyword-only.

**Constructor examples**

```pycon
>>> database = Database()
>>> learner = Learner(database, profile=database.add_profile("Ada"))
>>> learner.profile.name
'Ada'
```

### Learner.set_profile

```python
def set_profile(profile: Profile) -> None
```

Open a profile's practice queues and resume its selected scheduler.

**Parameters**

- `profile` (*Profile*): Profile loaded at launch, selected in the app, or restored from backup.

**Examples**

```pycon
>>> db = Database()
>>> learner = Learner(db, profile=db.add_profile("Ada"))
>>> learner.set_profile(db.add_profile("Ben"))
>>> learner.profile.name
'Ben'
```

### Learner.mode

```python
@property
def mode() -> str
```

Return this profile's question scheduler.

**Returns**

- *str*: ASRS, ARTS, SM-2 or FSRS.

**Examples**

```pycon
>>> db = Database()
>>> Learner(db, profile=db.add_profile("Ada")).mode
'ASRS'
```

### Learner.self_grading

```python
@property
def self_grading() -> bool
```

Read the profile's SM-2 and FSRS grading preference.

**Returns**

- *bool*: Whether a correct answer waits for a grade.

**Examples**

```pycon
>>> db = Database()
>>> Learner(db, profile=db.add_profile("Ada")).self_grading
False
```

### Learner.response_times

```python
def response_times(exercise: str) -> ResponseTimes
```

Read the rolling sample for one exercise and the current profile's thresholds.

**Parameters**

- `exercise` (*str*): Registered exercise class name.

**Returns**

- *ResponseTimes*: Up to 100 recent, uninterrupted, correct first answers across practice modes.

**Examples**

```pycon
>>> db = Database()
>>> Learner(db, profile=db.add_profile("Ada")).response_times("KeyboardNotes").times
()
```

### Learner.set_speed_thresholds

```python
def set_speed_thresholds(
    *,
    easy: int,
    hard: int,
) -> None
```

Save the two tail percentages for this profile.

**Parameters**

- `easy` (*int*): Percentage of fastest correct answers.
- `hard` (*int*): Percentage of slowest correct answers.

**Raises**

- *ValueError*: If the bands overlap or a percentage is negative.

**Examples**

```pycon
Setting both tails to zero assigns Good to every correct first answer.
```

### Learner.set_self_grading

```python
def set_self_grading(enabled: bool) -> None
```

Choose how this profile grades correct calendar reviews.

**Parameters**

- `enabled` (*bool*): Show Hard, Good, and Easy after a correct answer.

**Examples**

```pycon
>>> db = Database()
>>> learner = Learner(db, profile=db.add_profile("Ada"))
>>> learner.set_self_grading(True)
>>> learner.self_grading
True
```

### Learner.set_mode

```python
def set_mode(mode: str) -> None
```

Select the question scheduler for this profile.

**Parameters**

- `mode` (*str*): Scheduler name.

**Raises**

- *ValueError*: For an unsupported scheduler.

**Examples**

```pycon
>>> db = Database()
>>> learner = Learner(db, profile=db.add_profile("Ada"))
>>> learner.set_mode("FSRS")
>>> learner.mode
'FSRS'
```

### Learner.pick

```python
def pick(
    exercise: Exercise,
    *,
    rng: random.Random,
    avoid: str | None = None,
    now: float | None = None,
) -> Question
```

Return the next eligible question using the profile's selected scheduler.

**Parameters**

- `exercise` (*Exercise*): The exercise being practiced.
- `rng` (*random.Random*): The random number generator used to make new questions and to draw one. Keyword-only.
- `avoid` (*str or None, default None*): The `item_key` of the question just asked, so it does not come straight back. Keyword-only.
- `now` (*float or None, default None*): The current time as a timestamp; the clock is used if None. Keyword-only.

**Returns**

- *Question*: The question to ask.

**Raises**

- *PracticeComplete*: If the calendar scheduler has no cards currently available.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> db = Database()
>>> learner = Learner(db, profile=db.add_profile("Ada"))
>>> first = learner.pick(NoteNames(), rng=random.Random(3))
>>> second = learner.pick(NoteNames(), rng=random.Random(3), avoid=first.item_key())
>>> second.item_key() != first.item_key()
True
```

### Learner.record

```python
def record(
    exercise: Exercise,
    *,
    question: Question,
    answer: str,
    correct: bool,
    attempt_no: int,
    seconds: float,
    now: float | None = None,
    preview: ReviewInterval | None = None,
    passing_previews: dict[Rating, ReviewInterval] | None = None,
    self_grading: bool = False,
    timing_valid: bool = True,
) -> ReviewInterval | None
```

Log one answer and update what is known about the question.

**Parameters**

- `exercise` (*Exercise*): The exercise being practiced.
- `question` (*Question*): The question that was answered. Keyword-only.
- `answer` (*str*): What was answered. Keyword-only.
- `correct` (*bool*): Whether the answer was right. Keyword-only.
- `attempt_no` (*int*): 1 for the first answer to this showing of the question, 2 for the second and so on. Keyword-only.
- `seconds` (*float*): How long the answer took. Keyword-only.
- `now` (*float or None, default None*): When it was answered, as a timestamp; the clock is used if None. Keyword-only.
- `preview` (*ReviewInterval or None*): Correct-answer interval displayed for this question.
- `passing_previews` (*dict or None*): Hard, Good, and Easy intervals shown during speed grading.
- `self_grading` (*bool*): Defer scheduling a correct calendar answer until the learner rates it.
- `timing_valid` (*bool*): Whether the presentation was uninterrupted. False excludes it from timing.

**Returns**

- *ReviewInterval or None*: The interval chosen by speed grading, once enough earlier answers exist.

**Examples**

```pycon
>>> from alto.exercises.library import NoteNames
>>> db = Database()
>>> learner = Learner(db, profile=db.add_profile("Ada"))
>>> q = learner.pick(NoteNames(), rng=random.Random(4))
>>> learner.record(NoteNames(), question=q, answer="?", correct=False, attempt_no=1, seconds=3.0)
>>> learner.record(NoteNames(), question=q, answer=q.answer, correct=True, attempt_no=2, seconds=1.0)
>>> [row["correct"] for row in db.attempts(learner.profile.id)]
[0, 1]
>>> # noinspection PyUnresolvedReferences
>>> db.get_item(learner.profile.id, exercise="NoteNames", item_key=q.item_key()).wrong_attempts
1
```
{% endraw %}
