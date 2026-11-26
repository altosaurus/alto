---
title: database_path
parent: alto.location
api_module: alto.location
package: alto
permalink: /api/alto.location/function-database_path/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def database_path(
    *,
    environ: Mapping[str, str] = os.environ,
) -> Path
```

{% endraw %}{% include api-source.html name="database_path" line=67 %}{% raw %}

</div>

Give the file that holds the practice history.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `environ` | `mapping of str to str` | The environment to read. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Path` | `data/alto.db` in the `ALTO_HOME` folder if there is one, otherwise `alto.db` in the system's data folder for Alto. The folder need not exist yet. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> database_path(
...     environ={"ALTO_HOME": "/tmp/alto-dev"}
... ).as_posix()
'/tmp/alto-dev/data/alto.db'
>>> database_path(environ={}).name
'alto.db'
```
{% endraw %}
