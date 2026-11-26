---
title: self_check
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-self_check/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def self_check() -> list[str]
```

{% endraw %}{% include api-source.html name="self_check" line=1169 %}{% raw %}

</div>

Check, without any network, that what a copy needs to check an
update is there and works.

It is what `alto --self-test` runs, so that the build can tell that
a packaged copy carries the certificate list and the
signature library (which PyInstaller must be told about), and that
the keys in the code are keys.

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | What is wrong, one sentence each; empty if all is well. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> self_check()
[]
```
{% endraw %}
