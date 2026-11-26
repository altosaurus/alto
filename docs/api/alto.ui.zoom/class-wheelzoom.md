---
title: WheelZoom
parent: alto.ui.zoom
api_module: alto.ui.zoom
package: alto.ui
permalink: /api/alto.ui.zoom/class-wheelzoom/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
WheelZoom(parent: QObject | None = None)
```

{% endraw %}{% include api-source.html name="WheelZoom" line=365 %}{% raw %}

</div>

Bases: `QObject`

Zoom when the mouse wheel turns with Ctrl held, wherever the pointer
is.

A touchpad that sends small steps is added up, so that a whole notch
is needed to move one step.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> WheelZoom().eventFilter(
...     QObject(), QEvent(QEvent.Type.None_)
... )
False
```

**Constructor**

Start with no wheel turned.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QObject or None, default None` | The object that owns the filter. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> WheelZoom()._turned
0
```

## WheelZoom.follow

<div class="api-signature" markdown="1">

```python
def follow(app: QGuiApplication) -> None
```

{% endraw %}{% include api-source.html name="WheelZoom.follow" line=398 %}{% raw %}

</div>

Watch the window that has the focus, and each window that gains
it later, such as a dialog that opens.

The filter goes on the windows, not on the application. A window
is handed each wheel turn before the widget under the
pointer is, so a turn anywhere in it is seen, while the many
events that pass between the widgets inside it are not:
a filter on the application runs for every one of those, which
made building a page half as slow again.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `app` | `QGuiApplication` | The application whose windows to watch. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> handler = WheelZoom()
>>> handler.follow(app)
```

## WheelZoom.watch

<div class="api-signature" markdown="1">

```python
def watch(window: QWindow | None) -> None
```

{% endraw %}{% include api-source.html name="WheelZoom.watch" line=423 %}{% raw %}

</div>

Zoom when the wheel turns with Ctrl held over a window.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `window` | `QWindow or None` | The window. None, which is what Qt passes when no window has the focus, does nothing. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtWidgets import QWidget
>>> widget = QWidget()
>>> widget.show()
>>> handler = WheelZoom()
>>> handler.watch(widget.windowHandle())
>>> handler.watch(None)
```

## WheelZoom.eventFilter

<div class="api-signature" markdown="1">

```python
def eventFilter(
    watched: QObject,
    event: QEvent,
) -> bool
```

{% endraw %}{% include api-source.html name="WheelZoom.eventFilter" line=448 %}{% raw %}

</div>

Take a wheel event with Ctrl held as a zoom, and let every other
event through.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `watched` | `QObject` | The object the event is for. |
| `event` | `QEvent` | The event. |

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True when the event was a zoom, so that nothing under the pointer scrolls. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> WheelZoom().eventFilter(
...     QObject(), QEvent(QEvent.Type.None_)
... )
False
```
{% endraw %}
