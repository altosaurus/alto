---
title: SidebarToggle
parent: alto.ui.widgets
api_module: alto.ui.widgets
package: alto.ui
permalink: /api/alto.ui.widgets/class-sidebartoggle/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
SidebarToggle(
    parent: QWidget | None = None,
    *,
    noun: str = 'exercise list',
)
```

{% endraw %}{% include api-source.html name="SidebarToggle" line=216 %}{% raw %}

</div>

Bases: `QToolButton`

A button that shows or hides the exercise list.

Connect to `clicked`; the main window decides what to show and calls
`set_open` to match.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> button = SidebarToggle()
>>> button.toolTip()
'Hide exercise list'
>>> button.set_open(False)
>>> button.toolTip()
'Show exercise list'
```

**Constructor**

Create the toggle, showing the list as open.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns the button. |
| `noun` | `str, default "exercise list"` | What the list is called in the tooltip: "Hide exercise list". Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> SidebarToggle().autoRaise()
True
>>> SidebarToggle(noun="lesson list").toolTip()
'Hide lesson list'
```

## SidebarToggle.set_open

<div class="api-signature" markdown="1">

```python
def set_open(is_open: bool) -> None
```

{% endraw %}{% include api-source.html name="SidebarToggle.set_open" line=265 %}{% raw %}

</div>

Show the icon and tooltip for the list being open or closed.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `is_open` | `bool` | True if the exercise list is showing. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> button = SidebarToggle()
>>> button.set_open(False)
>>> button.toolTip()
'Show exercise list'
```
{% endraw %}
