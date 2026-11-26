---
title: alto.anki_export
parent: api
package: alto
api_components: [{"title": "DeckSelection", "url": "/api/alto.anki_export/class-deckselection/"}, {"title": "ExportControl", "url": "/api/alto.anki_export/class-exportcontrol/"}, {"title": "PlannedDeck", "url": "/api/alto.anki_export/class-planneddeck/"}, {"title": "Review", "url": "/api/alto.anki_export/class-review/"}, {"title": "deck_candidates", "url": "/api/alto.anki_export/function-deck_candidates/"}, {"title": "export_deck", "url": "/api/alto.anki_export/function-export_deck/"}, {"title": "export_decks", "url": "/api/alto.anki_export/function-export_decks/"}, {"title": "plan_deck", "url": "/api/alto.anki_export/function-plan_deck/"}, {"title": "profile_reviews", "url": "/api/alto.anki_export/function-profile_reviews/"}, {"title": "write_decks", "url": "/api/alto.anki_export/function-write_decks/"}]
permalink: /api/alto.anki_export/
---
{% raw %}
Write portable Anki decks from Alto questions and optional calendar
review dates.

## Classes

- [`Review`](class-review/) — One practiced example and its calendar schedule in the exporting profile.
- [`DeckSelection`](class-deckselection/) — One exercise deck and its optional review schedules.
- [`PlannedDeck`](class-planneddeck/) — Distinct questions and their stable export identities for one exercise.
- [`ExportControl`](class-exportcontrol/) — Coordinate a cancellation decision with the final replacement of the destination.

## Functions

- [`profile_reviews`](function-profile_reviews/) — Read this profile's graded calendar cards in due order.
- [`deck_candidates`](function-deck_candidates/) — Visit eligible scheduled examples before generating additional questions.
- [`export_deck`](function-export_deck/) — Write a deck and replace the destination only after the package is complete.
- [`plan_deck`](function-plan_deck/) — Select the exact cards to count in the summary and write to the package.
- [`export_decks`](function-export_decks/) — Save the selected exercise decks together in one Anki package.
- [`write_decks`](function-write_decks/) — Write the cards from a completed export plan into a single package.
{% endraw %}

<script type="application/json" id="api-fragments">{"review": "class-review/", "profile_reviews": "function-profile_reviews/", "deck_candidates": "function-deck_candidates/", "export_deck": "function-export_deck/", "deckselection": "class-deckselection/", "planneddeck": "class-planneddeck/", "plan_deck": "function-plan_deck/", "export_decks": "function-export_decks/", "exportcontrol": "class-exportcontrol/", "exportcontrolconfirm_cancel": "class-exportcontrol/#exportcontrolconfirm_cancel", "exportcontrolcheck": "class-exportcontrol/#exportcontrolcheck", "exportcontrolpublish": "class-exportcontrol/#exportcontrolpublish", "write_decks": "function-write_decks/"}</script>
{% include api-fragments.html %}
