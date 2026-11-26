---
title: custom_scheme
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/function-custom_scheme/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def custom_scheme(record: CustomRecord) -> Scheme
```

{% endraw %}{% include api-source.html name="custom_scheme" line=866 %}{% raw %}

</div>

Make a scheme from one of the user's own records.

The colors in a record are what a cell looks like when lit; the
quiet cells are the same hue, calmer and darker (or, on a
light wedges, paler).

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `record` | `CustomRecord` | A record that `clean_record` accepted. |

**Returns**

| Type | Description |
| --- | --- |
| `Scheme` | The scheme, with the key and name of the record. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> scheme = custom_scheme(
...     record_of(
...         "custom-1",
...         name="Mine",
...         mode="rings",
...         colors=["#2f6bd0", "#18a0c0"],
...     )
... )
>>> scheme.key, scheme.name, scheme.light
('custom-1', 'Mine', False)
>>> scheme.cells["outer"][0][1][
...     0
... ] != scheme.cells["inner"][0][1][
...     0
... ]  # two rings, two hues
True
```
{% endraw %}
