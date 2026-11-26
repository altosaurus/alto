---
title: parse_latest_release
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-parse_latest_release/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def parse_latest_release(text: str) -> Release | None
```

{% endraw %}{% include api-source.html name="parse_latest_release" line=740 %}{% raw %}

</div>

Read GitHub's answer about the latest release.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text` | `str` | The JSON that `releases/latest` answers with. |

**Returns**

| Type | Description |
| --- | --- |
| `Release or None` | The release, or None if the answer is not one, is a draft or a pre-release, or has a tag that is not a plain version. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> answer = (
...     '{"tag_name": "v0.1.0", "html_url": '
...     '"https://example.org/r", "draft": false, "prerelease": '
...     'false}'
... )
>>> parse_latest_release(answer)
Release(version='0.1.0', tag='v0.1.0', url='https://example.org/r',
assets=())
>>> parse_latest_release(
...     answer.replace(
...         '"prerelease": false',
...         '"prerelease": true',
...     )
... ) is None
True
>>> parse_latest_release("not json") is None
True
```
{% endraw %}
