---
title: Step
parent: alto.lessons.base
api_module: alto.lessons.base
package: alto.lessons
permalink: /api/alto.lessons.base/class-step/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
Step(
    title: str,
    text: str,
    circle: str = 'none',
    hear: tuple[tuple[str, ...], ...] = (),
    hear_label: str = 'Hear it',
    make_task: Callable[[random.Random], Task] | None = field(default=None, compare=False),
    closing: bool = False,
    staves: tuple[Staff, ...] = (),
    task_staff: bool = False,
    scale: str = '',
    scale_tonic: str = 'C4',
    scale_explore: bool = True,
    keyboard_note: str = '',
    hear_display: Literal['', 'staff', 'keyboard'] = '',
    picture: PicturePosition | FingerboardPosition | None = None,
    hear_instrument: str = '',
    single_question: bool = False,
    label_middle_c: bool = False,
    rhythm: tuple[str, ...] = (),
    rhythm_meter: tuple[int, int] = (4, 4),
)
```

{% endraw %}{% include api-source.html name="Step" line=209 %}{% raw %}

</div>

One page of a lesson.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `title` | `str` | The heading. |
| `text` | `str` | What to read, as simple HTML. |
| `circle` | `str` | How the circle of fifths is shown: "none" for no circle, "rest" for a picture that does not respond, "explore" for one that can be clicked, or "walk" for one that can also be walked around with two buttons. |
| `hear` | `tuple of tuple of str` | Notes to play from a Hear it button, as columns of note names such as "C4"; empty for no button. |
| `hear_label` | `str` | What the Hear it button says. |
| `make_task` | `callable or None` | Makes a fresh task from a random generator each time one is wanted; None for a step with no task. |
| `single_question` | `bool` | True when the knowledge check repeats the same question on every attempt. |
| `closing` | `bool` | True for the last step, which offers to practice. |
| `staves` | `tuple of Staff` | Captioned staves in reading order. Adjacent examples share a panel and wrap when space is limited. |
| `task_staff` | `bool` | Show one staff beside the words that follows the task: it draws the task’s clef and key signature. |
| `scale` | `str` | Scale type for an interactive notation diagram; empty for none. |
| `scale_tonic` | `str` | Starting note of the diagram, including its octave. |
| `scale_explore` | `bool` | Allow changing the example. False hides the selectors for identification tasks. |
| `hear_display` | `str` | Show the playback pitches on a treble staff or keyboard ("staff" or "keyboard"). Empty hides this diagram. |
| `keyboard_note` | `str` | A named pitch to highlight on the lesson keyboard, which spans middle C to the C above it. |
| `picture` | `PicturePosition or FingerboardPosition or None` | An instrument picture to show beside the words, such as one supplied by a plugin. Alto draws it with the same widget the exercises use. None for no picture. |
| `hear_instrument` | `str` | The key of the instrument that plays the Hear it notes, such as one supplied by a plugin. Empty for the learner's own choice of sound. |
| `rhythm` | `tuple of str` | Written note and rest values to count with a metronome. |
| `rhythm_meter` | `tuple of int` | Numerator and denominator for the rhythm example. |
| `label_middle_c` | `bool` | Label middle C and bracket the pair of black keys beside it. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Step(
...     title="Hello", text="<p>Hi.</p>"
... ).circle
'none'
```
{% endraw %}
