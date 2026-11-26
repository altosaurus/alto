---
title: alto.terms
parent: api
package: alto
api_components: [{"title": "PluginTerm", "url": "/api/alto.terms/class-pluginterm/"}, {"title": "read_terms", "url": "/api/alto.terms/function-read_terms/"}, {"title": "register_term", "url": "/api/alto.terms/function-register_term/"}]
permalink: /api/alto.terms/
---
{% raw %}
Glossary entries that an installed plugin supplies, kept apart from the
built-in ones.

## Classes

- [`PluginTerm`](class-pluginterm/) — One glossary entry from a plugin.

## Functions

- [`register_term`](function-register_term/) — Add a plugin's glossary entry.
- [`read_terms`](function-read_terms/) — Validate the optional ``glossary`` list of a plugin manifest.

<details markdown="1">
<summary>Module notes and examples</summary>

A plugin describes each entry in its manifest as plain text, and may
show one of its own instrument pictures with it. The glossary
page merges these with the built-in terms and lists them under their own
names.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> entry = PluginTerm(
...     name="scroll",
...     pack="Demo",
...     definition="The carved end.",
...     lessons=("pack.demo.parts",),
... )
>>> register_term(entry)
>>> PLUGIN_TERMS["scroll"] is entry
True
>>> _ = PLUGIN_TERMS.pop("scroll")
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"pluginterm": "class-pluginterm/", "register_term": "function-register_term/", "read_terms": "function-read_terms/"}</script>
{% include api-fragments.html %}
