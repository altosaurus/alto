---
title: store
parent: alto.ui.store
api_module: alto.ui.store
package: alto.ui
permalink: /api/alto.ui.store/function-store/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def store() -> QSettings
```

{% endraw %}{% include api-source.html name="store" line=30 %}{% raw %}

</div>

Return the app's saved settings.

The first time it is opened under the name "alto" it brings across
anything saved under the old name ("mtheory"), so a
rename does not reset anyone's preferences. If `ALTO_HOME` is set
the settings are kept in a file in that folder instead,
and nothing is brought across from the system's own.

**Returns**

| Type | Description |
| --- | --- |
| `QSettings` | The settings, kept in the user's configuration folder or in `ALTO_HOME`. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings = store()
>>> settings.setValue("demo/name", "Ada")
>>> str(store().value("demo/name"))
'Ada'
>>> settings.remove("demo")
```
{% endraw %}
