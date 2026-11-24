---
title: alto.ui.practice_limits
parent: api
package: alto.ui
permalink: /api/alto.ui.practice_limits/
---
{% raw %}
Daily card allowances in profile and exercise settings.

## DailyLimitsEditor

<div class="api-signature" markdown="1">

```python
DailyLimitsEditor(
    learner: Learner,
    *,
    exercise: str = '',
)
```

{% endraw %}{% include api-source.html name="DailyLimitsEditor" line=19 %}{% raw %}

</div>

Bases: `QWidget`

Edit a profile's daily limits or an exercise's overrides.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.learning import Database
>>> db = Database()
>>> editor = DailyLimitsEditor(
...     Learner(
...         db, profile=db.add_profile("Ada")
...     )
... )
>>> editor.fields[0].value()
10
```

**Constructor**

Build one number field per limit, with an inheritance choice in
exercise settings.

**Parameters**

- `learner` (*Learner*): Profile whose limits to edit.
- `exercise` (*str*): Exercise class name, or empty for profile defaults.

**Constructor examples**

```text
The exercise fields initially show the values from Practice
settings.
```

### DailyLimitsEditor.reload

<div class="api-signature" markdown="1">

```python
def reload() -> None
```

{% endraw %}{% include api-source.html name="DailyLimitsEditor.reload" line=100 %}{% raw %}

</div>

Show current values and disable fields that follow the profile
defaults.

**Examples**

```text
Reopening Daily Limits reflects edits made in the global
settings dialog.
```
{% endraw %}
