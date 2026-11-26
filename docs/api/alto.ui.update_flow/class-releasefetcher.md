---
title: ReleaseFetcher
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/class-releasefetcher/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ReleaseFetcher(parent: QObject | None = None)
```

{% endraw %}{% include api-source.html name="ReleaseFetcher" line=544 %}{% raw %}

</div>

Bases: `QObject`

Ask GitHub for the latest release on another thread, so that the
window never freezes while it waits.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `done` | `Signal` | Emitted once, with the HTTP status (0 if GitHub was not reached) and the answer or the reason there was none. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ReleaseFetcher().cancel()
```

**Constructor**

Make a fetcher that has not asked anything.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QObject or None, default None` | The object that owns it. |

## ReleaseFetcher.start

<div class="api-signature" markdown="1">

```python
def start(
    *,
    seconds: int,
) -> None
```

{% endraw %}{% include api-source.html name="ReleaseFetcher.start" line=574 %}{% raw %}

</div>

Start asking.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `seconds` | `int` | How long to wait for GitHub. Keyword-only. |

## ReleaseFetcher.cancel

<div class="api-signature" markdown="1">

```python
def cancel() -> None
```

{% endraw %}{% include api-source.html name="ReleaseFetcher.cancel" line=591 %}{% raw %}

</div>

Stop caring about the answer; the thread ends by itself when
GitHub answers or the time is up.
{% endraw %}
