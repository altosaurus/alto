---
title: alto.ui.staff
parent: api
package: alto.ui
api_components: [{"title": "StaffWidget", "url": "/api/alto.ui.staff/class-staffwidget/"}, {"title": "clef_target_of", "url": "/api/alto.ui.staff/function-clef_target_of/"}, {"title": "clef_targets", "url": "/api/alto.ui.staff/function-clef_targets/"}, {"title": "draw_key_signature", "url": "/api/alto.ui.staff/function-draw_key_signature/"}, {"title": "draw_signature_sign", "url": "/api/alto.ui.staff/function-draw_signature_sign/"}, {"title": "keyboard_key_staff", "url": "/api/alto.ui.staff/function-keyboard_key_staff/"}]
permalink: /api/alto.ui.staff/
---
{% raw %}
The staff: lines, clefs, key signatures and notes, drawn on a rounded
white "paper".

## Classes

- [`StaffWidget`](class-staffwidget/) — A staff with notes, a clef, a key signature and, optionally, a caption.

## Functions

- [`clef_targets`](function-clef_targets/) — Return the ways a clef can be written: the symbol and where on the staff it goes.
- [`clef_target_of`](function-clef_target_of/) — Return the symbol and the place of one way of writing a clef.
- [`draw_key_signature`](function-draw_key_signature/) — Draw the sharps or flats of a key signature, left to right.
- [`draw_signature_sign`](function-draw_signature_sign/) — Draw one sharp or flat at its written position in a key signature.
- [`keyboard_key_staff`](function-keyboard_key_staff/) — Build the compact key signature shown above a keyboard question.

<details markdown="1">
<summary>Module notes and examples</summary>

`StaffWidget` draws one staff, or a grand staff with a brace, in any of
the seven clefs. Notes and key signatures are
placed by their staff step (`Note.diatonic`) measured from the bottom
line of the clef, and are engraved in the notation
font chosen in the settings.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> key_signature_positions("treble", sign=1)
['F5', 'C5', 'G5', 'D5', 'A4', 'E5', 'B4']
>>> staff = StaffWidget()
>>> staff.show_notes(
...     [[Note.parse("C4")]],
...     clef="treble",
...     key=2,
... )
>>> staff.clef, staff.key
('treble', 2)
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"clef_targets": "function-clef_targets/", "clef_target_of": "function-clef_target_of/", "draw_key_signature": "function-draw_key_signature/", "draw_signature_sign": "function-draw_signature_sign/", "staffwidget": "class-staffwidget/", "staffwidgetshow_notes": "class-staffwidget/#staffwidgetshow_notes", "staffwidgetsizehint": "class-staffwidget/#staffwidgetsizehint", "staffwidgetresizeevent": "class-staffwidget/#staffwidgetresizeevent", "staffwidgethighlight_column": "class-staffwidget/#staffwidgethighlight_column", "staffwidgetset_note_color": "class-staffwidget/#staffwidgetset_note_color", "staffwidgetstaff_bottoms": "class-staffwidget/#staffwidgetstaff_bottoms", "staffwidgetpaintevent": "class-staffwidget/#staffwidgetpaintevent", "staffwidgetmousemoveevent": "class-staffwidget/#staffwidgetmousemoveevent", "staffwidgetleaveevent": "class-staffwidget/#staffwidgetleaveevent", "staffwidgethits_notation": "class-staffwidget/#staffwidgethits_notation", "keyboard_key_staff": "function-keyboard_key_staff/"}</script>
{% include api-fragments.html %}
