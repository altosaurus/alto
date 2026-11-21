---
title: alto.exercises.packs
parent: api
package: alto.exercises
permalink: /api/alto.exercises.packs/
---
{% raw %}
Load third-party instrument packs from ZIP archives and authoring folders.

## PackExercise

```python
class PackExercise(ChoiceExercise)
```

A finite set of illustrated multiple-choice cards declared by an instrument pack.

**Examples**

```pycon
The viola pack contributes one practice card for every eligible string and pitch.
```

### PackExercise.options

```python
@classmethod
def options() -> settings.PackExerciseSettings
```

Return the learner's options for this exercise, creating the defaults the first time.

**Returns**

- *PackExerciseSettings*: The shared, editable options, kept under the exercise's class name.

**Examples**

```pycon
>>> class Demo(PackExercise):
...     span = (21, 30)
...     range_clef = "alto"
>>> Demo.options().range_for("alto"), Demo.options().sound
((21, 30), None)
>>> _ = settings.pack_exercises.pop("Demo")
```

### PackExercise.is_keyboard

```python
@property
def is_keyboard() -> bool
```

Report whether this is a keyboard interval exercise.

**Returns**

- *bool*: True when the pack declared the exercise with type ``keyboard-intervals``.

**Examples**

```pycon
>>> class Demo(PackExercise):
...     spec = {"type": "keyboard-intervals"}
>>> Demo().is_keyboard
True
```

### PackExercise.chosen_keys

```python
@classmethod
def chosen_keys() -> tuple[int, int]
```

Find the lowest and highest key a keyboard exercise asks.

**Returns**

- *tuple of int*: The learner's range if the plugin offers one and it fits the exercise, otherwise the plugin's default range.

**Examples**

```pycon
>>> class Demo(PackExercise):
...     key_span, key_default = (28, 89), (48, 72)
>>> Demo.chosen_keys()
(48, 72)
```

### PackExercise.chosen_span

```python
@classmethod
def chosen_span() -> tuple[str, str]
```

Name the lowest and highest key a keyboard exercise asks, for drawing the keyboards over that range.

**Returns**

- *tuple of str*: The two keys, such as ``("C3", "C5")``.

**Examples**

```pycon
>>> class Demo(PackExercise):
...     key_span, key_default = (28, 89), (48, 72)
>>> Demo.chosen_span()
('C3', 'C5')
```

### PackExercise.chosen_intervals

```python
@classmethod
def chosen_intervals() -> tuple[str, ...]
```

Find the intervals a keyboard exercise asks.

**Returns**

- *tuple of str*: The learner's choice among the intervals the plugin lists, or all of them if the plugin offers no choice or the choice leaves none.

**Examples**

```pycon
>>> class Demo(PackExercise):
...     interval_names = ("m2", "M2", "m3")
>>> Demo.chosen_intervals()
('m2', 'M2', 'm3')
```

### PackExercise.chosen_manuals

```python
@classmethod
def chosen_manuals() -> tuple[str, ...]
```

Find the keyboards a keyboard exercise puts its highlighted keys on.

**Returns**

- *tuple of str*: The learner's choice among the keyboards the exercise uses, or all of them if the plugin offers no choice or the choice leaves none.

**Examples**

```pycon
>>> class Demo(PackExercise):
...     manual_names = ("Upper manual", "Lower manual")
>>> Demo.chosen_manuals()
('Upper manual', 'Lower manual')
```

### PackExercise.active_cards

```python
def active_cards() -> tuple[Question, ...]
```

Build the cards for the learner's settings: the sharps and flats, the octave, and the range they chose.

**Returns**

- *tuple of Question*: The cards, or all of the pack's cards for an exercise with no settings, or when the range leaves none.

**Examples**

```pycon
An exercise whose pack declares no settings always asks every card.
```

### PackExercise.sound_instrument

```python
def sound_instrument(key: str | None) -> str | None
```

Play the pack's own sound unless the pack offers the choice and the learner chose another instrument.

**Parameters**

- `key` (*str or None*): The key of the pack's instrument.

**Returns**

- *str or None*: The learner's chosen instrument if there is one and it is installed, otherwise the pack's own.

**Examples**

```pycon
An exercise with no sound setting always plays the pack's instrument.
```

### PackExercise.sound_options

```python
@classmethod
def sound_options() -> list[tuple[str, list[tuple[str, str]]]]
```

List the instruments a learner can choose to sound in this exercise, in the order they are offered.

The instruments that came with the plugin come first, then other instruments of the same kind (other harpsichords
for a harpsichord), then every other installed instrument, whatever its kind. An instrument with no recordings on
disk is left out.

**Returns**

- *list of tuple of str and list of tuple of str and str*: Each group's heading and its instruments as (key, label), with empty groups left out.

**Examples**

```pycon
>>> from alto.audio import INSTRUMENTS
>>> class Demo(PackExercise):
...     pack_name = "Demo pack"
...     instruments = {}
>>> [heading for heading, _ in Demo.sound_options()]
['Other instruments']
```

### PackExercise.practice_signature

```python
def practice_signature() -> str
```

Identify the pack settings used to generate this catalog.

**Returns**

- *str*: Signature shared by cards from this exercise revision.

**Examples**

```pycon
Adding an eligible pitch changes the signature, and so does asking sharps and flats or the octave.
```

### PackExercise.refresh

```python
def refresh(question: Question) -> Question
```

Restore the instrument reference on cards saved by the single-instrument prototype.

**Parameters**

- `question` (*Question*): Saved question.

**Returns**

- *Question*: Card with its pack-qualified instrument reference.

**Examples**

```pycon
An existing D-string card keeps its original position when a pack is upgraded.
```

### PackExercise.make_question

```python
def make_question(rng: random.Random) -> Question
```

Pick one of the illustrated questions in the pack.

**Parameters**

- `rng` (*random.Random*): Source of the question choice.

**Returns**

- *Question*: The marked position, prompt, and answer choices.

**Examples**

```pycon
An open D4 on a viola asks for D.
```

### PackExercise.daily_candidates

```python
def daily_candidates(rng: random.Random) -> Iterator[Question]
```

Visit each question in the pack once in shuffled order.

**Parameters**

- `rng` (*random.Random*): Source of the order and button selection.

**Yields**

- *Question*: Each distinct marked position.

**Examples**

```pycon
Open G and G on the C string yield separate cards.
```

### PackExercise.card_count

```python
def card_count() -> int
```

Count the distinct questions in the exercise.

**Returns**

- *int*: Number of cards in this exercise.

**Examples**

```pycon
The viola example offers twenty positions.
```

## read_controls

```python
def read_controls(
    value: object,
    *,
    key: str,
    kinds: tuple[str, ...] = CONTROL_KINDS,
) -> dict[str, str | bool]
```

Validate the settings a pack offers for one of its exercises.

**Parameters**

- `value` (*object*): The exercise's ``settings`` entry: an object that may hold ``sound`` (the label of a switch that plays the pack's own sound), ``range`` (a clef to draw a range selector on, or true for the keys of a keyboard exercise), ``accidentals`` and ``octave`` (true for a switch), ``intervals`` (true for a choice of intervals), ``manuals`` (true for a choice of keyboards), or None.
- `key` (*str*): The exercise id, for diagnostics. Keyword-only.
- `kinds` (*tuple of str, default CONTROL_KINDS*): The settings this kind of exercise can have. Keyword-only.

**Returns**

- *dict of str to str or bool*: The declared settings by kind; empty when the pack declares none.

**Raises**

- *ValueError*: If the entry has an unknown kind or a value of the wrong type.

**Examples**

```pycon
>>> read_controls({"range": "alto", "octave": True}, key="pack.v.notes")
{'range': 'alto', 'octave': True}
>>> read_controls({"range": True, "intervals": True}, key="pack.v.keys", kinds=KEYBOARD_CONTROL_KINDS)
{'range': True, 'intervals': True}
>>> read_controls(None, key="pack.v.notes")
{}
```

## read_pack

```python
def read_pack(path: Path) -> list[type[PackExercise]]
```

Read and validate every exercise before making any of them available.

**Parameters**

- `path` (*Path*): A pack.json file or a ZIP containing it at the root.

**Returns**

- *list of type*: Exercise classes with stable identifiers.

**Raises**

- *ValueError*: If the file or one of its exercises has an invalid format.

**Examples**

```pycon
The viola example contributes note identification and instrument anatomy exercises.
```

## pack_manifests

```python
def pack_manifests(folder: Path) -> tuple[list[Path], list[str]]
```

Find each installed ZIP or folder manifest, including packs that failed validation.

**Parameters**

- `folder` (*Path*): The plugins directory.

**Returns**

- *tuple of list of Path and list of str*: ZIP files and pack.json files in discovery order, and any discovery errors.

**Examples**

```pycon
An author can install either viola.zip or viola/pack.json.
```

## installed_pack_info

```python
def installed_pack_info(path: Path) -> dict
```

Read a pack's manifest for display or duplicate detection without loading its media.

**Parameters**

- `path` (*Path*): An installed ZIP or an editable pack.json.

**Returns**

- *dict*: The manifest, or an empty dictionary for an invalid manifest or archive.

**Examples**

```pycon
A damaged pack can still be listed for removal by filename.
```

## InstalledPlugin

```python
InstalledPlugin(
    title: str,
    path: Path,
    manifest: Path,
    snapshot: stat_result,
)
```

One pack in the plugins folder, as listed for removal.

**Attributes**

- `title` (*str*): The pack's name, or its file name without the .zip extension when the manifest cannot be read.
- `path` (*Path*): The ZIP file or editable pack folder that removal moves to the trash.
- `manifest` (*Path*): The ZIP or the folder's pack.json.
- `snapshot` (*stat_result*): The state of ``path`` when it was listed, used to notice a change before removal.

**Examples**

```pycon
>>> from pathlib import Path
>>> import os
>>> plugin = InstalledPlugin(title="Viola", path=Path("viola.zip"), manifest=Path("viola.zip"), snapshot=os.stat("."))
>>> plugin.title
'Viola'
```

## installed_plugins

```python
def installed_plugins(folder: Path) -> tuple[list[InstalledPlugin], list[str]]
```

List the packs in the plugins folder, including damaged ones, so each can be removed.

**Parameters**

- `folder` (*Path*): The plugins directory.

**Returns**

- *tuple of list of InstalledPlugin and list of str*: The packs in discovery order, and any discovery errors.

**Examples**

```pycon
>>> from pathlib import Path
>>> installed_plugins(Path("no-such-plugins-folder"))
([], [])
```

## install_pack

```python
def install_pack(
    source: Path,
    *,
    folder: Path,
    expected_id: str | None = None,
    replacing: InstalledPlugin | None = None,
) -> str
```

Validate a copy of the selected ZIP and install it for the next startup.

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

```pycon
Installing a downloaded viola.zip adds both of its exercises on the next launch.
```

## load_packs

```python
def load_packs(folder: Path) -> list[str]
```

Register valid packs and return readable errors for any packs that were skipped.

**Parameters**

- `folder` (*Path*): The plugins folder containing pack ZIPs or editable pack folders.

**Returns**

- *list of str*: File names and reasons for packs that could not be loaded.

**Examples**

```pycon
A missing plugins folder yields an empty list.
```
{% endraw %}
