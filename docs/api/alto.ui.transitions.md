---
title: alto.ui.transitions
parent: api
package: alto.ui
api_components: [{"title": "Motion", "url": "/api/alto.ui.transitions/class-motion/"}, {"title": "Scene", "url": "/api/alto.ui.transitions/class-scene/"}, {"title": "Sprite", "url": "/api/alto.ui.transitions/class-sprite/"}, {"title": "Transition", "url": "/api/alto.ui.transitions/class-transition/"}, {"title": "TransitionCanvas", "url": "/api/alto.ui.transitions/class-transitioncanvas/"}, {"title": "blur", "url": "/api/alto.ui.transitions/function-blur/"}, {"title": "built", "url": "/api/alto.ui.transitions/function-built/"}, {"title": "cascade", "url": "/api/alto.ui.transitions/function-cascade/"}, {"title": "crossfade", "url": "/api/alto.ui.transitions/function-crossfade/"}, {"title": "drop", "url": "/api/alto.ui.transitions/function-drop/"}, {"title": "ease_out", "url": "/api/alto.ui.transitions/function-ease_out/"}, {"title": "eased", "url": "/api/alto.ui.transitions/function-eased/"}, {"title": "fade_in", "url": "/api/alto.ui.transitions/function-fade_in/"}, {"title": "flip", "url": "/api/alto.ui.transitions/function-flip/"}, {"title": "hide", "url": "/api/alto.ui.transitions/function-hide/"}, {"title": "made", "url": "/api/alto.ui.transitions/function-made/"}, {"title": "move", "url": "/api/alto.ui.transitions/function-move/"}, {"title": "paint_sprites", "url": "/api/alto.ui.transitions/function-paint_sprites/"}, {"title": "ramp", "url": "/api/alto.ui.transitions/function-ramp/"}, {"title": "ranks", "url": "/api/alto.ui.transitions/function-ranks/"}, {"title": "rise", "url": "/api/alto.ui.transitions/function-rise/"}, {"title": "save_transition", "url": "/api/alto.ui.transitions/function-save_transition/"}, {"title": "saved_transition", "url": "/api/alto.ui.transitions/function-saved_transition/"}, {"title": "slide", "url": "/api/alto.ui.transitions/function-slide/"}, {"title": "span", "url": "/api/alto.ui.transitions/function-span/"}, {"title": "transition_named", "url": "/api/alto.ui.transitions/function-transition_named/"}, {"title": "wipe", "url": "/api/alto.ui.transitions/function-wipe/"}, {"title": "zoom", "url": "/api/alto.ui.transitions/function-zoom/"}]
permalink: /api/alto.ui.transitions/
---
{% raw %}
The transitions between the exercises and the lessons on the home page.

## Classes

- [`Sprite`](class-sprite/) — A photograph of one card, and how it is drawn at this moment.
- [`Scene`](class-scene/) — What a transition is given at each moment: the time, the two sets of sprites and the direction.
- [`Transition`](class-transition/) — One way of moving between the exercises and the lessons.
- [`Motion`](class-motion/) — How one set of cards moves in a transition built from parts: when each card starts, how long it takes, and what it does.
- [`TransitionCanvas`](class-transitioncanvas/) — A see-through sheet laid over the cards, on which a transition is drawn.

## Functions

- [`ease_out`](function-ease_out/) — Ease a progress from 0 to 1 so that it starts fast and slows to a stop.
- [`ramp`](function-ramp/) — Say how far along a part of a transition is, from 0 before it starts to 1 once it has finished.
- [`hide`](function-hide/) — Make sprites invisible.
- [`fade_in`](function-fade_in/) — Set the sprites for a fade in: the new cards fade up from clear, and nothing of the old remains.
- [`crossfade`](function-crossfade/) — Set the sprites for a crossfade: the old cards fade out as the new ones fade in.
- [`slide`](function-slide/) — Set the sprites for a slide: both sets move sideways, toward the side of the switch that was pressed.
- [`rise`](function-rise/) — Set the sprites for a rise: the old cards sink and fade, and the new ones rise into place.
- [`cascade`](function-cascade/) — Set the sprites for a cascade: the new cards arrive one after another, each rising a little as it appears.
- [`zoom`](function-zoom/) — Set the sprites for a zoom: the old cards grow a little as they fade, and the new ones grow into place.
- [`flip`](function-flip/) — Set the sprites for a flip: each old card turns edge on and goes, then each new one turns face on.
- [`blur`](function-blur/) — Set the sprites for a blur: the old cards dissolve into a blur and the new ones come into focus.
- [`wipe`](function-wipe/) — Set the sprites for a wipe: the new cards are uncovered from one side while the old ones fade.
- [`drop`](function-drop/) — Set the sprites for drop and pop: the old cards drop away one by one, then the new ones pop in with a small bounce.
- [`eased`](function-eased/) — Time a progress from 0 to 1 in one of the ways a motion can be eased.
- [`ranks`](function-ranks/) — Say where each sprite comes in an order: 0 for the first to start.
- [`span`](function-span/) — Say how long a motion takes for a number of cards, from when it starts to when the last card has finished.
- [`move`](function-move/) — Set the sprites for a transition built from a motion for the cards that leave and one for the cards that arrive.
- [`built`](function-built/) — Make the frame and length functions of a transition built from motions.
- [`made`](function-made/) — Make a transition from motions.
- [`transition_named`](function-transition_named/) — Find a transition by its key.
- [`saved_transition`](function-saved_transition/) — Return the key of the transition that is chosen in the settings.
- [`save_transition`](function-save_transition/) — Remember which transition to use.
- [`paint_sprites`](function-paint_sprites/) — Draw sprites as they now look.

<details markdown="1">
<summary>Module notes and examples</summary>

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

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"sprite": "class-sprite/", "scene": "class-scene/", "ease_out": "function-ease_out/", "ramp": "function-ramp/", "hide": "function-hide/", "fade_in": "function-fade_in/", "crossfade": "function-crossfade/", "slide": "function-slide/", "rise": "function-rise/", "cascade": "function-cascade/", "zoom": "function-zoom/", "flip": "function-flip/", "blur": "function-blur/", "wipe": "function-wipe/", "drop": "function-drop/", "transition": "class-transition/", "motion": "class-motion/", "eased": "function-eased/", "ranks": "function-ranks/", "span": "function-span/", "move": "function-move/", "built": "function-built/", "made": "function-made/", "transition_named": "function-transition_named/", "saved_transition": "function-saved_transition/", "save_transition": "function-save_transition/", "paint_sprites": "function-paint_sprites/", "transitioncanvas": "class-transitioncanvas/", "transitioncanvascover": "class-transitioncanvas/#transitioncanvascover", "transitioncanvasplay": "class-transitioncanvas/#transitioncanvasplay", "transitioncanvasstop": "class-transitioncanvas/#transitioncanvasstop", "transitioncanvaspaintevent": "class-transitioncanvas/#transitioncanvaspaintevent"}</script>
{% include api-fragments.html %}
