---
title: alto.ui.background
parent: api
package: alto.ui
api_components: [{"title": "run_in_background", "url": "/api/alto.ui.background/function-run_in_background/"}]
permalink: /api/alto.ui.background/
---
{% raw %}
Run slow work, such as a download, on another thread, and hear how it
went on the window's thread.

## Functions

- [`run_in_background`](function-run_in_background/) — Run work on another thread, then call `done` with its result, or `failed` with its exception, on the owner's thread.

<details markdown="1">
<summary>Module notes and examples</summary>

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

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"run_in_background": "function-run_in_background/"}</script>
{% include api-fragments.html %}
