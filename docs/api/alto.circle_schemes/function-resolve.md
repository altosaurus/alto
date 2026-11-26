---
title: resolve
parent: alto.circle_schemes
api_module: alto.circle_schemes
package: alto
permalink: /api/alto.circle_schemes/function-resolve/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def resolve(
    key: str,
    *,
    customs: list[CustomRecord],
) -> Scheme
```

{% endraw %}{% include api-source.html name="resolve" line=1065 %}{% raw %}

</div>

Find a scheme by its key, among the presets and the user's own,
falling back to the default.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The saved choice. |
| `customs` | `list of CustomRecord` | The user's own schemes. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `Scheme` | The scheme, or the default one if the key is unknown (for instance after the scheme was deleted). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     resolve("midnight", customs=[]).name,
...     resolve("gone", customs=[]).key,
... )
('Midnight', 'cyan-indigo')
```
{% endraw %}
