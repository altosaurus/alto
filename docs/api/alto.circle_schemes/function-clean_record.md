---
title: clean_record
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/function-clean_record/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def clean_record(raw: object) -> CustomRecord | None
```

{% endraw %}{% include api-source.html name="clean_record" line=786 %}{% raw %}

</div>

Check one saved scheme of the user's own, and tidy it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `raw` | `object` | What was read back from the saved data. |

**Returns**

| Type | Description |
| --- | --- |
| `CustomRecord or None` | The record, with a name of at most 40 characters, or None if anything in it is missing or wrong: an unknown mode, a color that is not "#rrggbb", or the wrong number of colors for the mode. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> good = record_of(
...     "custom-1",
...     name="Mine",
...     mode="rings",
...     colors=["#2f6bd0", "#18a0c0"],
... )
>>> clean_record(good) == good
True
>>> few = record_of(
...     "custom-1",
...     name="Mine",
...     mode="rings",
...     colors=["#2f6bd0"],
... )
>>> unknown = record_of(
...     "custom-1",
...     name="Mine",
...     mode="nope",
...     colors=["#2f6bd0", "#18a0c0"],
... )
>>> (
...     clean_record(few) is None,
...     clean_record(unknown) is None,
... )
(True, True)
>>> clean_record("not a record") is None
True
```
{% endraw %}
