---
title: alto.ui.profile_dialog
parent: api
package: alto.ui
api_components: [{"title": "ProfileDialog", "url": "/api/alto.ui.profile_dialog/class-profiledialog/"}, {"title": "remember_profile", "url": "/api/alto.ui.profile_dialog/function-remember_profile/"}, {"title": "startup_profile", "url": "/api/alto.ui.profile_dialog/function-startup_profile/"}]
permalink: /api/alto.ui.profile_dialog/
---
{% raw %}
Choosing who is practicing. There is no password: a profile is just a
name that keeps its own history.

## Classes

- [`ProfileDialog`](class-profiledialog/) — Ask who is practicing: a first name on launch, then a list to switch between.

## Functions

- [`remember_profile`](function-remember_profile/) — Remember which profile was used, so the next launch can open with it.
- [`startup_profile`](function-startup_profile/) — Return the profile to open with: the one used last time, else ask.

<details markdown="1">
<summary>Module notes and examples</summary>

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> db = Database()
>>> remember_profile(db.add_profile("Ada"))
>>> # noinspection PyUnresolvedReferences
>>> startup_profile(
...     db
... ).name  # the one used last time, with no dialog
'Ada'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"profiledialog": "class-profiledialog/", "remember_profile": "function-remember_profile/", "startup_profile": "function-startup_profile/"}</script>
{% include api-fragments.html %}
