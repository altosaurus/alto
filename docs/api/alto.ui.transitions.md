---
title: alto.ui.transitions
parent: api
package: alto.ui
permalink: /api/alto.ui.transitions/
---
{% raw %}
The transitions between the exercises and the lessons on the home page.

A transition moves between two sets of cards. Each card is photographed
first, as a sprite, and a sprite can be faded, slid,
scaled, blurred or cut away from one side. A transition is a function
that sets how every sprite looks at each moment, so ten
different ones share one player.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [
...     transition.key
...     for transition in TRANSITIONS
... ][:3]
['none', 'cascade', 'fade']
>>> DEFAULT_TRANSITION
'cascade'
```

## Sprite

<div class="api-signature" markdown="1">

```python
Sprite(
    pixmap: QPixmap,
    rect: QRectF,
    opacity: float = 1.0,
    dx: float = 0.0,
    dy: float = 0.0,
    sx: float = 1.0,
    sy: float = 1.0,
    blur: float = 0.0,
    angle: float = 0.0,
    reveal: float = 1.0,
    reveal_from: int = 1,
)
```

{% endraw %}{% include api-source.html name="Sprite" line=61 %}{% raw %}

</div>

A photograph of one card, and how it is drawn at this moment.

**Attributes**

- `pixmap` (*QPixmap*): The photograph.
- `rect` (*QRectF*): Where the card is, in the canvas.
- `opacity` (*float*): 0 for invisible to 1 for solid.
- `dx` (*float*): How far it is moved right, in pixels.
- `dy` (*float*): How far it is moved down, in pixels.
- `sx` (*float*): How much it is stretched across, about its middle; 1 is as it was.
- `sy` (*float*): How much it is stretched down, about its middle.
- `blur` (*float*): 0 for sharp to 1 for fully blurred.
- `angle` (*float*): How far it is turned about its middle, in degrees, clockwise.
- `reveal` (*float*): How much of it shows, from 0 to 1.
- `reveal_from` (*int*): 1 to uncover it from the left, -1 from the right, 0 from the middle outwards.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sprite = Sprite(
...     pixmap=QPixmap(),
...     rect=QRectF(0, 0, 10, 10),
... )
>>> sprite.opacity, sprite.reveal
(1.0, 1.0)
```

## Scene

<div class="api-signature" markdown="1">

```python
Scene(
    time: float,
    old: Sequence[Sprite],
    new: Sequence[Sprite],
    direction: int,
)
```

{% endraw %}{% include api-source.html name="Scene" line=116 %}{% raw %}

</div>

What a transition is given at each moment: the time, the two sets of
sprites and the direction.

**Attributes**

- `time` (*float*): The time since the transition began, in milliseconds.
- `old` (*sequence of Sprite*): The cards that are leaving.
- `new` (*sequence of Sprite*): The cards that are arriving.
- `direction` (*int*): 1 when going toward the lessons, -1 when coming back.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Scene(
...     time=0.0, old=[], new=[], direction=1
... ).direction
1
```

## ease_out

<div class="api-signature" markdown="1">

```python
def ease_out(progress: float) -> float
```

{% endraw %}{% include api-source.html name="ease_out" line=146 %}{% raw %}

</div>

Ease a progress from 0 to 1 so that it starts fast and slows to a
stop.

**Parameters**

- `progress` (*float*): How far along, from 0 to 1.

**Returns**

- *float*: The eased progress.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ease_out(0.0), ease_out(1.0), ease_out(0.5)
(0.0, 1.0, 0.875)
```

## ramp

<div class="api-signature" markdown="1">

```python
def ramp(
    time: float,
    *,
    start: float,
    length: float,
) -> float
```

{% endraw %}{% include api-source.html name="ramp" line=170 %}{% raw %}

</div>

Say how far along a part of a transition is, from 0 before it starts
to 1 once it has finished.

**Parameters**

- `time` (*float*): The time since the transition began, in milliseconds.
- `start` (*float*): When the part begins. Keyword-only.
- `length` (*float*): How long it lasts. Keyword-only.

**Returns**

- *float*: The progress, from 0 to 1.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     ramp(50, start=100, length=200),
...     ramp(200, start=100, length=200),
...     ramp(900, start=100, length=200),
... )
(0.0, 0.5, 1.0)
```

## hide

<div class="api-signature" markdown="1">

```python
def hide(sprites: Sequence[Sprite]) -> None
```

{% endraw %}{% include api-source.html name="hide" line=206 %}{% raw %}

</div>

Make sprites invisible.

**Parameters**

- `sprites` (*sequence of Sprite*): The sprites.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> card = Sprite(
...     pixmap=QPixmap(), rect=QRectF()
... )
>>> hide([card])
>>> card.opacity
0.0
```

## fade_in

<div class="api-signature" markdown="1">

```python
def fade_in(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="fade_in" line=228 %}{% raw %}

</div>

Set the sprites for a fade in: the new cards fade up from clear, and
nothing of the old remains.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> fade_in(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].opacity
0.0
```

## crossfade

<div class="api-signature" markdown="1">

```python
def crossfade(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="crossfade" line=257 %}{% raw %}

</div>

Set the sprites for a crossfade: the old cards fade out as the new
ones fade in.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> old, new = (
...     [
...         Sprite(
...             pixmap=QPixmap(), rect=QRectF()
...         )
...     ],
...     [
...         Sprite(
...             pixmap=QPixmap(), rect=QRectF()
...         )
...     ],
... )
>>> crossfade(
...     Scene(
...         time=300,
...         old=old,
...         new=new,
...         direction=1,
...     )
... )
>>> old[0].opacity, new[0].opacity
(0.0, 1.0)
```

## slide

<div class="api-signature" markdown="1">

```python
def slide(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="slide" line=300 %}{% raw %}

</div>

Set the sprites for a slide: both sets move sideways, toward the
side of the switch that was pressed.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> slide(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].dx
60.0
```

## rise

<div class="api-signature" markdown="1">

```python
def rise(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="rise" line=337 %}{% raw %}

</div>

Set the sprites for a rise: the old cards sink and fade, and the new
ones rise into place.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> rise(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].dy, new[0].opacity
(22.0, 0.0)
```

## cascade

<div class="api-signature" markdown="1">

```python
def cascade(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="cascade" line=371 %}{% raw %}

</div>

Set the sprites for a cascade: the new cards arrive one after
another, each rising a little as it appears.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
...     for _ in range(2)
... ]
>>> cascade(
...     Scene(
...         time=100,
...         old=[],
...         new=new,
...         direction=1,
...     )
... )
>>> new[0].opacity > new[1].opacity > 0.0
True
```

## zoom

<div class="api-signature" markdown="1">

```python
def zoom(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="zoom" line=405 %}{% raw %}

</div>

Set the sprites for a zoom: the old cards grow a little as they
fade, and the new ones grow into place.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> zoom(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].sx
0.92
```

## flip

<div class="api-signature" markdown="1">

```python
def flip(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="flip" line=441 %}{% raw %}

</div>

Set the sprites for a flip: each old card turns edge on and goes,
then each new one turns face on.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> flip(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].opacity
0.0
```

## blur

<div class="api-signature" markdown="1">

```python
def blur(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="blur" line=479 %}{% raw %}

</div>

Set the sprites for a blur: the old cards dissolve into a blur and
the new ones come into focus.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> blur(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].blur, new[0].opacity
(1.0, 0.0)
```

## wipe

<div class="api-signature" markdown="1">

```python
def wipe(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="wipe" line=513 %}{% raw %}

</div>

Set the sprites for a wipe: the new cards are uncovered from one
side while the old ones fade.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> wipe(
...     Scene(
...         time=0,
...         old=[],
...         new=new,
...         direction=-1,
...     )
... )
>>> new[0].reveal, new[0].reveal_from
(0.0, -1)
```

## drop

<div class="api-signature" markdown="1">

```python
def drop(scene: Scene) -> None
```

{% endraw %}{% include api-source.html name="drop" line=547 %}{% raw %}

</div>

Set the sprites for drop and pop: the old cards drop away one by
one, then the new ones pop in with a small bounce.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> drop(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     )
... )
>>> new[0].opacity
0.0
```

## Transition

<div class="api-signature" markdown="1">

```python
Transition(
    key: str,
    label: str,
    about: str,
    frame: Callable[[Scene], None] | None = field(default=None, compare=False),
    length: Callable[[Scene], float] = field(default=lambda scene: 0.0, compare=False),
)
```

{% endraw %}{% include api-source.html name="Transition" line=590 %}{% raw %}

</div>

One way of moving between the exercises and the lessons.

**Attributes**

- `key` (*str*): What it is saved as.
- `label` (*str*): What the settings call it.
- `about` (*str*): A sentence saying what it looks like.
- `frame` (*callable or None*): Sets how every sprite looks in a scene; None for no transition at all.
- `length` (*callable*): Says how long it lasts, in milliseconds, from a scene that has the cards but no time.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> TRANSITIONS[0].frame is None
True
```

## Motion

<div class="api-signature" markdown="1">

```python
Motion(
    length: float = 320.0,
    per_card: float = 0.0,
    start: float = 0.0,
    after: bool = False,
    order: str = 'index',
    ease: str = 'out',
    dx: float = 0.0,
    dy: float = 0.0,
    scale: float = 1.0,
    sx: float = 1.0,
    sy: float = 1.0,
    angle: float = 0.0,
    blur: float = 0.0,
    fade: bool = True,
    reveal: str = '',
)
```

{% endraw %}{% include api-source.html name="Motion" line=642 %}{% raw %}

</div>

How one set of cards moves in a transition built from parts: when
each card starts, how long it takes, and what it does.

Every card goes between its resting look and a look given here, so
the same description serves for cards arriving (from that
look to rest) and leaving (from rest to that look).

**Attributes**

- `length` (*float*): How long each card takes, in milliseconds.
- `per_card` (*float*): How much later each card starts than the one before it.
- `start` (*float*): When the first card starts.
- `after` (*bool*): True to wait until the cards that are leaving have all finished before starting; only for cards that are arriving.
- `order` (*str*): The order the cards start in: one of `ORDERS`.
- `ease` (*str*): How the motion is timed: one of `EASES`.
- `dx` (*float*): How far to the right the card is at the far look, in pixels; it follows the direction of the switch.
- `dy` (*float*): How far down the card is at the far look.
- `scale` (*float*): How big the card is at the far look, as a fraction of its size.
- `sx` (*float*): As well as `scale`, how wide, for a card that turns on its edge.
- `sy` (*float*): As well as `scale`, how tall.
- `angle` (*float*): How far the card is turned at the far look, in degrees; it follows the direction of the switch.
- `blur` (*float*): How blurred it is at the far look, from 0 to 1.
- `fade` (*bool*): True to fade between solid and clear; False to keep it solid, and hide it only once it is out of the way.
- `reveal` (*str*): "" for none, or "side" or "center" to uncover it from one side or from the middle.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Motion().order, Motion().ease
('index', 'out')
```

## eased

<div class="api-signature" markdown="1">

```python
def eased(
    progress: float,
    *,
    how: str,
) -> float
```

{% endraw %}{% include api-source.html name="eased" line=712 %}{% raw %}

</div>

Time a progress from 0 to 1 in one of the ways a motion can be
eased.

**Parameters**

- `progress` (*float*): How far along, from 0 to 1.
- `how` (*str*): One of `EASES`: "out" slows to a stop, "in" speeds up, "back" overshoots a little and settles, "linear" does neither. Keyword-only.

**Returns**

- *float*: The timed progress, which "back" takes a little past 1 on the way.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     eased(0.5, how="linear"),
...     eased(1.0, how="back"),
...     eased(0.5, how="in"),
... )
(0.5, 1.0, 0.25)
>>> eased(0.8, how="back") > 1.0
True
```

## ranks

<div class="api-signature" markdown="1">

```python
def ranks(
    sprites: Sequence[Sprite],
    *,
    order: str,
) -> list[int]
```

{% endraw %}{% include api-source.html name="ranks" line=761 %}{% raw %}

</div>

Say where each sprite comes in an order: 0 for the first to start.

**Parameters**

- `sprites` (*sequence of Sprite*): The cards of one side.
- `order` (*str*): One of `ORDERS`: "index" is as laid out, "reverse" backwards, "outward" from the middle of the cards to the edges, "inward" the other way, "diagonal" from the top left to the bottom right, and "random" in a fixed scrambled order. Keyword-only.

**Returns**

- *list of int*: The rank of each sprite, in the sprites' own order.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> row = [
...     Sprite(
...         pixmap=QPixmap(),
...         rect=QRectF(x, 0, 10, 10),
...     )
...     for x in (0, 20, 40)
... ]
>>> (
...     ranks(row, order="index"),
...     ranks(row, order="reverse"),
...     ranks(row, order="outward"),
... )
([0, 1, 2], [2, 1, 0], [1, 0, 2])
```

## span

<div class="api-signature" markdown="1">

```python
def span(
    motion: Motion,
    *,
    count: int,
) -> float
```

{% endraw %}{% include api-source.html name="span" line=833 %}{% raw %}

</div>

Say how long a motion takes for a number of cards, from when it
starts to when the last card has finished.

**Parameters**

- `motion` (*Motion*): The motion.
- `count` (*int*): How many cards.

**Returns**

- *float*: The time in milliseconds.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> span(
...     Motion(
...         length=300.0,
...         per_card=50.0,
...         start=10.0,
...     ),
...     count=4,
... )
460.0
```

## move

<div class="api-signature" markdown="1">

```python
def move(
    scene: Scene,
    *,
    leaving: Motion | None,
    arriving: Motion,
) -> None
```

{% endraw %}{% include api-source.html name="move" line=869 %}{% raw %}

</div>

Set the sprites for a transition built from a motion for the cards
that leave and one for the cards that arrive.

**Parameters**

- `scene` (*Scene*): The time, the cards and the direction.
- `leaving` (*Motion or None*): What the old cards do; None for them to be gone at once.
- `arriving` (*Motion*): What the new cards do.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> new = [
...     Sprite(pixmap=QPixmap(), rect=QRectF())
... ]
>>> move(
...     Scene(
...         time=0, old=[], new=new, direction=1
...     ),
...     leaving=None,
...     arriving=Motion(dy=20),
... )
>>> new[0].opacity, new[0].dy
(0.0, 20.0)
```

## built

<div class="api-signature" markdown="1">

```python
def built(
    *,
    leaving: Motion | None,
    arriving: Motion,
) -> tuple[Callable[[Scene], None], Callable[[Scene], float]]
```

{% endraw %}{% include api-source.html name="built" line=1014 %}{% raw %}

</div>

Make the frame and length functions of a transition built from
motions.

**Parameters**

- `leaving` (*Motion or None*): What the old cards do. Keyword-only.
- `arriving` (*Motion*): What the new cards do. Keyword-only.

**Returns**

- *tuple of (callable, callable)*: The frame function, and the length function.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> draw, lasts = built(
...     leaving=None,
...     arriving=Motion(
...         length=300, per_card=50
...     ),
... )
>>> lasts(
...     Scene(
...         time=0,
...         old=[],
...         new=[
...             Sprite(
...                 pixmap=QPixmap(),
...                 rect=QRectF(),
...             )
...         ]
...         * 3,
...         direction=1,
...     )
... )
400.0
```

## made

<div class="api-signature" markdown="1">

```python
def made(
    key: str,
    *,
    label: str,
    about: str,
    leaving: Motion | None,
    arriving: Motion,
) -> Transition
```

{% endraw %}{% include api-source.html name="made" line=1102 %}{% raw %}

</div>

Make a transition from motions.

**Parameters**

- `key` (*str*): What it is saved as.
- `label` (*str*): What the settings call it. Keyword-only.
- `about` (*str*): A sentence saying what it looks like. Keyword-only.
- `leaving` (*Motion or None*): What the old cards do. Keyword-only.
- `arriving` (*Motion*): What the new cards do. Keyword-only.

**Returns**

- *Transition*: The transition.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> made(
...     "x",
...     label="X",
...     about="Does x.",
...     leaving=None,
...     arriving=Motion(),
... ).key
'x'
```

## transition_named

<div class="api-signature" markdown="1">

```python
def transition_named(key: str) -> Transition
```

{% endraw %}{% include api-source.html name="transition_named" line=1487 %}{% raw %}

</div>

Find a transition by its key.

**Parameters**

- `key` (*str*): The key.

**Returns**

- *Transition*: The transition, or the default one if there is none with that key.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     transition_named("flip").label,
...     transition_named("nonsense").key,
... )
('Flip', 'cascade')
```

## saved_transition

<div class="api-signature" markdown="1">

```python
def saved_transition() -> str
```

{% endraw %}{% include api-source.html name="saved_transition" line=1516 %}{% raw %}

</div>

Return the key of the transition that is chosen in the settings.

**Returns**

- *str*: The key; the default if none is saved or the saved one no longer exists.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().remove("ui/homeTransition")
>>> saved_transition()
'cascade'
```

## save_transition

<div class="api-signature" markdown="1">

```python
def save_transition(key: str) -> None
```

{% endraw %}{% include api-source.html name="save_transition" line=1541 %}{% raw %}

</div>

Remember which transition to use.

**Parameters**

- `key` (*str*): The key.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> save_transition("flip")
>>> saved_transition()
'flip'
>>> store().remove("ui/homeTransition")
```

## paint_sprites

<div class="api-signature" markdown="1">

```python
def paint_sprites(
    painter: QPainter,
    *,
    sprites: Sequence[Sprite],
) -> None
```

{% endraw %}{% include api-source.html name="paint_sprites" line=1560 %}{% raw %}

</div>

Draw sprites as they now look.

**Parameters**

- `painter` (*QPainter*): The painter to draw with.
- `sprites` (*sequence of Sprite*): The sprites, drawn in order. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from PySide6.QtGui import QImage
>>> image = QImage(
...     20, 20, QImage.Format.Format_ARGB32
... )
>>> brush = QPainter(image)
>>> paint_sprites(
...     brush,
...     sprites=[
...         Sprite(
...             pixmap=QPixmap(10, 10),
...             rect=QRectF(0, 0, 10, 10),
...         )
...     ],
... )
>>> brush.end()
True
```

## TransitionCanvas

<div class="api-signature" markdown="1">

```python
TransitionCanvas(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="TransitionCanvas" line=1639 %}{% raw %}

</div>

Bases: `QWidget`

A see-through sheet laid over the cards, on which a transition is
drawn.

**Attributes**

- `old` (*list of Sprite*): The cards that are leaving.
- `new` (*list of Sprite*): The cards that are arriving.
- `finished` (*Signal*): Emitted when a transition has played to its end.
- `running` (*bool*): True while a transition is playing.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> canvas = TransitionCanvas()
>>> canvas.running
False
```

**Constructor**

Build the canvas, hidden.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget it is laid over.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> TransitionCanvas().isHidden()
True
```

### TransitionCanvas.cover

<div class="api-signature" markdown="1">

```python
def cover(old: list[Sprite]) -> None
```

{% endraw %}{% include api-source.html name="TransitionCanvas.cover" line=1692 %}{% raw %}

</div>

Show the old cards on the canvas as they are, so that they can
be swapped for the new ones unseen.

**Parameters**

- `old` (*list of Sprite*): The photographs of the cards that are leaving.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> canvas = TransitionCanvas()
>>> canvas.cover([])
>>> canvas.running
True
```

### TransitionCanvas.play

<div class="api-signature" markdown="1">

```python
def play(
    transition: Transition,
    *,
    new: list[Sprite],
    direction: int,
) -> None
```

{% endraw %}{% include api-source.html name="TransitionCanvas.play" line=1718 %}{% raw %}

</div>

Play a transition from the old cards that cover the canvas to
the new ones.

**Parameters**

- `transition` (*Transition*): Which one.
- `new` (*list of Sprite*): The photographs of the cards that are arriving. Keyword-only.
- `direction` (*int*): 1 when going toward the lessons, -1 when coming back. Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> canvas = TransitionCanvas()
>>> canvas.cover([])
>>> canvas.play(
...     TRANSITIONS[1], new=[], direction=1
... )
>>> canvas.running
True
>>> canvas.stop()
```

### TransitionCanvas.stop

<div class="api-signature" markdown="1">

```python
def stop() -> None
```

{% endraw %}{% include api-source.html name="TransitionCanvas.stop" line=1763 %}{% raw %}

</div>

End the transition at once and take the canvas away.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> canvas = TransitionCanvas()
>>> canvas.cover([])
>>> canvas.stop()
>>> canvas.running, canvas.isHidden()
(False, True)
```

### TransitionCanvas.paintEvent

<div class="api-signature" markdown="1">

```python
def paintEvent(_: QPaintEvent) -> None
```

{% endraw %}{% include api-source.html name="TransitionCanvas.paintEvent" line=1808 %}{% raw %}

</div>

Draw every sprite as it now looks.

**Parameters**

- `_` (*QPaintEvent*): The paint request.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> canvas = TransitionCanvas()
>>> canvas.resize(100, 100)
>>> canvas.grab().isNull()
False
```
{% endraw %}
