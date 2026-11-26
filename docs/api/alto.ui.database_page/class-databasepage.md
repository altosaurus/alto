---
title: DatabasePage
parent: alto.ui.database_page
api_module: alto.ui.database_page
package: alto.ui
permalink: /api/alto.ui.database_page/class-databasepage/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
DatabasePage(
    learner: Learner,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="DatabasePage" line=915 %}{% raw %}

</div>

Bases: `QWidget`

The tables behind the app.

Answers and questions are the active profile's own; profiles lists
everyone.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `back` | `Signal` | Emitted by Escape; the main window provides the shared Back button. |
| `learner` | `Learner` | Whose answers and questions are shown. |
| `tabs` | `dict of str to QPushButton` | The buttons that choose the table: "answers", "questions" and "profiles". |
| `search` | `QLineEdit` | Filters every column at once. |
| `view` | `QTableView` | The table. |
| `proxy` | `QSortFilterProxyModel` | Sorts and filters the rows. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.learning import Database
>>> db = Database()
>>> page = DatabasePage(
...     Learner(
...         db, profile=db.add_profile("Ada")
...     )
... )
>>> page.note.text()
'0 answers by Ada.'
```

**Constructor**

Build the page, showing the answers table.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `learner` | `Learner` | Whose data to show. |
| `parent` | `QWidget or None, default None` | The widget that owns the page. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.learning import Database
>>> db = Database()
>>> page = DatabasePage(
...     Learner(
...         db, profile=db.add_profile("Ada")
...     )
... )
>>> page.tabs["answers"].isChecked()
True
```

## DatabasePage.show_table

<div class="api-signature" markdown="1">

```python
def show_table(
    key: str,
    *,
    keep_sort: bool = False,
) -> None
```

{% endraw %}{% include api-source.html name="DatabasePage.show_table" line=1293 %}{% raw %}

</div>

Show one of the tables.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | "answers", "questions" or "profiles". |
| `keep_sort` | `bool` | Preserve the current column and order when refreshing the open table. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.learning import Database
>>> db = Database()
>>> page = DatabasePage(
...     Learner(
...         db, profile=db.add_profile("Ada")
...     )
... )
>>> page.show_table("profiles")
>>> page.note.text()
'1 profile.'
```
{% endraw %}
