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

## CalendarPractice

```python
CalendarPractice(db: Database)
```

Prepare daily exercise queues and store each scheduler's review dates.

**Examples**

```pycon
>>> practice = CalendarPractice(Database())
>>> practice.db.profiles()
[]
```

**Constructor**

Attach the queues to an Alto database.

**Parameters**

- `db` (*Database*): Database containing the profile and its cards.

**Constructor examples**

```pycon
>>> CalendarPractice(Database())._batches
{}
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

- *tuple of int and int*: New cards and completed reviews allowed per exercise per local day.

**Examples**

```pycon
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

```pycon
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
- `new_cards` (*int or None*): Daily introductions, or None to inherit.
- `reviews` (*int or None*): Daily reviews, or None to inherit.

**Examples**

```pycon
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

```pycon
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

```pycon
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

```pycon
>>> from alto.exercises.library import NoteNames
>>> db = Database()
>>> CalendarPractice(db).counts(NoteNames(), profile=db.add_profile("Ada").id, mode="SM-2", now=100)[1] > 0
True
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

```pycon
>>> from alto.exercises.library import ChordQualities
>>> db = Database()
>>> practice = CalendarPractice(db)
>>> question = practice.take(ChordQualities(), profile=db.add_profile("Ada").id, mode="SM-2", now=1000)
>>> isinstance(question, Question)
True
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
) -> None
```

Reschedule a card from the first submission to this presentation.

**Parameters**

- `exercise` (*str*): Exercise class name.
- `profile` (*int*): Active profile ID.
- `key` (*str*): Stable card identity.
- `mode` (*str*): Scheduler selected for this review.
- `correct` (*bool*): Whether the first submission was correct.
- `now` (*float*): Answer timestamp.

**Examples**

```pycon
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
