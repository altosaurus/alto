---
title: MidiInput
parent: alto.ui.midi_input
api_module: alto.ui.midi_input
package: alto.ui
permalink: /api/alto.ui.midi_input/class-midiinput/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
MidiInput()
```

{% endraw %}{% include api-source.html name="MidiInput" line=17 %}{% raw %}

</div>

Bases: `QToolButton`

Select one ALSA sequencer source and forward its key presses on the
Qt event loop.

**Constructor**

Create the source menu with input turned off.

## MidiInput.disconnect_port

<div class="api-signature" markdown="1">

```python
def disconnect_port() -> None
```

{% endraw %}{% include api-source.html name="MidiInput.disconnect_port" line=135 %}{% raw %}

</div>

Release the input when the learner turns it off or leaves the
exercise.
{% endraw %}
