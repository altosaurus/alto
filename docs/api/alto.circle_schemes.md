---
title: alto.circle_schemes
parent: api
package: alto
api_components: [{"title": "CellMaker", "url": "/api/alto.circle_schemes/class-cellmaker/"}, {"title": "CustomRecord", "url": "/api/alto.circle_schemes/class-customrecord/"}, {"title": "Scheme", "url": "/api/alto.circle_schemes/class-scheme/"}, {"title": "clean_record", "url": "/api/alto.circle_schemes/function-clean_record/"}, {"title": "custom_scheme", "url": "/api/alto.circle_schemes/function-custom_scheme/"}, {"title": "dump_customs", "url": "/api/alto.circle_schemes/function-dump_customs/"}, {"title": "hex_of", "url": "/api/alto.circle_schemes/function-hex_of/"}, {"title": "hsl_of", "url": "/api/alto.circle_schemes/function-hsl_of/"}, {"title": "load_customs", "url": "/api/alto.circle_schemes/function-load_customs/"}, {"title": "next_custom_key", "url": "/api/alto.circle_schemes/function-next_custom_key/"}, {"title": "preset", "url": "/api/alto.circle_schemes/function-preset/"}, {"title": "record_of", "url": "/api/alto.circle_schemes/function-record_of/"}, {"title": "resolve", "url": "/api/alto.circle_schemes/function-resolve/"}, {"title": "rgb_of", "url": "/api/alto.circle_schemes/function-rgb_of/"}, {"title": "signature_of", "url": "/api/alto.circle_schemes/function-signature_of/"}]
permalink: /api/alto.circle_schemes/
---
{% raw %}
The color schemes of the circle of fifths: the presets, and the schemes
a user makes.

## Classes

- [`CellMaker`](class-cellmaker/) — A function that gives the cell at a place on a ring its quiet and lit colors.
- [`CustomRecord`](class-customrecord/) — A scheme of the user's own, as it is saved.
- [`Scheme`](class-scheme/) — A color scheme for the circle.

## Functions

- [`rgb_of`](function-rgb_of/) — Turn a color into red, green and blue, keeping a dark circle's cells from getting too bright.
- [`hex_of`](function-hex_of/) — Write a color as "#rrggbb".
- [`hsl_of`](function-hsl_of/) — Read a color written as "#rrggbb".
- [`signature_of`](function-signature_of/) — Return how far a place is from C, with flats as negative: the key signature of the major key there.
- [`preset`](function-preset/) — Return a preset by its key.
- [`record_of`](function-record_of/) — Make the record of a scheme of the user's own.
- [`clean_record`](function-clean_record/) — Check one saved scheme of the user's own, and tidy it.
- [`custom_scheme`](function-custom_scheme/) — Make a scheme from one of the user's own records.
- [`dump_customs`](function-dump_customs/) — Write the user's own schemes as text to save.
- [`load_customs`](function-load_customs/) — Read the user's own schemes back, leaving out any that are not valid and any beyond the limit.
- [`resolve`](function-resolve/) — Find a scheme by its key, among the presets and the user's own, falling back to the default.
- [`next_custom_key`](function-next_custom_key/) — Return a key that none of the user's schemes has.

<details markdown="1">
<summary>Module notes and examples</summary>

A scheme says what color each of the 24 cells of the circle is when it
is quiet and when it is lit, and whether its wedges
are light, with dark names. The circle blends between the two as a cell
brightens. The disc in the middle is not part of a
scheme: it takes the colors of the app's theme. Nothing here needs Qt,
so the schemes can be tested, saved and shown anywhere;
`alto.ui.circle` turns them into pictures.

A color is a hue (0 to 360), a saturation and a lightness (both 0 to 1).

**Examples**

```console?lang=python&prompt=%3E%3E%3E,...
>>> scheme = preset("cyan-indigo")
>>> scheme.name, scheme.light
('Cyan to indigo', False)
>>> round(
...     scheme.color(
...         "outer", place=0, lift=1.0
...     )[2],
...     2,
... ) > round(
...     scheme.color(
...         "outer", place=0, lift=0.0
...     )[2],
...     2,
... )
True
```

</details>
{% endraw %}

<script type="application/json" id="api-fragments">{"cellmaker": "class-cellmaker/", "customrecord": "class-customrecord/", "scheme": "class-scheme/", "schemecolor": "class-scheme/#schemecolor", "schemenames": "class-scheme/#schemenames", "rgb_of": "function-rgb_of/", "hex_of": "function-hex_of/", "hsl_of": "function-hsl_of/", "signature_of": "function-signature_of/", "preset": "function-preset/", "record_of": "function-record_of/", "clean_record": "function-clean_record/", "custom_scheme": "function-custom_scheme/", "dump_customs": "function-dump_customs/", "load_customs": "function-load_customs/", "resolve": "function-resolve/", "next_custom_key": "function-next_custom_key/"}</script>
{% include api-fragments.html %}
