---
title: alto.ui.exercise_settings
parent: api
package: alto.ui
api_components: [{"title": "load_arpeggio", "url": "/api/alto.ui.exercise_settings/function-load_arpeggio/"}, {"title": "load_choice_buttons", "url": "/api/alto.ui.exercise_settings/function-load_choice_buttons/"}, {"title": "load_circle", "url": "/api/alto.ui.exercise_settings/function-load_circle/"}, {"title": "load_clef_basics", "url": "/api/alto.ui.exercise_settings/function-load_clef_basics/"}, {"title": "load_construction", "url": "/api/alto.ui.exercise_settings/function-load_construction/"}, {"title": "load_exercise_settings", "url": "/api/alto.ui.exercise_settings/function-load_exercise_settings/"}, {"title": "load_intervals", "url": "/api/alto.ui.exercise_settings/function-load_intervals/"}, {"title": "load_key_construction", "url": "/api/alto.ui.exercise_settings/function-load_key_construction/"}, {"title": "load_key_signatures", "url": "/api/alto.ui.exercise_settings/function-load_key_signatures/"}, {"title": "load_keyboard", "url": "/api/alto.ui.exercise_settings/function-load_keyboard/"}, {"title": "load_keyboard_intervals", "url": "/api/alto.ui.exercise_settings/function-load_keyboard_intervals/"}, {"title": "load_notation_terms", "url": "/api/alto.ui.exercise_settings/function-load_notation_terms/"}, {"title": "load_note_names", "url": "/api/alto.ui.exercise_settings/function-load_note_names/"}, {"title": "load_order_of_keys", "url": "/api/alto.ui.exercise_settings/function-load_order_of_keys/"}, {"title": "load_pack_options", "url": "/api/alto.ui.exercise_settings/function-load_pack_options/"}, {"title": "load_scale_construction", "url": "/api/alto.ui.exercise_settings/function-load_scale_construction/"}, {"title": "load_scale_identification", "url": "/api/alto.ui.exercise_settings/function-load_scale_identification/"}, {"title": "save_arpeggio", "url": "/api/alto.ui.exercise_settings/function-save_arpeggio/"}, {"title": "save_circle", "url": "/api/alto.ui.exercise_settings/function-save_circle/"}, {"title": "save_clef_basics", "url": "/api/alto.ui.exercise_settings/function-save_clef_basics/"}, {"title": "save_construction", "url": "/api/alto.ui.exercise_settings/function-save_construction/"}, {"title": "save_key_settings", "url": "/api/alto.ui.exercise_settings/function-save_key_settings/"}, {"title": "save_keyboard", "url": "/api/alto.ui.exercise_settings/function-save_keyboard/"}, {"title": "save_keyboard_intervals", "url": "/api/alto.ui.exercise_settings/function-save_keyboard_intervals/"}, {"title": "save_note_names", "url": "/api/alto.ui.exercise_settings/function-save_note_names/"}, {"title": "save_pack_options", "url": "/api/alto.ui.exercise_settings/function-save_pack_options/"}, {"title": "saved_notation_terms", "url": "/api/alto.ui.exercise_settings/function-saved_notation_terms/"}]
permalink: /api/alto.ui.exercise_settings/
---
{% raw %}
Load and save each exercise's settings.

## Functions

- [`load_note_names`](function-load_note_names/) — Load the saved note identification settings into the shared settings object.
- [`save_note_names`](function-save_note_names/) — Save the note identification settings.
- [`load_keyboard`](function-load_keyboard/) — Load the saved keyboard exercise settings into the shared settings object.
- [`save_keyboard`](function-save_keyboard/) — Save the keyboard exercise settings.
- [`load_keyboard_intervals`](function-load_keyboard_intervals/) — Load keyboard interval settings, ignoring invalid values and intervals that cannot fit.
- [`save_keyboard_intervals`](function-save_keyboard_intervals/) — Save the keyboard interval range and selected distances.
- [`load_construction`](function-load_construction/) — Load the saved note construction settings into the shared settings object.
- [`save_construction`](function-save_construction/) — Save the note construction settings.
- [`load_arpeggio`](function-load_arpeggio/) — Load the saved arpeggio settings into the shared settings object.
- [`save_arpeggio`](function-save_arpeggio/) — Save the arpeggio settings.
- [`load_intervals`](function-load_intervals/) — Restore the saved staff interval options, keeping valid choices and per-clef ranges.
- [`save_key_settings`](function-save_key_settings/) — Save the settings of a key exercise: its clefs, scales and key signatures, and the options of the kind of exercise it is.
- [`load_key_signatures`](function-load_key_signatures/) — Load the saved key signature identification settings into the shared settings object.
- [`load_key_construction`](function-load_key_construction/) — Load the saved key signature construction settings into the shared settings object.
- [`load_order_of_keys`](function-load_order_of_keys/) — Restore the clefs, scales, and key signatures selected for Order of Keys.
- [`load_scale_identification`](function-load_scale_identification/) — Load the saved scale identification options independently of scale construction.
- [`load_scale_construction`](function-load_scale_construction/) — Load the saved scale construction settings into the shared settings object.
- [`saved_notation_terms`](function-saved_notation_terms/) — Read the last nonempty selection of notation terms.
- [`load_notation_terms`](function-load_notation_terms/) — Restore the question type and term selection, defaulting to Answer Button and all terms.
- [`load_clef_basics`](function-load_clef_basics/) — Load the saved clef basics settings into the shared settings object.
- [`save_clef_basics`](function-save_clef_basics/) — Save clef basics settings, the form `load_clef_basics` reads.
- [`load_circle`](function-load_circle/) — Load the saved circle of fifths settings into the shared settings object.
- [`save_circle`](function-save_circle/) — Save the circle of fifths settings.
- [`load_pack_options`](function-load_pack_options/) — Restore the options learners chose for each plugin exercise that offers settings.
- [`save_pack_options`](function-save_pack_options/) — Save the options chosen for one plugin exercise.
- [`load_choice_buttons`](function-load_choice_buttons/) — Restore the independent button preferences for each multiple-choice exercise.
- [`load_exercise_settings`](function-load_exercise_settings/) — Load the saved exercise options before creating a practice or export settings panel.

<details markdown="1">
<summary>Module notes and examples</summary>

The settings themselves are plain dataclasses in `alto.settings`, one
shared object per exercise. The functions here read them
from the saved preferences when Alto starts (`load_exercise_settings`)
and write them back when a settings panel changes them.
Values saved by older versions are converted, and anything saved that is
not valid any more is ignored.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> load_note_names()
>>> settings.note_names.naming in NAMINGS
True
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"load_note_names": "function-load_note_names/", "save_note_names": "function-save_note_names/", "load_keyboard": "function-load_keyboard/", "save_keyboard": "function-save_keyboard/", "load_keyboard_intervals": "function-load_keyboard_intervals/", "save_keyboard_intervals": "function-save_keyboard_intervals/", "load_construction": "function-load_construction/", "save_construction": "function-save_construction/", "load_arpeggio": "function-load_arpeggio/", "save_arpeggio": "function-save_arpeggio/", "load_intervals": "function-load_intervals/", "save_key_settings": "function-save_key_settings/", "load_key_signatures": "function-load_key_signatures/", "load_key_construction": "function-load_key_construction/", "load_order_of_keys": "function-load_order_of_keys/", "load_scale_identification": "function-load_scale_identification/", "load_scale_construction": "function-load_scale_construction/", "saved_notation_terms": "function-saved_notation_terms/", "load_notation_terms": "function-load_notation_terms/", "load_clef_basics": "function-load_clef_basics/", "save_clef_basics": "function-save_clef_basics/", "load_circle": "function-load_circle/", "save_circle": "function-save_circle/", "load_pack_options": "function-load_pack_options/", "save_pack_options": "function-save_pack_options/", "load_choice_buttons": "function-load_choice_buttons/", "load_exercise_settings": "function-load_exercise_settings/"}</script>
{% include api-fragments.html %}
