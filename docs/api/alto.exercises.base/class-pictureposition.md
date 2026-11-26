---
title: PicturePosition
parent: alto.exercises.base
api_module: alto.exercises.base
package: alto.exercises
permalink: /api/alto.exercises.base/class-pictureposition/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
PicturePosition(
    instrument: str,
    point: tuple[float, float],
    note: str = '',
    size: float = 0.0,
    focus: tuple[float, ...] = (),
    marker: bool = True,
    view: str = '',
    keys: tuple[tuple[str, str], ...] = (),
    notes: tuple[str, ...] = (),
    span: tuple[str, ...] = (),
)
```

{% endraw %}{% include api-source.html name="PicturePosition" line=66 %}{% raw %}

</div>

A pack-owned image and a marked location in its original pixels.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `instrument` | `str` | The pack-qualified instrument whose picture is shown. |
| `point` | `tuple of float` | The marked location, in the picture's own pixels. |
| `note` | `str, default ""` | A pitch to play when the answer is right, or an empty string for a silent question. |
| `size` | `float, default 0.0` | The marker's diameter in the picture's own pixels. Zero asks for Alto's default size, which suits a large part. |
| `focus` | `tuple of float, default ()` | The region to show, as left, top, width and height in the picture's own pixels, so a small part is easy to see. Empty shows the whole picture. |
| `marker` | `bool, default True` | False shows the picture without a dot, for a lesson that introduces the whole instrument. |
| `view` | `str, default ""` | The instrument's extra picture to use, such as "back", with the point and focus in that picture's pixels. Empty uses the instrument's main picture. |
| `keys` | `tuple of tuple of str, default ()` | Keys to highlight on the instrument's keyboards, which Alto draws instead of the picture. Each is the name of a keyboard and the pitch of a key on it, such as ``("Lower manual", "C4")``. |
| `notes` | `tuple of str, default ()` | Pitches to play one after another when the answer is right, such as the two keys of an interval. They take the place of `note`. |
| `span` | `tuple of str, default ()` | The lowest and highest key to draw on each keyboard, such as ``("C3", "C5")``. Empty draws each keyboard's whole range. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> PicturePosition(
...     "pack.studio.drum", (80, 50)
... ).point
(80, 50)
>>> PicturePosition(
...     "pack.studio.organ",
...     (0, 0),
...     keys=(("Great", "C4"), ("Swell", "E4")),
... ).keys[1]
('Swell', 'E4')
```
{% endraw %}
