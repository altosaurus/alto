---
title: alto.learning.database
parent: api
package: alto.learning
permalink: /api/alto.learning.database/
---
{% raw %}
The SQLite store: profiles, every answer given, and what is known about
each question. Pure Python (no Qt).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> db.add_attempt(
...     ada.id,
...     exercise="NoteNames",
...     item_key="k",
...     attempt_no=1,
...     answer="C",
...     correct=True,
...     duration_ms=2000,
...     answered_at=100.0,
... )
>>> db.count_attempts(ada.id)
1
```

## check_snapshot

<div class="api-signature" markdown="1">

```python
def check_snapshot(data: bytes) -> tuple[int, int, int]
```

{% endraw %}{% include api-source.html name="check_snapshot" line=211 %}{% raw %}

</div>

Check that bytes are an intact Alto database that this version can
read, and say what is in it.

**Parameters**

- `data` (*bytes*): A snapshot, as `Database.snapshot` returns it.

**Returns**

- *tuple of (int, int, int)*: The schema version, the number of profiles and the number of answers.

**Raises**

- *ValueError*: If the data is not a SQLite database, is damaged, is not an Alto database, or has a newer schema than this version knows.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> check_snapshot(Database().snapshot()) == (
...     SCHEMA_VERSION,
...     0,
...     0,
... )
True
>>> check_snapshot(b"not a database")
Traceback (most recent call last):
    ...
ValueError: This is not an Alto database.
```

## Profile

<div class="api-signature" markdown="1">

```python
Profile(
    id: int,
    *,
    name: str,
)
```

{% endraw %}{% include api-source.html name="Profile" line=292 %}{% raw %}

</div>

A person who practices: their answers are kept apart from everyone
else's.

**Attributes**

- `id` (*int*): The profile's row number in the database.
- `name` (*str*): The name shown in the interface. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Profile(1, name="Ada")
Profile(id=1, name='Ada')
```

## ItemRecord

<div class="api-signature" markdown="1">

```python
ItemRecord(
    strain: float,
    *,
    seen: int,
    first_try_right: int,
    wrong_attempts: int,
    total_first_ms: int,
    last_seen: float,
    signature: str,
    payload: str,
    item_key: str = '',
)
```

{% endraw %}{% include api-source.html name="ItemRecord" line=316 %}{% raw %}

</div>

What a profile's history says about one question.

**Attributes**

- `strain` (*float*): How much practice the question needs; higher means it comes back sooner.
- `seen` (*int*): How many times the question was shown and answered. Keyword-only.
- `first_try_right` (*int*): How many of those showings were answered right on the first try. Keyword-only.
- `wrong_attempts` (*int*): How many wrong answers there have been in all. Keyword-only.
- `total_first_ms` (*int*): Time to the first answer, summed over the showings, in milliseconds. Keyword-only.
- `last_seen` (*float*): When the question was last answered, as a timestamp. Keyword-only.
- `signature` (*str*): The exercise settings it was asked under; it is only asked again while these are unchanged. Keyword-only.
- `payload` (*str*): The question itself as JSON, so it can be asked again. Keyword-only.
- `item_key` (*str, default ""*): The question's identity. Empty when the record is built to be saved, filled in when it is read back. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> record = ItemRecord(
...     2.0,
...     seen=3,
...     first_try_right=1,
...     wrong_attempts=2,
...     total_first_ms=9000,
...     last_seen=100.0,
...     signature="s",
...     payload="{}",
... )
>>> record.seen
3
```

## Database

<div class="api-signature" markdown="1">

```python
Database(path: str | Path = ':memory:')
```

{% endraw %}{% include api-source.html name="Database" line=377 %}{% raw %}

</div>

The SQLite database behind profiles, answers and per-question
history.

**Attributes**

- `conn` (*sqlite3.Connection*): The open connection, with rows returned as `sqlite3.Row` so columns can be read by name.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()  # in memory; give a path to keep it on disk
>>> db.profiles()
[]
>>> db.add_profile("Ada")
Profile(id=1, name='Ada')
```

**Constructor**

Open the database, creating it and its tables if they do not
exist.

**Parameters**

- `path` (*str or Path, default ":memory:"*): The file to use, whose folder is created if needed, or ":memory:" for a throwaway database.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> db.conn.execute(
...     "PRAGMA user_version"
... ).fetchone()[0] == SCHEMA_VERSION
True
```

### Database.write_transaction

<div class="api-signature" markdown="1">

```python
@contextmanager
def write_transaction() -> Iterator[None]
```

{% endraw %}{% include api-source.html name="Database.write_transaction" line=477 %}{% raw %}

</div>

Share the caller's write transaction or begin one before reading
the state to be updated.

**Yields**

- *None*: Control while the transaction is active.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> with db.write_transaction():
...     print(db.conn.in_transaction)
True
>>> db.conn.in_transaction
False
```

### Database.close

<div class="api-signature" markdown="1">

```python
def close() -> None
```

{% endraw %}{% include api-source.html name="Database.close" line=503 %}{% raw %}

</div>

Close the connection.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> db.close()
```

### Database.snapshot

<div class="api-signature" markdown="1">

```python
def snapshot() -> bytes
```

{% endraw %}{% include api-source.html name="Database.snapshot" line=514 %}{% raw %}

</div>

Return the whole database as bytes: every profile, answer and
question record, exactly as they are now.

**Returns**

- *bytes*: A complete SQLite database, which `restore` can load into another database.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> check_snapshot(db.snapshot()) == (
...     SCHEMA_VERSION,
...     1,
...     0,
... )
True
```

### Database.restore

<div class="api-signature" markdown="1">

```python
def restore(data: bytes) -> None
```

{% endraw %}{% include api-source.html name="Database.restore" line=539 %}{% raw %}

</div>

Replace everything in the database with a snapshot, so it is
exactly as it was when the snapshot was taken.

Profiles, answers and question records that are here now are
gone afterwards, and the ones in the snapshot take their
place with the same ids. A snapshot made by an older version of
Alto is brought up to date.

**Parameters**

- `data` (*bytes*): A snapshot, as `snapshot` returns it.

**Raises**

- *ValueError*: If the data is not an intact Alto database, or was made by a newer version of Alto. The database is not changed.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> source = Database()
>>> ada = source.add_profile("Ada")
>>> target = Database()
>>> _ = target.add_profile("Someone else")
>>> target.restore(source.snapshot())
>>> [p.name for p in target.profiles()]
['Ada']
```

### Database.profiles

<div class="api-signature" markdown="1">

```python
def profiles() -> list[Profile]
```

{% endraw %}{% include api-source.html name="Database.profiles" line=589 %}{% raw %}

</div>

Return every profile, sorted by name without regard to case.

**Returns**

- *list of Profile*: The profiles.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> _ = db.add_profile("ben")
>>> _ = db.add_profile("Ada")
>>> [p.name for p in db.profiles()]
['Ada', 'ben']
```

### Database.profile

<div class="api-signature" markdown="1">

```python
def profile(profile_id: int) -> Profile | None
```

{% endraw %}{% include api-source.html name="Database.profile" line=611 %}{% raw %}

</div>

Return one profile by its id.

**Parameters**

- `profile_id` (*int*): The profile's id.

**Returns**

- *Profile or None*: The profile, or None if there is none with that id.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> # noinspection PyUnresolvedReferences
>>> db.profile(ada.id).name
'Ada'
>>> db.profile(999) is None
True
```

### Database.add_profile

<div class="api-signature" markdown="1">

```python
def add_profile(name: str) -> Profile
```

{% endraw %}{% include api-source.html name="Database.add_profile" line=641 %}{% raw %}

</div>

Create a profile.

**Parameters**

- `name` (*str*): The name. Runs of spaces are collapsed to one, and case does not matter when checking for a duplicate.

**Returns**

- *Profile*: The new profile.

**Raises**

- *ValueError*: If the name is empty, or is already taken.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> db.add_profile("  Ada   Lovelace ")
Profile(id=1, name='Ada Lovelace')
>>> db.add_profile("ada lovelace")
Traceback (most recent call last):
    ...
ValueError: There is already a profile called ada lovelace.
```

### Database.delete_profile

<div class="api-signature" markdown="1">

```python
def delete_profile(profile_id: int) -> None
```

{% endraw %}{% include api-source.html name="Database.delete_profile" line=688 %}{% raw %}

</div>

Delete a profile together with all of its answers and question
history.

**Parameters**

- `profile_id` (*int*): The profile's id.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> db.delete_profile(ada.id)
>>> db.profiles()
[]
```

### Database.get_item

<div class="api-signature" markdown="1">

```python
def get_item(
    profile_id: int,
    *,
    exercise: str,
    item_key: str,
) -> ItemRecord | None
```

{% endraw %}{% include api-source.html name="Database.get_item" line=715 %}{% raw %}

</div>

Return what is known about one question for a profile.

**Parameters**

- `profile_id` (*int*): The profile's id.
- `exercise` (*str*): The exercise's class name. Keyword-only.
- `item_key` (*str*): The question's identity. Keyword-only.

**Returns**

- *ItemRecord or None*: The record, or None if the question has never been answered.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> db.get_item(
...     ada.id,
...     exercise="NoteNames",
...     item_key="k",
... ) is None
True
```

### Database.save_item

<div class="api-signature" markdown="1">

```python
def save_item(
    profile_id: int,
    *,
    exercise: str,
    item_key: str,
    item: ItemRecord,
) -> None
```

{% endraw %}{% include api-source.html name="Database.save_item" line=759 %}{% raw %}

</div>

Store what is known about a question, replacing any earlier
record of it.

**Parameters**

- `profile_id` (*int*): The profile's id.
- `exercise` (*str*): The exercise's class name. Keyword-only.
- `item_key` (*str*): The question's identity. Keyword-only.
- `item` (*ItemRecord*): What to store. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> record = ItemRecord(
...     2.0,
...     seen=1,
...     first_try_right=0,
...     wrong_attempts=1,
...     total_first_ms=3000,
...     last_seen=100.0,
...     signature="s",
...     payload="{}",
... )
>>> db.save_item(
...     ada.id,
...     exercise="NoteNames",
...     item_key="k",
...     item=record,
... )
>>> # noinspection PyUnresolvedReferences
>>> db.get_item(
...     ada.id,
...     exercise="NoteNames",
...     item_key="k",
... ).strain
2.0
```

### Database.add_attempt

<div class="api-signature" markdown="1">

```python
def add_attempt(
    profile_id: int,
    *,
    exercise: str,
    item_key: str,
    attempt_no: int,
    answer: str,
    correct: bool,
    duration_ms: int,
    answered_at: float,
    timing_valid: bool = True,
) -> None
```

{% endraw %}{% include api-source.html name="Database.add_attempt" line=839 %}{% raw %}

</div>

Log one answer, right or wrong.

**Parameters**

- `profile_id` (*int*): The profile's id.
- `exercise` (*str*): The exercise's class name. Keyword-only.
- `item_key` (*str*): The question's identity. Keyword-only.
- `attempt_no` (*int*): 1 for the first answer to this showing of the question, 2 for the second and so on. Keyword-only.
- `answer` (*str*): What was answered. Keyword-only.
- `correct` (*bool*): Whether it was right. Keyword-only.
- `duration_ms` (*int*): How long it took, in milliseconds. Keyword-only.
- `answered_at` (*float*): When it was answered, as a timestamp. Keyword-only.
- `timing_valid` (*bool*): Whether the question remained available for an uninterrupted response.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> db.add_attempt(
...     ada.id,
...     exercise="NoteNames",
...     item_key="k",
...     attempt_no=1,
...     answer="C",
...     correct=False,
...     duration_ms=1500,
...     answered_at=50.0,
... )
>>> [
...     (r["answer"], r["correct"])
...     for r in db.attempts(ada.id)
... ]
[('C', 0)]
```

### Database.attempts

<div class="api-signature" markdown="1">

```python
def attempts(
    profile_id: int,
    *,
    exercise: str | None = None,
) -> list[sqlite3.Row]
```

{% endraw %}{% include api-source.html name="Database.attempts" line=918 %}{% raw %}

</div>

Return all of a profile's answers in the order they were given.

**Parameters**

- `profile_id` (*int*): The profile's id.
- `exercise` (*str or None, default None*): Only answers to this exercise (its class name); every exercise if None. Keyword-only.

**Returns**

- *list of sqlite3.Row*: Every column of each answer.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> for i, name in enumerate(
...     ["NoteNames", "IntervalNames"]
... ):
...     db.add_attempt(
...         ada.id,
...         exercise=name,
...         item_key="k",
...         attempt_no=1,
...         answer="x",
...         correct=True,
...         duration_ms=1000,
...         answered_at=float(i),
...     )
>>> [r["exercise"] for r in db.attempts(ada.id)]
['NoteNames', 'IntervalNames']
>>> [
...     r["exercise"]
...     for r in db.attempts(
...         ada.id, exercise="IntervalNames"
...     )
... ]
['IntervalNames']
```

### Database.attempts_in

<div class="api-signature" markdown="1">

```python
def attempts_in(
    profile_ids: list[int] | None = None,
    *,
    exercise: str | None = None,
    since: float | None = None,
    item_key: str | None = None,
) -> list[sqlite3.Row]
```

{% endraw %}{% include api-source.html name="Database.attempts_in" line=1037 %}{% raw %}

</div>

Return answers given, oldest first, for some profiles, an
exercise and a period.

**Parameters**

- `profile_ids` (*list of int or None, default None*): The profiles to include; every profile if None.
- `exercise` (*str or None, default None*): Only this exercise (its class name); every exercise if None. Keyword-only.
- `since` (*float or None, default None*): Only answers from this timestamp on; the whole history if None. Keyword-only.
- `item_key` (*str or None, default None*): Only answers for this question key. Pass the exercise to identify the question. Keyword-only.

**Returns**

- *list of sqlite3.Row*: Each answer's exercise, attempt number, correctness, duration in milliseconds and time.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> for t in (10.0, 20.0, 30.0):
...     db.add_attempt(
...         ada.id,
...         exercise="NoteNames",
...         item_key="k",
...         attempt_no=1,
...         answer="C",
...         correct=True,
...         duration_ms=1000,
...         answered_at=t,
...     )
>>> [
...     r["answered_at"]
...     for r in db.attempts_in(
...         [ada.id], since=15.0
...     )
... ]
[20.0, 30.0]
```

### Database.first_attempts_per_day

<div class="api-signature" markdown="1">

```python
def first_attempts_per_day(
    profile_ids: list[int] | None = None,
    *,
    exercise: str | None = None,
    since: float | None = None,
) -> dict[str, int]
```

{% endraw %}{% include api-source.html name="Database.first_attempts_per_day" line=1108 %}{% raw %}

</div>

Count the questions first answered on each day, in local time,
counting the days in the database.

**Parameters**

- `profile_ids` (*list of int or None, default None*): The profiles to count; None for all of them.
- `exercise` (*str or None, default None*): Only this exercise's questions; None for every exercise. Keyword-only.
- `since` (*float or None, default None*): Only answers from this time on, in seconds since the epoch. Keyword-only.

**Returns**

- *dict of str to int*: The number of first answers on each day that has any, by the day as "YYYY-MM-DD".

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> for attempt_no in (1, 2, 1):
...     db.add_attempt(
...         ada.id,
...         exercise="NoteNames",
...         item_key="k",
...         attempt_no=attempt_no,
...         answer="C",
...         correct=True,
...         duration_ms=900,
...         answered_at=86_400.0 * 100 + 43_200,
...     )
>>> list(
...     db.first_attempts_per_day(
...         [ada.id]
...     ).values()
... )  # the second try of a question is not counted
[2]
```

### Database.strained_items

<div class="api-signature" markdown="1">

```python
def strained_items(
    profile_ids: list[int] | None = None,
    *,
    exercise: str | None = None,
    since: float | None = None,
    min_strain: float = 0.0,
    limit: int = 10,
) -> list[sqlite3.Row]
```

{% endraw %}{% include api-source.html name="Database.strained_items" line=1172 %}{% raw %}

</div>

Return the questions that need most practice, the same question
from different profiles counted together.

**Parameters**

- `profile_ids` (*list of int or None, default None*): The profiles to include; every profile if None.
- `exercise` (*str or None, default None*): Only this exercise (its class name); every exercise if None. Keyword-only.
- `since` (*float or None, default None*): Only questions last seen from this timestamp on; the whole history if None. Keyword-only.
- `min_strain` (*float, default 0.0*): Leave out questions with less strain than this. Keyword-only.
- `limit` (*int, default 10*): The most questions to return. Keyword-only.

**Returns**

- *list of sqlite3.Row*: Each question's exercise, key, average strain, times seen, wrong attempts and stored payload, most strained first.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> for key, strain in (
...     ("easy", 0.5),
...     ("hard", 4.0),
... ):
...     item = ItemRecord(
...         strain,
...         seen=1,
...         first_try_right=0,
...         wrong_attempts=1,
...         total_first_ms=1000,
...         last_seen=1.0,
...         signature="s",
...         payload="{}",
...     )
...     db.save_item(
...         ada.id,
...         exercise="NoteNames",
...         item_key=key,
...         item=item,
...     )
>>> [
...     r["item_key"]
...     for r in db.strained_items(
...         [ada.id], min_strain=1.0
...     )
... ]
['hard']
```

### Database.count_attempts

<div class="api-signature" markdown="1">

```python
def count_attempts(
    profile_id: int,
    *,
    exercise: str | None = None,
    since: float | None = None,
    until: float | None = None,
) -> int
```

{% endraw %}{% include api-source.html name="Database.count_attempts" line=1260 %}{% raw %}

</div>

Return how many answers a profile has given, optionally of one
exercise and within a period.

**Parameters**

- `profile_id` (*int*): The profile's id.
- `exercise` (*str or None, default None*): Count only answers to this exercise (a class name); all exercises if None. Keyword-only.
- `since` (*float or None, default None*): Count only answers given at or after this time (a timestamp). Keyword-only.
- `until` (*float or None, default None*): Count only answers given before this time (a timestamp). Keyword-only.

**Returns**

- *int*: The number of answers, wrong ones included.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> db.count_attempts(ada.id)
0
>>> for t in (1.0, 5.0, 9.0):
...     db.add_attempt(
...         ada.id,
...         exercise="NoteNames",
...         item_key="k",
...         attempt_no=1,
...         answer="C",
...         correct=True,
...         duration_ms=1000,
...         answered_at=t,
...     )
>>> db.count_attempts(
...     ada.id, since=2.0, until=9.0
... # from the start of the period up to, not including, its end
... )
1
```

### Database.attempt_rows

<div class="api-signature" markdown="1">

```python
def attempt_rows(
    profile_id: int,
    *,
    limit: int = 10000,
    exercise: str | None = None,
    since: float | None = None,
    until: float | None = None,
) -> list[sqlite3.Row]
```

{% endraw %}{% include api-source.html name="Database.attempt_rows" line=1395 %}{% raw %}

</div>

Return the newest answers first, each with the stored question
it was an answer to (if that is still known).

**Parameters**

- `profile_id` (*int*): The profile's id.
- `limit` (*int, default 10000*): The most rows to return. Keyword-only.
- `exercise` (*str or None, default None*): Return only answers to this exercise (a class name); all exercises if None. Keyword-only.
- `since` (*float or None, default None*): Return only answers given at or after this time (a timestamp). Keyword-only.
- `until` (*float or None, default None*): Return only answers given before this time (a timestamp). Keyword-only.

**Returns**

- *list of sqlite3.Row*: Each answer's time, exercise, question key, answer, correctness, attempt number, duration, question payload, and the question's current due timestamp under the active scheduler (NULL if unscheduled).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> for t in (1.0, 2.0):
...     db.add_attempt(
...         ada.id,
...         exercise="NoteNames",
...         item_key="k",
...         attempt_no=1,
...         answer="C",
...         correct=True,
...         duration_ms=1000,
...         answered_at=t,
...     )
>>> [
...     r["answered_at"]
...     for r in db.attempt_rows(ada.id)
... ]
[2.0, 1.0]
>>> [
...     r["answered_at"]
...     for r in db.attempt_rows(
...         ada.id, since=1.5
...     )
... ]
[2.0]
```

### Database.answer_window

<div class="api-signature" markdown="1">

```python
def answer_window(
    profile_id: int,
    *,
    limit: int,
) -> tuple[int, int, int]
```

{% endraw %}{% include api-source.html name="Database.answer_window" line=1476 %}{% raw %}

</div>

Capture the range of attempts for a database browser session.

**Parameters**

- `profile_id` (*int*): The profile whose answers are being browsed.
- `limit` (*int*): The number of recent attempts to include. Keyword-only.

**Returns**

- *tuple of int*: The profile's total count and inclusive lower and upper IDs for its newest `limit` attempts. Later inserts are excluded.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> db.answer_window(db.add_profile("Ada").id, limit=100)
(0, 0, 0)
```

### Database.answer_page

<div class="api-signature" markdown="1">

```python
def answer_page(
    profile_id: int,
    *,
    id_range: tuple[int, int],
    offset: int,
    limit: int,
) -> list[sqlite3.Row]
```

{% endraw %}{% include api-source.html name="Database.answer_page" line=1518 %}{% raw %}

</div>

Read answer details for a slice of the browser's history.

**Parameters**

- `profile_id` (*int*): The profile whose answers are being browsed.
- `id_range` (*tuple of int*): Inclusive ID bounds from `answer_window`. Keyword-only.
- `offset` (*int*): The number of rows to skip. Keyword-only.
- `limit` (*int*): The maximum size of this page. Keyword-only.

**Returns**

- *list of sqlite3.Row*: Up to `limit` answers starting at `offset`, newest time first. The insertion ID breaks ties within a timestamp.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> pid = db.add_profile("Ada").id
>>> _, low, high = db.answer_window(pid, limit=100)
>>> bounds = (low, high)
>>> db.answer_page(pid, id_range=bounds, offset=0, limit=64)
[]
```

### Database.item_rows

<div class="api-signature" markdown="1">

```python
def item_rows(
    profile_id: int,
    *,
    limit: int = 10000,
) -> list[sqlite3.Row]
```

{% endraw %}{% include api-source.html name="Database.item_rows" line=1564 %}{% raw %}

</div>

Return what is known about each of a profile's questions, the
most strained first.

**Parameters**

- `profile_id` (*int*): The profile's id.
- `limit` (*int, default 10000*): The most rows to return. Keyword-only.

**Returns**

- *list of sqlite3.Row*: Every column of each question's record and the active scheduler's due timestamp, or NULL if unscheduled.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> db.item_rows(ada.id)
[]
```

### Database.profile_rows

<div class="api-signature" markdown="1">

```python
def profile_rows() -> list[sqlite3.Row]
```

{% endraw %}{% include api-source.html name="Database.profile_rows" line=1605 %}{% raw %}

</div>

Return every profile with how many answers and questions it has.

**Returns**

- *list of sqlite3.Row*: Each profile's id, name, creation time, number of answers and number of questions, sorted by name.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> _ = db.add_profile("Ada")
>>> [
...     (
...         r["name"],
...         r["attempts"],
...         r["questions"],
...     )
...     for r in db.profile_rows()
... ]
[('Ada', 0, 0)]
```

### Database.replay_candidates

<div class="api-signature" markdown="1">

```python
def replay_candidates(
    profile_id: int,
    *,
    exercise: str,
    signature: str,
    hardest: int = 25,
    random_extra: int = 10,
) -> list[ItemRecord]
```

{% endraw %}{% include api-source.html name="Database.replay_candidates" line=1637 %}{% raw %}

</div>

Return questions asked before under these same settings: the
ones that need most practice, plus a few at random.

**Parameters**

- `profile_id` (*int*): The profile's id.
- `exercise` (*str*): The exercise's class name. Keyword-only.
- `signature` (*str*): The exercise's current settings signature; only questions asked under it qualify. Keyword-only.
- `hardest` (*int, default 25*): How many of the most strained questions to include. Keyword-only.
- `random_extra` (*int, default 10*): How many more to pick at random. Keyword-only.

**Returns**

- *list of ItemRecord*: The questions, each at most once.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> ada = db.add_profile("Ada")
>>> item = ItemRecord(
...     3.0,
...     seen=1,
...     first_try_right=0,
...     wrong_attempts=1,
...     total_first_ms=1000,
...     last_seen=1.0,
...     signature="s1",
...     payload="{}",
... )
>>> db.save_item(
...     ada.id,
...     exercise="NoteNames",
...     item_key="k",
...     item=item,
... )
>>> [
...     row_.item_key
...     for row_ in db.replay_candidates(
...         ada.id,
...         exercise="NoteNames",
...         signature="s1",
...     )
... ]
['k']
>>> db.replay_candidates(
...     ada.id,
...     exercise="NoteNames",
...     signature="other settings",
... )
[]
```
{% endraw %}
