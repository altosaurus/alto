---
title: ClefBasicsSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-clefbasicssettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ClefBasicsSettings(
    *,
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    question_type: str = 'construction',
)
```

{% endraw %}{% include api-source.html name="ClefBasicsSettings" line=1709 %}{% raw %}

</div>

Bases: `ClefChoice`

The settings of the clef basics exercise: what kind of question is
asked, and which clefs.

Every clef is one of three symbols, the G, C or F clef, put on a
line of the staff: the mezzo-soprano clef is the C clef
on the second line. The three symbols can always be chosen from.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `clefs` | `set of str` | The clefs that are asked for, any of `CLEF_BASICS_CLEFS`. Keyword-only. |
| `question_type` | `str, default "construction"` | "construction" to put a named clef on a blank staff, or "identification" to name the clef shown on a staff by pressing a button. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefBasicsSettings(
...     clefs={"subbass", "alto"}
... ).active_clefs()
['alto', 'subbass']
>>> ClefBasicsSettings().question_type
'construction'
```

## ClefBasicsSettings.active_type

<div class="api-signature" markdown="1">

```python
def active_type() -> str
```

{% endraw %}{% include api-source.html name="ClefBasicsSettings.active_type" line=1746 %}{% raw %}

</div>

Return the kind of question to ask.

**Returns**

| Type | Description |
| --- | --- |
| `str` | "construction" or "identification"; construction if the setting is anything else. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefBasicsSettings(
...     question_type="identification"
... ).active_type()
'identification'
>>> ClefBasicsSettings(
...     question_type="nonsense"
... ).active_type()
'construction'
```

## ClefBasicsSettings.answer_clefs

<div class="api-signature" markdown="1">

```python
def answer_clefs() -> list[str]
```

{% endraw %}{% include api-source.html name="ClefBasicsSettings.answer_clefs" line=1773 %}{% raw %}

</div>

Return the clefs to offer as buttons when a clef is to be named:
those asked for, and enough others to have a choice.

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | In canonical order; at least two, the treble and bass clefs being added if only one is asked for. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ClefBasicsSettings(
...     clefs={"alto", "tenor"}
... ).answer_clefs()
['alto', 'tenor']
>>> ClefBasicsSettings(
...     clefs={"alto"}
... ).answer_clefs()
['treble', 'alto']
```
{% endraw %}
