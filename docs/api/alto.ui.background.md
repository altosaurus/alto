---
title: alto.ui.background
parent: api
package: alto.ui
permalink: /api/alto.ui.background/
---
{% raw %}
Run slow work, such as a download, on another thread, and hear how it
went on the window's thread.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> import time
>>> heard = []
>>> owner = QObject()
>>> _ = run_in_background(
...     lambda: 6 * 7,
...     owner=owner,
...     done=heard.append,
...     failed=heard.append,
... )
>>> deadline = time.monotonic() + 5
>>> while (
...     not heard
...     and time.monotonic() < deadline
... ):
...     app.processEvents()
>>> heard
[42]
```

## run_in_background

```python
def run_in_background(
    work: Callable[[], T],
    *,
    owner: QObject,
    done: Callable[[T], None],
    failed: Callable[[Exception], None],
) -> threading.Thread
```

Run work on another thread, then call `done` with its result, or
`failed` with its exception, on the owner's thread.

The window stays responsive while the work runs. If the owner is
deleted before the work ends, neither is called. The thread
does not keep Alto from quitting.

**Parameters**

- `work` (*callable*): The slow part. It must not touch widgets.
- `owner` (*QObject*): The object the work is for, such as the dialog that started it. Keyword-only.
- `done` (*callable*): Called with what `work` returned. Keyword-only.
- `failed` (*callable*): Called with the exception `work` raised. Keyword-only.

**Returns**

- *threading.Thread*: The thread doing the work, already started. Callers need not keep it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> import time
>>> heard = []
>>> owner = QObject()
>>> def broken():
...     raise OSError("offline")
>>> _ = run_in_background(
...     broken,
...     owner=owner,
...     done=heard.append,
...     failed=lambda error: heard.append(
...         str(error)
...     ),
... )
>>> deadline = time.monotonic() + 5
>>> while (
...     not heard
...     and time.monotonic() < deadline
... ):
...     app.processEvents()
>>> heard
['offline']
```
{% endraw %}
