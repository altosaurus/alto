---
title: written_signature
parent: alto.theory.key_signatures
api_module: alto.theory.key_signatures
package: alto.theory
permalink: /api/alto.theory.key_signatures/function-written_signature/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
def written_signature(
    clef: str,
    *,
    key: int,
) -> list[Note]
```

{% endraw %}{% include api-source.html name="written_signature" line=120 %}{% raw %}

</div>

Spell a key signature at its conventional staff positions, from left
to right.

**Parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `clef` | `str` | The clef the signature is written in. |
| `key` | `int` | Signed count of sharps or flats. |

**Returns**

| Type | Description |
| --- | --- |
| `list of Note` | Pitches of the printed accidentals, including their octaves and signs. |

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> [
...     str(note)
...     for note in written_signature(
...         "bass", key=-2
...     )
... ]
['B♭2', 'E♭3']
```
{% endraw %}
