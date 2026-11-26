---
title: Profile
parent: alto.learning.database
api_module: alto.learning.database
package: alto.learning
permalink: /api/alto.learning.database/class-profile/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Profile(
    id: int,
    *,
    name: str,
)
```

{% endraw %}{% include api-source.html name="Profile" line=292 %}{% raw %}

</div>

A person who practices: their answers are kept apart from everyone
else's.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | `int` | The profile's row number in the database. |
| `name` | `str` | The name shown in the interface. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Profile(1, name="Ada")
Profile(id=1, name='Ada')
```
{% endraw %}
