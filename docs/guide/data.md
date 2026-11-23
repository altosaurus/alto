---
title: Data and persistence
parent: guide
order: 10
permalink: /guide/data/
---
Alto keeps two kinds of stored information in two places, and keeps the code that touches them apart. This chapter explains
what is stored where and why, how the SQLite database is used, and, most important for the long run, how to change the
database structure without losing anyone's practice history.

## Two stores

| Kind | Where | Written by | Contains |
|---|---|---|---|
| **History** | one SQLite file, `alto.db`, in the user's data folder | `alto/learning/database.py` | profiles, every answer, what is known about each question |
| **Preferences** | `QSettings("alto", "alto")`, in the user's configuration folder | `alto/ui/store.py` and the `save_*` functions in `alto/ui/exercise_settings.py` and the theme, notation, keyboard and instrument modules | theme, notation font, keyboard style, instrument, each exercise's settings, sidebar width, the profile used last |

The split is by *nature*: history is a large and growing table of facts you can query, so it belongs in a database.
Preferences are a few dozen small values, so they belong in the platform's settings mechanism. [Your data]({{ '/data/' | relative_url }})
tells users where both are. The settings objects in `alto/settings.py` are plain data and never save themselves; saving is a UI
concern, so `alto/learning`, `alto/exercises` and `alto/theory` never touch the disk except through `Database`.

## SQLite in one page

SQLite is a database that is a library, not a server: a database is one file, and your program reads and writes it directly.
Python includes it as the standard `sqlite3` module. It is the right tool for a single-user desktop program.

Concepts the code relies on:

- **Tables, rows, columns, and a primary key** that identifies a row. `PRAGMA foreign_keys = ON` (set on every connection, because
  SQLite's default is *off*) makes a **foreign key** enforced: `attempts.profile_id REFERENCES profiles(id) ON DELETE CASCADE`
  means deleting a profile deletes its attempts and items.
- **SQL** with **parameters**: `execute("SELECT ... WHERE profile_id = ?", (profile_id,))`. The `?` is filled by the library, never by
  string formatting your values in. That is what prevents **SQL injection**, and it is a rule with one narrow exception: in
  `database.py` a few queries build a `WHERE` clause from *fixed strings in the code*, never from user text, and
  still pass every value as a parameter.
- **Transactions.** `with self.conn:` groups statements so they all happen or none do, and commits at the end. Alto writes the
  attempt, item summary and any review schedule update in one transaction in `Learner.record`.
- **Indexes.** `CREATE INDEX attempts_by_item ON attempts(profile_id, exercise, item_key)` makes "find all attempts for this
  question" fast. Without it SQLite reads every row. An index can also be the slower way: `EXPLAIN QUERY PLAN` shows which one
  SQLite picked. The database page's newest answers are found faster by walking the table from its end and stopping at the
  limit, so that query writes `+a.profile_id`, which keeps SQLite from using an index for that column.
- **`sqlite3.Row`** (`conn.row_factory = sqlite3.Row`) lets you read a column by name: `row["strain"]`.
- **In-memory databases.** `Database()` with no path uses `":memory:"`: a fresh database that vanishes when closed. Every test
  and every doctest uses one, and the simulation in [Spaced repetition]({{ '/guide/spaced-repetition/' | relative_url }}) does too.

## The schema

```sql
CREATE TABLE profiles (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE, created_at REAL NOT NULL);

CREATE TABLE attempts (                      -- one row per answer, wrong ones included
    id INTEGER PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    exercise TEXT NOT NULL, item_key TEXT NOT NULL,
    attempt_no INTEGER NOT NULL,             -- 1 for the first answer to this showing of the question
    answer TEXT NOT NULL, correct INTEGER NOT NULL,
    duration_ms INTEGER NOT NULL, answered_at REAL NOT NULL
);

CREATE TABLE items (                         -- one row per question per profile: the current state
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    exercise TEXT NOT NULL, item_key TEXT NOT NULL,
    strain REAL NOT NULL, seen INTEGER NOT NULL DEFAULT 0, first_try_right INTEGER NOT NULL DEFAULT 0,
    wrong_attempts INTEGER NOT NULL DEFAULT 0, total_first_ms INTEGER NOT NULL DEFAULT 0,
    last_seen REAL NOT NULL, signature TEXT NOT NULL, payload TEXT NOT NULL,
    PRIMARY KEY (profile_id, exercise, item_key)
);
```

The current definitions are `_SCHEMA` and `_CALENDAR_SCHEMA` in `alto/learning/database.py`. Two design decisions are worth understanding.

**`attempts` is the log; `items` is a summary.** The log is **append-only**: facts that happened, never edited. The summary is
**derived**: it could be rebuilt by replaying the log through `update_strain`. This is a miniature of a well-known pattern
(*event sourcing*): keep the facts, derive the state. It is what lets you change the scheduler's formula later and recompute
strains without losing anything, and it is why the statistics (accuracy, speed, activity over time) are computed from `attempts`,
which has the full history, rather than from `items`, which only has the current state.

**Times are numbers.** `answered_at` and `last_seen` are seconds since 1970 (`REAL`), and durations are integer milliseconds. This
sorts and subtracts without date parsing. Convert to local dates only when displaying (the statistics code groups into local
days, weeks and months; see `_floor` in `stats.py`).

**The question is stored in the row.** `items.payload` is the `Question` as JSON (`Question.to_dict`). That is how an old question
can be asked again without regenerating it, and also why changing `Question` is a data-format change: old payloads must still
load. `Learner.pick` handles an unreadable payload by skipping it, which is a safety net, not a plan. Add fields with defaults.

## Changing the schema: migrations

A shipped database has users' history in it, so the structure cannot just change. A **migration** is a script that takes a
database from one version to the next. SQLite has a built-in integer for this, the **`user_version` pragma**, which belongs to
the application and which SQLite does not otherwise use. Alto applies missing migrations in order within one transaction.
When a 0.0.1 database is opened in 0.0.2, its profiles, answers, and question history are preserved. SM-2 and FSRS start
with a fresh review queue. Eligible earlier answers can still contribute to response-time grading. Schema version 7 records
each profile’s grading thresholds and whether an answer’s timing is usable.

## What each `Database` method is for

You can find all of them in the [API reference]({{ '/api/alto.learning.database/' | relative_url }}). In groups:

- **Profiles:** `profiles()`, `profile(id)`, `add_profile(name)` (names are unique ignoring case), `delete_profile(id)` (cascades).
- **Writing history:** `add_attempt(...)` appends to the log; `save_item(...)` upserts the summary
  (`INSERT ... ON CONFLICT DO UPDATE`: insert, or update if the key exists).
- **Reading state for the scheduler:** `get_item(...)` for one question; `replay_candidates(...)` for the questions that may be
  asked again (the 25 highest-strain plus 10 random ones, for the same exercise and settings signature).
- **Statistics and the browser:** `attempts(...)`, `attempts_in(...)`, `strained_items(...)`, `count_attempts(...)` and the `*_rows`
  methods that feed the read-only tables in the database page.

`ORDER BY RANDOM() LIMIT 10` is not efficient for huge tables (it sorts everything), but at this size it is instant. If a profile
ever has millions of items, replace it with a cheaper sampling method.

## Saved preferences

The preferences are read and written through four small functions, because `QSettings` returns whatever it finds, which on some
platforms is a string where you stored a number:

- `store()` returns the single `QSettings`.
- `int_value(settings, key=, default=)` reads an integer and falls back to the default.
- `text_value(settings, key=, default=)` reads a string likewise.
- booleans are stored as the text `"true"` or `"false"`, because that is the form that survives every platform.

Adding a saved preference means: pick a key (`"ui/something"`, a "group/name" path), read it with a default at start-up, write it
when it changes. Tests redirect the settings to a throwaway folder, so use `store()` and nothing else.

## Backup and restore

A backup must be complete enough that importing it into a clean install leaves the program as if nothing had changed, so it
holds **both stores**: the whole database and every saved preference. The code is in three places.

- **`alto/learning/backup.py`** (no Qt) writes and reads the file. A backup is a zip with `alto.db` (the database), `settings.json`
  (the preferences) and `manifest.json` (a format number, the Alto version, the schema version, the counts and a SHA-256 of each
  of the other two parts). `read_backup` checks everything before returning anything: that the file is a zip with the three
  parts, that the format is not newer than this version knows, that both checksums match, and that the database is an intact Alto
  database (`check_snapshot`). Any failure is a `BackupError` with a sentence fit to show the user.
- **`Database.snapshot()` and `Database.restore()`** in `alto/learning/database.py`. A snapshot is `sqlite3.Connection.serialize()`:
  the whole database as bytes, consistent even while the program runs. Restoring loads the bytes into a throwaway in-memory
  database, checks it, and then copies it into the live connection with SQLite's online backup API
  (`copy.backup(self.conn)`). The live connection is never closed or swapped, so every object that holds it keeps working, and
  the ids of profiles and items are exactly what they were, which is why the saved "last profile" id still points at the right
  person. (Do not use `Connection.deserialize` on the live connection: it would detach it from its file.)
- **`export_settings()` and `import_settings()`** in `alto/ui/store.py`. Export reads every key in `QSettings`; import clears the
  settings and sets the backup's, so a key the backup lacks does not survive. Both keep the marker `migratedFromMtheory`: without it
  `store()` would bring old "mtheory" preferences back in on the next call.
- **`alto/ui/backup_flow.py`** asks the questions: the file dialogs, a description of the backup before it is applied, and a
  **safety copy** of the current data saved beside `alto.db` before anything is replaced. `MainWindow._restored` then picks up the
  profile, applies the theme and opens a fresh window, which loads every setting as it starts.

What this means when you change the program:

1. **A new table or column** is in backups automatically (the whole database is copied). Give it a migration as described above, and
   an older backup is brought up to date by `_migrate` as it is restored.
2. **A new saved preference** is in backups automatically, whatever its key. Keep values to text, numbers, true and false, lists
   and bytes, which is what the backup format can hold.
3. **Anything stored somewhere else**, such as a file in the data folder, a new `QSettings` organization, or state kept only in
   memory that the user would expect to survive, is *not* in a backup. Add it to `write_backup` and `import_backup`, and extend
   `tests/test_backup_flow.py`, whose end-to-end test is the statement of the promise.
4. **A change to the backup format itself** (the files in the zip, or the manifest) must raise `FORMAT` in `backup.py` and keep
   reading the old one. A file with a format number above the running version's is refused, which is the safe behavior for a
   backup made by a later Alto.
5. **Schema compatibility only goes one way.** A backup from an older schema is migrated; one from a newer schema is refused,
   because the older program cannot know what the newer one added.

The tests (`tests/test_backup.py`, `tests/test_backup_flow.py`) cover the exact round trip of every row, the refusal of each kind of
damaged or foreign file, a restore replacing rather than merging, the safety copy being a working undo, and an end-to-end import
into a clean install through the real window.

## Privacy

Profiles and practice history stay in the local database. On supported installations, Alto checks GitHub for a published release up to once a day while the main grid is active. The request does not include profile names or practice records. Turn off automatic checks in **Settings → Updates**, or check manually with **Tools → Check for updates…**. [Updating Alto]({{ '/getting-started/' | relative_url }}#updating-alto)

## Words to search for

*ACID* (what a transaction guarantees). *Write-ahead logging* (SQLite's `journal_mode = WAL`, a faster and more concurrent journal;
Alto uses the default). *Schema migration, schema versioning.* *Event sourcing, append-only log.* *Normalization* (why `items` and
`attempts` are separate tables). *Upsert.* *Index, covering index, query plan* (`EXPLAIN QUERY PLAN`). *ORM* (object-relational
mapper; Alto does not use one, deliberately). *Serialization* (JSON for the question payload).

## Further reading

- The SQLite documentation, sqlite.org/docs.html: especially "Datatypes in SQLite", "Foreign Key Support", "ALTER TABLE" (with the
  steps for changes it cannot do directly), "PRAGMA user_version", "UPSERT" and "Appropriate Uses For SQLite".
- Python Software Foundation, the `sqlite3` module documentation, docs.python.org: transactions, `row_factory`, parameters.
- Martin Kleppmann, *Designing Data-Intensive Applications* (O'Reilly, 2017): chapters 1 to 3 explain schemas, storage and indexes;
  the chapter on stream processing covers the log-and-derived-state idea.
- C. J. Date, *An Introduction to Database Systems*, 8th ed. (Pearson, 2003): the relational model from its source.
