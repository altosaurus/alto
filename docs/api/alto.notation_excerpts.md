---
title: alto.notation_excerpts
parent: api
package: alto
permalink: /api/alto.notation_excerpts/
---
{% raw %}
Public-domain piano excerpts available for offline notation practice.

## Excerpt

```python
Excerpt(
    folder: Path,
    credit: str,
    targets: tuple[str, ...],
)
```

A versioned score and its visible notation components in SVG marker order.

## excerpts

```python
@cache
def excerpts() -> dict[str, Excerpt]
```

Read the bundled excerpt manifests.

**Returns**

- *dict*: Passages keyed by their permanent, versioned directory names.

## passages_by_term

```python
@cache
def passages_by_term() -> dict[str, dict[str, list[int]]]
```

Group score locations by term and passage so dense passages do not dominate the selection.

**Returns**

- *dict*: Matching marker indices for each term in each passage.
{% endraw %}
