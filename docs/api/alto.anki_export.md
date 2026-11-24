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

One practiced example and its calendar schedule in the exporting
profile.

## profile_reviews

```python
def profile_reviews(learner: Learner) -> dict[str, list[Review]]
```

Read this profile's graded calendar cards in due order.

**Returns**

- *dict of str to list of Review*: Scheduled questions grouped by exercise class name.

## deck_candidates

```python
def deck_candidates(
    exercise: Exercise,
    *,
    reviews: Sequence[Review],
) -> Iterator[tuple[Question, Review | None]]
```

Visit eligible scheduled examples before generating additional
questions.

**Yields**

- *tuple of Question and optional Review*: Question to render and its matching schedule, if available.

## export_deck

```python
def export_deck(
    path: Path,
    *,
    exercise: Exercise,
    reviews: Sequence[Review],
    render: Callable[[Question, Path], list[str]],
) -> int
```

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

```python
DeckSelection(
    exercise: Exercise,
    reviews: Sequence[Review],
)
```

One exercise deck and its optional review schedules.

## PlannedDeck

```python
PlannedDeck(
    exercise: Exercise,
    cards: list[tuple[str, Question, Review | None]],
)
```

Distinct questions and their stable export identities for one
exercise.

## plan_deck

```python
def plan_deck(selection: DeckSelection) -> PlannedDeck
```

Select the exact cards to count in the summary and write to the
package.

**Returns**

- *PlannedDeck*: Eligible cards in export order, with reviewed cards first.

## export_decks

```python
def export_decks(
    path: Path,
    *,
    selections: Sequence[DeckSelection],
    render: Callable[[Question, Path, Exercise], list[str]],
    progress: Callable[[str, int, int], None] | None = None,
) -> int
```

Save the selected exercise decks together in one Anki package.

**Parameters**

- `path` (*Path*): Destination replaced once all selected decks and their media are ready.
- `selections` (*sequence of DeckSelection*): Exercises to export and their optional schedules.
- `render` (*callable*): Renders the fields and writes the media for one exercise question.
- `progress` (*callable, optional*): Receives the current operation, completed work, and a fixed total for the whole package.

**Returns**

- *int*: Total cards written across all decks.

## ExportControl

```python
ExportControl()
```

Coordinate a cancellation decision with the final replacement of the
destination.

**Constructor**

Start with a pending export and an untouched destination.

### ExportControl.confirm_cancel

```python
def confirm_cancel(confirm: Callable[[], bool]) -> bool
```

Reserve the destination until the user decides whether to
cancel.

**Returns**

- *bool*: True if cancellation was confirmed before the package was saved.

### ExportControl.check

```python
def check() -> None
```

Stop work and unwind temporary files after confirmed
cancellation.

**Raises**

- *CancelledError*: When the user has confirmed cancellation.

### ExportControl.publish

```python
def publish(
    package: Path,
    *,
    destination: Path,
) -> None
```

Replace the destination only while cancellation is excluded.

## write_decks

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

Write the cards from a completed export plan into a single package.

**Returns**

- *int*: Number of cards written across the selected decks.
{% endraw %}
