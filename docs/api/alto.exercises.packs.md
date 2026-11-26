---
title: alto.exercises.packs
parent: api
package: alto.exercises
api_components: [{"title": "InstalledPlugin", "url": "/api/alto.exercises.packs/class-installedplugin/"}, {"title": "PackExercise", "url": "/api/alto.exercises.packs/class-packexercise/"}, {"title": "install_pack", "url": "/api/alto.exercises.packs/function-install_pack/"}, {"title": "installed_pack_info", "url": "/api/alto.exercises.packs/function-installed_pack_info/"}, {"title": "installed_plugins", "url": "/api/alto.exercises.packs/function-installed_plugins/"}, {"title": "load_packs", "url": "/api/alto.exercises.packs/function-load_packs/"}, {"title": "pack_manifests", "url": "/api/alto.exercises.packs/function-pack_manifests/"}, {"title": "read_controls", "url": "/api/alto.exercises.packs/function-read_controls/"}, {"title": "read_pack", "url": "/api/alto.exercises.packs/function-read_pack/"}]
permalink: /api/alto.exercises.packs/
---
{% raw %}
Load third-party instrument packs from ZIP archives and authoring
folders.

## Classes

- [`PackExercise`](class-packexercise/) — A finite set of illustrated multiple-choice cards declared by an instrument pack.
- [`InstalledPlugin`](class-installedplugin/) — One pack in the plugins folder, as listed for removal.

## Functions

- [`read_controls`](function-read_controls/) — Validate the settings a pack offers for one of its exercises.
- [`read_pack`](function-read_pack/) — Read and validate every exercise before making any of them available.
- [`pack_manifests`](function-pack_manifests/) — Find each installed ZIP or folder manifest, including packs that failed validation.
- [`installed_pack_info`](function-installed_pack_info/) — Read a pack's manifest for display or duplicate detection without loading its media.
- [`installed_plugins`](function-installed_plugins/) — List the packs in the plugins folder, including damaged ones, so each can be removed.
- [`install_pack`](function-install_pack/) — Validate a copy of the selected ZIP and install it for the next startup.
- [`load_packs`](function-load_packs/) — Register valid packs and return readable errors for any packs that were skipped.
{% endraw %}

<script type="application/json" id="api-fragments">{"packexercise": "class-packexercise/", "packexerciseoptions": "class-packexercise/#packexerciseoptions", "packexerciseis_keyboard": "class-packexercise/#packexerciseis_keyboard", "packexercisechosen_keys": "class-packexercise/#packexercisechosen_keys", "packexercisechosen_span": "class-packexercise/#packexercisechosen_span", "packexercisechosen_intervals": "class-packexercise/#packexercisechosen_intervals", "packexercisechosen_manuals": "class-packexercise/#packexercisechosen_manuals", "packexerciseactive_cards": "class-packexercise/#packexerciseactive_cards", "packexercisesound_instrument": "class-packexercise/#packexercisesound_instrument", "packexercisesound_options": "class-packexercise/#packexercisesound_options", "packexercisepractice_signature": "class-packexercise/#packexercisepractice_signature", "packexerciserefresh": "class-packexercise/#packexerciserefresh", "packexercisemake_question": "class-packexercise/#packexercisemake_question", "packexercisedaily_candidates": "class-packexercise/#packexercisedaily_candidates", "packexercisecard_count": "class-packexercise/#packexercisecard_count", "read_controls": "function-read_controls/", "read_pack": "function-read_pack/", "pack_manifests": "function-pack_manifests/", "installed_pack_info": "function-installed_pack_info/", "installedplugin": "class-installedplugin/", "installed_plugins": "function-installed_plugins/", "install_pack": "function-install_pack/", "load_packs": "function-load_packs/"}</script>
{% include api-fragments.html %}
