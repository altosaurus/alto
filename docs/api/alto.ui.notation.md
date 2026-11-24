---
title: alto.ui.notation
parent: api
package: alto.ui
permalink: /api/alto.ui.notation/
---
{% raw %}
Notation styles: which music font the staff, clefs, notes and
accidentals are engraved in.

Also holds the choice of how the baritone clef is written (an F clef or
a C clef).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> BY_KEY["leland"].label
'Leland'
>>> clef_shape("treble")
'treble'
```

## NotationStyle

<div class="api-signature" markdown="1">

```python
NotationStyle(
    key: str,
    *,
    label: str,
    note: str,
    font: str | None,
    line: float = 1.4,
)
```

{% endraw %}{% include api-source.html name="NotationStyle" line=31 %}{% raw %}

</div>

One look for the music: a font and how heavy the staff lines are.

**Attributes**

- `key` (*str*): The identifier saved in the settings.
- `label` (*str*): The name shown in the interface. Keyword-only.
- `note` (*str*): A few words on where this look comes from. Keyword-only.
- `font` (*str or None*): A key in engraving.json, or None for the built-in Noto Music drawing. Keyword-only.
- `line` (*float, default 1.4*): The staff line weight in pixels, for the built-in drawing (the SMuFL fonts state their own). Keyword-only.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> style = BY_KEY["noto"]
>>> style.label, style.font
('Noto Music', None)
```

## baritone_clef

<div class="api-signature" markdown="1">

```python
def baritone_clef() -> str
```

{% endraw %}{% include api-source.html name="baritone_clef" line=153 %}{% raw %}

</div>

Return which way the baritone clef is written.

**Returns**

- *str*: "f" for an F clef on the middle line, or "c" for a C clef on the top line.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> baritone_clef() in BARITONE_CLEFS
True
```

## clef_shape

<div class="api-signature" markdown="1">

```python
def clef_shape(clef: str) -> str
```

{% endraw %}{% include api-source.html name="clef_shape" line=171 %}{% raw %}

</div>

Return the clef as it is drawn.

**Parameters**

- `clef` (*str*): A clef name such as "treble" or "baritone".

**Returns**

- *str*: The same name, except that "baritone" becomes "baritone_f" or "baritone_c" by the chosen way of writing it.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> clef_shape("alto")
'alto'
>>> set_baritone_clef("c")
>>> clef_shape("baritone")
'baritone_c'
>>> set_baritone_clef(
...     "f"
... )  # back to the default
>>> clef_shape("baritone")
'baritone_f'
```

## set_baritone_clef

<div class="api-signature" markdown="1">

```python
def set_baritone_clef(kind: str) -> None
```

{% endraw %}{% include api-source.html name="set_baritone_clef" line=202 %}{% raw %}

</div>

Choose and save how the baritone clef is written, and redraw every
staff already on screen.

**Parameters**

- `kind` (*str*): "f" or "c"; anything else gives the default (F).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> set_baritone_clef("c")
>>> baritone_clef()
'c'
>>> set_baritone_clef(
...     "sideways"
... )  # not a choice: the default
>>> baritone_clef()
'f'
```

## current

<div class="api-signature" markdown="1">

```python
def current() -> NotationStyle
```

{% endraw %}{% include api-source.html name="current" line=229 %}{% raw %}

</div>

Return the notation style in use.

**Returns**

- *NotationStyle*: The style chosen in the settings (Finale Maestro until another is chosen).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> current().key in BY_KEY
True
```

## load_style

<div class="api-signature" markdown="1">

```python
def load_style() -> None
```

{% endraw %}{% include api-source.html name="load_style" line=247 %}{% raw %}

</div>

Apply the saved choices: the style (Finale Maestro if none is saved
or it is unknown) and the baritone clef.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue("ui/notation", "bravura")
>>> load_style()
>>> current().key
'bravura'
>>> set_style(DEFAULT)  # back to the default
```

## set_style

<div class="api-signature" markdown="1">

```python
def set_style(key: str) -> None
```

{% endraw %}{% include api-source.html name="set_style" line=274 %}{% raw %}

</div>

Choose and save a style, and redraw every staff already on screen.

**Parameters**

- `key` (*str*): A key of `BY_KEY`; an unknown key gives the default.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> set_style("leland")
>>> current().label
'Leland'
>>> set_style(DEFAULT)
```

## on_redraw

<div class="api-signature" markdown="1">

```python
def on_redraw(hook: Callable[[], None]) -> None
```

{% endraw %}{% include api-source.html name="on_redraw" line=299 %}{% raw %}

</div>

Register a function to call whenever the notation style changes.

The staff widgets live in a module that imports this one, so they
register themselves here instead of being found by
this module.

**Parameters**

- `hook` (*Callable*): A function with no arguments that repaints what depends on the style.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> calls = []
>>> def repaint() -> None:
...     calls.append(1)
>>> on_redraw(repaint)
>>> _redraw()
>>> calls
[1]
>>> _redraw_hooks.remove(repaint)
```
{% endraw %}
