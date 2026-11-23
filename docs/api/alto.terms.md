---
title: alto.terms
parent: api
package: alto
permalink: /api/alto.terms/
---
{% raw %}
Glossary entries that an installed plugin supplies, kept apart from the built-in ones.

A plugin describes each entry in its manifest as plain text, and may show one of its own instrument pictures with it. The glossary
page merges these with the built-in terms and lists them under their own names.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> entry = PluginTerm(name="scroll", pack="Demo", definition="The carved end.", lessons=("pack.demo.parts",))
>>> register_term(entry)
>>> PLUGIN_TERMS["scroll"] is entry
True
>>> _ = PLUGIN_TERMS.pop("scroll")
```

## PluginTerm

```python
PluginTerm(
    name: str,
    pack: str,
    definition: str,
    guide: str = '',
    picture: PicturePosition | None = None,
    caption: str = '',
    exercises: tuple[str, ...] = (),
    lessons: tuple[str, ...] = (),
)
```

One glossary entry from a plugin.

**Attributes**

- `name` (*str*): The term, as listed.
- `pack` (*str*): The plugin's display name.
- `definition` (*str*): What the term means, as simple HTML.
- `guide` (*str*): How to recognize or use it, as simple HTML. May be empty.
- `picture` (*PicturePosition or None*): An instrument picture to show beside the text, with the term marked on it. None for none.
- `caption` (*str*): The words under the picture. May be empty.
- `exercises` (*tuple of str*): The registered keys of the exercises to offer as practice.
- `lessons` (*tuple of str*): The keys of the lessons to offer.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> PluginTerm(name="nut", pack="Demo", definition="It holds the strings.").exercises
()
```

## register_term

```python
def register_term(entry: PluginTerm) -> None
```

Add a plugin's glossary entry.

**Parameters**

- `entry` (*PluginTerm*): The entry.

**Raises**

- *ValueError*: If another plugin already supplies the same term.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> register_term(PluginTerm(name="bridge", pack="Demo", definition="It lifts the strings."))
>>> register_term(PluginTerm(name="bridge", pack="Other", definition="Again."))
Traceback (most recent call last):
...
ValueError: The term bridge is already supplied by Demo.
>>> _ = PLUGIN_TERMS.pop("bridge")
```

## read_terms

```python
def read_terms(
    value: object,
    *,
    pack_id: str,
    pack_name: str,
    instruments: Mapping[str, PackInstrument],
    exercises: Mapping[str, str],
    lessons: Mapping[str, str],
) -> tuple[PluginTerm, ...]
```

Validate the optional ``glossary`` list of a plugin manifest.

**Parameters**

- `value` (*object*): The manifest's ``glossary`` entry: a list of objects with a ``term`` and a ``definition``, and optionally a ``guide``, a ``picture`` with a ``caption``, and the ids of related ``exercises`` and ``lessons``. None when there is none.
- `pack_id` (*str*): The plugin's id. Keyword-only.
- `pack_name` (*str*): The plugin's display name. Keyword-only.
- `instruments` (*mapping of str to PackInstrument*): The plugin's instruments by qualified key. Keyword-only.
- `exercises` (*mapping of str to str*): The plugin's exercises, from the id the manifest uses to the key Alto registers it under. Keyword-only.
- `lessons` (*mapping of str to str*): The plugin's lessons, from the id the manifest uses to the key Alto registers it under. Keyword-only.

**Returns**

- *tuple of PluginTerm*: The entries, in the order the manifest lists them.

**Raises**

- *ValueError*: If an entry is malformed, repeats a term, or links to an exercise or lesson the plugin does not declare.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> read_terms(None, pack_id="demo", pack_name="Demo", instruments={}, exercises={}, lessons={})
()
>>> read_terms([{"term": "nut", "definition": "It holds the strings."}], pack_id="demo", pack_name="Demo",
...            instruments={}, exercises={}, lessons={})[0].name
'nut'
```
{% endraw %}
