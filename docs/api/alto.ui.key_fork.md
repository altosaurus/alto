---
title: alto.ui.key_fork
parent: api
package: alto.ui
api_components: [{"title": "KeyFork", "url": "/api/alto.ui.key_fork/class-keyfork/"}, {"title": "draw_natural", "url": "/api/alto.ui.key_fork/function-draw_natural/"}, {"title": "fork_path", "url": "/api/alto.ui.key_fork/function-fork_path/"}, {"title": "nearest_on_fork", "url": "/api/alto.ui.key_fork/function-nearest_on_fork/"}, {"title": "node_position", "url": "/api/alto.ui.key_fork/function-node_position/"}, {"title": "path_between", "url": "/api/alto.ui.key_fork/function-path_between/"}, {"title": "point_along", "url": "/api/alto.ui.key_fork/function-point_along/"}, {"title": "route", "url": "/api/alto.ui.key_fork/function-route/"}]
permalink: /api/alto.ui.key_fork/
---
{% raw %}
The fork: a picker for a key signature, shaped like a tuning fork lying
on its side.

## Classes

- [`KeyFork`](class-keyfork/) — A tuning fork on its side, for choosing how many sharps or flats a key signature has.

## Functions

- [`node_position`](function-node_position/) — Return where a signature sits on the fork.
- [`route`](function-route/) — Return the way along the fork from the end of the stem to a signature.
- [`path_between`](function-path_between/) — Return the way along the fork from one signature to another.
- [`point_along`](function-point_along/) — Return the point a fraction of the way along a path made of short straight pieces.
- [`nearest_on_fork`](function-nearest_on_fork/) — Return the point on the fork's line that is closest to a point.
- [`fork_path`](function-fork_path/) — Return the outline of the fork: the stem, a half circle for the U, and the two tines.
- [`draw_natural`](function-draw_natural/) — Draw a natural sign: two upright lines joined by two slanting bars.

<details markdown="1">
<summary>Module notes and examples</summary>

The stem on the left ends in a natural sign (no sharps or flats, C
major). At the right the stem opens into two tines:
the top one has the sharps, 1 to 7, and the bottom one the flats, 1 to
7. A circle marks the chosen signature. Click a
number to choose it, drag the circle along the fork, or turn the mouse
wheel to move it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> fork = KeyFork()
>>> fork.set_value(-3)
>>> fork.value
-3
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"node_position": "function-node_position/", "route": "function-route/", "path_between": "function-path_between/", "point_along": "function-point_along/", "nearest_on_fork": "function-nearest_on_fork/", "fork_path": "function-fork_path/", "draw_natural": "function-draw_natural/", "keyfork": "class-keyfork/", "keyforkset_value": "class-keyfork/#keyforkset_value", "keyforkset_marker_color": "class-keyfork/#keyforkset_marker_color", "keyforkvalue_at": "class-keyfork/#keyforkvalue_at", "keyforkmousepressevent": "class-keyfork/#keyforkmousepressevent", "keyforkmousemoveevent": "class-keyfork/#keyforkmousemoveevent", "keyforkmousereleaseevent": "class-keyfork/#keyforkmousereleaseevent", "keyforkleaveevent": "class-keyfork/#keyforkleaveevent", "keyforkwheelevent": "class-keyfork/#keyforkwheelevent", "keyforkkeypressevent": "class-keyfork/#keyforkkeypressevent", "keyforkpaintevent": "class-keyfork/#keyforkpaintevent"}</script>
{% include api-fragments.html %}
