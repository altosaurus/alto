---
title: SchemePage
parent: alto.ui.circle_colors
api_module: alto.ui.circle_colors
package: alto.ui
permalink: /api/alto.ui.circle_colors/class-schemepage/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
SchemePage(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="SchemePage" line=228 %}{% raw %}

</div>

Bases: `QWidget`

The page that lists the color schemes: the presets, the user's own,
and a button to make another.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `chosen` | `Signal` | Emitted with the key of the scheme that was clicked. |
| `new` | `Signal` | Emitted when "Create your own" is clicked. |
| `edit_asked` | `Signal` | Emitted with the key of one of the user's schemes when its Edit button is clicked. |
| `thumbs` | `dict of str to SchemeThumb` | The picture of each scheme, by its key. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = SchemePage()
>>> page.load(current="midnight", customs=[])
>>> (
...     page.thumbs["midnight"].isChecked(),
...     len(page.thumbs),
... )
(True, 14)
```

**Constructor**

Build the page, empty until `load` is called.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> SchemePage().thumbs
{}
```

## SchemePage.load

<div class="api-signature" markdown="1">

```python
def load(
    *,
    current: str,
    customs: list[CustomRecord],
) -> None
```

{% endraw %}{% include api-source.html name="SchemePage.load" line=279 %}{% raw %}

</div>

Fill the page: a picture and a name for each scheme, with the
current one marked.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `current` | `str` | The key of the chosen scheme. Keyword-only. |
| `customs` | `list of CustomRecord` | The user's own schemes. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> page = SchemePage()
>>> from alto.circle_schemes import record_of
>>> mine = record_of(
...     "custom-1",
...     name="Mine",
...     mode="single",
...     colors=["#2f6bd0"],
... )
>>> page.load(
...     current="custom-1", customs=[mine]
... )
>>> (
...     page.thumbs["custom-1"].isChecked(),
...     page.thumbs["midnight"].isChecked(),
... )
(True, False)
```
{% endraw %}
