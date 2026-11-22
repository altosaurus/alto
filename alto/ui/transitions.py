"""
The transitions between the exercises and the lessons on the home page.

A transition moves between two sets of cards. Each card is photographed first, as a sprite, and a sprite can be faded, slid,
scaled, blurred or cut away from one side. A transition is a function that sets how every sprite looks at each moment, so ten
different ones share one player.

Examples
--------
>>> [transition.key for transition in TRANSITIONS][:3]
['none', 'cascade', 'fade']
>>> DEFAULT_TRANSITION
'cascade'
"""

from __future__ import annotations

import math
from collections.abc import (
    Callable,
    Sequence,
)
from dataclasses import (
    dataclass,
    field,
)

from PySide6.QtCore import (
    QEasingCurve,
    QRectF,
    Qt,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QPainter,
    QPaintEvent,
    QPixmap,
)
from PySide6.QtWidgets import QWidget

from alto.ui import motion
from alto.ui.store import (
    store,
    text_value,
)

DEFAULT_TRANSITION = "cascade"
SIDEBAR_SLIDE_MS = 180
BLUR_STEPS = 9.0  # how much smaller a fully blurred sprite is drawn, before it is stretched back up


@dataclass
class Sprite:
    """
    A photograph of one card, and how it is drawn at this moment.

    Attributes
    ----------
    pixmap : QPixmap
        The photograph.
    rect : QRectF
        Where the card is, in the canvas.
    opacity : float
        0 for invisible to 1 for solid.
    dx : float
        How far it is moved right, in pixels.
    dy : float
        How far it is moved down, in pixels.
    sx : float
        How much it is stretched across, about its middle; 1 is as it was.
    sy : float
        How much it is stretched down, about its middle.
    blur : float
        0 for sharp to 1 for fully blurred.
    angle : float
        How far it is turned about its middle, in degrees, clockwise.
    reveal : float
        How much of it shows, from 0 to 1.
    reveal_from : int
        1 to uncover it from the left, -1 from the right, 0 from the middle outwards.

    Examples
    --------
    >>> sprite = Sprite(pixmap=QPixmap(), rect=QRectF(0, 0, 10, 10))
    >>> sprite.opacity, sprite.reveal
    (1.0, 1.0)
    """

    pixmap: QPixmap
    rect: QRectF
    opacity: float = 1.0
    dx: float = 0.0
    dy: float = 0.0
    sx: float = 1.0
    sy: float = 1.0
    blur: float = 0.0
    angle: float = 0.0
    reveal: float = 1.0
    reveal_from: int = 1


@dataclass(frozen=True)
class Scene:
    """
    What a transition is given at each moment: the time, the two sets of sprites and the direction.

    Attributes
    ----------
    time : float
        The time since the transition began, in milliseconds.
    old : sequence of Sprite
        The cards that are leaving.
    new : sequence of Sprite
        The cards that are arriving.
    direction : int
        1 when going toward the lessons, -1 when coming back.

    Examples
    --------
    >>> Scene(time=0.0, old=[], new=[], direction=1).direction
    1
    """

    time: float
    old: Sequence[Sprite]
    new: Sequence[Sprite]
    direction: int


def ease_out(progress: float) -> float:
    """
    Ease a progress from 0 to 1 so that it starts fast and slows to a stop.

    Parameters
    ----------
    progress : float
        How far along, from 0 to 1.

    Returns
    -------
    float
        The eased progress.

    Examples
    --------
    >>> ease_out(0.0), ease_out(1.0), ease_out(0.5)
    (0.0, 1.0, 0.875)
    """
    progress = min(max(progress, 0.0), 1.0)
    return 1.0 - (1.0 - progress) ** 3


def ramp(
    time: float,
    *,
    start: float,
    length: float,
) -> float:
    """
    Say how far along a part of a transition is, from 0 before it starts to 1 once it has finished.

    Parameters
    ----------
    time : float
        The time since the transition began, in milliseconds.
    start : float
        When the part begins. Keyword-only.
    length : float
        How long it lasts. Keyword-only.

    Returns
    -------
    float
        The progress, from 0 to 1.

    Examples
    --------
    >>> ramp(50, start=100, length=200), ramp(200, start=100, length=200), ramp(900, start=100, length=200)
    (0.0, 0.5, 1.0)
    """
    return min(max((time - start) / length, 0.0), 1.0)


def hide(sprites: Sequence[Sprite]) -> None:
    """
    Make sprites invisible.

    Parameters
    ----------
    sprites : sequence of Sprite
        The sprites.

    Examples
    --------
    >>> card = Sprite(pixmap=QPixmap(), rect=QRectF())
    >>> hide([card])
    >>> card.opacity
    0.0
    """
    for sprite in sprites:
        sprite.opacity = 0.0


def fade_in(scene: Scene) -> None:
    """
    Set the sprites for a fade in: the new cards fade up from clear, and nothing of the old remains.

    Parameters
    ----------
    scene : Scene
        The time, the cards that are leaving and arriving, and the direction.

    Examples
    --------
    >>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
    >>> fade_in(Scene(time=0, old=[], new=new, direction=1))
    >>> new[0].opacity
    0.0
    """
    hide(scene.old)
    for sprite in scene.new:
        sprite.opacity = ease_out(ramp(scene.time, start=0, length=260))


def crossfade(scene: Scene) -> None:
    """
    Set the sprites for a crossfade: the old cards fade out as the new ones fade in.

    Parameters
    ----------
    scene : Scene
        The time, the cards that are leaving and arriving, and the direction.

    Examples
    --------
    >>> old, new = [Sprite(pixmap=QPixmap(), rect=QRectF())], [Sprite(pixmap=QPixmap(), rect=QRectF())]
    >>> crossfade(Scene(time=300, old=old, new=new, direction=1))
    >>> old[0].opacity, new[0].opacity
    (0.0, 1.0)
    """
    progress = ease_out(ramp(scene.time, start=0, length=300))
    for sprite in scene.old:
        sprite.opacity = 1.0 - progress
    for sprite in scene.new:
        sprite.opacity = progress


def slide(scene: Scene) -> None:
    """
    Set the sprites for a slide: both sets move sideways, toward the side of the switch that was pressed.

    Parameters
    ----------
    scene : Scene
        The time, the cards that are leaving and arriving, and the direction.

    Examples
    --------
    >>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
    >>> slide(Scene(time=0, old=[], new=new, direction=1))
    >>> new[0].dx
    60.0
    """
    out, arrive = ease_out(ramp(scene.time, start=0, length=300)), ease_out(ramp(scene.time, start=0, length=340))
    for sprite in scene.old:
        sprite.dx, sprite.opacity = -scene.direction * 60.0 * out, 1.0 - out
    for sprite in scene.new:
        sprite.dx, sprite.opacity = scene.direction * 60.0 * (1.0 - arrive), arrive


def rise(scene: Scene) -> None:
    """
    Set the sprites for a rise: the old cards sink and fade, and the new ones rise into place.

    Parameters
    ----------
    scene : Scene
        The time, the cards that are leaving and arriving, and the direction.

    Examples
    --------
    >>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
    >>> rise(Scene(time=0, old=[], new=new, direction=1))
    >>> new[0].dy, new[0].opacity
    (22.0, 0.0)
    """
    out, arrive = ease_out(ramp(scene.time, start=0, length=220)), ease_out(ramp(scene.time, start=120, length=360))
    for sprite in scene.old:
        sprite.dy, sprite.opacity = 16.0 * out, 1.0 - out
    for sprite in scene.new:
        sprite.dy, sprite.opacity = 22.0 * (1.0 - arrive), arrive


def cascade(scene: Scene) -> None:
    """
    Set the sprites for a cascade: the new cards arrive one after another, each rising a little as it appears.

    Parameters
    ----------
    scene : Scene
        The time, the cards that are leaving and arriving, and the direction.

    Examples
    --------
    >>> new = [Sprite(pixmap=QPixmap(), rect=QRectF()) for _ in range(2)]
    >>> cascade(Scene(time=100, old=[], new=new, direction=1))
    >>> new[0].opacity > new[1].opacity > 0.0
    True
    """
    hide(scene.old)
    for number, sprite in enumerate(scene.new):
        progress = ease_out(ramp(scene.time, start=number * 70, length=320))
        sprite.opacity, sprite.dy = progress, 14.0 * (1.0 - progress)


def zoom(scene: Scene) -> None:
    """
    Set the sprites for a zoom: the old cards grow a little as they fade, and the new ones grow into place.

    Parameters
    ----------
    scene : Scene
        The time, the cards that are leaving and arriving, and the direction.

    Examples
    --------
    >>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
    >>> zoom(Scene(time=0, old=[], new=new, direction=1))
    >>> new[0].sx
    0.92
    """
    out, arrive = ease_out(ramp(scene.time, start=0, length=220)), ease_out(ramp(scene.time, start=100, length=340))
    for sprite in scene.old:
        sprite.sx = sprite.sy = 1.0 + 0.06 * out
        sprite.opacity = 1.0 - out
    for sprite in scene.new:
        sprite.sx = sprite.sy = 0.92 + 0.08 * arrive
        sprite.opacity = arrive


def flip(scene: Scene) -> None:
    """
    Set the sprites for a flip: each old card turns edge on and goes, then each new one turns face on.

    Parameters
    ----------
    scene : Scene
        The time, the cards that are leaving and arriving, and the direction.

    Examples
    --------
    >>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
    >>> flip(Scene(time=0, old=[], new=new, direction=1))
    >>> new[0].opacity
    0.0
    """
    gone = 180.0 + 30.0 * max(len(scene.old) - 1, 0)  # when the last scene.old card has turned away
    for number, sprite in enumerate(scene.old):
        turn = ramp(scene.time, start=number * 30, length=180)
        sprite.sx = max(math.cos(math.pi / 2 * turn), 0.0)
        sprite.opacity = 1.0 if turn < 1.0 else 0.0
    for number, sprite in enumerate(scene.new):
        turn = ramp(scene.time, start=gone + number * 30, length=220)
        sprite.sx = max(math.sin(math.pi / 2 * turn), 0.0)
        sprite.opacity = 1.0 if turn > 0.0 else 0.0


def blur(scene: Scene) -> None:
    """
    Set the sprites for a blur: the old cards dissolve into a blur and the new ones come into focus.

    Parameters
    ----------
    scene : Scene
        The time, the cards that are leaving and arriving, and the direction.

    Examples
    --------
    >>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
    >>> blur(Scene(time=0, old=[], new=new, direction=1))
    >>> new[0].blur, new[0].opacity
    (1.0, 0.0)
    """
    out, arrive = ease_out(ramp(scene.time, start=0, length=260)), ease_out(ramp(scene.time, start=120, length=320))
    for sprite in scene.old:
        sprite.blur, sprite.opacity = out, 1.0 - out
    for sprite in scene.new:
        sprite.blur, sprite.opacity = 1.0 - arrive, arrive


def wipe(scene: Scene) -> None:
    """
    Set the sprites for a wipe: the new cards are uncovered from one side while the old ones fade.

    Parameters
    ----------
    scene : Scene
        The time, the cards that are leaving and arriving, and the direction.

    Examples
    --------
    >>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
    >>> wipe(Scene(time=0, old=[], new=new, direction=-1))
    >>> new[0].reveal, new[0].reveal_from
    (0.0, -1)
    """
    progress = ease_out(ramp(scene.time, start=0, length=420))
    for sprite in scene.old:
        sprite.opacity = 1.0 - progress
    for sprite in scene.new:
        sprite.reveal, sprite.reveal_from = progress, scene.direction


def drop(scene: Scene) -> None:
    """
    Set the sprites for drop and pop: the old cards drop away one by one, then the new ones pop in with a small bounce.

    Parameters
    ----------
    scene : Scene
        The time, the cards that are leaving and arriving, and the direction.

    Examples
    --------
    >>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
    >>> drop(Scene(time=0, old=[], new=new, direction=1))
    >>> new[0].opacity
    0.0
    """
    gone = 200.0 + 25.0 * max(len(scene.old) - 1, 0)  # when the last scene.old card has dropped
    for number, sprite in enumerate(scene.old):
        fall = ramp(scene.time, start=number * 25, length=200)
        sprite.dy, sprite.opacity = 40.0 * fall * fall, 1.0 - fall
    for number, sprite in enumerate(scene.new):
        pop = ramp(scene.time, start=gone + number * 55, length=380)
        scale = 0.7 + 0.34 * (pop / 0.7) if pop < 0.7 else 1.04 - 0.04 * ((pop - 0.7) / 0.3)
        sprite.sx = sprite.sy = scale if pop > 0.0 else 0.7
        sprite.opacity = min(pop / 0.4, 1.0)


@dataclass(frozen=True)
class Transition:
    """
    One way of moving between the exercises and the lessons.

    Attributes
    ----------
    key : str
        What it is saved as.
    label : str
        What the settings call it.
    about : str
        A sentence saying what it looks like.
    frame : callable or None
        Sets how every sprite looks in a scene; None for no transition at all.
    length : callable
        Says how long it lasts, in milliseconds, from a scene that has the cards but no time.

    Examples
    --------
    >>> TRANSITIONS[0].frame is None
    True
    """

    key: str
    label: str
    about: str
    frame: Callable[[Scene], None] | None = field(default=None, compare=False)
    length: Callable[[Scene], float] = field(default=lambda scene: 0.0, compare=False)


ORDERS = ("index", "reverse", "outward", "inward", "diagonal", "random")  # the orders in which a motion visits the cards
EASES = ("out", "in", "back", "linear")  # how a motion speeds up and slows down


@dataclass(frozen=True)
class Motion:
    """
    How one set of cards moves in a transition built from parts: when each card starts, how long it takes, and what it does.

    Every card goes between its resting look and a look given here, so the same description serves for cards arriving (from that
    look to rest) and leaving (from rest to that look).

    Attributes
    ----------
    length : float
        How long each card takes, in milliseconds.
    per_card : float
        How much later each card starts than the one before it.
    start : float
        When the first card starts.
    after : bool
        True to wait until the cards that are leaving have all finished before starting; only for cards that are arriving.
    order : str
        The order the cards start in: one of `ORDERS`.
    ease : str
        How the motion is timed: one of `EASES`.
    dx : float
        How far to the right the card is at the far look, in pixels; it follows the direction of the switch.
    dy : float
        How far down the card is at the far look.
    scale : float
        How big the card is at the far look, as a fraction of its size.
    sx : float
        As well as `scale`, how wide, for a card that turns on its edge.
    sy : float
        As well as `scale`, how tall.
    angle : float
        How far the card is turned at the far look, in degrees; it follows the direction of the switch.
    blur : float
        How blurred it is at the far look, from 0 to 1.
    fade : bool
        True to fade between solid and clear; False to keep it solid, and hide it only once it is out of the way.
    reveal : str
        "" for none, or "side" or "center" to uncover it from one side or from the middle.

    Examples
    --------
    >>> Motion().order, Motion().ease
    ('index', 'out')
    """

    length: float = 320.0
    per_card: float = 0.0
    start: float = 0.0
    after: bool = False
    order: str = "index"
    ease: str = "out"
    dx: float = 0.0
    dy: float = 0.0
    scale: float = 1.0
    sx: float = 1.0
    sy: float = 1.0
    angle: float = 0.0
    blur: float = 0.0
    fade: bool = True
    reveal: str = ""


def eased(
    progress: float,
    *,
    how: str,
) -> float:
    """
    Time a progress from 0 to 1 in one of the ways a motion can be eased.

    Parameters
    ----------
    progress : float
        How far along, from 0 to 1.
    how : str
        One of `EASES`: "out" slows to a stop, "in" speeds up, "back" overshoots a little and settles, "linear" does neither.
        Keyword-only.

    Returns
    -------
    float
        The timed progress, which "back" takes a little past 1 on the way.

    Examples
    --------
    >>> eased(0.5, how="linear"), eased(1.0, how="back"), eased(0.5, how="in")
    (0.5, 1.0, 0.25)
    >>> eased(0.8, how="back") > 1.0
    True
    """
    progress = min(max(progress, 0.0), 1.0)
    if how == "in":
        return progress * progress
    if how == "back":
        return 1.0 + 2.70158 * (progress - 1.0) ** 3 + 1.70158 * (progress - 1.0) ** 2
    if how == "linear":
        return progress
    return ease_out(progress)


def ranks(
    sprites: Sequence[Sprite],
    *,
    order: str,
) -> list[int]:
    """
    Say where each sprite comes in an order: 0 for the first to start.

    Parameters
    ----------
    sprites : sequence of Sprite
        The cards of one side.
    order : str
        One of `ORDERS`: "index" is as laid out, "reverse" backwards, "outward" from the middle of the cards to the edges,
        "inward" the other way, "diagonal" from the top left to the bottom right, and "random" in a fixed scrambled order.
        Keyword-only.

    Returns
    -------
    list of int
        The rank of each sprite, in the sprites' own order.

    Examples
    --------
    >>> row = [Sprite(pixmap=QPixmap(), rect=QRectF(x, 0, 10, 10)) for x in (0, 20, 40)]
    >>> ranks(row, order="index"), ranks(row, order="reverse"), ranks(row, order="outward")
    ([0, 1, 2], [2, 1, 0], [1, 0, 2])
    """
    count = len(sprites)
    if order == "reverse":
        return [count - 1 - number for number in range(count)]
    if order == "random":
        scrambled = sorted(range(count), key=lambda number: (number * 7919 + 13) % 104729)
        return [scrambled.index(number) for number in range(count)]
    if order in {"outward", "inward", "diagonal"} and count:
        middle_x = sum(sprite.rect.center().x() for sprite in sprites) / count
        middle_y = sum(sprite.rect.center().y() for sprite in sprites) / count
        if order == "diagonal":
            keys = [sprite.rect.center().x() + sprite.rect.center().y() for sprite in sprites]
        else:
            keys = [math.hypot(sprite.rect.center().x() - middle_x, sprite.rect.center().y() - middle_y) for sprite in sprites]
            if order == "inward":
                keys = [-key for key in keys]
        by_key = sorted(range(count), key=lambda number: keys[number])
        return [by_key.index(number) for number in range(count)]
    return list(range(count))


def span(
    motion: Motion,
    *,
    count: int,
) -> float:
    """
    Say how long a motion takes for a number of cards, from when it starts to when the last card has finished.

    Parameters
    ----------
    motion : Motion
        The motion.
    count : int
        How many cards.

    Returns
    -------
    float
        The time in milliseconds.

    Examples
    --------
    >>> span(Motion(length=300.0, per_card=50.0, start=10.0), count=4)
    460.0
    """
    return motion.start + motion.per_card * max(count - 1, 0) + motion.length


def move(
    scene: Scene,
    *,
    leaving: Motion | None,
    arriving: Motion,
) -> None:
    """
    Set the sprites for a transition built from a motion for the cards that leave and one for the cards that arrive.

    Parameters
    ----------
    scene : Scene
        The time, the cards and the direction.
    leaving : Motion or None
        What the old cards do; None for them to be gone at once.
    arriving : Motion
        What the new cards do.

    Examples
    --------
    >>> new = [Sprite(pixmap=QPixmap(), rect=QRectF())]
    >>> move(Scene(time=0, old=[], new=new, direction=1), leaving=None, arriving=Motion(dy=20))
    >>> new[0].opacity, new[0].dy
    (0.0, 20.0)
    """
    hide(scene.old)
    base_new = 0.0
    if leaving is not None:
        base_new = span(leaving, count=len(scene.old)) if arriving.after else 0.0
        for sprite, rank in zip(scene.old, ranks(scene.old, order=leaving.order), strict=True):
            _pose(
                sprite,
                motion=leaving,
                progress=ramp(scene.time, start=leaving.start + rank * leaving.per_card, length=leaving.length),
                scene=scene,
                arrives=False,
            )
    for sprite, rank in zip(scene.new, ranks(scene.new, order=arriving.order), strict=True):
        began = base_new + arriving.start + rank * arriving.per_card
        _pose(sprite, motion=arriving, progress=ramp(scene.time, start=began, length=arriving.length), scene=scene, arrives=True)


def _pose(
    sprite: Sprite,
    *,
    motion: Motion,
    progress: float,
    scene: Scene,
    arrives: bool,
) -> None:
    """
    Pose one sprite part of the way through a motion.

    Parameters
    ----------
    sprite : Sprite
        The sprite to set.
    motion : Motion
        What it is doing.
    progress : float
        How far through its motion it is, from 0 to 1, before easing.
    scene : Scene
        The scene, for the direction.
    arrives : bool
        True if the card is arriving, so that it ends at rest; False if it is leaving, so that it starts at rest.

    Examples
    --------
    >>> card = Sprite(pixmap=QPixmap(), rect=QRectF())
    >>> _pose(card, motion=Motion(dy=30), progress=0.0, scene=Scene(time=0, old=[], new=[], direction=1), arrives=True)
    >>> card.dy, card.opacity
    (30.0, 0.0)
    """
    done = eased(progress, how=motion.ease)
    away = 1.0 - done if arrives else done  # how far it is from rest, as a fraction of its far look
    if motion.fade:
        sprite.opacity = min(max(done, 0.0), 1.0) if arrives else 1.0 - min(max(done, 0.0), 1.0)
    elif arrives:
        sprite.opacity = 1.0 if progress > 0.0 else 0.0
    else:
        sprite.opacity = 1.0 if progress < 1.0 else 0.0
    sprite.dx = motion.dx * away * scene.direction
    sprite.dy = motion.dy * away
    sprite.angle = motion.angle * away * scene.direction
    sprite.blur = min(max(motion.blur * away, 0.0), 1.0)
    grow = 1.0 + (motion.scale - 1.0) * away
    sprite.sx = max(grow * (1.0 + (motion.sx - 1.0) * away), 0.0)
    sprite.sy = max(grow * (1.0 + (motion.sy - 1.0) * away), 0.0)
    if motion.reveal:
        sprite.reveal = min(max(done, 0.0), 1.0) if arrives else 1.0 - min(max(done, 0.0), 1.0)
        sprite.reveal_from = 0 if motion.reveal == "center" else scene.direction


def built(
    *,
    leaving: Motion | None,
    arriving: Motion,
) -> tuple[Callable[[Scene], None], Callable[[Scene], float]]:
    """
    Make the frame and length functions of a transition built from motions.

    Parameters
    ----------
    leaving : Motion or None
        What the old cards do. Keyword-only.
    arriving : Motion
        What the new cards do. Keyword-only.

    Returns
    -------
    tuple of (callable, callable)
        The frame function, and the length function.

    Examples
    --------
    >>> draw, lasts = built(leaving=None, arriving=Motion(length=300, per_card=50))
    >>> lasts(Scene(time=0, old=[], new=[Sprite(pixmap=QPixmap(), rect=QRectF())] * 3, direction=1))
    400.0
    """

    def frame(scene: Scene) -> None:
        """
        Set the sprites for a scene.

        Parameters
        ----------
        scene : Scene
            The time, the cards and the direction.

        Examples
        --------
        >>> frame  # doctest: +SKIP
        """
        move(scene, leaving=leaving, arriving=arriving)

    def length(scene: Scene) -> float:
        """
        Say how long the transition lasts for the cards in a scene.

        Parameters
        ----------
        scene : Scene
            The cards.

        Returns
        -------
        float
            The time in milliseconds.

        Examples
        --------
        >>> length  # doctest: +SKIP
        """
        gone = span(leaving, count=len(scene.old)) if leaving is not None else 0.0
        coming = span(arriving, count=len(scene.new))
        return gone + coming if arriving.after else max(gone, coming)

    return frame, length


def made(
    key: str,
    *,
    label: str,
    about: str,
    leaving: Motion | None,
    arriving: Motion,
) -> Transition:
    """
    Make a transition from motions.

    Parameters
    ----------
    key : str
        What it is saved as.
    label : str
        What the settings call it. Keyword-only.
    about : str
        A sentence saying what it looks like. Keyword-only.
    leaving : Motion or None
        What the old cards do. Keyword-only.
    arriving : Motion
        What the new cards do. Keyword-only.

    Returns
    -------
    Transition
        The transition.

    Examples
    --------
    >>> made("x", label="X", about="Does x.", leaving=None, arriving=Motion()).key
    'x'
    """
    frame, length = built(leaving=leaving, arriving=arriving)
    return Transition(key, label, about, frame, length)


TRANSITIONS: tuple[Transition, ...] = (
    Transition("none", "No transition", "The cards change at once."),
    Transition(
        "cascade",
        "Cascade",
        "The new cards arrive one after another, left to right.",
        cascade,
        lambda scene: 320.0 + 70.0 * max(len(scene.new) - 1, 0),
    ),
    Transition("fade", "Fade in", "The new cards fade up from clear. Nothing leaves.", fade_in, lambda scene: 260.0),
    Transition(
        "crossfade",
        "Crossfade",
        "The old cards fade out as the new ones fade in, overlapping.",
        crossfade,
        lambda scene: 300.0,
    ),
    Transition(
        "slide",
        "Slide sideways",
        "Both sets slide, toward the side of the switch you pressed.",
        slide,
        lambda scene: 340.0,
    ),
    Transition("rise", "Rise", "The old cards sink and fade, the new ones rise into place.", rise, lambda scene: 480.0),
    Transition(
        "zoom",
        "Zoom",
        "The new cards grow from a little smaller, while the old ones shrink away.",
        zoom,
        lambda scene: 440.0,
    ),
    Transition(
        "flip",
        "Flip",
        "Every card turns over to show its replacement.",
        flip,
        lambda scene: 400.0 + 30.0 * (max(len(scene.old) - 1, 0) + max(len(scene.new) - 1, 0)),
    ),
    Transition(
        "blur",
        "Blur",
        "The old cards dissolve into a blur and the new ones come into focus.",
        blur,
        lambda scene: 440.0,
    ),
    Transition(
        "wipe",
        "Wipe",
        "The new cards are uncovered from one side, like a curtain.",
        wipe,
        lambda scene: 420.0,
    ),
    Transition(
        "drop",
        "Drop and pop",
        "The old cards drop away one by one, then the new ones pop in with a small bounce.",
        drop,
        lambda scene: 580.0 + 25.0 * max(len(scene.old) - 1, 0) + 55.0 * max(len(scene.new) - 1, 0),
    ),
    made(
        "slide_up",
        label="Slide up",
        about="The old cards slide up and away while the new ones rise in from below.",
        leaving=Motion(length=260.0, dy=-40.0, ease="in"),
        arriving=Motion(length=360.0, dy=40.0),
    ),
    made(
        "fall",
        label="Fall in",
        about="The new cards fall from above one after another, and settle with a small bounce.",
        leaving=Motion(length=160.0),
        arriving=Motion(length=520.0, per_card=60.0, start=80.0, dy=-130.0, ease="back"),
    ),
    made(
        "wave",
        label="Wave",
        about="A wave runs across the new cards from the top left to the bottom right.",
        leaving=Motion(length=200.0),
        arriving=Motion(length=380.0, per_card=55.0, start=60.0, order="diagonal", dy=34.0),
    ),
    made(
        "ripple",
        label="Ripple",
        about="The new cards appear from the middle outwards, each a little smaller than it ends up.",
        leaving=Motion(length=200.0),
        arriving=Motion(length=360.0, per_card=60.0, start=60.0, order="outward", scale=0.8),
    ),
    made(
        "gather",
        label="Gather",
        about="The new cards come in from the edges toward the middle.",
        leaving=Motion(length=200.0),
        arriving=Motion(length=360.0, per_card=60.0, start=60.0, order="inward", scale=0.8),
    ),
    made(
        "burst",
        label="Burst",
        about="The new cards burst out from the middle, growing past their size and settling.",
        leaving=Motion(length=180.0, scale=0.9),
        arriving=Motion(length=480.0, per_card=45.0, start=80.0, order="outward", scale=0.25, ease="back"),
    ),
    made(
        "elastic",
        label="Elastic",
        about="All the new cards spring in together, stretching a little past their size.",
        leaving=Motion(length=160.0),
        arriving=Motion(length=560.0, start=60.0, scale=0.55, ease="back"),
    ),
    made(
        "shrink",
        label="Shrink and grow",
        about="The old cards shrink to nothing, then the new ones grow from nothing.",
        leaving=Motion(length=220.0, per_card=20.0, scale=0.0, ease="in"),
        arriving=Motion(length=360.0, per_card=40.0, after=True, scale=0.0, ease="back"),
    ),
    made(
        "spin",
        label="Spin",
        about="The new cards spin into place as they grow and fade up.",
        leaving=Motion(length=240.0, angle=90.0, scale=0.7, ease="in"),
        arriving=Motion(length=560.0, per_card=40.0, start=100.0, angle=-200.0, scale=0.4),
    ),
    made(
        "swing",
        label="Swing",
        about="The new cards swing down into place like signs, one after another.",
        leaving=Motion(length=200.0, dy=20.0),
        arriving=Motion(length=520.0, per_card=70.0, start=80.0, angle=-28.0, dy=-30.0, ease="back"),
    ),
    made(
        "whirl",
        label="Whirl",
        about="The old cards whirl away and shrink, then the new ones whirl in.",
        leaving=Motion(length=300.0, per_card=30.0, angle=180.0, scale=0.0, ease="in"),
        arriving=Motion(length=420.0, per_card=40.0, after=True, angle=-180.0, scale=0.0),
    ),
    made(
        "flip_down",
        label="Flip over",
        about="Each card turns over top to bottom to show its replacement.",
        leaving=Motion(length=180.0, per_card=30.0, sy=0.0, fade=False, ease="linear"),
        arriving=Motion(length=220.0, per_card=30.0, after=True, sy=0.0, fade=False, ease="linear"),
    ),
    made(
        "unfold",
        label="Unfold",
        about="The new cards unfold from a flat line, one after another.",
        leaving=Motion(length=200.0),
        arriving=Motion(length=380.0, per_card=60.0, start=80.0, sy=0.0),
    ),
    made(
        "curtain",
        label="Curtain",
        about="The new cards are revealed from the middle outwards, like a curtain opening.",
        leaving=Motion(length=480.0),
        arriving=Motion(length=480.0, reveal="center"),
    ),
    made(
        "stream",
        label="Stream",
        about="The new cards slide in one at a time from the side you pressed.",
        leaving=Motion(length=240.0, dx=-50.0, ease="in"),
        arriving=Motion(length=380.0, per_card=65.0, start=60.0, dx=90.0),
    ),
    made(
        "focus",
        label="Focus pull",
        about="The new cards come into focus one after another, out of a blur.",
        leaving=Motion(length=220.0, blur=1.0),
        arriving=Motion(length=380.0, per_card=60.0, start=80.0, blur=1.0),
    ),
    made(
        "scatter",
        label="Scatter",
        about="The new cards appear in a scattered order, each growing a little as it does.",
        leaving=Motion(length=200.0),
        arriving=Motion(length=320.0, per_card=55.0, start=60.0, order="random", scale=0.88),
    ),
    made(
        "zoom_out",
        label="Zoom out",
        about="The new cards start too big and settle down to their size, while the old ones grow and fade.",
        leaving=Motion(length=220.0, scale=1.12),
        arriving=Motion(length=380.0, start=100.0, scale=1.18),
    ),
    made(
        "slow_fade",
        label="Slow dissolve",
        about="A long, gentle crossfade.",
        leaving=Motion(length=700.0, ease="linear"),
        arriving=Motion(length=700.0, ease="linear"),
    ),
)


def transition_named(key: str) -> Transition:
    """
    Find a transition by its key.

    Parameters
    ----------
    key : str
        The key.

    Returns
    -------
    Transition
        The transition, or the default one if there is none with that key.

    Examples
    --------
    >>> transition_named("flip").label, transition_named("nonsense").key
    ('Flip', 'cascade')
    """
    fallback = next(item for item in TRANSITIONS if item.key == DEFAULT_TRANSITION)
    return next((item for item in TRANSITIONS if item.key == key), fallback)


def saved_transition() -> str:
    """
    Return the key of the transition that is chosen in the settings.

    Returns
    -------
    str
        The key; the default if none is saved or the saved one no longer exists.

    Examples
    --------
    >>> store().remove("ui/homeTransition")
    >>> saved_transition()
    'cascade'
    """
    return transition_named(text_value(store(), key="ui/homeTransition", default=DEFAULT_TRANSITION)).key


def save_transition(key: str) -> None:
    """
    Remember which transition to use.

    Parameters
    ----------
    key : str
        The key.

    Examples
    --------
    >>> save_transition("flip")
    >>> saved_transition()
    'flip'
    >>> store().remove("ui/homeTransition")
    """
    store().setValue("ui/homeTransition", transition_named(key).key)


def paint_sprites(
    painter: QPainter,
    *,
    sprites: Sequence[Sprite],
) -> None:
    """
    Draw sprites as they now look.

    Parameters
    ----------
    painter : QPainter
        The painter to draw with.
    sprites : sequence of Sprite
        The sprites, drawn in order. Keyword-only.

    Examples
    --------
    >>> from PySide6.QtGui import QImage
    >>> image = QImage(20, 20, QImage.Format.Format_ARGB32)
    >>> brush = QPainter(image)
    >>> paint_sprites(brush, sprites=[Sprite(pixmap=QPixmap(10, 10), rect=QRectF(0, 0, 10, 10))])
    >>> brush.end()
    True
    """
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    for sprite in sprites:
        if sprite.opacity <= 0.0 or sprite.pixmap.isNull() or sprite.sx <= 0.0 or sprite.sy <= 0.0:
            continue
        width, height = sprite.rect.width() * sprite.sx, sprite.rect.height() * sprite.sy
        painter.save()
        painter.setOpacity(min(sprite.opacity, 1.0))
        painter.translate(sprite.rect.center().x() + sprite.dx, sprite.rect.center().y() + sprite.dy)
        painter.rotate(sprite.angle)
        target = QRectF(-width / 2, -height / 2, width, height)
        if sprite.reveal < 1.0:
            shown = width * sprite.reveal
            if sprite.reveal_from > 0:
                left = target.left()
            elif sprite.reveal_from < 0:
                left = target.right() - shown
            else:
                left = -shown / 2
            painter.setClipRect(QRectF(left, target.top(), shown, target.height()))
        picture = sprite.pixmap
        if sprite.blur > 0.0:
            factor = 1.0 + sprite.blur * BLUR_STEPS
            picture = picture.scaled(
                max(int(picture.width() / factor), 1),
                max(int(picture.height() / factor), 1),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        painter.drawPixmap(target, picture, QRectF(picture.rect()))
        painter.restore()


class TransitionCanvas(QWidget):
    """
    A see-through sheet laid over the cards, on which a transition is drawn.

    Attributes
    ----------
    old : list of Sprite
        The cards that are leaving.
    new : list of Sprite
        The cards that are arriving.
    finished : Signal
        Emitted when a transition has played to its end.
    running : bool
        True while a transition is playing.

    Examples
    --------
    >>> canvas = TransitionCanvas()
    >>> canvas.running
    False
    """

    finished = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """
        Build the canvas, hidden.

        Parameters
        ----------
        parent : QWidget or None, default None
            The widget it is laid over.

        Examples
        --------
        >>> TransitionCanvas().isHidden()
        True
        """
        super().__init__(parent)
        self.old: list[Sprite] = []
        self.new: list[Sprite] = []
        self.running = False
        self._direction = 1
        self._frame: Callable[[Scene], None] | None = None
        self._animation = QVariantAnimation(self)
        self._animation.setStartValue(0.0)
        self._animation.setEasingCurve(QEasingCurve.Type.Linear)
        self._animation.valueChanged.connect(self._advance)
        self._animation.finished.connect(self.stop)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()

    def cover(self, old: list[Sprite]) -> None:
        """
        Show the old cards on the canvas as they are, so that they can be swapped for the new ones unseen.

        Parameters
        ----------
        old : list of Sprite
            The photographs of the cards that are leaving.

        Examples
        --------
        >>> canvas = TransitionCanvas()
        >>> canvas.cover([])
        >>> canvas.running
        True
        """
        self.old, self.new = old, []
        self.running = True
        parent = self.parentWidget()
        if parent is not None:
            self.setGeometry(parent.rect())
        self.show()
        self.raise_()
        self.update()

    def play(
        self,
        transition: Transition,
        *,
        new: list[Sprite],
        direction: int,
    ) -> None:
        """
        Play a transition from the old cards that cover the canvas to the new ones.

        Parameters
        ----------
        transition : Transition
            Which one.
        new : list of Sprite
            The photographs of the cards that are arriving. Keyword-only.
        direction : int
            1 when going toward the lessons, -1 when coming back. Keyword-only.

        Examples
        --------
        >>> canvas = TransitionCanvas()
        >>> canvas.cover([])
        >>> canvas.play(TRANSITIONS[1], new=[], direction=1)
        >>> canvas.running
        True
        >>> canvas.stop()
        """
        self.new = new
        self._direction = direction
        self._frame = transition.frame
        self._animation.stop()
        length = transition.length(Scene(time=0.0, old=self.old, new=new, direction=direction))
        self._animation.setEndValue(length)
        self._animation.setDuration(max(int(length), 1))
        self._advance(0.0)
        motion.play(self._animation)

    def stop(self) -> None:
        """
        End the transition at once and take the canvas away.

        Examples
        --------
        >>> canvas = TransitionCanvas()
        >>> canvas.cover([])
        >>> canvas.stop()
        >>> canvas.running, canvas.isHidden()
        (False, True)
        """
        was = self.running
        self._animation.stop()
        self.running = False
        self.old, self.new = [], []
        self.hide()
        if was:
            self.finished.emit()

    def _advance(self, time: float) -> None:
        """
        Set how every sprite looks at a time, and draw.

        Parameters
        ----------
        time : float
            Milliseconds since the transition began.

        Examples
        --------
        >>> canvas = TransitionCanvas()
        >>> canvas._advance(0.0)
        """
        if self._frame is not None:
            self._frame(Scene(time=float(time), old=self.old, new=self.new, direction=self._direction))
        self.update()

    def paintEvent(self, _: QPaintEvent) -> None:
        """
        Draw every sprite as it now looks.

        Parameters
        ----------
        _ : QPaintEvent
            The paint request.

        Examples
        --------
        >>> canvas = TransitionCanvas()
        >>> canvas.resize(100, 100)
        >>> canvas.grab().isNull()
        False
        """
        painter = QPainter(self)
        paint_sprites(painter, sprites=(*self.old, *self.new))
        painter.end()
