---
title: remember_profile
parent: alto.ui.profile_dialog
api_module: alto.ui.profile_dialog
package: alto.ui
permalink: /api/alto.ui.profile_dialog/function-remember_profile/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def remember_profile(profile: Profile) -> None
```

{% endraw %}{% include api-source.html name="remember_profile" line=220 %}{% raw %}

</div>

Remember which profile was used, so the next launch can open with
it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `profile` | `Profile` | The profile in use. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> remember_profile(Profile(7, name="Ada"))
>>> int_value(
...     store(), key="profile/last", default=-1
... )
7
```
{% endraw %}
