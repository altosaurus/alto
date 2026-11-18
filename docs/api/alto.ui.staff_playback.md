---
title: alto.ui.staff_playback
parent: api
package: alto.ui
order: 60
permalink: /api/alto.ui.staff_playback/
---
{% raw %}
Connect a displayed music sample to the notes sounding on its staff.

## StaffPlayback

```python
StaffPlayback(
    parent: QWidget,
    *,
    highlight: Callable[[int | None], object],
)
```

Bases: `QObject`

Follow a sample's audio onsets and end playback when its view closes.

**Constructor**

Attach playback to its view.

**Parameters**

- `parent` (*QWidget*): The view containing the sample.
- `highlight` (*callable*): Draw the current step on the displayed staff or staves.

### StaffPlayback.play

```python
def play(
    columns: Sequence[Sequence[Note]],
    *,
    gap_ms: int = 450,
    force: bool = False,
) -> None
```

Play the displayed notes in order.

**Parameters**

- `columns` (*sequence of sequence of Note*): Notes grouped by onset.
- `gap_ms` (*int*): Time between onsets in milliseconds.
- `force` (*bool*): Allow explicit auditions even when exercise sounds are muted.

### StaffPlayback.stop

```python
def stop() -> None
```

Clear this view's sounding note and cancel its pending audio.

### StaffPlayback.eventFilter

```python
def eventFilter(
    watched: QObject,
    event: QEvent,
) -> bool
```

End the sample when the learner leaves its view.

**Parameters**

- `watched` (*QObject*): The sample's containing view.
- `event` (*QEvent*): The pending Qt event.

**Returns**

- *bool*: Whether the event was consumed.
{% endraw %}
