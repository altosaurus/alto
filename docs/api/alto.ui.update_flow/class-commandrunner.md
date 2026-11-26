---
title: CommandRunner
parent: alto.ui.update_flow
api_module: alto.ui.update_flow
package: alto.ui
permalink: /api/alto.ui.update_flow/class-commandrunner/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
CommandRunner(parent: QObject | None = None)
```

{% endraw %}{% include api-source.html name="CommandRunner" line=136 %}{% raw %}

</div>

Bases: `QObject`

Run one program without freezing the window, handing on what it
prints as it prints it, and how it ended.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `output` | `Signal` | Emitted with each piece of text the program prints, as it arrives. Its errors are mixed in with it. |
| `done` | `Signal` | Emitted once, with the exit code and everything the program printed. The exit code is -1 if the program could not be started, was stopped for taking too long, or crashed. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> runner = CommandRunner()
>>> runner.running
False
```

**Constructor**

Make a runner that has not started anything.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QObject or None, default None` | The object that owns it. |

## CommandRunner.running

<div class="api-signature" markdown="1">

```python
@property
def running() -> bool
```

{% endraw %}{% include api-source.html name="CommandRunner.running" line=191 %}{% raw %}

</div>

Say whether a program has been started and has not yet ended.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True while it runs. |

## CommandRunner.start

<div class="api-signature" markdown="1">

```python
def start(
    program: str,
    *,
    arguments: list[str],
    seconds: int = 0,
) -> None
```

{% endraw %}{% include api-source.html name="CommandRunner.start" line=202 %}{% raw %}

</div>

Start a program.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `program` | `str` | The program's path. |
| `arguments` | `list of str` | What to give it. Keyword-only. |
| `seconds` | `int, default 0` | Stop it if it has not ended by then; 0 lets it take as long as it takes. Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> import sys
>>> runner = CommandRunner()
>>> runner.start(
...     sys.executable,
...     arguments=[
...         "-c",
...         "import time; time.sleep(30)",
...     ],
... )
>>> runner.stop()
>>> runner.running
False
```

## CommandRunner.stop

<div class="api-signature" markdown="1">

```python
def stop() -> None
```

{% endraw %}{% include api-source.html name="CommandRunner.stop" line=247 %}{% raw %}

</div>

Stop the program, if it is running, without announcing that it
has ended.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> CommandRunner().stop()
```
{% endraw %}
