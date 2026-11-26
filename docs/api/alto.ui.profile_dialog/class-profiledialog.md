---
title: ProfileDialog
parent: alto.ui.profile_dialog
api_module: alto.ui.profile_dialog
package: alto.ui
permalink: /api/alto.ui.profile_dialog/class-profiledialog/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ProfileDialog(
    db: Database,
    *,
    current: Profile | None = None,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="ProfileDialog" line=43 %}{% raw %}

</div>

Bases: `QDialog`

Ask who is practicing: a first name on launch, then a list to switch
between.

On first launch (no profiles yet) it asks for a name. Afterwards it
lists the profiles to switch between and lets you add
another.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `db` | `Database` | Where the profiles are kept. |
| `chosen` | `Profile or None` | The profile that was picked or created, once the dialog is accepted. |
| `list` | `QListWidget` | The existing profiles. |
| `name` | `QLineEdit` | Where a new name is typed. |
| `error` | `QLabel` | Says why a name was refused. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> dialog = ProfileDialog(db)
>>> dialog.windowTitle()  # nobody has a profile yet
'Welcome'
```

**Constructor**

Build the dialog for the profiles in a database.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `db` | `Database` | The database whose profiles are listed and added to. |
| `current` | `Profile or None, default None` | The profile to select in the list at first. Keyword-only. |
| `parent` | `QWidget or None, default None` | The widget that owns the dialog. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> database = Database()
>>> _ = database.add_profile("Ada")
>>> ProfileDialog(database).windowTitle()
'Profile'
```
{% endraw %}
