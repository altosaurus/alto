---
title: CircleSettingsPanel
parent: alto.ui.settings_panel
api_module: alto.ui.settings_panel
package: alto.ui
permalink: /api/alto.ui.settings_panel/class-circlesettingspanel/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
CircleSettingsPanel(
    cfg: settings.CircleSettings,
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="CircleSettingsPanel" line=3502 %}{% raw %}

</div>

Bases: `ExerciseSettingsPanel`

The settings of the circle of fifths exercise: which kinds of
question to ask, and the colors of the circle.

The menu has two rows. Questions opens a page of switches. Colors
opens a page of color schemes to choose from, with a
button to make one of your own, which opens an editor. Edits are
live: each changes the settings and saves them. A new kind
of question emits `changed`, and a new color scheme emits
`restyled`, which keeps the question.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `cfg` | `CircleSettings` | The settings being edited. |
| `stack` | `SlideStack` | The menu and its pages: the menu, the questions, the color schemes and the editor of a scheme. |
| `questions_row` | `MenuRow` | The menu row for the questions. |
| `colors_row` | `MenuRow` | The menu row for the colors; its value is the name of the chosen scheme. |
| `questions` | `ChoiceChecklist` | The kinds of question: relative major, relative minor and Roman numerals. |
| `schemes` | `SchemePage` | The color schemes. |
| `editor` | `SchemeEditor` | The editor of a scheme of your own. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> panel = CircleSettingsPanel(
...     settings.CircleSettings()
... )
>>> (
...     panel.questions_row.value.text(),
...     panel.colors_row.value.text(),
... )
('3 of 3', 'Cyan to indigo')
```

**Constructor**

Build the panel for a set of settings.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `cfg` | `CircleSettings` | The settings to edit. |
| `parent` | `QWidget or None, default None` | The widget that owns the panel. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CircleSettingsPanel(
...     settings.CircleSettings()
... # the menu, the questions, the colors and the editor
... ).stack.count()
4
```
{% endraw %}
