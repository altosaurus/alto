---
title: StatsPage
parent: alto.ui.stats_dialog
api_module: alto.ui.stats_dialog
package: alto.ui
permalink: /api/alto.ui.stats_dialog/class-statspage/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
StatsPage(
    learner: Learner,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="StatsPage" line=304 %}{% raw %}

</div>

Bases: `QWidget`

The statistics, as a page of the main window.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `back` | `Signal` | Emitted by Escape; the main window provides the shared Back button. |
| `learner` | `Learner` | Whose answers are shown; only the active profile's own. |
| `exercise` | `FieldComboBox` | The exercise filter. |
| `timeframe` | `FieldComboBox` | The timeframe filter. |
| `tiles` | `dict of str to Tile` | The headline numbers, by name. |
| `detail` | `QFrame` | The panel under the charts that lists the answers behind a clicked bar, point, row or day. Hidden until one is clicked. |
| `answers` | `AnswerList` | The table in the detail panel. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.learning import Database
>>> db = Database()
>>> page = StatsPage(
...     Learner(
...         db, profile=db.add_profile("Ada")
...     )
... )
>>> page.note.text().startswith(
...     "No answers recorded for Ada"
... )
True
```

**Constructor**

Build the page and fill it for the current filters.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `learner` | `Learner` | Whose statistics to show. |
| `parent` | `QWidget or None, default None` | The widget that owns the page. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.learning import Database
>>> db = Database()
>>> page = StatsPage(
...     Learner(
...         db, profile=db.add_profile("Ada")
...     )
... )
>>> # the last 30 days, until another is chosen
>>> page.timeframe.currentText()
'Last 30 days'
```

## StatsPage.refresh

<div class="api-signature" markdown="1">

```python
def refresh() -> None
```

{% endraw %}{% include api-source.html name="StatsPage.refresh" line=620 %}{% raw %}

</div>

Recalculate everything for the chosen exercise and timeframe and
show it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.learning import Database
>>> db = Database()
>>> page = StatsPage(
...     Learner(
...         db, profile=db.add_profile("Ada")
...     )
... )
>>> page.refresh()
>>> page.tiles[
...     "questions"
... ].value.text()  # nothing answered yet
'0'
```
{% endraw %}
