---
title: alto.ui.instrument_picker
parent: api
package: alto.ui
permalink: /api/alto.ui.instrument_picker/
---
{% raw %}
Choosing the instrument that plays notes, with a summary of what each
one is made from.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> format_size(2_500_000)
'2.5 MB'
>>> list(PREVIEW)
[74, 75, 72, 71]
```

## sound_picker_layout

<div class="api-signature" markdown="1">

```python
def sound_picker_layout(
    picker: QWidget,
    *,
    choices: QListWidget,
    card: QFrame,
) -> None
```

{% endraw %}{% include api-source.html name="sound_picker_layout" line=68 %}{% raw %}

</div>

Place sound choices beside their detail card in Settings.

**Parameters**

- `picker` (*QWidget*): The instrument or metronome picker.
- `choices` (*QListWidget*): The list of sounds.
- `card` (*QFrame*): The selected sound's details and preview.

**Examples**

```text
Resizing the picker gives extra width to the detail card.
```

## load_instrument

<div class="api-signature" markdown="1">

```python
def load_instrument() -> None
```

{% endraw %}{% include api-source.html name="load_instrument" line=97 %}{% raw %}

</div>

Apply the saved instrument.

The piano is used if nothing is saved or the saved key is not an
instrument.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> store().setValue(
...     "audio/instrument", "flute"
... )
>>> load_instrument()
>>> sounds.instrument
'flute'
>>> store().setValue(
...     "audio/instrument", "not an instrument"
... )
>>> load_instrument()
>>> sounds.instrument
'piano'
```

## save_instrument

<div class="api-signature" markdown="1">

```python
def save_instrument() -> None
```

{% endraw %}{% include api-source.html name="save_instrument" line=123 %}{% raw %}

</div>

Remember the instrument in use.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sounds.instrument = "marimba"
>>> save_instrument()
>>> str(store().value("audio/instrument"))
'marimba'
>>> sounds.instrument = "piano"
>>> save_instrument()
```

## tokens

<div class="api-signature" markdown="1">

```python
def tokens(widget: QWidget) -> dict[str, str]
```

{% endraw %}{% include api-source.html name="tokens" line=139 %}{% raw %}

</div>

Return the summary page's colors.

All are mixed from the system palette so they follow its light or
dark theme.

**Parameters**

- `widget` (*QWidget*): The widget whose palette to use.

**Returns**

- *dict of str to str*: Color name to '#rrggbb': accent, accent_soft, muted, line, panel and well, and for each of good, warn and bad a text color and a soft background (such as good and good_soft).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> colors = tokens(QWidget())
>>> sorted(colors)[:3]
['accent', 'accent_soft', 'bad']
>>> colors["panel"].startswith("#")
True
```

## format_size

<div class="api-signature" markdown="1">

```python
def format_size(nbytes: int) -> str
```

{% endraw %}{% include api-source.html name="format_size" line=202 %}{% raw %}

</div>

Write a file size the way the instrument page shows it.

**Parameters**

- `nbytes` (*int*): The size in bytes.

**Returns**

- *str*: Megabytes with one decimal from a million bytes, otherwise whole kilobytes (at least 1).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     format_size(2_500_000),
...     format_size(500_000),
...     format_size(10),
... )
('2.5 MB', '500 KB', '1 KB')
```

## InstrumentPicker

<div class="api-signature" markdown="1">

```python
InstrumentPicker(parent: QWidget | None = None)
```

{% endraw %}{% include api-source.html name="InstrumentPicker" line=233 %}{% raw %}

</div>

Bases: `QWidget`

The instruments in a box on the left; on the right, what the
selected one is made from.

An instrument that can be played in more than one way (the viola,
arco or pizzicato) is one entry, and its page has a
'Use this instrument' and a 'Hear it' for each way. 'Hear it' plays
a short arpeggio even while sound is muted.

**Attributes**

- `chosen` (*Signal*): Emitted with the key of the instrument that is now in use.
- `groups` (*dict of str to list of Instrument*): The entries in the list, each with the instruments (ways of playing) it holds.
- `list` (*QListWidget*): The box of entries.
- `shown` (*str or None*): The entry whose page is showing.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picker = InstrumentPicker()
>>> picker.select("viola_plucked")
>>> picker.shown
'Viola'
```

**Constructor**

Build the picker, showing the page of the instrument in use.

**Parameters**

- `parent` (*QWidget or None, default None*): The widget that owns the picker.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picker = InstrumentPicker()
>>> picker.list.count() == len(picker.groups)
True
```

### InstrumentPicker.select

<div class="api-signature" markdown="1">

```python
def select(key: str) -> None
```

{% endraw %}{% include api-source.html name="InstrumentPicker.select" line=449 %}{% raw %}

</div>

Show the page of the entry an instrument belongs to.

**Parameters**

- `key` (*str*): An instrument's key.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picker = InstrumentPicker()
>>> picker.select("marimba")
>>> picker.shown
'Marimba'
```

### InstrumentPicker.show_group

<div class="api-signature" markdown="1">

```python
def show_group(group: str) -> None
```

{% endraw %}{% include api-source.html name="InstrumentPicker.show_group" line=793 %}{% raw %}

</div>

Fill the summary page for an entry from what is known about it
and what is on disk.

**Parameters**

- `group` (*str*): An entry in the list, such as "Flute" or "Viola".

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picker = InstrumentPicker()
>>> picker.show_group("Flute")
>>> picker.shown
'Flute'
```

### InstrumentPicker.changeEvent

<div class="api-signature" markdown="1">

```python
def changeEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="InstrumentPicker.changeEvent" line=1010 %}{% raw %}

</div>

Redraw the summary page when the palette changes, so its colors
follow the theme.

**Parameters**

- `event` (*QEvent*): The change.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picker = InstrumentPicker()
>>> picker.show_group("Flute")
>>> picker.changeEvent(
...     QEvent(QEvent.Type.PaletteChange)
... )
>>> picker.shown
'Flute'
```

### InstrumentPicker.use

<div class="api-signature" markdown="1">

```python
def use(key: str) -> None
```

{% endraw %}{% include api-source.html name="InstrumentPicker.use" line=1037 %}{% raw %}

</div>

Make an instrument the one for notes and the correct-answer
chime.

Nothing happens if it has no recordings installed.

**Parameters**

- `key` (*str*): The instrument's key.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picker = InstrumentPicker()
>>> chosen = []
>>> _ = picker.chosen.connect(chosen.append)
>>> picker.use("marimba")
>>> sounds.instrument, chosen
('marimba', ['marimba'])
>>> picker.use("piano")
```

### InstrumentPicker.preview

<div class="api-signature" markdown="1">

```python
def preview(key: str) -> None
```

{% endraw %}{% include api-source.html name="InstrumentPicker.preview" line=1068 %}{% raw %}

</div>

Play the DSCH motif in an instrument, even if sound is muted.

**Parameters**

- `key` (*str*): The instrument's key.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> InstrumentPicker().preview(
...     "flute"
... )  # doctest: +SKIP
```
{% endraw %}
