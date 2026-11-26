---
title: QuestionTexts
parent: alto.ui.database_page
api_module: alto.ui.database_page
package: alto.ui
permalink: /api/alto.ui.database_page/class-questiontexts/
---
{% raw %}
<div class="api-signature" markdown="1">

```python
QuestionTexts()
```

{% endraw %}{% include api-source.html name="QuestionTexts" line=353 %}{% raw %}

</div>

Describes stored questions in words, remembering each one so it is
worked out only once.

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> texts = QuestionTexts()
>>> texts("NoteNames", key="k", payload=None)
'(no longer stored)'
```

**Constructor**

Create an empty memory.

**Constructor examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> QuestionTexts()._described
{}
```
{% endraw %}
