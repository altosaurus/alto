---
title: alto.ui.engraving
parent: api
package: alto.ui
api_components: [{"title": "accidental_width", "url": "/api/alto.ui.engraving/function-accidental_width/"}, {"title": "draw_accidental", "url": "/api/alto.ui.engraving/function-draw_accidental/"}, {"title": "draw_beamed_notes", "url": "/api/alto.ui.engraving/function-draw_beamed_notes/"}, {"title": "draw_brace", "url": "/api/alto.ui.engraving/function-draw_brace/"}, {"title": "draw_clef", "url": "/api/alto.ui.engraving/function-draw_clef/"}, {"title": "draw_note", "url": "/api/alto.ui.engraving/function-draw_note/"}, {"title": "fill_path", "url": "/api/alto.ui.engraving/function-fill_path/"}, {"title": "ledger_width", "url": "/api/alto.ui.engraving/function-ledger_width/"}, {"title": "notation_glyph", "url": "/api/alto.ui.engraving/function-notation_glyph/"}, {"title": "staff_line_width", "url": "/api/alto.ui.engraving/function-staff_line_width/"}]
permalink: /api/alto.ui.engraving/
---
{% raw %}
Drawing notation with SMuFL music fonts (Bravura, Leland, Petaluma,
MuseJazz and others).

## Functions

- [`notation_glyph`](function-notation_glyph/) — Read a score marking from a bundled font at four staff spaces per em.
- [`staff_line_width`](function-staff_line_width/) — Return the thickness of a staff line, as the font specifies.
- [`ledger_width`](function-ledger_width/) — Return the thickness of a ledger line, as the font specifies.
- [`fill_path`](function-fill_path/) — Fill a path with a color and no outline.
- [`draw_note`](function-draw_note/) — Draw a note with its head centered on a point.
- [`draw_beamed_notes`](function-draw_beamed_notes/) — Draw a group with one beam for eighths or more for shorter notes.
- [`draw_clef`](function-draw_clef/) — Draw a clef with its left edge at a point.
- [`accidental_width`](function-accidental_width/) — Return how wide a sharp, flat or natural is drawn, so that it can be placed beside other things.
- [`draw_accidental`](function-draw_accidental/) — Draw a sharp, flat or natural with its left edge at a point.
- [`draw_brace`](function-draw_brace/) — Draw the font's brace stretched between two heights, for a grand staff.

<details markdown="1">
<summary>Module notes and examples</summary>

A SMuFL font has the parts of a note rather than whole notes: the head,
the flag, and the clef and accidental glyphs,
all measured in staff spaces (four to the em). The stem is a plain
rectangle that the code draws, placed using the stem
anchors the font publishes for each head. Heights are measured upward,
so they are flipped on screen.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> sorted(HEADS)
['breve', 'half', 'whole']
>>> ACCIDENTALS[1]
'accidentalSharp'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"notation_glyph": "function-notation_glyph/", "staff_line_width": "function-staff_line_width/", "ledger_width": "function-ledger_width/", "fill_path": "function-fill_path/", "draw_note": "function-draw_note/", "draw_beamed_notes": "function-draw_beamed_notes/", "draw_clef": "function-draw_clef/", "accidental_width": "function-accidental_width/", "draw_accidental": "function-draw_accidental/", "draw_brace": "function-draw_brace/"}</script>
{% include api-fragments.html %}
