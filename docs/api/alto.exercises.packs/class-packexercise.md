---
title: PackExercise
parent: alto.exercises.packs
api_module: alto.exercises.packs
package: alto.exercises
permalink: /api/alto.exercises.packs/class-packexercise/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
class PackExercise(ChoiceExercise)
```

{% endraw %}{% include api-source.html name="PackExercise" line=60 %}{% raw %}

</div>

A finite set of illustrated multiple-choice cards declared by an
instrument pack.

**Examples**

```text
The viola pack contributes one practice card for every eligible
string and pitch.
```

## PackExercise.options

<div class="api-signature" markdown="1">

```python
@classmethod
def options() -> settings.PackExerciseSettings
```

{% endraw %}{% include api-source.html name="PackExercise.options" line=123 %}{% raw %}

</div>

Return the learner's options for this exercise, creating the
defaults the first time.

**Returns**

| Type | Description |
| --- | --- |
| `PackExerciseSettings` | The shared, editable options, kept under the exercise's class name. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(PackExercise):
...     span = (21, 30)
...     range_clef = "alto"
>>> (
...     Demo.options().range_for("alto"),
...     Demo.options().sound,
... )
((21, 30), None)
>>> _ = settings.pack_exercises.pop("Demo")
```

## PackExercise.is_keyboard

<div class="api-signature" markdown="1">

```python
@property
def is_keyboard() -> bool
```

{% endraw %}{% include api-source.html name="PackExercise.is_keyboard" line=158 %}{% raw %}

</div>

Report whether this is a keyboard interval exercise.

**Returns**

| Type | Description |
| --- | --- |
| `bool` | True when the pack declared the exercise with type ``keyboard-intervals``. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(PackExercise):
...     spec = {"type": "keyboard-intervals"}
>>> Demo().is_keyboard
True
```

## PackExercise.chosen_keys

<div class="api-signature" markdown="1">

```python
@classmethod
def chosen_keys() -> tuple[int, int]
```

{% endraw %}{% include api-source.html name="PackExercise.chosen_keys" line=178 %}{% raw %}

</div>

Find the lowest and highest key a keyboard exercise asks.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of int` | The learner's range if the plugin offers one and it fits the exercise, otherwise the plugin's default range. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(PackExercise):
...     key_span, key_default = (
...         (28, 89),
...         (48, 72),
...     )
>>> Demo.chosen_keys()
(48, 72)
```

## PackExercise.chosen_span

<div class="api-signature" markdown="1">

```python
@classmethod
def chosen_span() -> tuple[str, str]
```

{% endraw %}{% include api-source.html name="PackExercise.chosen_span" line=207 %}{% raw %}

</div>

Name the lowest and highest key a keyboard exercise asks, for
drawing the keyboards over that range.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of str` | The two keys, such as ``("C3", "C5")``. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(PackExercise):
...     key_span, key_default = (
...         (28, 89),
...         (48, 72),
...     )
>>> Demo.chosen_span()
('C3', 'C5')
```

## PackExercise.chosen_intervals

<div class="api-signature" markdown="1">

```python
@classmethod
def chosen_intervals() -> tuple[str, ...]
```

{% endraw %}{% include api-source.html name="PackExercise.chosen_intervals" line=231 %}{% raw %}

</div>

Find the intervals a keyboard exercise asks.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of str` | The learner's choice among the intervals the plugin lists, or all of them if the plugin offers no choice or the choice leaves none. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(PackExercise):
...     interval_names = ("m2", "M2", "m3")
>>> Demo.chosen_intervals()
('m2', 'M2', 'm3')
```

## PackExercise.chosen_manuals

<div class="api-signature" markdown="1">

```python
@classmethod
def chosen_manuals() -> tuple[str, ...]
```

{% endraw %}{% include api-source.html name="PackExercise.chosen_manuals" line=260 %}{% raw %}

</div>

Find the keyboards a keyboard exercise puts its highlighted keys
on.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of str` | The learner's choice among the keyboards the exercise uses, or all of them if the plugin offers no choice or the choice leaves none. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(PackExercise):
...     manual_names = (
...         "Upper manual",
...         "Lower manual",
...     )
>>> Demo.chosen_manuals()
('Upper manual', 'Lower manual')
```

## PackExercise.active_cards

<div class="api-signature" markdown="1">

```python
def active_cards() -> tuple[Question, ...]
```

{% endraw %}{% include api-source.html name="PackExercise.active_cards" line=328 %}{% raw %}

</div>

Build the cards for the learner's settings: the sharps and
flats, the octave, and the range they chose.

**Returns**

| Type | Description |
| --- | --- |
| `tuple of Question` | The cards, or all of the pack's cards for an exercise with no settings, or when the range leaves none. |

**Examples**

```text
An exercise whose pack declares no settings always asks every
card.
```

## PackExercise.sound_instrument

<div class="api-signature" markdown="1">

```python
def sound_instrument(key: str | None) -> str | None
```

{% endraw %}{% include api-source.html name="PackExercise.sound_instrument" line=367 %}{% raw %}

</div>

Play the pack's own sound unless the pack offers the choice and
the learner chose another instrument.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `key` | `str or None` | The key of the pack's instrument. |

**Returns**

| Type | Description |
| --- | --- |
| `str or None` | The learner's chosen instrument if there is one and it is installed, otherwise the pack's own. |

**Examples**

```text
An exercise with no sound setting always plays the pack's
instrument.
```

## PackExercise.sound_options

<div class="api-signature" markdown="1">

```python
@classmethod
def sound_options() -> list[tuple[str, list[tuple[str, str]]]]
```

{% endraw %}{% include api-source.html name="PackExercise.sound_options" line=394 %}{% raw %}

</div>

List the instruments a learner can choose to sound in this
exercise, in the order they are offered.

The instruments that came with the plugin come first, then other
instruments of the same kind (other harpsichords
for a harpsichord), then every other installed instrument,
whatever its kind. An instrument with no recordings on
disk is left out.

**Returns**

| Type | Description |
| --- | --- |
| `list of tuple of str and list of tuple of str and str` | Each group's heading and its instruments as (key, label), with empty groups left out. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from alto.audio import INSTRUMENTS
>>> class Demo(PackExercise):
...     pack_name = "Demo pack"
...     instruments = {}
>>> [
...     heading
...     for heading, _ in Demo.sound_options()
... ]
['Other instruments']
```

## PackExercise.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="PackExercise.practice_signature" line=479 %}{% raw %}

</div>

Identify the pack settings used to generate this catalog.

**Returns**

| Type | Description |
| --- | --- |
| `str` | Signature shared by cards from this exercise revision. |

**Examples**

```text
Adding an eligible pitch changes the signature, and so does
asking sharps and flats or the octave.
```

## PackExercise.refresh

<div class="api-signature" markdown="1">

```python
def refresh(question: Question) -> Question
```

{% endraw %}{% include api-source.html name="PackExercise.refresh" line=534 %}{% raw %}

</div>

Restore the instrument reference on cards saved by the
single-instrument prototype.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `question` | `Question` | Saved question. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | Card with its pack-qualified instrument reference. |

**Examples**

```text
An existing D-string card keeps its original position when a
pack is upgraded.
```

## PackExercise.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="PackExercise.make_question" line=568 %}{% raw %}

</div>

Pick one of the illustrated questions in the pack.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Source of the question choice. |

**Returns**

| Type | Description |
| --- | --- |
| `Question` | The marked position, prompt, and answer choices. |

**Examples**

```text
An open D4 on a viola asks for D.
```

## PackExercise.daily_candidates

<div class="api-signature" markdown="1">

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

{% endraw %}{% include api-source.html name="PackExercise.daily_candidates" line=588 %}{% raw %}

</div>

Visit each question in the pack once in shuffled order.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `rng` | `random.Random` | Source of the order and button selection. |

**Yields**

- *Question*: Each distinct marked position.

**Examples**

```text
Open G and G on the C string yield separate cards.
```

## PackExercise.card_count

<div class="api-signature" markdown="1">

```python
def card_count() -> int
```

{% endraw %}{% include api-source.html name="PackExercise.card_count" line=610 %}{% raw %}

</div>

Count the distinct questions in the exercise.

**Returns**

| Type | Description |
| --- | --- |
| `int` | Number of cards in this exercise. |

**Examples**

```text
The viola example offers twenty positions.
```
{% endraw %}
