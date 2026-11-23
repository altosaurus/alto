---
title: alto.ui.scale_explorer
parent: api
package: alto.ui
permalink: /api/alto.ui.scale_explorer/
---
{% raw %}
Interactive notation and step patterns for learning scales.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> explorer = ScaleExplorer()
>>> len(explorer.notes)
8
```

## ScaleExplorer

```python
ScaleExplorer(
    *,
    scale: str = 'Major (Ionian)',
    tonic: str = 'C4',
    editable: bool = True,
    lesson_layout: bool = False,
)
```

Bases: `QWidget`

Compare scales on a staff and hear individual steps.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleExplorer().mode.currentText()
'Major (Ionian)'
```

**Constructor**

Build the scale diagram and its controls.

**Parameters**

- `scale` (*str*): Initial scale type.
- `tonic` (*str*): Initial tonic with octave.
- `editable` (*bool*): Allow changing the example; false keeps a lesson question fixed.
- `lesson_layout` (*bool*): Use content-sized staff lines in the lesson pane.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleExplorer(scale="Dorian", tonic="D4").notes[0].name
'D'
```

### ScaleExplorer.refresh

```python
def refresh() -> None
```

Rebuild the notation and gap labels for the selected example.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> explorer = ScaleExplorer()
>>> explorer.mode.setCurrentText("Harmonic minor")
>>> explorer.steps[5].text()
'3H'
```

### ScaleExplorer.select_gap

```python
def select_gap(index: int) -> None
```

Highlight and play the notes around a gap.

**Parameters**

- `index` (*int*): Gap index, from zero to six.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> explorer = ScaleExplorer()
>>> explorer.select_gap(2)  # doctest: +SKIP
```

### ScaleExplorer.hear

```python
def hear(
    *,
    force: bool = True,
) -> None
```

Play the example using the selected instrument.

**Parameters**

- `force` (*bool*): Audition the scale while muted. The lesson's main Hear button follows its sound setting.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ScaleExplorer().hear()  # doctest: +SKIP
```
{% endraw %}
