---
title: alto.lessons.packs
parent: api
package: alto.lessons
permalink: /api/alto.lessons.packs/
---
{% raw %}
Turn the lessons that an instrument plugin declares into `Lesson`s that Alto lists and shows.

A plugin describes each lesson in its manifest as plain text and small objects: paragraphs, an optional picture of its own
instrument, notes to hear, and a question with buttons. This module checks all of that and builds the same `Lesson` and `Step`
objects the built-in lessons use, so the lesson pages need to know nothing about any particular plugin or instrument.

**Examples**

```pycon
>>> inline("A **scroll** is the carved end.")
'A <b>scroll</b> is the carved end.'
```

## inline

```python
def inline(text: str) -> str
```

Escape plain text for a lesson page, turning ``**word**`` into bold type for a term being defined.

**Parameters**

- `text` (*str*): Plain text from a manifest.

**Returns**

- *str*: Simple HTML.

**Examples**

```pycon
>>> inline("The **nut** & the bridge.")
'The <b>nut</b> &amp; the bridge.'
```

## read_lessons

```python
def read_lessons(
    value: object,
    *,
    pack_id: str,
    pack_name: str,
    instruments: Mapping[str, PackInstrument],
    exercises: Mapping[str, str],
    icons: Mapping[str, str] | None = None,
) -> tuple[Lesson, ...]
```

Validate the optional ``lessons`` list of a plugin manifest and build its lessons.

**Parameters**

- `value` (*object*): The manifest's ``lessons`` entry, or None when the plugin has no lessons.
- `pack_id` (*str*): The plugin's id, which qualifies each lesson's key. Keyword-only.
- `pack_name` (*str*): The plugin's display name, used as a lesson's category when it names none. Keyword-only.
- `instruments` (*mapping of str to PackInstrument*): The plugin's instruments by qualified key, which pictures and sounds refer to. Keyword-only.
- `exercises` (*mapping of str to str*): The plugin's exercises, from the id the manifest uses to the key Alto registers it under. Keyword-only.
- `icons` (*mapping of str to str or None, default None*): The plugin's icons by the file name the manifest uses, already read. Keyword-only.

**Returns**

- *tuple of Lesson*: The lessons, in the order the manifest lists them.

**Raises**

- *ValueError*: If a lesson, step, picture, or question is malformed, or refers to something the plugin does not declare.

**Examples**

```pycon
>>> read_lessons(None, pack_id="demo", pack_name="Demo", instruments={}, exercises={})
()
```

## read_picture

```python
def read_picture(
    spec: object,
    *,
    where: str,
    pack_id: str,
    instruments: Mapping[str, PackInstrument],
) -> PicturePosition | FingerboardPosition
```

Build a step's instrument picture: a note on a string, or a marked place on the picture.

**Parameters**

- `spec` (*object*): The picture's manifest object. Give ``string`` and ``note`` for a note on a string, or ``point`` for a place.
- `where` (*str*): Which lesson and step this is, for messages. Keyword-only.
- `pack_id` (*str*): The plugin's id. Keyword-only.
- `instruments` (*mapping of str to PackInstrument*): The plugin's instruments by qualified key. Keyword-only.

**Returns**

- *PicturePosition or FingerboardPosition*: What the step's picture shows.

**Raises**

- *ValueError*: If the picture is malformed or refers to something the plugin does not declare.
{% endraw %}
