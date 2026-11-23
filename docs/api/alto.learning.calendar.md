---
title: alto.learning.calendar
parent: api
package: alto.learning
permalink: /api/alto.learning.calendar/
---
{% raw %}
Daily exercise queues for SM-2 and FSRS.

The scheduler controls when an introduced card is due. Each exercise supplies new
questions under its current settings. Counting a prepared question does not introduce it.

## ReviewInterval

```python
ReviewInterval(
    seconds: int,
    identity: tuple[int, str, str, str],
    previous_state: str | None,
    rating: Rating = Rating.Good,
    graded_state: str | None = None,
    previous_due: float | None = None,
)
```

A preview of one rating for a card in its current scheduling state.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ReviewInterval(600, (1, "NoteNames", "abc", "FSRS"), None).seconds
600
```

### ReviewInterval.duration

```python
@property
def duration() -> str
```

Format a review interval for display above a grade button or beside the music.

**Returns**

- *str*: A whole-day interval or a short learning step in minutes and seconds.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ReviewInterval(330, (1, "NoteNames", "abc", "FSRS"), None).duration
'5 min 30 s'
```

## CalendarPractice

```python
CalendarPractice(db: Database)
```

Prepare daily exercise queues and store each scheduler's review dates.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> practice = CalendarPractice(Database())
>>> practice.db.profiles()
[]
```

**Constructor**

Attach the queues to an Alto database.

**Parameters**

- `db` (*Database*): Database containing the profile and its cards.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CalendarPractice(Database())._batches
{}
```

### CalendarPractice.inherit_schedules

```python
def inherit_schedules(
    profile: int,
    *,
    mode: str,
) -> None
```

Initialize missing schedules for this profile from the other calendar scheduler.

**Parameters**

- `profile` (*int*): Profile entering calendar practice.
- `mode` (*str*): Selected scheduler. Adaptive practice uses no calendar schedules.

**Examples**

```text
Switching to FSRS carries over an SM-2 due date without consuming a review.
```

### CalendarPractice.limits

```python
def limits(
    profile: int,
    *,
    exercise: str = '',
) -> tuple[int, int]
```

Return the effective daily new-card and review limits.

**Parameters**

- `profile` (*int*): Profile whose settings to read.
- `exercise` (*str*): Exercise class name, or an empty string for profile defaults.

**Returns**

- *tuple of int and int*: New cards and completed reviews allowed per exercise per local day. UNLIMITED removes the cap.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CalendarPractice(Database()).limits(1)
(10, 200)
```

### CalendarPractice.overrides

```python
def overrides(
    profile: int,
    *,
    exercise: str,
) -> tuple[int | None, int | None]
```

Read the two explicitly saved limits for an exercise.

**Parameters**

- `profile` (*int*): Active profile.
- `exercise` (*str*): Exercise class name.

**Returns**

- *tuple*: A number for each override, or None for each inherited value.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CalendarPractice(Database()).overrides(1, exercise="NoteNames")
(None, None)
```

### CalendarPractice.set_limits

```python
def set_limits(
    profile: int,
    *,
    exercise: str = '',
    new_cards: int | None,
    reviews: int | None,
) -> None
```

Save the profile defaults or an exercise's individual overrides.

**Parameters**

- `profile` (*int*): Active profile.
- `exercise` (*str*): Exercise class name, or an empty string for the profile defaults.
- `new_cards` (*int or None*): Daily introductions, UNLIMITED for no cap, or None to inherit.
- `reviews` (*int or None*): Daily reviews, UNLIMITED for no cap, or None to inherit.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> practice = CalendarPractice(db)
>>> profile = db.add_profile("Ada").id
>>> practice.set_limits(profile, new_cards=5, reviews=30)
>>> practice.limits(profile, exercise="NoteNames")
(5, 30)
```

### CalendarPractice.reset_limits

```python
def reset_limits(profile: int) -> None
```

Restore the profile defaults and remove its exercise overrides.

**Parameters**

- `profile` (*int*): Profile whose limits to reset.

**Examples**

```text
Restoring defaults keeps the day's introductions and completed reviews.
```

### CalendarPractice.queue

```python
def queue(
    exercise: Exercise,
    *,
    profile: int,
    mode: str,
    now: float,
) -> tuple[list[Question], list[Question]]
```

Find due reviews and prepare the remaining new cards for this local day.

**Parameters**

- `exercise` (*Exercise*): Exercise with its current settings.
- `profile` (*int*): Active profile ID.
- `mode` (*str*): Calendar scheduler whose due dates apply.
- `now` (*float*): Current timestamp.

**Returns**

- *tuple of list of Question and list of Question*: Due reviews, oldest first, and new questions available for introduction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> due, new = CalendarPractice(db).queue(NoteNames(), profile=ada.id, mode="FSRS", now=1000)
>>> not due and len(new) == DAILY_NEW
True
```

### CalendarPractice.counts

```python
def counts(
    exercise: Exercise,
    *,
    profile: int,
    mode: str,
    now: float,
) -> tuple[int, int]
```

Count due reviews and unseen cards available with the selected settings.

**Parameters**

- `exercise` (*Exercise*): Exercise shown on the tile.
- `profile` (*int*): Active profile.
- `mode` (*str*): Calendar scheduler.
- `now` (*float*): Current timestamp.

**Returns**

- *tuple of int and int*: Due and new counts. Exact catalogs can be counted without rendering their cards.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> db = Database()
>>> CalendarPractice(db).counts(NoteNames(), profile=db.add_profile("Ada").id, mode="SM-2", now=100)[1] > 0
True
```

### CalendarPractice.tile_counts

```python
def tile_counts(
    exercise: Exercise,
    *,
    profile: int,
    mode: str,
    now: float,
) -> tuple[int, int, int]
```

Count available reviews, new cards, and missed cards awaiting a correct review.

**Parameters**

- `exercise` (*Exercise*): Exercise with the current settings.
- `profile` (*int*): Active profile ID.
- `mode` (*str*): Active calendar scheduler.
- `now` (*float*): Current timestamp.

**Returns**

- *tuple of int, int, int*: Due reviews, available new cards, and outstanding incorrect cards. A due retry counts in both review totals.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> db = Database()
>>> CalendarPractice(db).tile_counts(NoteNames(), profile=db.add_profile("Ada").id, mode="SM-2", now=100)[2]
0
```

### CalendarPractice.study_counts

```python
def study_counts(
    exercise: Exercise,
    *,
    profile: int,
    mode: str,
    now: float,
    current_key: str | None = None,
) -> tuple[tuple[int, int, int], str | None]
```

Count the exercise queues and identify the queue of the question on screen.

**Parameters**

- `exercise` (*Exercise*): Exercise with the current settings.
- `profile` (*int*): Active profile ID.
- `mode` (*str*): Active calendar scheduler.
- `now` (*float*): Current timestamp.
- `current_key` (*str or None*): Item key of the question awaiting an answer.

**Returns**

- *tuple*: The same review, new, and incorrect counts as the tiles, plus the current queue if a question is active.

**Examples**

```text
A missed card that comes due again is underlined as incorrect during its retry.
```

### CalendarPractice.take

```python
def take(
    exercise: Exercise,
    *,
    profile: int,
    mode: str,
    now: float,
) -> Question | None
```

Take the first eligible card, recording a new introduction only when served.

**Parameters**

- `exercise` (*Exercise*): Exercise being opened or advanced.
- `profile` (*int*): Active profile ID.
- `mode` (*str*): Active calendar scheduler.
- `now` (*float*): Presentation timestamp.

**Returns**

- *Question or None*: Next question, or None once the available work is finished.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import ChordQualities
>>> db = Database()
>>> practice = CalendarPractice(db)
>>> question = practice.take(ChordQualities(), profile=db.add_profile("Ada").id, mode="SM-2", now=1000)
>>> isinstance(question, Question)
True
```

### CalendarPractice.take_or_wait

```python
def take_or_wait(
    exercise: Exercise,
    *,
    profile: int,
    mode: str,
    now: float,
    avoid: str | None = None,
    wait_learning: bool = False,
) -> tuple[Question | None, float | None]
```

Draw an eligible card or return the time when a missed card can be reviewed.

**Parameters**

- `exercise` (*Exercise*): Exercise with the current settings.
- `profile` (*int*): Active profile ID.
- `mode` (*str*): Active calendar scheduler.
- `now` (*float*): Presentation timestamp.
- `avoid` (*str or None*): Prefer another available card to the one just shown.
- `wait_learning` (*bool*): Also wake the exercise when a correctly answered learning card comes due.

**Returns**

- *tuple*: The next question and, when the queue is waiting for a retry, its due timestamp.

**Examples**

```text
A single missed card can wake the exercise when its learning step expires.
```

### CalendarPractice.introduce

```python
def introduce(
    exercise: Exercise,
    *,
    profile: int,
    question: Question,
    now: float,
) -> None
```

Register a calendar introduction once, in the caller's draw or answer transaction.

**Parameters**

- `exercise` (*Exercise*): Exercise that supplied this question.
- `profile` (*int*): Practicing profile.
- `question` (*Question*): New or previously introduced question.
- `now` (*float*): Time of introduction.

**Examples**

```text
Answering a pending card keeps its original introduction day.
```

### CalendarPractice.correct_interval

```python
def correct_interval(
    exercise: str,
    *,
    profile: int,
    key: str,
    mode: str,
    now: float,
) -> ReviewInterval
```

Preview the next correct answer without grading the card.

**Parameters**

- `exercise` (*str*): Exercise class name.
- `profile` (*int*): Active profile ID.
- `key` (*str*): Card identity.
- `mode` (*str*): Calendar scheduler.
- `now` (*float*): Presentation timestamp.

**Returns**

- *ReviewInterval*: Delay to display and reuse when the answer is submitted.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CalendarPractice(Database()).correct_interval("NoteNames", profile=1, key="abc", mode="FSRS", now=1000).seconds
600
```

### CalendarPractice.passing_intervals

```python
def passing_intervals(
    exercise: str,
    *,
    profile: int,
    key: str,
    mode: str,
    now: float,
    displayed: dict[Rating, ReviewInterval] | None = None,
) -> dict[Rating, ReviewInterval]
```

Preview the three passing outcomes from one snapshot of this card.

**Parameters**

- `exercise` (*str*): Exercise class name.
- `profile` (*int*): Active profile.
- `key` (*str*): Card identity.
- `mode` (*str*): Calendar scheduler.
- `now` (*float*): Presentation or answer timestamp.
- `displayed` (*dict or None*): Previously displayed outcomes to reuse while this card's schedule is current.

**Returns**

- *dict*: Passing grades and their previews, including the state to save.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> practice = CalendarPractice(Database())
>>> practice.passing_intervals("NoteNames", profile=1, key="abc", mode="SM-2", now=0)[Rating.Good].seconds
600
```

### CalendarPractice.grade

```python
def grade(
    exercise: str,
    *,
    profile: int,
    key: str,
    mode: str,
    correct: bool,
    now: float,
    manual_rating: Rating | None = None,
    preview: ReviewInterval | None = None,
) -> None
```

Reschedule a card from the first submission to this presentation.

**Parameters**

- `exercise` (*str*): Exercise class name.
- `profile` (*int*): Active profile ID.
- `key` (*str*): Stable card identity.
- `mode` (*str*): Scheduler selected for this review.
- `correct` (*bool*): Whether the first submission was correct.
- `manual_rating` (*Rating or None*): Explicit grade from a button or response time. None uses the original automatic schedule.
- `now` (*float*): Answer timestamp.
- `preview` (*ReviewInterval or None*): Correct-answer interval shown for this presentation.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises.library import NoteNames
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> practice = CalendarPractice(db)
>>> question = practice.take(NoteNames(), profile=ada.id, mode="SM-2", now=1000)
>>> practice.grade("NoteNames", profile=ada.id, key=question.item_key(), mode="SM-2", correct=True, now=1002)
>>> db.conn.execute("SELECT due FROM review_schedules").fetchone()[0]
87402.0
```
{% endraw %}
