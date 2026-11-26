---
title: note_words
parent: alto.ui.exercise_view
api_module: alto.ui.exercise_view
package: alto.ui
permalink: /api/alto.ui.exercise_view/function-note_words/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def note_words(
    note: Note,
    *,
    key: int | None = None,
    minor: bool = False,
) -> str
```

{% endraw %}{% include api-source.html name="note_words" line=363 %}{% raw %}

</div>

Return a note's name in words, for a screen reader: "F sharp 4".

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `note` | `Note` | The note. |
| `key` | `int or None, default None` | The major key signature for scale degrees. Without a key context, use letter names. Keyword-only. |
| `minor` | `bool, default False` | Use natural minor scale degrees. Keyword-only. |

**Returns**

| Type | Description |
| --- | --- |
| `str` | The letter, then "sharp", "flat" or "natural" if it has a sign, then the octave number. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> (
...     note_words(Note.parse("F#4")),
...     note_words(Note.parse("Bb3")),
...     note_words(Note.parse("C4")),
... )
('F sharp 4', 'B flat 3', 'C 4')
```
{% endraw %}
