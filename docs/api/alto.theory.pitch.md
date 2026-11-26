---
title: alto.theory.pitch
parent: api
package: alto.theory
api_components: [{"title": "Interval", "url": "/api/alto.theory.pitch/class-interval/"}, {"title": "Note", "url": "/api/alto.theory.pitch/class-note/"}, {"title": "key_accidental", "url": "/api/alto.theory.pitch/function-key_accidental/"}]
permalink: /api/alto.theory.pitch/
---
{% raw %}
Pitches and intervals, spelled correctly (C# is not Db).

## Classes

- [`Note`](class-note/) — A spelled pitch: a letter name, an accidental and an octave.
- [`Interval`](class-interval/) — A simple or compound interval between two spelled notes.

## Functions

- [`key_accidental`](function-key_accidental/) — Return the accidental a key signature applies to a letter.

<details markdown="1">
<summary>Module notes and examples</summary>

A `Note` is a pitch with its spelling (a letter, an accidental and an
octave), so C♯4 and D♭4 are different notes even
though they sound the same. An `Interval` is a distance between two
spelled notes, such as a major third or a perfect
fifth. Together they can transpose a note by an interval and work out
the interval between two notes.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> c4 = Note.parse("C4")
>>> str(c4.transpose(Interval.parse("M3")))
'E4'
>>> Interval.between(c4, high=Note.parse("G4"))
Interval(number=5, quality='P')
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"note": "class-note/", "notemidi": "class-note/#notemidi", "notediatonic": "class-note/#notediatonic", "notepitch_class": "class-note/#notepitch_class", "notename": "class-note/#notename", "notefrom_diatonic": "class-note/#notefrom_diatonic", "noteparse": "class-note/#noteparse", "notetranspose": "class-note/#notetranspose", "interval": "class-interval/", "intervalinversion": "class-interval/#intervalinversion", "intervalis_perfect_type": "class-interval/#intervalis_perfect_type", "intervalsemitones": "class-interval/#intervalsemitones", "intervalshort": "class-interval/#intervalshort", "intervalbetween": "class-interval/#intervalbetween", "intervalparse": "class-interval/#intervalparse", "key_accidental": "function-key_accidental/"}</script>
{% include api-fragments.html %}
