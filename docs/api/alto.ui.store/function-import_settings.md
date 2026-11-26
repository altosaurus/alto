---
title: import_settings
parent: alto.ui.store
api_module: alto.ui.store
package: alto.ui
permalink: /api/alto.ui.store/function-import_settings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def import_settings(values: Mapping[str, object]) -> None
```

{% endraw %}{% include api-source.html name="import_settings" line=506 %}{% raw %}

</div>

Replace every saved preference with the ones from a backup, so the
preferences are exactly as they were.

Preferences saved now that the backup does not have are removed. The
marker that stops old "mtheory" preferences being
brought across again is kept, so an old installation's leftovers
cannot leak back in.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `values` | `mapping of str to object` | The preferences, by key, as `export_settings` returned them. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> import_settings(
...     {"demo/name": "Ada", "demo/count": 3}
... )
>>> (
...     store().value("demo/name"),
...     int_value(
...         store(), key="demo/count", default=0
...     ),
... )
('Ada', 3)
>>> store().remove("demo")
>>> store().remove("")
```
{% endraw %}
