---
title: SlideStack
parent: alto.ui.settings_menu
api_module: alto.ui.settings_menu
package: alto.ui
permalink: /api/alto.ui.settings_menu/class-slidestack/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
SlideStack(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="SlideStack" line=1425 %}{% raw %}

</div>

Bases: `QStackedWidget`

A stacked widget whose pages slide in from the right (going deeper)
or the left (going back).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> stack = SlideStack()
>>> _ = stack.addWidget(QWidget())
>>> _ = stack.addWidget(QWidget())
>>> stack.sliding
False
```

**Constructor**

Create an empty stack.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns it. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> SlideStack().count()
0
```

## SlideStack.sliding

<div class="api-signature" markdown="1">

```python
@property
def sliding() -> bool
```

{% endraw %}{% include api-source.html name="SlideStack.sliding" line=1457 %}{% raw %}

</div>

Report whether a page is sliding in.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True from the start of a slide until it finishes. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> SlideStack().sliding
False
```

## SlideStack.slide_to

<div class="api-signature" markdown="1">

```python
def slide_to(index: int) -> None
```

{% endraw %}{% include api-source.html name="SlideStack.slide_to" line=1473 %}{% raw %}

</div>

Slide to another page.

Going to a later page slides it in from the right and going back
slides it in from the left. A request made during a
slide, or for the page already showing, is ignored.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `index` | `int` | The page to go to. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> stack = SlideStack()
>>> _ = stack.addWidget(QWidget())
>>> _ = stack.addWidget(QWidget())
>>> stack.slide_to(1)
>>> stack.sliding
True
```
{% endraw %}
