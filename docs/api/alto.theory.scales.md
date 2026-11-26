---
title: alto.theory.scales
parent: api
package: alto.theory
api_components: [{"title": "all_tonics", "url": "/api/alto.theory.scales/function-all_tonics/"}, {"title": "arpeggio", "url": "/api/alto.theory.scales/function-arpeggio/"}, {"title": "build", "url": "/api/alto.theory.scales/function-build/"}, {"title": "format_key_signature", "url": "/api/alto.theory.scales/function-format_key_signature/"}, {"title": "key_signature", "url": "/api/alto.theory.scales/function-key_signature/"}, {"title": "major_key_tonic", "url": "/api/alto.theory.scales/function-major_key_tonic/"}, {"title": "mode_tonic", "url": "/api/alto.theory.scales/function-mode_tonic/"}]
permalink: /api/alto.theory.scales/
---
{% raw %}
Scales, modes, key signatures and chords, built from spelled intervals.

## Functions

- [`major_key_tonic`](function-major_key_tonic/) — Return the tonic of the major key with a given number of sharps or flats.
- [`mode_tonic`](function-mode_tonic/) — Return the note a scale in a given mode starts on, for a given key signature.
- [`arpeggio`](function-arpeggio/) — Return a chord broken and rising from its lowest note, then that note again an octave higher.
- [`build`](function-build/) — Build the notes of a scale or chord above a tonic.
- [`key_signature`](function-key_signature/) — Return the key signature of a scale as a signed count of accidentals.
- [`format_key_signature`](function-format_key_signature/) — Describe a key signature in words.
- [`all_tonics`](function-all_tonics/) — Return every spelled tonic in octave 4, within a limit on accidentals.

<details markdown="1">
<summary>Module notes and examples</summary>

`SCALES` and `CHORDS` map a name to the list of intervals above the
tonic or root. `build` turns such a list into notes,
and the other functions work out key signatures, mode tonics and
arpeggios from them.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [
...     str(n)
...     for n in build(
...         Note.parse("D4"),
...         intervals=SCALES["Dorian"],
...     )
... ]
['D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
>>> [
...     str(n)
...     for n in build(
...         Note.parse("C4"),
...         intervals=CHORDS["minor 7th"],
...     )
... ]
['C4', 'E♭4', 'G4', 'B♭4']
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"major_key_tonic": "function-major_key_tonic/", "mode_tonic": "function-mode_tonic/", "arpeggio": "function-arpeggio/", "build": "function-build/", "key_signature": "function-key_signature/", "format_key_signature": "function-format_key_signature/", "all_tonics": "function-all_tonics/"}</script>
{% include api-fragments.html %}
