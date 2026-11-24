---
title: alto.notation_excerpts
parent: api
package: alto
permalink: /api/alto.notation_excerpts/
---
{% raw %}
Public-domain piano excerpts available for offline notation practice.

## Excerpt

<div class="api-signature" markdown="1">

```python
Excerpt(
    folder: Path,
    credit: str,
    targets: tuple[str, ...],
)
```

{% endraw %}{% include api-source.html name="Excerpt" line=14 %}{% raw %}

</div>

A versioned score and its visible notation components in SVG marker
order.

## excerpts

<div class="api-signature" markdown="1">

```python
@cache
def excerpts() -> dict[str, Excerpt]
```

{% endraw %}{% include api-source.html name="excerpts" line=26 %}{% raw %}

</div>

Read the bundled excerpt manifests.

**Returns**

- *dict*: Passages keyed by their permanent, versioned directory names.

## passages_by_term

<div class="api-signature" markdown="1">

```python
@cache
def passages_by_term() -> dict[str, dict[str, list[int]]]
```

{% endraw %}{% include api-source.html name="passages_by_term" line=55 %}{% raw %}

</div>

Group score locations by term and passage so dense passages do not
dominate the selection.

**Returns**

- *dict*: Matching marker indices for each term in each passage.
{% endraw %}
