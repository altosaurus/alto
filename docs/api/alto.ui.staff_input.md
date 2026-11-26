---
title: alto.ui.staff_input
parent: api
package: alto.ui
api_components: [{"title": "ClefInput", "url": "/api/alto.ui.staff_input/class-clefinput/"}, {"title": "ScaleInput", "url": "/api/alto.ui.staff_input/class-scaleinput/"}, {"title": "SignatureInput", "url": "/api/alto.ui.staff_input/class-signatureinput/"}, {"title": "StaffInput", "url": "/api/alto.ui.staff_input/class-staffinput/"}]
permalink: /api/alto.ui.staff_input/
---
{% raw %}
The staffs you click to place notes or a clef.

## Classes

- [`StaffInput`](class-staffinput/) — A single staff you click to place a note, or place a note on with the keyboard.
- [`ScaleInput`](class-scaleinput/) — A staff you click to place the notes of a scale one after another, left to right, and then, if asked, its steps.
- [`SignatureInput`](class-signatureinput/) — Place accidentals in consecutive key-signature slots immediately after the clef.
- [`ClefInput`](class-clefinput/) — A blank staff on which you put a clef symbol: choose the G, C or F clef, then click where it goes.

<details markdown="1">
<summary>Module notes and examples</summary>

One note for the note construction exercise, a row of them for scale
construction, and a clef for the clef exercise.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> staff = StaffInput()
>>> staff.accidental is None and not staff.locked
True
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"staffinput": "class-staffinput/", "staffinputreset": "class-staffinput/#staffinputreset", "staffinputnote_at": "class-staffinput/#staffinputnote_at", "staffinputnote_for": "class-staffinput/#staffinputnote_for", "staffinputcaret_start": "class-staffinput/#staffinputcaret_start", "staffinputcaret_note": "class-staffinput/#staffinputcaret_note", "staffinputmove_cursor": "class-staffinput/#staffinputmove_cursor", "staffinputjump_to_letter": "class-staffinput/#staffinputjump_to_letter", "staffinputplace_caret": "class-staffinput/#staffinputplace_caret", "staffinputshow_note": "class-staffinput/#staffinputshow_note", "staffinputrefresh_preview": "class-staffinput/#staffinputrefresh_preview", "staffinputmousemoveevent": "class-staffinput/#staffinputmousemoveevent", "staffinputleaveevent": "class-staffinput/#staffinputleaveevent", "staffinputmousepressevent": "class-staffinput/#staffinputmousepressevent", "scaleinput": "class-scaleinput/", "scaleinputreset_scale": "class-scaleinput/#scaleinputreset_scale", "scaleinputcomplete": "class-scaleinput/#scaleinputcomplete", "scaleinputplacing_steps": "class-scaleinput/#scaleinputplacing_steps", "scaleinputdone": "class-scaleinput/#scaleinputdone", "scaleinputshow_note": "class-scaleinput/#scaleinputshow_note", "scaleinputset_pending_step": "class-scaleinput/#scaleinputset_pending_step", "scaleinputtoggle_step": "class-scaleinput/#scaleinputtoggle_step", "scaleinputundo": "class-scaleinput/#scaleinputundo", "scaleinputwheelevent": "class-scaleinput/#scaleinputwheelevent", "scaleinputcaret_start": "class-scaleinput/#scaleinputcaret_start", "scaleinputplace_next": "class-scaleinput/#scaleinputplace_next", "scaleinputplace_caret": "class-scaleinput/#scaleinputplace_caret", "scaleinputmousepressevent": "class-scaleinput/#scaleinputmousepressevent", "signatureinput": "class-signatureinput/", "signatureinputreset_signature": "class-signatureinput/#signatureinputreset_signature", "signatureinputentered_signature": "class-signatureinput/#signatureinputentered_signature", "signatureinputpaintevent": "class-signatureinput/#signatureinputpaintevent", "clefinput": "class-clefinput/", "clefinputreset": "class-clefinput/#clefinputreset", "clefinputselect": "class-clefinput/#clefinputselect", "clefinputstep_symbol": "class-clefinput/#clefinputstep_symbol", "clefinputstep_at": "class-clefinput/#clefinputstep_at", "clefinputmove_caret": "class-clefinput/#clefinputmove_caret", "clefinputplace": "class-clefinput/#clefinputplace", "clefinputplace_caret": "class-clefinput/#clefinputplace_caret", "clefinputclear_placed": "class-clefinput/#clefinputclear_placed", "clefinputset_clef_color": "class-clefinput/#clefinputset_clef_color", "clefinputmousemoveevent": "class-clefinput/#clefinputmousemoveevent", "clefinputleaveevent": "class-clefinput/#clefinputleaveevent", "clefinputmousepressevent": "class-clefinput/#clefinputmousepressevent", "clefinputwheelevent": "class-clefinput/#clefinputwheelevent", "clefinputpaintevent": "class-clefinput/#clefinputpaintevent"}</script>
{% include api-fragments.html %}
