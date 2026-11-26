---
title: CircleSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-circlesettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
CircleSettings(
    questions: set[str] = field(default_factory=lambda: set(CIRCLE_QUESTIONS)),
    scheme: str = DEFAULT_SCHEME,
    customs: list[CustomRecord] = field(default_factory=list),
)
```

{% endraw %}{% include api-source.html name="CircleSettings" line=1840 %}{% raw %}

</div>

The settings of the circle of fifths exercise.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `questions` | `set of str` | The kinds of question to ask, keys of `CIRCLE_QUESTIONS`: the relative major of a minor key, the relative minor of a major key, and the Roman numeral of a chord of a key. |
| `scheme` | `str` | The key of the color scheme the circle is drawn in: a preset of `alto.circle_schemes` or one of `customs`. |
| `customs` | `list of CustomRecord` | The color schemes the user made. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CircleSettings().active_questions()
['major', 'minor', 'numeral']
>>> CircleSettings(
...     questions={"numeral"}
... ).active_questions()
['numeral']
>>> CircleSettings().active_scheme().name
'Cyan to indigo'
```

## CircleSettings.active_questions

<div class="api-signature" markdown="1">

```python
def active_questions() -> list[str]
```

{% endraw %}{% include api-source.html name="CircleSettings.active_questions" line=1874 %}{% raw %}

</div>

Return the kinds of question to ask, in the order they are
listed.

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | The chosen kinds, or all of them if none is chosen. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CircleSettings(
...     questions=set()
... ).active_questions()
['major', 'minor', 'numeral']
>>> CircleSettings(
...     questions={"minor", "nonsense"}
... ).active_questions()
['minor']
```

## CircleSettings.active_scheme

<div class="api-signature" markdown="1">

```python
def active_scheme() -> Scheme
```

{% endraw %}{% include api-source.html name="CircleSettings.active_scheme" line=1899 %}{% raw %}

</div>

Return the color scheme to draw the circle in.

**Returns**

| Type | Description |
| --- | --- |
| `Scheme` | The chosen scheme, or the default if the saved choice is no longer available, such as a deleted custom scheme. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CircleSettings(
...     scheme="midnight"
... ).active_scheme().name
'Midnight'
>>> CircleSettings(
...     scheme="deleted"
... ).active_scheme().key
'cyan-indigo'
```
{% endraw %}
