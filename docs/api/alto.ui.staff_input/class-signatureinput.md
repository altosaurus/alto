---
title: SignatureInput
parent: alto.ui.staff_input
api_module: alto.ui.staff_input
package: alto.ui
permalink: /api/alto.ui.staff_input/class-signatureinput/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class SignatureInput(ScaleInput)
```

{% endraw %}{% include api-source.html name="SignatureInput" line=1192 %}{% raw %}

</div>

Place accidentals in consecutive key-signature slots immediately
after the clef.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = SignatureInput()
>>> staff.reset_scale(
...     "treble", slots=7, caption="D major"
... )
>>> staff.place_next(Note.parse("F#5"))
>>> staff.notes, staff.columns
([Note(octave=5, letter=3, accidental=1)], [])
```

## SignatureInput.reset_signature

<div class="api-signature" markdown="1">

```python
def reset_signature(
    clef: str,
    *,
    key: int,
    caption: str,
    starting_slots: list[int],
) -> None
```

{% endraw %}{% include api-source.html name="SignatureInput.reset_signature" line=1212 %}{% raw %}

</div>

Set the fixed signs for this question and clear the learner’s
entries.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `clef` | `str` | Clef used to read the positions. |
| `key` | `int` | Target signature. |
| `caption` | `str` | Name of the key under the staff. |
| `starting_slots` | `list of int` | Positions to fill before the learner begins. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = SignatureInput()
>>> staff.reset_signature(
...     "treble",
...     key=2,
...     caption="D major",
...     starting_slots=[1],
... )
>>> len(staff.template), staff.template[1]
(7, Note(octave=5, letter=0, accidental=1))
```

## SignatureInput.entered_signature

<div class="api-signature" markdown="1">

```python
def entered_signature() -> list[Note | None]
```

{% endraw %}{% include api-source.html name="SignatureInput.entered_signature" line=1259 %}{% raw %}

</div>

Combine the fixed signs and the learner's entries in staff
order.

**Returns**

| Type | Description |
| --- | --- |
| `list of Note or None` | One pitch per occupied slot, with None in each remaining gap. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = SignatureInput()
>>> staff.reset_signature(
...     "treble",
...     key=2,
...     caption="D major",
...     starting_slots=[1],
... )
>>> staff.place_next(Note.parse("F#5"))
>>> [
...     str(n)
...     for n in staff.entered_signature()
...     if n is not None
... ]
['F♯5', 'C♯5']
```

## SignatureInput.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(event: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="SignatureInput.paintEvent" line=1312 %}{% raw %}

</div>

Draw the blank staff and caption, then the placed signs and the
next sign under the pointer.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QPaintEvent` | The paint request. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = SignatureInput()
>>> staff.reset_scale("bass", slots=7)
>>> staff.place_next(Note.parse("Bb2"))
>>> staff.grab().isNull()
False
```
{% endraw %}
