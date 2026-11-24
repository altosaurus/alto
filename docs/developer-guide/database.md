---
title: Database
parent: developer-guide
order: 3
permalink: /developer-guide/database/
---
Alto keeps practice history for all local profiles in one SQLite file. At launch, `Database(database_path())` opens `alto.db` in the application data directory, or `$ALTO_HOME/data/alto.db` when a development directory is set. A new database uses schema version 7, recorded in SQLite’s `PRAGMA user_version`. [Application launch]({{ '/developer-guide/application-launch/' | relative_url }})

A single question can produce several answers. Suppose Ada answers a note question incorrectly after three seconds, then correctly one second later. Alto appends **two** rows to `attempts`, with durations of 3,000 and 1,000 milliseconds. It maintains **one** row in `items` for Ada and that question. After this first showing, the row records one showing, one wrong attempt, zero first-try successes, and 3,000 milliseconds of first-answer time. The attempt log preserves the sequence. The item row gives the scheduler a summary it can use the next time Ada practices.

## Database access

- **Connection and SQL.** `alto.learning.database.Database` uses Python’s standard `sqlite3` module. It opens a connection, enables foreign keys, and issues SQL with bound parameters. Its row factory, `sqlite3.Row`, lets callers read columns by name. Some methods return `Profile` or `ItemRecord` dataclasses. Calling `Database()` without a path creates an in-memory database, which is useful for trying queries in a Python shell. [Database API]({{ '/api/alto.learning.database/#database' | relative_url }})
- **Practice and replay.** `Learner.record()` appends the attempt, reads the old item summary, and inserts or updates the item under its composite key. `Learner.pick()` reads summaries and uses the scheduler to choose among fresh questions and saved questions that match the exercise settings. Python’s `json` module encodes and decodes the saved question. [Learner API]({{ '/api/alto.learning.learner/#learner' | relative_url }})
- **The database browser.** The **Answers**, **Questions**, and **Profiles** tabs present rows from `attempts`, `items`, and `profiles`, respectively. `DatabasePage` requests rows through `Database`. Its Qt table model, `RowsModel`, supplies display values, and a `QSortFilterProxyModel` handles sorting and filtering. [Database browser API]({{ '/api/alto.ui.database_page/#databasepage' | relative_url }})

## Entity–relationship diagram

Each attempt and each item belongs to exactly one profile. A profile may have zero or more of either, and deleting it cascades to both tables. The solid lines show those foreign keys. The dashed line shows how Alto looks up an item summary for an attempt. Many attempts can match the same summary, but an attempt can match at most one because the join uses the item’s full primary key. Select a table to jump to its dictionary.

{% include database-schema.html %}

## Data dictionary

The tables below follow the column order in `alto/learning/database.py`. The introduction date is optional for cards first practiced with ASRS. SQLite supplies the integer primary keys when Alto inserts a profile or an attempt. The four item counters have explicit defaults of zero. Times ending in `_at`, along with `last_seen`, are Unix timestamps in seconds. Durations use milliseconds.

### Profiles

One row per local practice profile.

| Column | SQLite type | Key or default | Meaning |
|---|---|---|---|
| `id` | INTEGER | Primary key | Profile identifier used by both history tables. |
| `name` | TEXT | Unique, `COLLATE NOCASE` | Display name. Alto trims and collapses whitespace before insertion. SQLite’s case-insensitive comparison treats names such as Ada and ada as duplicates. |
| `created_at` | REAL | | Time the profile was created. |
| `scheduler` | TEXT | Default `Alto` | The profile’s selected question scheduler. ASRS retains its original database identifier, `Alto`. |
| `self_grading` | INTEGER | Default 0 | Whether this profile rates correct answers in SM-2 and FSRS. |
| `easy_percent` | INTEGER | Default 15 | Fastest share of correct first answers graded Easy, in percent. |
| `hard_percent` | INTEGER | Default 15 | Slowest share graded Hard, in percent. |

### Attempts

One row per submitted answer, including each retry. The `attempts_by_item` index covers `(profile_id, exercise, item_key)`. The browser uses these three columns in a left join to obtain the question payload when an item summary exists. The `attempts_by_time` index covers `(profile_id, answered_at)`, for a profile's answers since a date, which the statistics read. It is created when the database opens rather than in a schema version, since an index changes no data and an older Alto can still open the file.

| Column | SQLite type | Key or default | Meaning |
|---|---|---|---|
| `id` | INTEGER | Primary key | Identifier for this submission. |
| `profile_id` | INTEGER | Foreign key → `profiles.id` | Profile that submitted the answer. |
| `exercise` | TEXT | | Python class name of the exercise, such as `NoteNames`. |
| `item_key` | TEXT | | Stable 20-character hexadecimal identifier returned by `Question.item_key()`. Reordering the answer buttons preserves this identifier. |
| `attempt_no` | INTEGER | | Submission number within this showing of the question, starting at 1. |
| `answer` | TEXT | | The answer the learner submitted. |
| `correct` | INTEGER | | Alto writes 1 for a correct answer and 0 for an incorrect answer. |
| `duration_ms` | INTEGER | | Elapsed time from presentation to the first answer, or from the preceding answer to a retry. |
| `answered_at` | REAL | | Time the answer was submitted. |
| `timing_valid` | INTEGER | Default 1 | Set to zero when the exercise was hidden or Alto lost focus during the question. Older attempts retain their recorded times. |

### Items

One row per distinct question practiced by a particular profile within an exercise. The first three columns together form the primary key. They also identify the submissions contributing to this summary. SQLite enforces the foreign key to `profiles`. Alto maintains the correspondence with `attempts` when it records an answer.

| Column | SQLite type | Key or default | Meaning |
|---|---|---|---|
| `profile_id` | INTEGER | Primary key (1), foreign key → `profiles.id` | Profile whose history this row summarizes. |
| `exercise` | TEXT | Primary key (2) | Exercise class name, as in `attempts.exercise`. |
| `item_key` | TEXT | Primary key (3) | Question identifier, as in `attempts.item_key`. |
| `strain` | REAL | | Scheduler score updated after each submission. A higher value gives the question more weight in later practice. |
| `seen` | INTEGER | Default 0 | Showings for which a first answer was submitted. A retry leaves this count unchanged. |
| `first_try_right` | INTEGER | Default 0 | Showings answered correctly on the first attempt. |
| `wrong_attempts` | INTEGER | Default 0 | Incorrect submissions across all showings, including retries. |
| `total_first_ms` | INTEGER | Default 0 | Sum of first-answer durations across showings, in milliseconds. |
| `last_seen` | REAL | | Time of the most recent submission for this item, including a retry. |
| `signature` | TEXT | | Identifier returned by `settings_signature()` for the most recently recorded exercise settings. Used to find eligible replay candidates. |
| `payload` | TEXT | | JSON from `Question.to_dict()` for the most recently recorded question. Alto uses it for replay and answer previews. |

### Practice cards

Each row identifies a calendar practice card. Version 6 removes adaptive-only entries from this table and retains their answer history in `items` and `attempts`.

| Column | SQLite type | Meaning |
|---|---|---|
| `profile_id`, `exercise`, `item_key` | INTEGER, TEXT, TEXT | Composite primary key. Deleting the profile removes its cards. |
| `signature`, `payload` | TEXT, TEXT | Exercise settings and playable question at introduction. |
| `introduced_on` | TEXT | Local date of a calendar introduction. May be empty for scheduled cards imported by older versions. |
| `pending_new` | INTEGER | 1 until the first answer to a new introduction, then 0. |

### Review schedules

A practice card can have a separate schedule for SM-2 and FSRS. On entry to a calendar scheduler, missing schedules are initialized from the other calendar scheduler for that profile. The inherited row preserves the due timestamp and last grade, with the state translated for its new scheduler. Existing schedules resume independently.

| Column | SQLite type | Meaning |
|---|---|---|
| `profile_id`, `exercise`, `item_key` | INTEGER, TEXT, TEXT | Composite foreign key referencing the practice card, with cascading deletion. |
| `scheduler` | TEXT | Together with the card identity, this forms the primary key. |
| `due` | REAL | Unix timestamp of the next review. |
| `state` | TEXT | Automatic SM-2 stores repetitions, interval and ease. Self-graded SM-2 also stores the learning phase, step and scheduled delay. FSRS stores its serialized card. |
| `last_rating` | INTEGER | The most recent grade (1 Again, 2 Hard, 3 Good, 4 Easy). Again marks a missed card for the red counter. |

### Practice limits

| Column | Type | Meaning |
| --- | --- | --- |
| `profile_id` | INTEGER | Owning profile. Part of the primary key with `exercise`. |
| `exercise` | TEXT | Exercise class name, or an empty string for the profile defaults. |
| `new_cards` | INTEGER | Daily new-card allowance. Zero pauses introductions, −1 allows unlimited introductions, and NULL inherits the default. |
| `reviews` | INTEGER | Daily review allowance. Zero pauses reviews, −1 allows unlimited reviews, and NULL inherits the default. |

### Daily reviews

| Column | Type | Meaning |
| --- | --- | --- |
| `profile_id` | INTEGER | Owning profile. |
| `exercise` | TEXT | Exercise class name. |
| `day` | TEXT | Local date. Together with profile and exercise, identifies the row. |
| `completed` | INTEGER | Reviews graded that day across SM-2 and FSRS. |
