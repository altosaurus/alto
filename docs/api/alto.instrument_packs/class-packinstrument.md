---
title: PackInstrument
parent: alto.instrument_packs
api_module: alto.instrument_packs
package: alto
permalink: /api/alto.instrument_packs/class-packinstrument/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PackInstrument(
    key: str,
    image: Path,
    size: tuple[int, int],
    strings: tuple[PackString, ...],
    sound: Instrument | None,
    correct_answer_animation: AnswerAnimation | None = None,
    sound_info: InstrumentInfo | None = None,
    positions: tuple[tuple[int, str], ...] = (),
    views: tuple[PackView, ...] = (),
    keyboards: tuple[PackKeyboard, ...] = (),
    keyboard_style: PackKeyboardStyle | None = None,
)
```

{% endraw %}{% include api-source.html name="PackInstrument" line=378 %}{% raw %}

</div>

A pack-qualified identity and the resources shared by its exercises.

## PackInstrument.keyboard

<div class="api-signature" markdown="1">

```python
def keyboard(name: str) -> PackKeyboard | None
```

{% endraw %}{% include api-source.html name="PackInstrument.keyboard" line=395 %}{% raw %}

</div>

Find one of the instrument's keyboards by name.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `name` | `str` | The keyboard's name as the plugin wrote it. |

**Returns**

| Type | Description |
| --- | --- |
| `PackKeyboard or None` | The keyboard, or None if the instrument has no keyboard with that name. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> keys = PackKeyboard("Manual", "C4", "E4")
>>> board = PackInstrument(
...     "pack.x.y",
...     Path("a.png"),
...     (10, 20),
...     (),
...     None,
...     keyboards=(keys,),
... )
>>> (
...     board.keyboard("Manual") is keys,
...     board.keyboard("Pedals"),
... )
(True, None)
```

## PackInstrument.picture

<div class="api-signature" markdown="1">

```python
def picture(view: str = '') -> tuple[Path, tuple[int, int]] | None
```

{% endraw %}{% include api-source.html name="PackInstrument.picture" line=432 %}{% raw %}

</div>

Find the picture for a view: the instrument's main picture for
an empty name, otherwise the named extra picture.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `view` | `str, default ""` | The view's name, or an empty string for the main picture. |

**Returns**

| Type | Description |
| --- | --- |
| `tuple of Path and tuple of int, or None` | The image file and its size in pixels, or None if the instrument has no such view. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> back = PackView(
...     "back", Path("back.png"), (30, 40)
... )
>>> board = PackInstrument(
...     "pack.x.y",
...     Path("front.png"),
...     (10, 20),
...     (),
...     None,
...     views=(back,),
... )
>>> (
...     board.picture(),
...     board.picture("back"),
...     board.picture("side"),
... )
((PosixPath('front.png'), (10, 20)), (PosixPath('back.png'),
(30, 40)), None)
```
{% endraw %}
