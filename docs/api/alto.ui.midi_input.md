---
title: alto.ui.midi_input
parent: api
package: alto.ui
permalink: /api/alto.ui.midi_input/
---
{% raw %}
ALSA keyboard input for answering a question with a played pitch.

## MidiInput

```python
MidiInput()
```

Bases: `QToolButton`

Select one ALSA sequencer source and forward its key presses on the Qt event loop.

**Constructor**

Create the source menu with input turned off.

### MidiInput.disconnect_port

```python
def disconnect_port() -> None
```

Release the input when the learner turns it off or leaves the exercise.
{% endraw %}
