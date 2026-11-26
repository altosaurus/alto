---
title: alto.theory.fifths
parent: api
package: alto.theory
api_components: [{"title": "accidentals_of", "url": "/api/alto.theory.fifths/function-accidentals_of/"}, {"title": "cells_of_key", "url": "/api/alto.theory.fifths/function-cells_of_key/"}, {"title": "display_major", "url": "/api/alto.theory.fifths/function-display_major/"}, {"title": "display_minor", "url": "/api/alto.theory.fifths/function-display_minor/"}, {"title": "explain", "url": "/api/alto.theory.fifths/function-explain/"}, {"title": "numeral_chords", "url": "/api/alto.theory.fifths/function-numeral_chords/"}, {"title": "place_of_major", "url": "/api/alto.theory.fifths/function-place_of_major/"}, {"title": "relative_minor", "url": "/api/alto.theory.fifths/function-relative_minor/"}]
permalink: /api/alto.theory.fifths/
---
{% raw %}
The circle of fifths: the twelve keys in order, each major with its
relative minor.

## Functions

- [`place_of_major`](function-place_of_major/) — Return where a major key is on the circle, by either of its names.
- [`relative_minor`](function-relative_minor/) — Return the relative minor of a major key.
- [`cells_of_key`](function-cells_of_key/) — Return the six wedges that hold the chords of a major key, and the Roman numeral of each.
- [`numeral_chords`](function-numeral_chords/) — Return the six chords of a major key that are on the circle, spelled as that key spells them.
- [`display_major`](function-display_major/) — Return the major key of a place as it is written to ask about it: "A major", or "B major / C♭ major".
- [`display_minor`](function-display_minor/) — Return the minor key of a place as it is written to ask about it: "F♯ minor", or "G♯ minor / A♭ minor".
- [`accidentals_of`](function-accidentals_of/) — Return the sharps or flats of a key signature, in the order they are written.
- [`explain`](function-explain/) — Explain a cell of the circle: its key signature, where it comes from, its relative key and its chords.

<details markdown="1">
<summary>Module notes and examples</summary>

Going clockwise from C at the top, each key is a fifth above the one
before, so it has one more sharp (or one fewer flat).
The relative minor of a major key has the same key signature and starts
on its sixth note: A minor goes with C major.

A key has six chords that fit on the circle: the major triads I, IV and
V on the outer ring, and the minor triads ii, iii and
vi on the inner ring. They are the key's own wedge and the wedge on each
side of it, on both rings. (The seventh chord, vii°,
is diminished and has no wedge.)

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> MAJORS[3], MINORS[3], SIGNATURES[3]
(('A',), ('F♯m',), 3)
>>> relative_minor("A")
'F♯m'
>>> numeral_chords(1)
{'I': 'G', 'ii': 'Am', 'iii': 'Bm', 'IV': 'C', 'V': 'D', 'vi': 'Em'}
>>> accidentals_of(-2)
['B♭', 'E♭']
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"place_of_major": "function-place_of_major/", "relative_minor": "function-relative_minor/", "cells_of_key": "function-cells_of_key/", "numeral_chords": "function-numeral_chords/", "display_major": "function-display_major/", "display_minor": "function-display_minor/", "accidentals_of": "function-accidentals_of/", "explain": "function-explain/"}</script>
{% include api-fragments.html %}
