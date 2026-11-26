---
title: startup_profile
parent: alto.ui.profile_dialog
api_module: alto.ui.profile_dialog
package: alto.ui
permalink: /api/alto.ui.profile_dialog/function-startup_profile/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def startup_profile(db: Database) -> Profile | None
```

{% endraw %}{% include api-source.html name="startup_profile" line=241 %}{% raw %}

</div>

Return the profile to open with: the one used last time, else ask.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `db` | `Database` | The database of profiles. |

**Returns**

| Type | Description |
| --- | --- |
| `Profile or None` | The profile, or None if the person closed the dialog without choosing one. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> database = Database()
>>> ada = database.add_profile("Ada")
>>> remember_profile(ada)
>>> # noinspection PyUnresolvedReferences
>>> startup_profile(database).name
'Ada'
```
{% endraw %}
