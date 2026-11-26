---
title: HelpButton
parent: alto.ui.widgets
api_module: alto.ui.widgets
package: alto.ui
permalink: /api/alto.ui.widgets/class-helpbutton/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
HelpButton(
    text_provider: Callable[[], str],
    *,
    parent: QWidget | None = None,
)
```

{% endraw %}{% include api-source.html name="HelpButton" line=290 %}{% raw %}

</div>

Bases: `QToolButton`

A "?" button that opens a small popover with help text.

Click anywhere else to close it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HelpButton(
...     lambda: "<b>Press the right note.</b>"
... ).toolTip()
'How this exercise works'
```

**Constructor**

Create the button.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `text_provider` | `callable` | Called with no arguments each time the help is shown, so the text can follow the current settings. It returns simple HTML. |
| `parent` | `QWidget or None, default None` | The widget that owns the button. Keyword-only. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> calls = []
>>> button = HelpButton(
...     lambda: calls.append(1) or "help"
... )
>>> # the text is not asked for until the button is clicked
>>> calls
[]
```

## HelpButton.show_help

<div class="api-signature" markdown="1">

```python
def show_help() -> None
```

{% endraw %}{% include api-source.html name="HelpButton.show_help" line=343 %}{% raw %}

</div>

Open the popover under the button, right-aligned with it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> HelpButton(
...     lambda: "<b>Help</b>"
... ).show_help()  # doctest: +SKIP
```
{% endraw %}
