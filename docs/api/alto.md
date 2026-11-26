---
title: alto
parent: api
package: alto
api_package: true
permalink: /api/alto/
---

Alto: a music theory trainer that learns what you find hard and asks it more often.

## Subpackages

- [alto.exercises](../alto.exercises/)
- [alto.learning](../alto.learning/)
- [alto.lessons](../alto.lessons/)
- [alto.theory](../alto.theory/)
- [alto.ui](../alto.ui/)

## Modules

| Module | What it is |
|---|---|
| [alto.anki_export](../alto.anki_export/) | Write portable Anki decks from Alto questions and optional calendar review dates. |
| [alto.audio](../alto.audio/) | Note playback: recorded instrument samples (University of Iowa), with pitch-shifting for missing notes. |
| [alto.circle_schemes](../alto.circle_schemes/) | The color schemes of the circle of fifths: the presets, and the schemes a user makes. |
| [alto.instrument_info](../alto.instrument_info/) | What is known about each instrument's recordings, for the summary shown in the instrument settings. |
| [alto.instrument_packs](../alto.instrument_packs/) | Media and fingerboard geometry supplied by third-party instrument packs. |
| [alto.location](../alto.location/) | Where Alto keeps its practice history and its settings, and how to keep them somewhere else with `ALTO_HOME`. |
| [alto.notation_excerpts](../alto.notation_excerpts/) | Public-domain piano excerpts available for offline notation practice. |
| [alto.notation_terms](../alto.notation_terms/) | Notation Identification terms, grouped by subject with their score placement and SMuFL code points. |
| [alto.plugin_registry](../alto.plugin_registry/) | Install registered instrument packs from the latest release in their public GitHub repositories. |
| [alto.selfupdate](../alto.selfupdate/) | Replacing a packaged copy of Alto with a newer release: whether it can, getting the update, checking it, and handing over. |
| [alto.settings](../alto.settings/) | User settings. Pure Python (no Qt); persistence lives in ui/exercise_settings.py. |
| [alto.terms](../alto.terms/) | Glossary entries that an installed plugin supplies, kept apart from the built-in ones. |
| [alto.updates](../alto.updates/) | What kind of copy of Alto is running, how it can be updated, and the commands and answers that checking involves. |
