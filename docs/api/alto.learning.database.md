---
title: alto.learning.database
parent: api
package: alto.learning
api_components: [{"title": "Database", "url": "/api/alto.learning.database/class-database/"}, {"title": "ItemRecord", "url": "/api/alto.learning.database/class-itemrecord/"}, {"title": "Profile", "url": "/api/alto.learning.database/class-profile/"}, {"title": "check_snapshot", "url": "/api/alto.learning.database/function-check_snapshot/"}]
permalink: /api/alto.learning.database/
---
{% raw %}
The SQLite store: profiles, every answer given, and what is known about
each question. Pure Python (no Qt).

## Classes

- [`Profile`](class-profile/) — A person who practices: their answers are kept apart from everyone else's.
- [`ItemRecord`](class-itemrecord/) — What a profile's history says about one question.
- [`Database`](class-database/) — The SQLite database behind profiles, answers and per-question history.

## Functions

- [`check_snapshot`](function-check_snapshot/) — Check that bytes are an intact Alto database that this version can read, and say what is in it.

<details markdown="1">
<summary>Module notes and examples</summary>

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

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"check_snapshot": "function-check_snapshot/", "profile": "class-profile/", "itemrecord": "class-itemrecord/", "database": "class-database/", "databasewrite_transaction": "class-database/#databasewrite_transaction", "databaseclose": "class-database/#databaseclose", "databasesnapshot": "class-database/#databasesnapshot", "databaserestore": "class-database/#databaserestore", "databaseprofiles": "class-database/#databaseprofiles", "databaseprofile": "class-database/#databaseprofile", "databaseadd_profile": "class-database/#databaseadd_profile", "databasedelete_profile": "class-database/#databasedelete_profile", "databaseget_item": "class-database/#databaseget_item", "databasesave_item": "class-database/#databasesave_item", "databaseadd_attempt": "class-database/#databaseadd_attempt", "databaseattempts": "class-database/#databaseattempts", "databaseattempts_in": "class-database/#databaseattempts_in", "databasefirst_attempts_per_day": "class-database/#databasefirst_attempts_per_day", "databasestrained_items": "class-database/#databasestrained_items", "databasecount_attempts": "class-database/#databasecount_attempts", "databaseattempt_rows": "class-database/#databaseattempt_rows", "databaseanswer_window": "class-database/#databaseanswer_window", "databaseanswer_page": "class-database/#databaseanswer_page", "databaseitem_rows": "class-database/#databaseitem_rows", "databaseprofile_rows": "class-database/#databaseprofile_rows", "databasereplay_candidates": "class-database/#databasereplay_candidates"}</script>
{% include api-fragments.html %}
