---
title: InstrumentPicker
parent: alto.ui.instrument_picker
api_module: alto.ui.instrument_picker
package: alto.ui
permalink: /api/alto.ui.instrument_picker/class-instrumentpicker/
---
{% raw %}
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

| Attribute | Type | Description |
| --- | --- | --- |
| `chosen` | `Signal` | Emitted with the key of the instrument that is now in use. |
| `groups` | `dict of str to list of Instrument` | The entries in the list, each with the instruments (ways of playing) it holds. |
| `list` | `QListWidget` | The box of entries. |
| `shown` | `str or None` | The entry whose page is showing. |

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

| Parameter | Type | Description |
| --- | --- | --- |
| `parent` | `QWidget or None, default None` | The widget that owns the picker. |

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picker = InstrumentPicker()
>>> picker.list.count() == len(picker.groups)
True
```

## InstrumentPicker.select

<div class="api-signature" markdown="1">

```python
def select(key: str) -> None
```

{% endraw %}{% include api-source.html name="InstrumentPicker.select" line=449 %}{% raw %}

</div>

Show the page of the entry an instrument belongs to.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | An instrument's key. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picker = InstrumentPicker()
>>> picker.select("marimba")
>>> picker.shown
'Marimba'
```

## InstrumentPicker.show_group

<div class="api-signature" markdown="1">

```python
def show_group(group: str) -> None
```

{% endraw %}{% include api-source.html name="InstrumentPicker.show_group" line=793 %}{% raw %}

</div>

Fill the summary page for an entry from what is known about it
and what is on disk.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `group` | `str` | An entry in the list, such as "Flute" or "Viola". |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> picker = InstrumentPicker()
>>> picker.show_group("Flute")
>>> picker.shown
'Flute'
```

## InstrumentPicker.changeEvent

<div class="api-signature" markdown="1">

```python
def changeEvent(event: QEvent) -> None
```

{% endraw %}{% include api-source.html name="InstrumentPicker.changeEvent" line=1010 %}{% raw %}

</div>

Redraw the summary page when the palette changes, so its colors
follow the theme.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `event` | `QEvent` | The change. |

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

## InstrumentPicker.use

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

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The instrument's key. |

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

## InstrumentPicker.preview

<div class="api-signature" markdown="1">

```python
def preview(key: str) -> None
```

{% endraw %}{% include api-source.html name="InstrumentPicker.preview" line=1068 %}{% raw %}

</div>

Play the DSCH motif in an instrument, even if sound is muted.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str` | The instrument's key. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> InstrumentPicker().preview(
...     "flute"
... )  # doctest: +SKIP
```
{% endraw %}
