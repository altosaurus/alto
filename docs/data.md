---
title: Database
nav_order: 8
nav_group: Using Alto
permalink: /data/
---
Everything Alto stores is on your own computer.

- Alto has no accounts, no sync and no analytics.
- Your name is only a label for a profile in a local file.
- On supported installations Alto contacts GitHub to check for releases. You can turn off daily checks in **Settings → Updates**.

## Browsing the database

Open the database using the button next to the statistics button at the upper right of the main window. It shows a read-only view of what is stored and never changes anything. Use **← Back** or <kbd>Esc</kbd> to return to the page you came from.

{% include shot.html src="database.png" alt="The Answers table with the next review date in the Due column at the right" %}

Three tables are available:

- **Answers:** every answer the active profile has given, newest first, with the question, your answer, whether it was right, the attempt number and the time.
- **Questions** shows each question’s strain, answer counts, typical response time, and last practice time.
- **Profiles:** everyone who has a profile, with how many answers and questions each has.

In both **Answers** and **Questions**, **Due** shows the next review in local time for the selected SM-2 or FSRS schedule. All answers to the same question show its current due date. A dash means the question has no due date under the current scheduler.

{% include shot.html src="database-questions.png" alt="The Questions table sorted by Last seen with Due dates beside the most recently practiced questions" caption="Last seen records when you practiced the question. Due shows when the scheduler wants to show it again." %}

Click a column heading to sort, and use the search box to filter every column at once. Answers and questions are
limited to the newest 10,000 rows each; the line above the table says when that applies.

### Previewing a question

Double-click a row in Answers or Questions to see that question as the exercise showed it, with its answer.
Choose the **Question Statistics** bar chart icon in the upper-right corner to graph your practice history for that question. Each point represents one time you were asked.
The speed graph shows seconds to your first answer. The accuracy graph shows the percentage answered correctly on the first try
up to that point. Hover over a point for its value. You can also open these graphs from an answer in [Statistics]({{ '/statistics/' | relative_url }}).

{% include shot.html src="question-preview.png" alt="A popup showing a chord on a staff with its answer and what was answered" caption="The preview shows the notes, the correct answer, what you answered and how long it took. Play sounds the notes." %}

## Where it is

Your practice history, profiles included, is one [SQLite](https://www.sqlite.org/) file named `alto.db`:

| System | Location |
|---|---|
| Linux | `~/.local/share/Alto/alto.db` |
| macOS | `~/Library/Application Support/Alto/alto.db` |
| Windows | `C:\Users\<you>\AppData\Roaming\Alto\alto.db` |

To keep a second copy of Alto apart, for example one you are changing while you use the installed one to practice, set
`ALTO_HOME` to a folder. Alto then keeps its history in `data/alto.db` there and its settings in `config/`, and leaves the
usual places alone. `scripts/dev.sh` starts Alto from a clone this way, in `~/.alto-dev`.

Your settings (theme, notation style, keyboard style, instrument, exercise options and the last profile you used) are stored separately by Qt, in
your usual configuration location.

## What the file contains

| Table | Holds |
|---|---|
| `profiles` | Each profile’s name, creation time, scheduler, self-grading preference, and response-time grading thresholds. |
| `attempts` | One row for every answer: the profile, exercise, question, your answer, whether it was right, the attempt number, how long it took and when. |
| `items` | What is known about each question: its strain, how often it was answered and missed, its typical time, when it was last seen, and the question itself so it can be asked again. |
| `practice_cards` | Introduced card identities, the questions themselves, and the local date each was introduced in scheduled practice. |
| `review_schedules` | The next review time and algorithm state for each card studied with SM-2 or FSRS. |
| `practice_limits` | Daily allowances for each profile and exercise. |
| `daily_reviews` | Completed calendar reviews by profile, exercise, and day. |

Because it is a normal SQLite file, you can open it with any SQLite tool if you want to run your own queries. Close Alto
first. Alto's own [database browser](#browsing-the-database) is read-only.

## Anki decks

Open **☰ → Tools → Anki Exporter** to turn Alto exercises into flashcards you can study in Anki. You can keep
practicing in Alto while the exporter is open.

### Deck selection and preview

Check the exercises you want to export. Checking a category selects every exercise in it. Choose **All exercises** to
select the whole list. Clicking an exercise name displays a sample card, even if its box is unchecked. **Front**
shows the question and its illustration, when there is one. **Back** adds the answer and explanation.

{% include shot.html src="anki-exporter.png" alt="Anki Exporter with Note Identification and Interval Identification checked and an interval card in the preview." %}

The settings button in the upper right opens the highlighted exercise’s options. These start with your current
practice settings. Changes you make here apply only to the export. For example, you can narrow an Interval
Identification deck to thirds and sixths and keep practicing all intervals in Alto. Exercises with a fixed set of
cards export every matching card. Exercises that generate a sample of questions export each distinct card in that sample.

### Review scheduling

By default, exported cards start as new in Anki. If your Alto profile uses SM-2 or FSRS, check **Include scheduling**
to carry over due dates and intervals for matching cards you’ve already reviewed. The exporter uses the schedule
from when you opened the window. Cards you haven’t studied start as new.

### Export summary and file

Choose **Export…** to see how many cards match. The table groups decks by exercise type. Each group starts expanded.
A row marked **No cards** is skipped. The total below the table is the number of cards in the package.

{% include shot.html src="anki-export-summary.png" alt="Export summary with separate Notation and Intervals groups, a card count for each deck, and a total below the table." %}

Use **Browse…** to choose a destination or enter a path in **File name**. A filename alone saves to your home
directory. The suggested name is `alto.apkg` for multiple exercises or, for a single exercise, a name such as
`alto - Interval Identification.apkg`.

Click **Export** to save. A spinner marks the deck being prepared and a green check marks each finished deck.
The progress bar tracks the whole package, including the final save. To stop, click **Cancel** and confirm.
Canceling preserves any existing file at the destination. When the status reads **Export successful**, click
**Close** to return to the exporter.

### Import into Anki

Open the saved `.apkg` file in Anki. If you exported schedules, enable **Import any learning progress** during
import to keep the review dates and intervals. Anki schedules subsequent reviews independently of Alto.

A package containing one nonempty deck places it directly under **Alto**. With several nonempty decks, Anki
groups them by Alto’s exercise categories, for example **Alto → Intervals → Interval Identification** and
**Alto → Notation → Note Identification**. Exporting the same question again preserves its card identity.

## Backing up and restoring

Open the ☰ menu and choose **Tools** → **Export backup…** to save everything Alto keeps to one file: all the profiles, every answer
and the record of each question, and every setting (the theme, the notation and keyboard styles, the instrument, each
exercise's options and the profile you used last). Choose **Tools** → **Import backup…** to read one back.

Importing **replaces everything** with the backup, so on a clean install, or on another computer, Alto comes up exactly as it
was when the backup was made: same profiles, same history, same settings, and the same profile open. Nothing is merged. What
is there before the import is gone from the app, so Alto saves a backup of it first, next to `alto.db` in a file named
`alto-before-import-<date and time>.altobackup`. If you imported the wrong file, import that one to put everything back.

- A backup file ends in `.altobackup`. It is a zip file holding the database, the settings and a note of which version of Alto
  made it, with a checksum of each part.
- Before anything is changed, Alto checks the file all the way through. A file that is damaged, is not an Alto backup, or was made
  by a **newer** version of Alto is refused with an explanation, and nothing changes. A backup from an older version is brought
  up to date as it is imported.
- A backup contains your whole practice history, so keep it as private as the history itself.

To move to another computer: install Alto there, start it once (it asks for a first profile), then import the backup.

## Copying the files by hand

- **Back up the history only:** close Alto and copy `alto.db` somewhere safe. Copy it back to restore it. This leaves out the settings; **Export backup…** includes them.
- **Move the history to another computer:** copy the file to the same location there.
- **Start over:** close Alto and delete `alto.db`. The next launch asks for a new profile and starts with an empty history.
