---
title: alto.learning.grading
parent: api
package: alto.learning
permalink: /api/alto.learning.grading/
---
{% raw %}
Answer-button intervals for Anki's default SM-2 and FSRS-6 deck
settings.

## Sm2State

```python
Sm2State(
    repetitions: int = 0,
    interval: int = 0,
    ease: float = 2.5,
    phase: str = 'learning',
    step: int = 0,
    delay: int = 0,
)
```

SM-2 learning step, review history, and actual delay for the current
presentation.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Sm2State.read(None).phase
'learning'
```

### Sm2State.read

```python
@classmethod
def read(previous: str | None) -> Sm2State
```

Read a button-graded or original automatic SM-2 schedule.

**Parameters**

- `previous` (*str or None*): Serialized schedule, if this card has been graded.

**Returns**

- *Sm2State*: Card state with the existing interval and ease preserved.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> Sm2State.read("[2, 6, 2.5]").phase
'review'
```

## inherited_state

```python
def inherited_state(
    key: str,
    *,
    source: str,
    state: str,
    due: float,
    rating: Rating,
) -> str
```

Translate one saved calendar schedule into the other scheduler's
initial state.

**Parameters**

- `key` (*str*): Card identity.
- `source` (*str*): Scheduler that produced the grade.
- `state` (*str*): Serialized source state.
- `due` (*float*): Original due timestamp.
- `rating` (*Rating*): Last calendar grade.

**Returns**

- *str*: Destination state with the same due date and learning phase.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> result = inherited_state(
...     "abc",
...     source="SM-2",
...     state="[8, 180, 2.5]",
...     due=200 * DAY,
...     rating=Rating.Good,
... )
>>> Card.from_json(result).stability
180.0
```

## read_fsrs_card

```python
def read_fsrs_card(
    key: str,
    *,
    previous: str | None,
    due: datetime,
) -> Card
```

Restore a saved FSRS card or start one for the question.

**Parameters**

- `key` (*str*): The question's stable card key.
- `previous` (*str or None*): The saved JSON, if the question has been reviewed.
- `due` (*datetime*): Initial due time for a new card.

**Returns**

- *Card*: The restored or newly scheduled card.

**Examples**

```text
A new card is due at the time of its first review.
```

## review_options

```python
def review_options(
    key: str,
    *,
    mode: str,
    previous: str | None,
    due: float,
    now: float,
) -> dict[Rating, tuple[int, str]]
```

Calculate a consistent set of answer-button intervals from one
scheduling state.

**Parameters**

- `key` (*str*): Card identity.
- `mode` (*str*): SM-2 or FSRS.
- `previous` (*str or None*): Schedule before this answer.
- `due` (*float*): Due timestamp of the previous schedule.
- `now` (*float*): Time of the answer.

**Returns**

- *dict*: Delay in seconds and serialized successor state for each grade.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> review_options(
...     "abc",
...     mode="SM-2",
...     previous=None,
...     due=0,
...     now=0,
... )[Rating.Again][0]
60
```
{% endraw %}
