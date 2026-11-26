---
title: alto.settings
parent: api
package: alto
api_components: [{"title": "ArpeggioSettings", "url": "/api/alto.settings/class-arpeggiosettings/"}, {"title": "CircleSettings", "url": "/api/alto.settings/class-circlesettings/"}, {"title": "ClefBasicsSettings", "url": "/api/alto.settings/class-clefbasicssettings/"}, {"title": "ClefChoice", "url": "/api/alto.settings/class-clefchoice/"}, {"title": "ConstructionSettings", "url": "/api/alto.settings/class-constructionsettings/"}, {"title": "IntervalSettings", "url": "/api/alto.settings/class-intervalsettings/"}, {"title": "KeyChoice", "url": "/api/alto.settings/class-keychoice/"}, {"title": "KeyConstructionSettings", "url": "/api/alto.settings/class-keyconstructionsettings/"}, {"title": "KeySignatureSettings", "url": "/api/alto.settings/class-keysignaturesettings/"}, {"title": "KeyboardIntervalSettings", "url": "/api/alto.settings/class-keyboardintervalsettings/"}, {"title": "KeyboardSettings", "url": "/api/alto.settings/class-keyboardsettings/"}, {"title": "NotationSettings", "url": "/api/alto.settings/class-notationsettings/"}, {"title": "NoteNameSettings", "url": "/api/alto.settings/class-notenamesettings/"}, {"title": "OrderOfKeysSettings", "url": "/api/alto.settings/class-orderofkeyssettings/"}, {"title": "PackExerciseSettings", "url": "/api/alto.settings/class-packexercisesettings/"}, {"title": "ScaleConstructionSettings", "url": "/api/alto.settings/class-scaleconstructionsettings/"}, {"title": "ScaleIdentificationSettings", "url": "/api/alto.settings/class-scaleidentificationsettings/"}, {"title": "StaffRangeSettings", "url": "/api/alto.settings/class-staffrangesettings/"}, {"title": "beat_note", "url": "/api/alto.settings/function-beat_note/"}, {"title": "diatonic_name", "url": "/api/alto.settings/function-diatonic_name/"}, {"title": "key_name", "url": "/api/alto.settings/function-key_name/"}, {"title": "keyboard_interval_name", "url": "/api/alto.settings/function-keyboard_interval_name/"}, {"title": "spell", "url": "/api/alto.settings/function-spell/"}]
permalink: /api/alto.settings/
---
{% raw %}
User settings. Pure Python (no Qt); persistence lives in
ui/exercise_settings.py.

## Classes

- [`ClefChoice`](class-clefchoice/) — Settings with a set of chosen clefs, which are always used in the same order.
- [`KeyChoice`](class-keychoice/) — Settings with a set of chosen key signatures.
- [`StaffRangeSettings`](class-staffrangesettings/) — Selected clefs and inclusive pitch limits for each staff.
- [`NoteNameSettings`](class-notenamesettings/) — The settings of the note identification exercise.
- [`PackExerciseSettings`](class-packexercisesettings/) — The options a plugin's exercise offers the learner, such as its range and whether to ask accidentals.
- [`IntervalSettings`](class-intervalsettings/) — Staff signatures, presentations, answer format and spelled intervals for Interval Identification.
- [`KeyboardSettings`](class-keyboardsettings/) — The settings of the keyboard identification exercise.
- [`KeyboardIntervalSettings`](class-keyboardintervalsettings/) — The keyboard range and interval distances used for keyboard interval identification.
- [`ConstructionSettings`](class-constructionsettings/) — The settings of the note construction exercise.
- [`ArpeggioSettings`](class-arpeggiosettings/) — The settings of the arpeggio identification exercise.
- [`KeySignatureSettings`](class-keysignaturesettings/) — The settings of the key signature identification exercise.
- [`OrderOfKeysSettings`](class-orderofkeyssettings/) — Choose the starting signs for writing a key signature.
- [`KeyConstructionSettings`](class-keyconstructionsettings/) — The settings of the key signature construction exercise: the same choices as key signature identification.
- [`ScaleIdentificationSettings`](class-scaleidentificationsettings/) — Choose the clefs, scale types and independent staff and scale key signatures for identification.
- [`ScaleConstructionSettings`](class-scaleconstructionsettings/) — The settings of the scale construction exercise: the same choices as key signature identification.
- [`ClefBasicsSettings`](class-clefbasicssettings/) — The settings of the clef basics exercise: what kind of question is asked, and which clefs.
- [`NotationSettings`](class-notationsettings/) — Terms eligible to be highlighted in Notation Identification.
- [`CircleSettings`](class-circlesettings/) — The settings of the circle of fifths exercise.

## Functions

- [`spell`](function-spell/) — Return a note name in the chosen naming system, optionally including its octave.
- [`diatonic_name`](function-diatonic_name/) — Return the name and octave of the natural note on a staff step.
- [`beat_note`](function-beat_note/) — Read a rhythm token's written value, tuplet count, and duration.
- [`key_name`](function-key_name/) — Return the name of a MIDI note with its octave, black keys as sharps.
- [`keyboard_interval_name`](function-keyboard_interval_name/) — Name a keyboard interval by its distance, including compound intervals.

<details markdown="1">
<summary>Module notes and examples</summary>

Each exercise with settings has a small dataclass here
(`NoteNameSettings`, `KeyboardSettings` and so on) and one shared
instance of it (`note_names`, `keyboard` ...) that the exercise and its
settings panel both read and write.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> NoteNameSettings().active_clefs()
['treble', 'bass']
>>> spell(Note.parse("F#4"))
'F♯'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"spell": "function-spell/", "diatonic_name": "function-diatonic_name/", "clefchoice": "class-clefchoice/", "clefchoiceactive_clefs": "class-clefchoice/#clefchoiceactive_clefs", "keychoice": "class-keychoice/", "keychoiceactive_keys": "class-keychoice/#keychoiceactive_keys", "staffrangesettings": "class-staffrangesettings/", "staffrangesettingsactive_values": "class-staffrangesettings/#staffrangesettingsactive_values", "staffrangesettingsrange_for": "class-staffrangesettings/#staffrangesettingsrange_for", "notenamesettings": "class-notenamesettings/", "notenamesettingsactive_keys": "class-notenamesettings/#notenamesettingsactive_keys", "packexercisesettings": "class-packexercisesettings/", "intervalsettings": "class-intervalsettings/", "intervalsettingsstaff_span": "class-intervalsettings/#intervalsettingsstaff_span", "beat_note": "function-beat_note/", "key_name": "function-key_name/", "keyboardsettings": "class-keyboardsettings/", "keyboard_interval_name": "function-keyboard_interval_name/", "keyboardintervalsettings": "class-keyboardintervalsettings/", "keyboardintervalsettingsanswer_button_limit": "class-keyboardintervalsettings/#keyboardintervalsettingsanswer_button_limit", "keyboardintervalsettingsbounds": "class-keyboardintervalsettings/#keyboardintervalsettingsbounds", "keyboardintervalsettingsactive_intervals": "class-keyboardintervalsettings/#keyboardintervalsettingsactive_intervals", "constructionsettings": "class-constructionsettings/", "arpeggiosettings": "class-arpeggiosettings/", "arpeggiosettingsactive_types": "class-arpeggiosettings/#arpeggiosettingsactive_types", "arpeggiosettingsactive_inversions": "class-arpeggiosettings/#arpeggiosettingsactive_inversions", "arpeggiosettingsinversions_for": "class-arpeggiosettings/#arpeggiosettingsinversions_for", "keysignaturesettings": "class-keysignaturesettings/", "keysignaturesettingsactive_modes": "class-keysignaturesettings/#keysignaturesettingsactive_modes", "orderofkeyssettings": "class-orderofkeyssettings/", "orderofkeyssettingsavailable_starts": "class-orderofkeyssettings/#orderofkeyssettingsavailable_starts", "keyconstructionsettings": "class-keyconstructionsettings/", "scaleidentificationsettings": "class-scaleidentificationsettings/", "scaleidentificationsettingsactive_staff_keys": "class-scaleidentificationsettings/#scaleidentificationsettingsactive_staff_keys", "scaleconstructionsettings": "class-scaleconstructionsettings/", "scaleconstructionsettingsactive_staff_keys": "class-scaleconstructionsettings/#scaleconstructionsettingsactive_staff_keys", "clefbasicssettings": "class-clefbasicssettings/", "clefbasicssettingsactive_type": "class-clefbasicssettings/#clefbasicssettingsactive_type", "clefbasicssettingsanswer_clefs": "class-clefbasicssettings/#clefbasicssettingsanswer_clefs", "notationsettings": "class-notationsettings/", "circlesettings": "class-circlesettings/", "circlesettingsactive_questions": "class-circlesettings/#circlesettingsactive_questions", "circlesettingsactive_scheme": "class-circlesettings/#circlesettingsactive_scheme"}</script>
{% include api-fragments.html %}
