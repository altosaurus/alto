---
title: counted
parent: alto.ui.backup_flow
api_module: alto.ui.backup_flow
package: alto.ui
permalink: /api/alto.ui.backup_flow/function-counted/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def counted(
    number: int,
    *,
    noun: str,
) -> str
```

{% endraw %}{% include api-source.html name="counted" line=77 %}{% raw %}

</div>

Write a count with its noun, in the plural unless there is one.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `number` | `int` | The count. |
| `noun` | `str` | The singular noun. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | For example "1 profile" or "12,345 answers". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     counted(1, noun="profile"),
...     counted(12345, noun="answer"),
... )
('1 profile', '12,345 answers')
```
{% endraw %}
