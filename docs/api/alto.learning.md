---
title: alto.learning
parent: api
package: alto.learning
api_package: true
permalink: /api/alto.learning/
---

Spaced repetition: who is learning (profiles), what they answered (a database) and what to ask next.

## Modules

| Module | What it is |
|---|---|
| [alto.learning.backup](../alto.learning.backup/) | Backup files: everything Alto keeps, in one file that can be read back into a clean install. Pure Python (no Qt). |
| [alto.learning.calendar](../alto.learning.calendar/) | Daily exercise queues for SM-2 and FSRS. |
| [alto.learning.database](../alto.learning.database/) | The SQLite store: profiles, every answer given, and what is known about each question. Pure Python (no Qt). |
| [alto.learning.grading](../alto.learning.grading/) | Answer-button intervals for Anki's default SM-2 and FSRS-6 deck settings. |
| [alto.learning.learner](../alto.learning.learner/) | Ties the profile, the database and the scheduler together for the exercise screen. |
| [alto.learning.response_times](../alto.learning.response_times/) | Rolling response times for one learner and exercise. |
| [alto.learning.scheduler](../alto.learning.scheduler/) | How a question's history turns into how soon it comes back. Pure Python, no database and no Qt. |
| [alto.learning.stats](../alto.learning.stats/) | Numbers and series for the statistics screen, worked out from the answers in the database. Pure Python, no Qt. |
