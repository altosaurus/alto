---
title: alto.audio
parent: api
package: alto
api_components: [{"title": "Instrument", "url": "/api/alto.audio/class-instrument/"}, {"title": "Sounds", "url": "/api/alto.audio/class-sounds/"}, {"title": "instrument_groups", "url": "/api/alto.audio/function-instrument_groups/"}, {"title": "metronome_preview_pcm", "url": "/api/alto.audio/function-metronome_preview_pcm/"}, {"title": "read_wav", "url": "/api/alto.audio/function-read_wav/"}, {"title": "shift_pitch", "url": "/api/alto.audio/function-shift_pitch/"}, {"title": "synth_piano", "url": "/api/alto.audio/function-synth_piano/"}, {"title": "to_wav_bytes", "url": "/api/alto.audio/function-to_wav_bytes/"}, {"title": "write_file_atomically", "url": "/api/alto.audio/function-write_file_atomically/"}]
permalink: /api/alto.audio/
---
{% raw %}
Note playback: recorded instrument samples (University of Iowa), with
pitch-shifting for missing notes.

## Classes

- [`Instrument`](class-instrument/) — An instrument that notes can be played on, and where its recordings are.
- [`Sounds`](class-sounds/) — A lazy cache of notes played through `QSoundEffect`, in the chosen instrument.

## Functions

- [`synth_piano`](function-synth_piano/) — Synthesize a piano note, for notes outside the recorded range.
- [`instrument_groups`](function-instrument_groups/) — Return the instruments as they are listed for choosing.
- [`read_wav`](function-read_wav/) — Read a mono 16-bit WAV file.
- [`shift_pitch`](function-shift_pitch/) — Change the pitch of samples by resampling them.
- [`to_wav_bytes`](function-to_wav_bytes/) — Encode samples as a mono 16-bit WAV file in memory.
- [`write_file_atomically`](function-write_file_atomically/) — Write a file so that nothing ever reads it half written, even another copy of Alto writing the same file.
- [`metronome_preview_pcm`](function-metronome_preview_pcm/) — Return the four beats used for playback and the spectrum display.

<details markdown="1">
<summary>Module notes and examples</summary>

`Sounds` plays notes through Qt's `QSoundEffect`, one effect per note,
created the first time it is needed. A note with
no recording is made by shifting the nearest recording (or, for the
piano outside its sampled range, by synthesis).
Instrument previews render the phrase as one cached clip to preserve
its rhythm from the first playback.
The module-level `sounds` is the one the interface uses.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [inst.label for inst in INSTRUMENTS][:2]
['Piano', 'Flute']
>>> Sounds().instrument
'piano'
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"synth_piano": "function-synth_piano/", "instrument": "class-instrument/", "instrumentkind_name": "class-instrument/#instrumentkind_name", "instrumentpicker_group": "class-instrument/#instrumentpicker_group", "instrumentplayback_volume": "class-instrument/#instrumentplayback_volume", "instrument_groups": "function-instrument_groups/", "read_wav": "function-read_wav/", "shift_pitch": "function-shift_pitch/", "to_wav_bytes": "function-to_wav_bytes/", "write_file_atomically": "function-write_file_atomically/", "metronome_preview_pcm": "function-metronome_preview_pcm/", "sounds": "class-sounds/", "soundsrecordings": "class-sounds/#soundsrecordings", "soundsunrecorded": "class-sounds/#soundsunrecorded", "soundsprepare": "class-sounds/#soundsprepare", "soundsnote_duration_ms": "class-sounds/#soundsnote_duration_ms", "soundsplay_midi": "class-sounds/#soundsplay_midi", "soundsplay_metronome_click": "class-sounds/#soundsplay_metronome_click", "soundspreview_metronome": "class-sounds/#soundspreview_metronome", "soundsstop_metronome_preview": "class-sounds/#soundsstop_metronome_preview", "soundsstop_all": "class-sounds/#soundsstop_all", "soundspreview": "class-sounds/#soundspreview", "soundsplay_rhythm": "class-sounds/#soundsplay_rhythm", "soundsplay_notes": "class-sounds/#soundsplay_notes", "soundsstop_sample": "class-sounds/#soundsstop_sample", "soundsplay_sample": "class-sounds/#soundsplay_sample", "soundsplay_correct": "class-sounds/#soundsplay_correct"}</script>
{% include api-fragments.html %}
