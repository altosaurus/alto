---
title: alto.exercises.packs
parent: api
package: alto.exercises
permalink: /api/alto.exercises.packs/
---
{% raw %}
Load third-party instrument packs from ZIP archives and authoring
folders.

## PackExercise

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

### PackExercise.options

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

- *PackExerciseSettings*: The shared, editable options, kept under the exercise's class name.

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

### PackExercise.is_keyboard

<div class="api-signature" markdown="1">

```python
@property
def is_keyboard() -> bool
```

{% endraw %}{% include api-source.html name="PackExercise.is_keyboard" line=158 %}{% raw %}

</div>

Report whether this is a keyboard interval exercise.

**Returns**

- *bool*: True when the pack declared the exercise with type ``keyboard-intervals``.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(PackExercise):
...     spec = {"type": "keyboard-intervals"}
>>> Demo().is_keyboard
True
```

### PackExercise.chosen_keys

<div class="api-signature" markdown="1">

```python
@classmethod
def chosen_keys() -> tuple[int, int]
```

{% endraw %}{% include api-source.html name="PackExercise.chosen_keys" line=178 %}{% raw %}

</div>

Find the lowest and highest key a keyboard exercise asks.

**Returns**

- *tuple of int*: The learner's range if the plugin offers one and it fits the exercise, otherwise the plugin's default range.

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

### PackExercise.chosen_span

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

- *tuple of str*: The two keys, such as ``("C3", "C5")``.

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

### PackExercise.chosen_intervals

<div class="api-signature" markdown="1">

```python
@classmethod
def chosen_intervals() -> tuple[str, ...]
```

{% endraw %}{% include api-source.html name="PackExercise.chosen_intervals" line=231 %}{% raw %}

</div>

Find the intervals a keyboard exercise asks.

**Returns**

- *tuple of str*: The learner's choice among the intervals the plugin lists, or all of them if the plugin offers no choice or the choice leaves none.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> class Demo(PackExercise):
...     interval_names = ("m2", "M2", "m3")
>>> Demo.chosen_intervals()
('m2', 'M2', 'm3')
```

### PackExercise.chosen_manuals

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

- *tuple of str*: The learner's choice among the keyboards the exercise uses, or all of them if the plugin offers no choice or the choice leaves none.

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

### PackExercise.active_cards

<div class="api-signature" markdown="1">

```python
def active_cards() -> tuple[Question, ...]
```

{% endraw %}{% include api-source.html name="PackExercise.active_cards" line=328 %}{% raw %}

</div>

Build the cards for the learner's settings: the sharps and
flats, the octave, and the range they chose.

**Returns**

- *tuple of Question*: The cards, or all of the pack's cards for an exercise with no settings, or when the range leaves none.

**Examples**

```text
An exercise whose pack declares no settings always asks every
card.
```

### PackExercise.sound_instrument

<div class="api-signature" markdown="1">

```python
def sound_instrument(key: str | None) -> str | None
```

{% endraw %}{% include api-source.html name="PackExercise.sound_instrument" line=367 %}{% raw %}

</div>

Play the pack's own sound unless the pack offers the choice and
the learner chose another instrument.

**Parameters**

- `key` (*str or None*): The key of the pack's instrument.

**Returns**

- *str or None*: The learner's chosen instrument if there is one and it is installed, otherwise the pack's own.

**Examples**

```text
An exercise with no sound setting always plays the pack's
instrument.
```

### PackExercise.sound_options

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

- *list of tuple of str and list of tuple of str and str*: Each group's heading and its instruments as (key, label), with empty groups left out.

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

### PackExercise.practice_signature

<div class="api-signature" markdown="1">

```python
def practice_signature() -> str
```

{% endraw %}{% include api-source.html name="PackExercise.practice_signature" line=479 %}{% raw %}

</div>

Identify the pack settings used to generate this catalog.

**Returns**

- *str*: Signature shared by cards from this exercise revision.

**Examples**

```text
Adding an eligible pitch changes the signature, and so does
asking sharps and flats or the octave.
```

### PackExercise.refresh

<div class="api-signature" markdown="1">

```python
def refresh(question: Question) -> Question
```

{% endraw %}{% include api-source.html name="PackExercise.refresh" line=534 %}{% raw %}

</div>

Restore the instrument reference on cards saved by the
single-instrument prototype.

**Parameters**

- `question` (*Question*): Saved question.

**Returns**

- *Question*: Card with its pack-qualified instrument reference.

**Examples**

```text
An existing D-string card keeps its original position when a
pack is upgraded.
```

### PackExercise.make_question

<div class="api-signature" markdown="1">

```python
def make_question(rng: random.Random) -> Question
```

{% endraw %}{% include api-source.html name="PackExercise.make_question" line=568 %}{% raw %}

</div>

Pick one of the illustrated questions in the pack.

**Parameters**

- `rng` (*random.Random*): Source of the question choice.

**Returns**

- *Question*: The marked position, prompt, and answer choices.

**Examples**

```text
An open D4 on a viola asks for D.
```

### PackExercise.daily_candidates

<div class="api-signature" markdown="1">

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

{% endraw %}{% include api-source.html name="PackExercise.daily_candidates" line=588 %}{% raw %}

</div>

Visit each question in the pack once in shuffled order.

**Parameters**

- `rng` (*random.Random*): Source of the order and button selection.

**Yields**

- *Question*: Each distinct marked position.

**Examples**

```text
Open G and G on the C string yield separate cards.
```

### PackExercise.card_count

<div class="api-signature" markdown="1">

```python
def card_count() -> int
```

{% endraw %}{% include api-source.html name="PackExercise.card_count" line=610 %}{% raw %}

</div>

Count the distinct questions in the exercise.

**Returns**

- *int*: Number of cards in this exercise.

**Examples**

```text
The viola example offers twenty positions.
```

## read_controls

<div class="api-signature" markdown="1">

```python
def read_controls(
    value: object,
    *,
    where: str,
    kinds: tuple[str, ...] = CONTROL_KINDS,
) -> dict[str, str | bool]
```

{% endraw %}{% include api-source.html name="read_controls" line=640 %}{% raw %}

</div>

Validate the settings a pack offers for one of its exercises.

**Parameters**

- `value` (*object*): The exercise's ``settings`` entry: an object that may hold ``sound`` (the label of a switch that plays the pack's own sound), ``range`` (a clef to draw a range selector on, or true for the keys of a keyboard exercise), ``accidentals`` and ``octave`` (true for a switch), ``intervals`` (true for a choice of intervals), ``manuals`` (true for a choice of keyboards), or None.
- `where` (*str*): The exercise id, for diagnostics. Keyword-only.
- `kinds` (*tuple of str, default CONTROL_KINDS*): The settings this kind of exercise can have. Keyword-only.

**Returns**

- *dict of str to str or bool*: The declared settings by kind; empty when the pack declares none.

**Raises**

- *ValueError*: If the entry has an unknown kind or a value of the wrong type.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_controls(
...     {"range": "alto", "octave": True},
...     where="pack.v.notes",
... )
{'range': 'alto', 'octave': True}
>>> read_controls(
...     {"range": True, "intervals": True},
...     where="pack.v.keys",
...     kinds=KEYBOARD_CONTROL_KINDS,
... )
{'range': True, 'intervals': True}
>>> read_controls(None, where="pack.v.notes")
{}
```

## read_pack

<div class="api-signature" markdown="1">

```python
def read_pack(path: Path) -> list[type[PackExercise]]
```

{% endraw %}{% include api-source.html name="read_pack" line=1425 %}{% raw %}

</div>

Read and validate every exercise before making any of them
available.

**Parameters**

- `path` (*Path*): A pack.json file or a ZIP containing it at the root.

**Returns**

- *list of type*: Exercise classes with stable identifiers.

**Raises**

- *ValueError*: If the file or one of its exercises has an invalid format.

**Examples**

```text
The viola example contributes note identification and instrument
anatomy exercises.
```

## pack_manifests

<div class="api-signature" markdown="1">

```python
def pack_manifests(folder: Path) -> tuple[list[Path], list[str]]
```

{% endraw %}{% include api-source.html name="pack_manifests" line=1776 %}{% raw %}

</div>

Find each installed ZIP or folder manifest, including packs that
failed validation.

**Parameters**

- `folder` (*Path*): The plugins directory.

**Returns**

- *tuple of list of Path and list of str*: ZIP files and pack.json files in discovery order, and any discovery errors.

**Examples**

```text
An author can install either viola.zip or viola/pack.json.
```

## installed_pack_info

<div class="api-signature" markdown="1">

```python
def installed_pack_info(path: Path) -> dict
```

{% endraw %}{% include api-source.html name="installed_pack_info" line=1818 %}{% raw %}

</div>

Read a pack's manifest for display or duplicate detection without
loading its media.

**Parameters**

- `path` (*Path*): An installed ZIP or an editable pack.json.

**Returns**

- *dict*: The manifest, or an empty dictionary for an invalid manifest or archive.

**Examples**

```text
A damaged pack can still be listed for removal by filename.
```

## InstalledPlugin

<div class="api-signature" markdown="1">

```python
InstalledPlugin(
    title: str,
    path: Path,
    manifest: Path,
    snapshot: stat_result,
)
```

{% endraw %}{% include api-source.html name="InstalledPlugin" line=1857 %}{% raw %}

</div>

One pack in the plugins folder, as listed for removal.

**Attributes**

- `title` (*str*): The pack's name, or its file name without the .zip extension when the manifest cannot be read.
- `path` (*Path*): The ZIP file or editable pack folder that removal moves to the trash.
- `manifest` (*Path*): The ZIP or the folder's pack.json.
- `snapshot` (*stat_result*): The state of ``path`` when it was listed, used to notice a change before removal.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> import os
>>> plugin = InstalledPlugin(
...     title="Viola",
...     path=Path("viola.zip"),
...     manifest=Path("viola.zip"),
...     snapshot=os.stat("."),
... )
>>> plugin.title
'Viola'
```

## installed_plugins

<div class="api-signature" markdown="1">

```python
def installed_plugins(folder: Path) -> tuple[list[InstalledPlugin], list[str]]
```

{% endraw %}{% include api-source.html name="installed_plugins" line=1895 %}{% raw %}

</div>

List the packs in the plugins folder, including damaged ones, so
each can be removed.

**Parameters**

- `folder` (*Path*): The plugins directory.

**Returns**

- *tuple of list of InstalledPlugin and list of str*: The packs in discovery order, and any discovery errors.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> from pathlib import Path
>>> installed_plugins(
...     Path("no-such-plugins-folder")
... )
([], [])
```

## install_pack

<div class="api-signature" markdown="1">

```python
def install_pack(
    source: Path,
    *,
    folder: Path,
    expected_id: str | None = None,
    replacing: InstalledPlugin | None = None,
) -> str
```

{% endraw %}{% include api-source.html name="install_pack" line=1946 %}{% raw %}

</div>

Validate a copy of the selected ZIP and install it for the next
startup.

**Parameters**

- `source` (*Path*): The downloaded instrument pack ZIP.
- `folder` (*Path*): The plugins directory used at startup.
- `expected_id` (*str or None*): The manifest ID assigned to a registered download.
- `replacing` (*InstalledPlugin or None*): The previously selected ZIP to replace after validation.

**Returns**

- *str*: The installed pack's display name.

**Raises**

- *ValueError*: If the ZIP is invalid or conflicts with an existing installation.
- *OSError*: If the installation cannot be read or written.

**Examples**

```text
Installing a downloaded viola.zip adds both of its exercises on the
next launch.
```

## load_packs

<div class="api-signature" markdown="1">

```python
def load_packs(folder: Path) -> list[str]
```

{% endraw %}{% include api-source.html name="load_packs" line=2076 %}{% raw %}

</div>

Register valid packs and return readable errors for any packs that
were skipped.

**Parameters**

- `folder` (*Path*): The plugins folder containing pack ZIPs or editable pack folders.

**Returns**

- *list of str*: File names and reasons for packs that could not be loaded.

**Examples**

```text
A missing plugins folder yields an empty list.
```
{% endraw %}
