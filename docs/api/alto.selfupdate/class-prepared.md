---
title: Prepared
parent: alto.selfupdate
api_module: alto.selfupdate
package: alto
permalink: /api/alto.selfupdate/class-prepared/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Prepared(
    work: Path,
    installer: Path | None,
    root: Path | None,
)
```

{% endraw %}{% include api-source.html name="Prepared" line=147 %}{% raw %}

</div>

An update that has been downloaded and checked, and is ready to be
handed over.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `work` | `Path` | The temporary folder that holds it, which is removed after the update. |
| `installer` | `Path or None` | On Windows, the installer to run. |
| `root` | `Path or None` | On Linux, the unpacked download, with its `install.sh`. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Prepared(
...     Path("/tmp/x"),
...     installer=None,
...     root=Path("/tmp/x/unpacked/alto-0.1.0"),
... ).installer is None
True
```
{% endraw %}
