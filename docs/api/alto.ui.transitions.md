---
title: alto.ui.transitions
parent: api
package: alto.ui
order: 50
permalink: /api/alto.ui.transitions/
---
{% raw %}
The transitions between the exercises and the lessons on the home page.

A transition moves between two sets of cards. Each card is photographed first, as a sprite, and a sprite can be faded, slid,
scaled, blurred or cut away from one side. A transition is a function that sets how every sprite looks at each moment, so ten
different ones share one player.

**Examples**

```pycon
>>> [transition.key for transition in TRANSITIONS][:3]
['none', 'cascade', 'fade']
>>> DEFAULT_TRANSITION
'cascade'
```

## Sprite

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

```pycon
>>> sprite = Sprite(pixmap=QPixmap(), rect=QRectF(0, 0, 10, 10))
>>> sprite.opacity, sprite.reveal
(1.0, 1.0)
```

## Scene

```python
Scene(
    time: float,
    old: Sequence[Sprite],
    new: Sequence[Sprite],
    direction: int,
)
```

What a transition is given at each moment: the time, the two sets of sprites and the direction.

**Attributes**

- `time` (*float*): The time since the transition began, in milliseconds.
- `old` (*sequence of Sprite*): The cards that are leaving.
- `new` (*sequence of Sprite*): The cards that are arriving.
- `direction` (*int*): 1 when going towards the lessons, -1 when coming back.

**Examples**

```pycon
>>> Scene(time=0.0, old=[], new=[], direction=1).direction
1
```

## ease_out

```python
def ease_out(progress: float) -> float
```

Ease a progress from 0 to 1 so that it starts fast and slows to a stop.

**Parameters**

- `progress` (*float*): How far along, from 0 to 1.

**Returns**

- *float*: The eased progress.

**Examples**

```pycon
>>> ease_out(0.0), ease_out(1.0), ease_out(0.5)
(0.0, 1.0, 0.875)
```

## ramp

```python
def ramp(
    time: float,
    *,
    start: float,
    length: float,
) -> float
```

Say how far along a part of a transition is, from 0 before it starts to 1 once it has finished.

**Parameters**

- `time` (*float*): The time since the transition began, in milliseconds.
- `start` (*float*): When the part begins. Keyword-only.
- `length` (*float*): How long it lasts. Keyword-only.

**Returns**

- *float*: The progress, from 0 to 1.

**Examples**

```pycon
>>> ramp(50, start=100, length=200), ramp(200, start=100, length=200), ramp(900, start=100, length=200)
(0.0, 0.5, 1.0)
```

## hide

```python
def hide(sprites: Sequence[Sprite]) -> None
```

Make sprites invisible.

**Parameters**

- `sprites` (*sequence of Sprite*): The sprites.

**Examples**

```pycon
>>> card = Sprite(pixmap=QPixmap(), rect=QRectF())
>>> hide([card])
>>> card.opacity
0.0
```

## fade_in

```python
def fade_in(scene: Scene) -> None
```

Set the sprites for a fade in: the new cards fade up from clear, and nothing of the old remains.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```pycon
>>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
>>> fade_in(Scene(time=0, old=[], new=new, direction=1))
>>> new[0].opacity
0.0
```

## crossfade

```python
def crossfade(scene: Scene) -> None
```

Set the sprites for a crossfade: the old cards fade out as the new ones fade in.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```pycon
>>> old, new = [Sprite(pixmap=QPixmap(), rect=QRectF())], [Sprite(pixmap=QPixmap(), rect=QRectF())]
>>> crossfade(Scene(time=300, old=old, new=new, direction=1))
>>> old[0].opacity, new[0].opacity
(0.0, 1.0)
```

## slide

```python
def slide(scene: Scene) -> None
```

Set the sprites for a slide: both sets move sideways, towards the side of the switch that was pressed.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```pycon
>>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
>>> slide(Scene(time=0, old=[], new=new, direction=1))
>>> new[0].dx
60.0
```

## rise

```python
def rise(scene: Scene) -> None
```

Set the sprites for a rise: the old cards sink and fade, and the new ones rise into place.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```pycon
>>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
>>> rise(Scene(time=0, old=[], new=new, direction=1))
>>> new[0].dy, new[0].opacity
(22.0, 0.0)
```

## cascade

```python
def cascade(scene: Scene) -> None
```

Set the sprites for a cascade: the new cards arrive one after another, each rising a little as it appears.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```pycon
>>> new = [Sprite(pixmap=QPixmap(), rect=QRectF()) for _ in range(2)]
>>> cascade(Scene(time=100, old=[], new=new, direction=1))
>>> new[0].opacity > new[1].opacity > 0.0
True
```

## zoom

```python
def zoom(scene: Scene) -> None
```

Set the sprites for a zoom: the old cards grow a little as they fade, and the new ones grow into place.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```pycon
>>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
>>> zoom(Scene(time=0, old=[], new=new, direction=1))
>>> new[0].sx
0.92
```

## flip

```python
def flip(scene: Scene) -> None
```

Set the sprites for a flip: each old card turns edge on and goes, then each new one turns face on.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```pycon
>>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
>>> flip(Scene(time=0, old=[], new=new, direction=1))
>>> new[0].opacity
0.0
```

## blur

```python
def blur(scene: Scene) -> None
```

Set the sprites for a blur: the old cards dissolve into a blur and the new ones come into focus.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```pycon
>>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
>>> blur(Scene(time=0, old=[], new=new, direction=1))
>>> new[0].blur, new[0].opacity
(1.0, 0.0)
```

## wipe

```python
def wipe(scene: Scene) -> None
```

Set the sprites for a wipe: the new cards are uncovered from one side while the old ones fade.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```pycon
>>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
>>> wipe(Scene(time=0, old=[], new=new, direction=-1))
>>> new[0].reveal, new[0].reveal_from
(0.0, -1)
```

## drop

```python
def drop(scene: Scene) -> None
```

Set the sprites for drop and pop: the old cards drop away one by one, then the new ones pop in with a small bounce.

**Parameters**

- `scene` (*Scene*): The time, the cards that are leaving and arriving, and the direction.

**Examples**

```pycon
>>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
>>> drop(Scene(time=0, old=[], new=new, direction=1))
>>> new[0].opacity
0.0
```

## Transition

```python
Transition(
    key: str,
    label: str,
    about: str,
    frame: Callable[[Scene], None] | None = field(default=None, compare=False),
    length: Callable[[Scene], float] = field(default=lambda scene: 0.0, compare=False),
)
```

One way of moving between the exercises and the lessons.

**Attributes**

- `key` (*str*): What it is saved as.
- `label` (*str*): What the settings call it.
- `about` (*str*): A sentence saying what it looks like.
- `frame` (*callable or None*): Sets how every sprite looks in a scene; None for no transition at all.
- `length` (*callable*): Says how long it lasts, in milliseconds, from a scene that has the cards but no time.

**Examples**

```pycon
>>> TRANSITIONS[0].frame is None
True
```

## Motion

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

How one set of cards moves in a transition built from parts: when each card starts, how long it takes, and what it does.

Every card goes between its resting look and a look given here, so the same description serves for cards arriving (from that
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
- `reveal` (*str*): "" for none, or "side" or "centre" to uncover it from one side or from the middle.

**Examples**

```pycon
>>> Motion().order, Motion().ease
('index', 'out')
```

## eased

```python
def eased(
    progress: float,
    *,
    how: str,
) -> float
```

Time a progress from 0 to 1 in one of the ways a motion can be eased.

**Parameters**

- `progress` (*float*): How far along, from 0 to 1.
- `how` (*str*): One of `EASES`: "out" slows to a stop, "in" speeds up, "back" overshoots a little and settles, "linear" does neither. Keyword-only.

**Returns**

- *float*: The timed progress, which "back" takes a little past 1 on the way.

**Examples**

```pycon
>>> eased(0.5, how="linear"), eased(1.0, how="back"), eased(0.5, how="in")
(0.5, 1.0, 0.25)
>>> eased(0.8, how="back") > 1.0
True
```

## ranks

```python
def ranks(
    sprites: Sequence[Sprite],
    *,
    order: str,
) -> list[int]
```

Say where each sprite comes in an order: 0 for the first to start.

**Parameters**

- `sprites` (*sequence of Sprite*): The cards of one side.
- `order` (*str*): One of `ORDERS`: "index" is as laid out, "reverse" backwards, "outward" from the middle of the cards to the edges, "inward" the other way, "diagonal" from the top left to the bottom right, and "random" in a fixed scrambled order. Keyword-only.

**Returns**

- *list of int*: The rank of each sprite, in the sprites' own order.

**Examples**

```pycon
>>> row = [Sprite(pixmap=QPixmap(), rect=QRectF(x, 0, 10, 10)) for x in (0, 20, 40)]
>>> ranks(row, order="index"), ranks(row, order="reverse"), ranks(row, order="outward")
([0, 1, 2], [2, 1, 0], [1, 0, 2])
```

## span

```python
def span(
    motion: Motion,
    *,
    count: int,
) -> float
```

Say how long a motion takes for a number of cards, from when it starts to when the last card has finished.

**Parameters**

- `motion` (*Motion*): The motion.
- `count` (*int*): How many cards.

**Returns**

- *float*: The time in milliseconds.

**Examples**

```pycon
>>> span(Motion(length=300.0, per_card=50.0, start=10.0), count=4)
460.0
```

## move

```python
def move(
    scene: Scene,
    *,
    leaving: Motion | None,
    arriving: Motion,
) -> None
```

Set the sprites for a transition built from a motion for the cards that leave and one for the cards that arrive.

**Parameters**

- `scene` (*Scene*): The time, the cards and the direction.
- `leaving` (*Motion or None*): What the old cards do; None for them to be gone at once.
- `arriving` (*Motion*): What the new cards do.

**Examples**

```pycon
>>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
>>> move(Scene(time=0, old=[], new=new, direction=1), leaving=None, arriving=Motion(dy=20))
>>> new[0].opacity, new[0].dy
(0.0, 20.0)
```

## built

```python
def built(
    *,
    leaving: Motion | None,
    arriving: Motion,
) -> tuple[Callable[[Scene], None], Callable[[Scene], float]]
```

Make the frame and length functions of a transition built from motions.

**Parameters**

- `leaving` (*Motion or None*): What the old cards do. Keyword-only.
- `arriving` (*Motion*): What the new cards do. Keyword-only.

**Returns**

- *tuple of (callable, callable)*: The frame function, and the length function.

**Examples**

```pycon
>>> draw, lasts = built(leaving=None, arriving=Motion(length=300, per_card=50))
>>> lasts(Scene(time=0, old=[], new=[Sprite(pixmap=QPixmap(), rect=QRectF())] * 3, direction=1))
400.0
```

## made

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

```pycon
>>> made("x", label="X", about="Does x.", leaving=None, arriving=Motion()).key
'x'
```

## transition_named

```python
def transition_named(key: str) -> Transition
```

Find a transition by its key.

**Parameters**

- `key` (*str*): The key.

**Returns**

- *Transition*: The transition, or the default one if there is none with that key.

**Examples**

```pycon
>>> transition_named("flip").label, transition_named("nonsense").key
('Flip', 'cascade')
```

## saved_transition

```python
def saved_transition() -> str
```

Return the key of the transition that is chosen in the settings.

**Returns**

- *str*: The key; the default if none is saved or the saved one no longer exists.

**Examples**

```pycon
>>> store().remove("ui/homeTransition")
>>> saved_transition()
'cascade'
```

## save_transition

```python
def save_transition(key: str) -> None
```

Remember which transition to use.

**Parameters**

- `key` (*str*): The key.

**Examples**

```pycon
>>> save_transition("flip")
>>> saved_transition()
'flip'
>>> store().remove("ui/homeTransition")
```

## paint_sprites

```python
def paint_sprites(
    painter: QPainter,
    *,
    sprites: Sequence[Sprite],
) -> None
```

Draw sprites as they now look.

**Parameters**

- `painter` (*QPainter*): The painter to draw with.
- `sprites` (*sequence of Sprite*): The sprites, drawn in order. Keyword-only.

**Examples**

```pycon
>>> from PySide6.QtGui import QImage
>>> image = QImage(20, 20, QImage.Format.Format_ARGB32)
>>> brush = QPainter(image)
>>> paint_sprites(brush, sprites=[Sprite(pixmap=QPixmap(10, 10), rect=QRectF(0, 0, 10, 10))])
>>> brush.end()
True
```

## TransitionCanvas

```python
TransitionCanvas(parent: QWidget | None = None)
```

Bases: `QWidget`

A see-through sheet laid over the cards, on which a transition is drawn.

**Attributes**

- `old` (*list of Sprite*): The cards that are leaving.
- `new` (*list of Sprite*): The cards that are arriving.
- `finished` (*Signal*): Emitted when a transition has played to its end.
- `running` (*bool*): True while a transition is playing.

**Examples**

```pycon
>>> canvas = TransitionCanvas()
>>> canvas.running
False
```

**Constructor**

Build the canvas, hidden.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget it is laid over.

**Constructor examples**

```pycon
>>> TransitionCanvas().isHidden()
True
```

### TransitionCanvas.cover

```python
def cover(old: list[Sprite]) -> None
```

Show the old cards on the canvas as they are, so that they can be swapped for the new ones unseen.

**Parameters**

- `old` (*list of Sprite*): The photographs of the cards that are leaving.

**Examples**

```pycon
>>> canvas = TransitionCanvas()
>>> canvas.cover([])
>>> canvas.running
True
```

### TransitionCanvas.play

```python
def play(
    transition: Transition,
    *,
    new: list[Sprite],
    direction: int,
) -> None
```

Play a transition from the old cards that cover the canvas to the new ones.

**Parameters**

- `transition` (*Transition*): Which one.
- `new` (*list of Sprite*): The photographs of the cards that are arriving. Keyword-only.
- `direction` (*int*): 1 when going towards the lessons, -1 when coming back. Keyword-only.

**Examples**

```pycon
>>> canvas = TransitionCanvas()
>>> canvas.cover([])
>>> canvas.play(TRANSITIONS[1], new=[], direction=1)
>>> canvas.running
True
>>> canvas.stop()
```

### TransitionCanvas.stop

```python
def stop() -> None
```

End the transition at once and take the canvas away.

**Examples**

```pycon
>>> canvas = TransitionCanvas()
>>> canvas.cover([])
>>> canvas.stop()
>>> canvas.running, canvas.isHidden()
(False, True)
```

### TransitionCanvas.paintEvent

```python
def paintEvent(_: QPaintEvent) -> None
```

Draw every sprite as it now looks.

**Parameters**

- `_` (*QPaintEvent*): The paint request.

**Examples**

```pycon
>>> canvas = TransitionCanvas()
>>> canvas.resize(100, 100)
>>> canvas.grab().isNull()
False
```
{% endraw %}
