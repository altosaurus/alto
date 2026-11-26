---
title: ArpeggioSettings
parent: alto.settings
api_module: alto.settings
package: alto
permalink: /api/alto.settings/class-arpeggiosettings/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
ArpeggioSettings(
    clefs: set[str] = field(default_factory=lambda: {'treble', 'bass'}),
    *,
    types: set[str] = field(default_factory=lambda: {'major', 'minor', 'dominant 7th', 'diminished 7th'}),
    inversions: set[int] = field(default_factory=lambda: set(INVERSIONS)),
    key_signature: bool = False,
    keys: set[int] = field(default_factory=lambda: {-3, -2, -1, 0, 1, 2, 3}),
)
```

{% endraw %}{% include api-source.html name="ArpeggioSettings" line=1243 %}{% raw %}

</div>

Bases: `ClefChoice, KeyChoice`

The settings of the arpeggio identification exercise.

**Attributes**

| Attribute | Type | Description |
| --- | --- | --- |
| `clefs` | `set of str` | The clefs to draw on, any of `CLEFS`. |
| `types` | `set of str` | The chord types to ask, from `ARPEGGIO_TYPES`. Keyword-only. |
| `inversions` | `set of int` | The inversions to ask: 0 for root position up to 3 for the third inversion. Keyword-only. |
| `key_signature` | `bool, default False` | Draw a key signature, so the arpeggio only gets signs where it differs from it. Keyword-only. |
| `keys` | `set of int` | The key signatures to draw from, as sharps (positive) or flats (negative). Keyword-only. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ArpeggioSettings().active_types()
['major', 'minor', 'dominant 7th', 'diminished 7th']
```

## ArpeggioSettings.active_types

<div class="api-signature" markdown="1">

```python
def active_types() -> list[str]
```

{% endraw %}{% include api-source.html name="ArpeggioSettings.active_types" line=1297 %}{% raw %}

</div>

Return the chord types to ask, triads first and then seventh
chords.

**Returns**

| Type | Description |
| --- | --- |
| `list of str` | The chosen types in the order of `ARPEGGIO_TYPES`, or "major" if none are chosen. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ArpeggioSettings(
...     types={"minor 7th", "major"}
... ).active_types()
['major', 'minor 7th']
```

## ArpeggioSettings.active_inversions

<div class="api-signature" markdown="1">

```python
def active_inversions() -> list[int]
```

{% endraw %}{% include api-source.html name="ArpeggioSettings.active_inversions" line=1317 %}{% raw %}

</div>

Return the inversions to ask, root position first.

**Returns**

| Type | Description |
| --- | --- |
| `list of int` | The chosen inversions, or root position (0) if none are chosen. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> ArpeggioSettings(
...     inversions={2, 0}
... ).active_inversions()
[0, 2]
```

## ArpeggioSettings.inversions_for

<div class="api-signature" markdown="1">

```python
def inversions_for(chord_type: str) -> list[int]
```

{% endraw %}{% include api-source.html name="ArpeggioSettings.inversions_for" line=1336 %}{% raw %}

</div>

Return the inversions that can be asked for a chord type.

A triad has no third inversion. If none of the chosen inversions
applies (only the third, for a triad), root position is
used.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `chord_type` | `str` | A key of `CHORDS`, such as "major" or "dominant 7th". |

**Returns**

| Type | Description |
| --- | --- |
| `list of int` | The inversions to choose from. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> cfg = ArpeggioSettings()
>>> (
...     cfg.inversions_for("major"),
...     cfg.inversions_for("dominant 7th"),
... )
([0, 1, 2], [0, 1, 2, 3])
>>> ArpeggioSettings(
...     inversions={3}
... ).inversions_for("major")
[0]
```
{% endraw %}
