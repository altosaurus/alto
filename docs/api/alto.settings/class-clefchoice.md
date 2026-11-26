---
title: ClefChoice
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-clefchoice/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class ClefChoice
```

{% endraw %}{% include api-source.html name="ClefChoice" line=330 %}{% raw %}

</div>

Settings with a set of chosen clefs, which are always used in the
same order.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `CLEF_ORDER` | `tuple of str` | Every clef the settings may hold, in the order they are offered and used. Each subclass sets it. |
| `clefs` | `set of str` | The chosen clefs. The dataclass that uses this mixin declares the field and its default. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ArpeggioSettings(
...     clefs={"tenor", "alto"}
... ).active_clefs()
['alto', 'tenor']
```

## ClefChoice.active_clefs

<div class="api-signature" markdown="1">

```python
def active_clefs() -> list[str]
```

{% endraw %}{% include api-source.html name="ClefChoice.active_clefs" line=355 %}{% raw %}

</div>

Return the clefs to use, in canonical order.

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | The chosen clefs in the order of `CLEF_ORDER`, or the treble clef if none are chosen. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNameSettings(
...     clefs={"grand", "tenor"}
... ).active_clefs()
['tenor', 'grand']
>>> ClefBasicsSettings(
...     clefs={"subbass", "treble"}
... ).active_clefs()
['treble', 'subbass']
>>> NoteNameSettings(clefs=set()).active_clefs()
['treble']
```
{% endraw %}
