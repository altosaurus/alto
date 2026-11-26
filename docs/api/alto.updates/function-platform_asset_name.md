---
title: platform_asset_name
parent: alto.updates
api_module: alto.updates
package: alto
permalink: /api/alto.updates/function-platform_asset_name/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def platform_asset_name(
    version: str,
    *,
    system: str,
    machine: str,
) -> str | None
```

{% endraw %}{% include api-source.html name="platform_asset_name" line=943 %}{% raw %}

</div>

Give the name of the file that updates a packaged copy on this
system, as the release workflow names it.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `version` | `str` | The version, such as "0.1.0". Keyword-only after the first. |
| `system` | `str` | The operating system, as `platform.system()` says it ("Linux", "Windows"). Keyword-only. |
| `machine` | `str` | The processor, as `platform.machine()` says it ("x86_64", "AMD64"). Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str or None` | The name, or None if there is no package for this system. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> platform_asset_name(
...     "0.1.0",
...     system="Linux",
...     machine="x86_64",
... )
'alto-0.1.0-linux-x86_64.tar.gz'
>>> platform_asset_name(
...     "0.1.0",
...     system="Windows",
...     machine="AMD64",
... )
'alto-0.1.0-windows-x64-setup.exe'
>>> platform_asset_name(
...     "0.1.0",
...     system="Linux",
...     machine="aarch64",
... ) is None
True
```
{% endraw %}
