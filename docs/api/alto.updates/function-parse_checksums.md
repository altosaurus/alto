---
title: parse_checksums
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-parse_checksums/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def parse_checksums(text: str) -> dict[str, str]
```

{% endraw %}{% include api-source.html name="parse_checksums" line=1055 %}{% raw %}

</div>

Read a `SHA256SUMS` file: a line for each file, with its SHA-256
hash and its name.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | The file's contents, as `sha256sum` writes them. |

**Returns**

| Type | Description |
| --- | --- |
| `dict of str to str` | The hash of each named file, in lower case. Lines that are not a hash and a plain file name are left out. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> entry = (
...     "ab" * 32
...     + "  alto-0.1.0-linux-x86_64.tar.gz"
... )
>>> parse_checksums(
...     entry
...     + "\nnot a line\n"
...     + "cd" * 32
...     + "  ../evil"
... )
{'alto-0.1.0-linux-x86_64.tar.gz':
'abababababababababababababababababababababababababababababababab'}
```
{% endraw %}
