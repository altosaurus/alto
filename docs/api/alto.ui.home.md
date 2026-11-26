---
title: alto.ui.home
parent: api
package: alto.ui
api_components: [{"title": "ExerciseCard", "url": "/api/alto.ui.home/class-exercisecard/"}, {"title": "HomePage", "url": "/api/alto.ui.home/class-homepage/"}, {"title": "TileCard", "url": "/api/alto.ui.home/class-tilecard/"}, {"title": "category_tree", "url": "/api/alto.ui.home/function-category_tree/"}, {"title": "exercise_icon", "url": "/api/alto.ui.home/function-exercise_icon/"}, {"title": "lesson_card", "url": "/api/alto.ui.home/function-lesson_card/"}, {"title": "lesson_icon", "url": "/api/alto.ui.home/function-lesson_icon/"}]
permalink: /api/alto.ui.home/
---
{% raw %}
The start screen: a card for every exercise, or for every lesson, in
rows.

## Classes

- [`TileCard`](class-tilecard/) — A big button: an icon on top, then a category, a name and a short description, and optionally a lesson's progress.
- [`ExerciseCard`](class-exercisecard/) — The card of an exercise: its icon on top, then its category, name and a one-line description.
- [`HomePage`](class-homepage/) — The start screen: a row of exercise buttons for each category.

## Functions

- [`category_tree`](function-category_tree/) — Build a navigation tree with themed checkboxes and right-aligned expansion arrows.
- [`exercise_icon`](function-exercise_icon/) — Find the icon for an exercise: the one its plugin supplies, or Alto's own.
- [`lesson_icon`](function-lesson_icon/) — Use the lesson's own icon when present, falling back to its primary exercise's icon.
- [`lesson_card`](function-lesson_card/) — Make the card of a lesson: the icon of the exercise that practices the same topic, and a bar for how far through it you are.

<details markdown="1">
<summary>Module notes and examples</summary>

A switch at the top chooses between the exercises and the lessons.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.exercises import REGISTRY
>>> page = HomePage(REGISTRY)
>>> len(page.cards) == len(REGISTRY)
True
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"category_tree": "function-category_tree/", "tilecard": "class-tilecard/", "tilecardchangeevent": "class-tilecard/#tilecardchangeevent", "exercise_icon": "function-exercise_icon/", "lesson_icon": "function-lesson_icon/", "exercisecard": "class-exercisecard/", "exercisecardset_counts": "class-exercisecard/#exercisecardset_counts", "lesson_card": "function-lesson_card/", "homepage": "class-homepage/", "homepageset_search": "class-homepage/#homepageset_search", "homepagematches_filter": "class-homepage/#homepagematches_filter", "homepageeventfilter": "class-homepage/#homepageeventfilter", "homepageset_filter_available": "class-homepage/#homepageset_filter_available", "homepagerestore_tile_filters": "class-homepage/#homepagerestore_tile_filters", "homepageset_category": "class-homepage/#homepageset_category", "homepageset_mode": "class-homepage/#homepageset_mode", "homepagepage_changed": "class-homepage/#homepagepage_changed", "homepagerefresh_counts": "class-homepage/#homepagerefresh_counts", "homepageshowevent": "class-homepage/#homepageshowevent", "homepageresizeevent": "class-homepage/#homepageresizeevent"}</script>
{% include api-fragments.html %}
