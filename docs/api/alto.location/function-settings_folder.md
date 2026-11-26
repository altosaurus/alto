---
title: settings_folder
parent: alto.location
api_module: alto.location
package: alto
permalink: /api/alto.location/function-settings_folder/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def settings_folder(
    *,
    environ: Mapping[str, str] = os.environ,
) -> Path | None
```

{% endraw %}{% include api-source.html name="settings_folder" line=105 %}{% raw %}

</div>

Give the folder that holds the settings when `ALTO_HOME` moves them.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `environ` | `mapping of str to str` | The environment to read. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Path or None` | `config` in the `ALTO_HOME` folder, or None if the settings are in the system's usual place. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> settings_folder(environ={}) is None
True
>>> str(
...     settings_folder(
...         environ={
...             "ALTO_HOME": "/tmp/alto-dev"
...         }
...     )
... )
'/tmp/alto-dev/config'
```
{% endraw %}
