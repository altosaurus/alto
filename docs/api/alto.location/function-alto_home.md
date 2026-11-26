---
title: alto_home
parent: alto.location
api_module: alto.location
package: alto
permalink: /api/alto.location/function-alto_home/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def alto_home(
    *,
    environ: Mapping[str, str] = os.environ,
) -> Path | None
```

{% endraw %}{% include api-source.html name="alto_home" line=29 %}{% raw %}

</div>

Give the folder named by `ALTO_HOME`, if there is one.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `environ` | `mapping of str to str` | The environment to read. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Path or None` | The folder, with `~` expanded and made absolute, or None if `ALTO_HOME` is not set or is empty. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> alto_home(environ={}) is None
True
>>> alto_home(environ={"ALTO_HOME": ""}) is None
True
>>> str(
...     alto_home(
...         environ={
...             "ALTO_HOME": "/tmp/alto-dev"
...         }
...     )
... )
'/tmp/alto-dev'
>>> alto_home(
...     environ={"ALTO_HOME": "~/alto-dev"}
... ) == Path.home() / "alto-dev"
True
```
{% endraw %}
