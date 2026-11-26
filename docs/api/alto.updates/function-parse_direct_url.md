---
title: parse_direct_url
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-parse_direct_url/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def parse_direct_url(text: str) -> Source | None
```

{% endraw %}{% include api-source.html name="parse_direct_url" line=153 %}{% raw %}

</div>

Read where a package was installed from, out of the
`direct_url.json` that the installer leaves with it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | The contents of the file. |

**Returns**

| Type | Description |
| --- | --- |
| `Source or None` | The git address, the commit and the ref, or None if the package was not installed from a git address (a copy that runs from a source folder has a folder there instead). |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> parse_direct_url(
...     '{"url": "https://example.org/a.git", "vcs_info": {"vcs": '
...     '"git", "commit_id": "abc1234"}}'
... )
Source(url='https://example.org/a.git', commit='abc1234',
ref='HEAD')
>>> named = (
...     '{"url": "https://x.org/a.git", "vcs_info": {"vcs": '
...     '"git", "commit_id": "abc1234", "requested_revision": '
...     '"dev"}}'
... )
>>> # noinspection PyUnresolvedReferences
>>> parse_direct_url(named).ref
'dev'
>>> parse_direct_url(
...     '{"url": "file:///home/me/alto", "dir_info": {"editable": '
...     'true}}'
... ) is None
True
>>> parse_direct_url("not json") is None
True
```
{% endraw %}
