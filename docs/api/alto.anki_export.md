---
title: alto.anki_export
parent: api
package: alto
permalink: /api/alto.anki_export/
---
{% raw %}
Write portable Anki decks from Alto questions and optional calendar
review dates.

## Review

<div class="api-signature" markdown="1">

```python
Review(
    item_key: str,
    signature: str,
    payload: str,
    scheduler: str,
    due: float,
    state: str,
    seen: int,
)
```

{% endraw %}{% include api-source.html name="Review" line=60 %}{% raw %}

</div>

One practiced example and its calendar schedule in the exporting
profile.

## profile_reviews

<div class="api-signature" markdown="1">

```python
def profile_reviews(learner: Learner) -> dict[str, list[Review]]
```

{% endraw %}{% include api-source.html name="profile_reviews" line=75 %}{% raw %}

</div>

Read this profile's graded calendar cards in due order.

**Returns**

- *dict of str to list of Review*: Scheduled questions grouped by exercise class name.

## deck_candidates

<div class="api-signature" markdown="1">

```python
def deck_candidates(
    exercise: Exercise,
    *,
    reviews: Sequence[Review],
) -> Iterator[tuple[Question, Review | None]]
```

{% endraw %}{% include api-source.html name="deck_candidates" line=102 %}{% raw %}

</div>

Visit eligible scheduled examples before generating additional
questions.

**Yields**

- *tuple of Question and optional Review*: Question to render and its matching schedule, if available.

## export_deck

<div class="api-signature" markdown="1">

```python
def export_deck(
    path: Path,
    *,
    exercise: Exercise,
    reviews: Sequence[Review],
    render: Callable[[Question, Path], list[str]],
) -> int
```

{% endraw %}{% include api-source.html name="export_deck" line=187 %}{% raw %}

</div>

Write a deck and replace the destination only after the package is
complete.

**Parameters**

- `path` (*Path*): Destination package.
- `exercise` (*Exercise*): Source of questions under the current export settings.
- `reviews` (*sequence of Review*): Eligible schedules to prioritize and transfer when requested.
- `render` (*callable*): Produces Anki fields and writes their PNG illustrations in the working directory.

**Returns**

- *int*: Number of exported cards. An empty selection leaves the destination untouched.

## DeckSelection

<div class="api-signature" markdown="1">

```python
DeckSelection(
    exercise: Exercise,
    reviews: Sequence[Review],
)
```

{% endraw %}{% include api-source.html name="DeckSelection" line=224 %}{% raw %}

</div>

One exercise deck and its optional review schedules.

## PlannedDeck

<div class="api-signature" markdown="1">

```python
PlannedDeck(
    exercise: Exercise,
    cards: list[tuple[str, Question, Review | None]],
)
```

{% endraw %}{% include api-source.html name="PlannedDeck" line=232 %}{% raw %}

</div>

Distinct questions and their stable export identities for one
exercise.

## plan_deck

<div class="api-signature" markdown="1">

```python
def plan_deck(selection: DeckSelection) -> PlannedDeck
```

{% endraw %}{% include api-source.html name="plan_deck" line=242 %}{% raw %}

</div>

Select the exact cards to count in the summary and write to the
package.

**Returns**

- *PlannedDeck*: Eligible cards in export order, with reviewed cards first.

## export_decks

<div class="api-signature" markdown="1">

```python
def export_decks(
    path: Path,
    *,
    selections: Sequence[DeckSelection],
    render: Callable[[Question, Path, Exercise], list[str]],
    progress: Callable[[str, int, int], None] | None = None,
) -> int
```

{% endraw %}{% include api-source.html name="export_decks" line=274 %}{% raw %}

</div>

Save the selected exercise decks together in one Anki package.

**Parameters**

- `path` (*Path*): Destination replaced once all selected decks and their media are ready.
- `selections` (*sequence of DeckSelection*): Exercises to export and their optional schedules.
- `render` (*callable*): Renders the fields and writes the media for one exercise question.
- `progress` (*callable, optional*): Receives the current operation, completed work, and a fixed total for the whole package.

**Returns**

- *int*: Total cards written across all decks.

## ExportControl

<div class="api-signature" markdown="1">

```python
ExportControl()
```

{% endraw %}{% include api-source.html name="ExportControl" line=311 %}{% raw %}

</div>

Coordinate a cancellation decision with the final replacement of the
destination.

**Constructor**

Start with a pending export and an untouched destination.

### ExportControl.confirm_cancel

<div class="api-signature" markdown="1">

```python
def confirm_cancel(confirm: Callable[[], bool]) -> bool
```

{% endraw %}{% include api-source.html name="ExportControl.confirm_cancel" line=323 %}{% raw %}

</div>

Reserve the destination until the user decides whether to
cancel.

**Returns**

- *bool*: True if cancellation was confirmed before the package was saved.

### ExportControl.check

<div class="api-signature" markdown="1">

```python
def check() -> None
```

{% endraw %}{% include api-source.html name="ExportControl.check" line=340 %}{% raw %}

</div>

Stop work and unwind temporary files after confirmed
cancellation.

**Raises**

- *CancelledError*: When the user has confirmed cancellation.

### ExportControl.publish

<div class="api-signature" markdown="1">

```python
def publish(
    package: Path,
    *,
    destination: Path,
) -> None
```

{% endraw %}{% include api-source.html name="ExportControl.publish" line=353 %}{% raw %}

</div>

Replace the destination only while cancellation is excluded.

## write_decks

<div class="api-signature" markdown="1">

```python
def write_decks(
    path: Path,
    *,
    plans: Sequence[PlannedDeck],
    render: Callable[[Question, Path, Exercise], list[str]],
    progress: Callable[[str, int, int], None] | None = None,
    control: ExportControl | None = None,
    deck_progress: Callable[[int, bool], None] | None = None,
) -> int
```

{% endraw %}{% include api-source.html name="write_decks" line=363 %}{% raw %}

</div>

Write the cards from a completed export plan into a single package.

**Returns**

- *int*: Number of cards written across the selected decks.
{% endraw %}
